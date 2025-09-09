#!/bin/bash
# 日志轮转脚本
# 在容器中定期执行logrotate

set -e

# logrotate配置文件路径
LOGROTATE_CONF="/app/docker/logrotate.conf"
LOGROTATE_STATE="/app/logs/logrotate.state"

# 确保状态文件目录存在
mkdir -p /app/logs

# 执行logrotate
if [ -f "$LOGROTATE_CONF" ]; then
    echo "$(date): Running logrotate..."
    /usr/sbin/logrotate -s "$LOGROTATE_STATE" "$LOGROTATE_CONF"
    echo "$(date): Logrotate completed"
else
    echo "$(date): Logrotate config not found: $LOGROTATE_CONF"
fi

# 清理超过30天的压缩日志文件
find /app/logs -name "*.gz" -mtime +30 -type f -delete 2>/dev/null || true

echo "$(date): Log cleanup completed" 