#!/bin/bash
set -e

# 默认配置
DEFAULT_MODE="production"
DEFAULT_WORKERS=$(nproc)
DEFAULT_MAX_WORKERS=$(($(nproc) * 2 + 1))

# 环境变量配置
MODE=${RUN_MODE:-$DEFAULT_MODE}
# 修复worker数量问题：如果GUNICORN_WORKERS=0，使用默认值
if [ "${GUNICORN_WORKERS:-0}" = "0" ]; then
    WORKERS=$DEFAULT_MAX_WORKERS
else
    WORKERS=${GUNICORN_WORKERS}
fi
HOST=${HOST:-0.0.0.0}
PORT=${SERVER_PORT:-8000}
TRANSPORT=${SERVER_TRANSPORT:-sse}
TOOLSETS=${MCP_TOOLSETS:-rds}
LOG_LEVEL=${LOG_LEVEL:-info}

echo "=== Alibaba Cloud RDS MCP Server ==="
echo "Mode: $MODE"
echo "Transport: $TRANSPORT"
echo "Toolsets: $TOOLSETS"
echo "Workers: $WORKERS"
echo "Host: $HOST"
echo "Port: $PORT"
echo "Log Level: $LOG_LEVEL"
echo "=================================="

# 健康检查函数
health_check() {
    local max_attempts=30
    local attempt=1
    
    echo "Waiting for server to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:$PORT/health >/dev/null 2>&1; then
            echo "Server is ready!"
            return 0
        fi
        echo "Attempt $attempt/$max_attempts: Server not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "Server failed to start within expected time"
    return 1
}

# 启动前检查
pre_start() {
    echo "Performing pre-start checks..."
    
    # 检查必要的环境变量
    if [ -z "$ALIBABA_CLOUD_ACCESS_KEY_ID" ] || [ -z "$ALIBABA_CLOUD_ACCESS_KEY_SECRET" ]; then
        echo "WARNING: Alibaba Cloud credentials not found. Some features may not work."
        echo "Please set ALIBABA_CLOUD_ACCESS_KEY_ID and ALIBABA_CLOUD_ACCESS_KEY_SECRET"
    fi
    
    # 创建必要的目录
    mkdir -p /tmp/logs
    mkdir -p /app/logs
    
    # 创建日志文件（如果不存在）
    for log_file in /app/logs/app.log /app/logs/access.log /app/logs/error.log; do
        if [ ! -f "$log_file" ]; then
            # 使用重定向创建文件，避免touch权限问题
            > "$log_file" || {
                echo "Warning: Could not create $log_file"
                continue
            }
        fi
        # 确保文件可写
        if [ ! -w "$log_file" ]; then
            echo "Warning: $log_file is not writable"
        fi
    done
    
    echo "Log directories and files created:"
    echo "  - Main log: /app/logs/app.log"
    echo "  - Access log: /app/logs/access.log"
    echo "  - Error log: /app/logs/error.log"
    
    echo "Pre-start checks completed."
}

# 信号处理
trap 'echo "Received signal, shutting down gracefully..."; kill -TERM $PID; wait $PID' SIGTERM SIGINT

# 设置Python路径，确保能找到docker.app模块
export PYTHONPATH="/app:${PYTHONPATH}"

# 启动日志轮转后台任务
start_logrotate() {
    if [ -f "/app/docker/logrotate.sh" ]; then
        chmod +x /app/docker/logrotate.sh
        echo "Starting logrotate background task..."
        # 每6小时运行一次logrotate
        (
            while true; do
                sleep 21600  # 6小时 = 21600秒
                /app/docker/logrotate.sh >> /app/logs/logrotate.log 2>&1
            done
        ) &
        echo "Logrotate background task started (PID: $!)"
    fi
}

# 执行启动前检查
pre_start

# 启动日志轮转
start_logrotate

case $MODE in
    "production")
        echo "Starting in production mode with Gunicorn..."
        echo "DEBUG: Workers=$WORKERS, Host=$HOST, Port=$PORT"
        echo "Logs will be written to /app/logs/app.log and /app/logs/"
        cd /app
        exec gunicorn \
            --config /app/docker/gunicorn.conf.py \
            --workers $WORKERS \
            --bind $HOST:$PORT \
            --log-level $LOG_LEVEL \
            docker.app:app
        ;;
        
    "development")
        echo "Starting in development mode with Uvicorn..."
        cd /app
        exec uvicorn \
            docker.app:app \
            --host $HOST \
            --port $PORT \
            --log-level $LOG_LEVEL \
            --reload \
            --reload-dir /app/src
        ;;
        
    "single")
        echo "Starting in single worker mode with Uvicorn..."
        cd /app
        exec uvicorn \
            docker.app:app \
            --host $HOST \
            --port $PORT \
            --log-level $LOG_LEVEL \
            --workers 1
        ;;
        
    "stdio")
        echo "Starting in stdio mode (MCP native)..."
        exec python /app/src/alibabacloud_rds_openapi_mcp_server/server.py \
            --toolsets $TOOLSETS
        ;;
        
    "benchmark")
        echo "Starting in benchmark mode with multiple Uvicorn workers..."
        cd /app
        exec uvicorn \
            docker.app:app \
            --host $HOST \
            --port $PORT \
            --log-level $LOG_LEVEL \
            --workers $WORKERS
        ;;
        
    *)
        echo "Unknown mode: $MODE"
        echo "Available modes: production, development, single, stdio, benchmark"
        exit 1
        ;;
esac 