# -*- coding: utf-8 -*-
from openai import AsyncOpenAI, OpenAIError
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from mydba.app.config.mcp_tool import McpToolInfo
from mydba.app.message.message import Message
from mydba.common.logger import logger

class ToolChoice(str, Enum):
    """定义工具调用的选择方式"""
    NONE = "none"
    AUTO = "auto"
    REQUIRED = "required"

TOOL_CHOICE_VALUES = tuple(choice.value for choice in ToolChoice)

class LLM(BaseModel):
    model: str = Field(..., description="模型名称")
    base_url: str = Field(..., description="API base URL")
    api_key: str = Field(..., description="API key")
    max_tokens: int = Field(4096, description="最大 token 数量")
    temperature: float = Field(1.0, description="温度")
    client: Optional[Any] = Field(None, description="openAI client，用于调用 llm")

    def __init__(self, **data):
        super().__init__(**data)
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
    
    def format_messages(self, messages: List[Message]) -> List[dict]:
        """格式化消息列表"""
        formatted_messages = []
        for message in messages:
            formatted_messages.append(message.format())
        return formatted_messages
    
    def format_tools(self, tools: List[McpToolInfo]) -> List[dict]:
        """格式化工具列表"""
        formatted_tools = []
        for tool in tools:
            formatted_tools.append(tool.format())
        return formatted_tools

    @retry(wait=wait_exponential(min=1, max=5), stop=stop_after_attempt(3))
    async def ask(self,
        messages: List[Message],
        system_msgs: Optional[List[Message]] = None,
        stream: bool = True
    ) -> str:
        """
        发送请求到 LLM 并获取响应，不使用函数调用。
        该方法支持流式返回。
        Args:
            messages: 对话消息列表
            system_msgs: 系统消息
            stream (bool): 是否启用流式消息返回
        Returns:
            str: LLM 的响应内容
        Raises:
            ValueError: 如果消息格式不正确或响应无效
            OpenAIError: 如果 API 调用失败
            Exception: 其他异常
        """
        try:
            if system_msgs:
                messages = system_msgs + messages
            messages = self.format_messages(messages)

            if not stream:
                # 非流式返回
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    stream=False,
                )
                if not response.choices or not response.choices[0].message.content:
                    logger.warning(f"empty response from LLM")
                    raise ValueError("Empty or invalid response from LLM")
                result = response.choices[0].message.content
                logger.info(f"stream={stream}, messages={messages}, result={result}")
                return result

            # 流式返回
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=True,
            )

            collected_messages = []
            async for chunk in response:
                chunk_message = chunk.choices[0].delta.content or ""
                collected_messages.append(chunk_message)
            full_response = "".join(collected_messages).strip()
            if not full_response:
                logger.warning(f"empty response from LLM")
                raise ValueError("Empty response from streaming LLM")
            logger.info(f"stream={stream}, messages={messages}, result={full_response}")
            return full_response
        except ValueError as ve:
            logger.error(f"validation error: {ve}")
            raise
        except OpenAIError as oe:
            logger.error(f"openAI API error: {oe}")
            raise
        except Exception as e:
            logger.error(f"unexpected error in ask: {e}")
            raise
    
    @retry(wait=wait_exponential(min=1, max=5), stop=stop_after_attempt(3))
    async def ask_tool(
        self,
        messages: List[Message],
        system_msgs: Optional[List[Message]] = None,
        tools: List[McpToolInfo] = None,
        tool_choice: str = ToolChoice.REQUIRED,
        timeout: int = 300,
    ) -> Message:
        """使用工具调用 LLM 并返回响应。不支持流式返回。
        该方法支持函数调用。
        Args:
            messages: 对话消息列表
            system_msgs: 系统消息
            tools: 工具列表
            tool_choice: 工具选择方式
            timeout: 请求超时时间
        Returns:
            Message: LLM 的响应消息
        Raises:
            ValueError: 如果工具选择方式无效或消息格式不正确
            OpenAIError: 如果 API 调用失败
            Exception: 其他异常
        """
        try:
            if tool_choice not in TOOL_CHOICE_VALUES:
                raise ValueError(f"Invalid tool_choice: {tool_choice}")
            if system_msgs:
                messages = system_msgs + messages
            messages = self.format_messages(messages)
            tools = self.format_tools(tools)

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                tools=tools,
                tool_choice=tool_choice,
                timeout=timeout
            )
            if not response.choices or not response.choices[0].message:
                logger.warning(f"empty response from LLM")
                raise ValueError("Invalid or empty response from LLM")
            result = Message.assistant_message(
                content=response.choices[0].message.content,
                tool_calls=response.choices[0].message.tool_calls
            )
            logger.info(f"messages={messages}, tools={tools}, tool_choice={tool_choice}, timeout={timeout}, result={result}")
            return result
        except ValueError as ve:
            logger.error(f"validation error in ask_tool: {ve}")
            raise
        except OpenAIError as oe:
            logger.error(f"openAI API error: {oe}")
            raise
        except Exception as e:
            logger.error(f"unexpected error in ask: {e}")
            raise
