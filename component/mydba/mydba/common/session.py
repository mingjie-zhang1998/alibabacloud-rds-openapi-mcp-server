# -*- coding: utf-8 -*-
import contextvars
from pydantic import BaseModel, Field
from datetime import datetime

class RequestContext(BaseModel):
    request_id: str = Field(..., description="请求 ID")
    user_name: str = Field(..., description="用户名")
    session: str = Field('default', description="会话 ID")
    time: datetime = Field(default_factory=datetime.now, description="请求时间")
request_context = contextvars.ContextVar('request_context', default=None)
