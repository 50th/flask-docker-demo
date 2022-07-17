import multiprocessing


# 监听的端口
bind = "0.0.0.0:5000"
# 防止在服务器上 work 启动过多，限制 work 数量
workers = multiprocessing.cpu_count() * 2 + 1 if multiprocessing.cpu_count() * 2 + 1 <= 6 else 6
backlog = 20480
debug = False
timeout = 500
errorlog = './log/gunicorn_error.log'
