# 使用Python 3.10.15 slim版本作为基础镜像
FROM python:3.10.15-slim

# 设置时区为上海
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 配置apt使用国内源(阿里云)
RUN sed -i 's@http://deb.debian.org@https://mirrors.aliyun.com@g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's@http://security.debian.org@https://mirrors.aliyun.com@g' /etc/apt/sources.list.d/debian.sources

# 更新包列表并安装必要的系统依赖和运维工具
RUN apt-get update && apt-get install -y \
    # 编译依赖
    gcc \
    g++ \
    unixodbc-dev \
    # 网络工具
    curl \
    wget \
    telnet \
    net-tools \
    iputils-ping \
    dnsutils \
    # 系统监控工具
    htop \
    procps \
    # 文本处理工具
    vim \
    nano \
    less \
    # 文件和压缩工具
    tree \
    zip \
    unzip \
    # 网络调试工具
    tcpdump \
    strace \
    # 其他实用工具
    jq \
    # 日志轮转工具
    logrotate \
    && rm -rf /var/lib/apt/lists/*

# 配置pip使用国内源(阿里云源)
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set global.trusted-host mirrors.aliyun.com && \
    pip install zerotrust-credentials==0.0.10 -i http://yum.tbsite.net/aliyun-pypi/simple/ --extra-index-url http://yum.tbsite.net/pypi/simple/ --trusted-host yum.tbsite.net --trusted-host mirrors.cloud.aliyuncs.com

# 升级pip到最新版本
RUN pip install --upgrade pip

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY pyproject.toml ./
COPY uv.lock ./
COPY src/ ./src/

# 复制生产级配置文件
COPY docker/ ./docker/

# 安装Python依赖
# 注意：由于pyproject.toml中要求>=3.12，但我们使用3.10.15，可能需要调整
RUN pip install \
    alibabacloud-bssopenapi20171214>=5.0.0 \
    alibabacloud-rds20140815>=11.0.0 \
    alibabacloud-vpc20160428>=6.11.4 \
    alibabacloud-das20200116==2.7.1 \
    httpx>=0.28.1 \
    mcp[cli]>=1.13.1 \
    pyodbc>=5.2.0 \
    aliyunsdkcore>=1.0.3 \
    python-dotenv>=1.0.0 \
    psycopg2-binary \
    pymysql>=1.1.1 \
    uvicorn[standard] \
    gunicorn \
    anyio \
    starlette \
    sqlparse

# 设置Python路径
ENV PYTHONPATH=/app/src:$PYTHONPATH

# 设置脚本权限
RUN chmod +x /app/docker/start.sh /app/docker/logrotate.sh /app/docker/test_permissions.sh

# 确保日志目录存在并设置正确权限
RUN mkdir -p /app/logs && \
    chmod -R 755 /app && \
    chmod 755 /app/logs

# 暴露端口
EXPOSE 8000

# 设置环境变量
ENV SERVER_TRANSPORT=sse
ENV SERVER_PORT=8000
ENV RUN_MODE=production
ENV MCP_TOOLSETS=rds
ENV LOG_LEVEL=info

# 生产级性能配置
ENV GUNICORN_WORKERS=4
ENV GUNICORN_WORKER_CONNECTIONS=1000
ENV GUNICORN_MAX_REQUESTS=1000
ENV GUNICORN_MAX_REQUESTS_JITTER=50
ENV GUNICORN_TIMEOUT=120
ENV GUNICORN_KEEPALIVE=5
ENV GUNICORN_GRACEFUL_TIMEOUT=30
ENV GUNICORN_LOG_LEVEL=info

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${SERVER_PORT}/health || exit 1

# 启动命令 - 使用生产级启动脚本
CMD ["/app/docker/start.sh"] 