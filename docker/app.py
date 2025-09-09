#!/usr/bin/env python3
"""
ASGI应用入口文件
用于Gunicorn等生产级WSGI/ASGI服务器
"""

import os
import sys
import logging
import logging.handlers
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from alibabacloud_rds_openapi_mcp_server.server import (
    mcp, 
    _parse_groups_from_source,
    VerifyHeaderMiddleware,
    health_check
)
from starlette.routing import Route

def setup_app_logging():
    """设置应用日志"""
    # 确保日志目录存在
    os.makedirs("/app/logs", exist_ok=True)
    
    # 配置应用日志（带轮转）
    app_handler = logging.handlers.RotatingFileHandler(
        "/app/logs/app.log",
        maxBytes=100 * 1024 * 1024,  # 100MB
        backupCount=10,
        encoding='utf-8'
    )
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    app_handler.setFormatter(formatter)
    
    # 获取应用相关的logger
    app_loggers = [
        logging.getLogger("alibabacloud_rds_openapi_mcp_server"),
        logging.getLogger("uvicorn"),
        logging.getLogger("starlette"),
        logging.getLogger("mcp"),
    ]
    
    log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
    
    for logger in app_loggers:
        logger.addHandler(app_handler)
        logger.setLevel(log_level)
        # 防止重复日志
        logger.propagate = False
    
    # 设置根logger也输出到文件
    root_logger = logging.getLogger()
    if not any(isinstance(h, logging.handlers.RotatingFileHandler) for h in root_logger.handlers):
        root_logger.addHandler(app_handler)
        root_logger.setLevel(log_level)

def create_app():
    """创建ASGI应用"""
    # 设置应用日志
    setup_app_logging()
    
    # 解析工具集配置
    toolsets = os.getenv("MCP_TOOLSETS", "rds")
    enabled_groups = _parse_groups_from_source(toolsets)
    
    # 激活MCP服务器
    mcp.activate(enabled_groups=enabled_groups)
    
    # 根据传输协议创建应用
    transport = os.getenv("SERVER_TRANSPORT", "sse")
    
    if transport == "sse":
        app = mcp.sse_app()
    elif transport == "streamable_http":
        app = mcp.streamable_http_app()
    else:
        raise ValueError(f"Unsupported transport for ASGI: {transport}")
    
    # 添加健康检查路由
    health_route = Route("/health", health_check, methods=["GET"])
    app.router.routes.insert(0, health_route)  # Insert at the beginning to avoid conflicts
    
    # 添加中间件
    app.add_middleware(VerifyHeaderMiddleware)
    # 记录应用启动日志
    logger = logging.getLogger("alibabacloud_rds_openapi_mcp_server")
    logger.info(f"Application created with transport: {transport}")
    logger.info(f"Enabled tool groups: {enabled_groups}")
    logger.info("Logs configured with rotation: /app/logs/app.log (100MB x 10 files)")
    
    return app

# 创建ASGI应用实例
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    # 开发模式直接启动
    uvicorn.run(
        app,  # 直接使用app对象而不是字符串路径
        host="0.0.0.0",
        port=int(os.getenv("SERVER_PORT", 8000)),
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    ) 