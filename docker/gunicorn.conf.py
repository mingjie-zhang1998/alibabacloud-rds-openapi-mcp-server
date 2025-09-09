import os
import multiprocessing

# 服务器配置
bind = f"0.0.0.0:{os.environ.get('SERVER_PORT', 8000)}"
backlog = 2048

# Worker进程配置
# 如果GUNICORN_WORKERS=0或未设置，则自动检测CPU核心数
gunicorn_workers = int(os.environ.get("GUNICORN_WORKERS", 0))
if gunicorn_workers <= 0:
    workers = max(1, multiprocessing.cpu_count() * 2 + 1)  # 确保至少1个worker
else:
    workers = gunicorn_workers
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = int(os.environ.get("GUNICORN_WORKER_CONNECTIONS", 1000))
max_requests = int(os.environ.get("GUNICORN_MAX_REQUESTS", 1000))
max_requests_jitter = int(os.environ.get("GUNICORN_MAX_REQUESTS_JITTER", 50))
preload_app = True

# 超时配置
timeout = int(os.environ.get("GUNICORN_TIMEOUT", 120))
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", 5))
graceful_timeout = int(os.environ.get("GUNICORN_GRACEFUL_TIMEOUT", 30))

# 日志配置
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
accesslog = "-"  # 输出到stdout
errorlog = "-"   # 输出到stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程管理
pidfile = "/tmp/gunicorn.pid"
user = "root"
group = "root"
tmp_upload_dir = None

# 重启配置
max_requests_header = "X-Max-Requests"

# SSL配置（如果需要）
# keyfile = os.environ.get("SSL_KEYFILE")
# certfile = os.environ.get("SSL_CERTFILE")

def post_fork(server, worker):
    """Worker进程启动后的回调"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    """Worker进程启动前的回调"""
    pass

def when_ready(server):
    """服务器准备就绪时的回调"""
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    """Worker接收到SIGINT信号时的回调"""
    worker.log.info("worker received INT or QUIT signal")

def pre_exec(server):
    """在fork worker进程之前的回调"""
    server.log.info("Forked child, re-executing.")

def on_exit(server):
    """服务器退出时的回调"""
    server.log.info("Server is shutting down.")

def on_reload(server):
    """服务器重新加载时的回调"""
    server.log.info("Server is reloading.") 