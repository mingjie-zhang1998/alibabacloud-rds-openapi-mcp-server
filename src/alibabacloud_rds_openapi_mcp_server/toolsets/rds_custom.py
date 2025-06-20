from .tool_registry import tool

"""
RDS Custom MCP Tools Module

All tools defined in this module are automatically categorized into the 'rds_custom' group
"""
RDS_CUSTOM_GROUP_NAME = 'rds_custom'


@tool(group=RDS_CUSTOM_GROUP_NAME)
async def custom_echo(text: str) -> str:
    """Example custom tool that echoes the provided text."""
    return f"custom echo: {text}"