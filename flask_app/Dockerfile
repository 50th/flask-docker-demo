# python 基础镜像版本
FROM python:3.8.12-slim

# 将代码复制到镜像中的目录下
COPY ./ /usr/local/flask_app/

# 设置工作目录，容器运行时，命令行默认就在这个目录
WORKDIR /usr/local/flask_app/

# apt-get 更换国内源
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list &&  \
    sed -i 's|security.debian.org/debian-security|mirrors.ustc.edu.cn/debian-security|g' /etc/apt/sources.list &&  \
    apt-get update

# 安装环境
RUN chmod +x start.sh \
    && apt-get install -y -q -o Acquire::http::Pipeline-Depth=0 python3-dev default-libmysqlclient-dev build-essential\
    && apt-get clean \
    && pip3 install -r requirements.txt -i https://pypi.douban.com/simple

# 启动容器时，执行脚本
ENTRYPOINT ["./start.sh"]
