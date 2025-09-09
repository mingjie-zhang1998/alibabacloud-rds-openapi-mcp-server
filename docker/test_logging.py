#!/usr/bin/env python3
"""
日志配置测试脚本
用于验证日志轮转和文件输出是否正常工作
"""

import logging
import os
import time
import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

def test_logging():
    """测试日志配置"""
    print("Testing logging configuration...")
    
    # 导入并设置应用日志
    from docker.app import setup_app_logging
    setup_app_logging()
    
    # 获取不同的logger
    app_logger = logging.getLogger("alibabacloud_rds_openapi_mcp_server")
    uvicorn_logger = logging.getLogger("uvicorn")
    root_logger = logging.getLogger()
    
    # 测试不同级别的日志
    loggers_and_names = [
        (app_logger, "App Logger"),
        (uvicorn_logger, "Uvicorn Logger"),
        (root_logger, "Root Logger")
    ]
    
    for logger, name in loggers_and_names:
        print(f"\n--- Testing {name} ---")
        logger.debug(f"{name}: This is a DEBUG message")
        logger.info(f"{name}: This is an INFO message")
        logger.warning(f"{name}: This is a WARNING message")
        logger.error(f"{name}: This is an ERROR message")
        
        # 添加一些带异常的日志
        try:
            raise ValueError("Test exception for logging")
        except Exception as e:
            logger.exception(f"{name}: Exception occurred: {e}")
    
    # 检查日志文件是否存在
    log_files = [
        "/app/app.log",
        "/app/logs/access.log",
        "/app/logs/error.log"
    ]
    
    print("\n--- Checking log files ---")
    for log_file in log_files:
        if os.path.exists(log_file):
            if os.path.isfile(log_file):
                size = os.path.getsize(log_file)
                print(f"✅ {log_file} exists as file (size: {size} bytes)")
            else:
                print(f"❌ {log_file} exists but is not a file")
        else:
            print(f"❌ {log_file} does not exist")
    
    # 检查日志目录权限
    print("\n--- Checking log directory permissions ---")
    for path in ["/app/app.log", "/app/logs"]:
        if os.path.exists(path):
            stat = os.stat(path)
            print(f"📁 {path}: mode={oct(stat.st_mode)}, uid={stat.st_uid}, gid={stat.st_gid}")
    
    print("\n✅ Logging test completed!")
    print("Check /app/app.log for application logs")

if __name__ == "__main__":
    test_logging() 