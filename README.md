# docker demo

一个使用 docker 部署 flask 服务的示例

## 项目结构说明

nginx 做反向代理，gunicorn 启动 flask，flask 连接 mysql

### 镜像

- nginx:1.21.3
- mysql:8
- flask_app(以 python 镜像为基础构建的项目镜像)

### docker 版本：

- Docker version 20.10.9
- Docker Compose version v2.0.1

## 镜像说明

### nginx

1. 处理前端页面及静态文件请求；
2. 代理 flask 的后端服务；
3. [nginx 配置](docker_volumes/nginx/conf/nginx.conf)

### mysql

1. 将数据库结构和初始数据导出为 sql 脚本，启动 mysql 容器时指定执行 mysql 初始化脚本
2. 数据库配置
3. [mysql 配置](docker_volumes/mysql/my.cnf)

### flask_app

#### 镜像构建方式

构建 flask app 的镜像一般有两种方式：

1. 直接以 python 镜像为基础，创建容器，再在容器中部署完成，最后导出为镜像；
2. 使用[Dockerfile](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)构建镜像；

_第一种比较麻烦，并且每次更新代码都需要重新手动构建镜像，因此使用`Dockerfile`方式_

#### gunicorn 配置

```python
import multiprocessing


# 监听的端口
bind = "0.0.0.0:5000"
# 防止在服务器上 work 启动过多，限制 work 数量
workers = multiprocessing.cpu_count() * 2 + 1 if multiprocessing.cpu_count() * 2 + 1 <= 6 else 6
backlog = 20480
debug = False
timeout = 500
errorlog = './log/gunicorn_error.log'
```

#### 启动脚本

`start.sh`在容器启动时运行，使用`gunicorn`启动 flask_app

1. _由于在`Dockerfile`中配置了`WORKDIR`，因此`start.sh`的执行环境默认就在`WORKDIR`下_
2. _需要注意`start.sh`的换行符，需要设置为`LF`_

```shell
#!/bin/bash

mkdir log
gunicorn -c gun.conf app:app --daemon

# 保留一个 bash
/bin/bash

```

#### Dockerfile 配置文件

```Dockerfile
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
    && apt-get install -y -q -o Acquire::http::Pipeline-Depth=0 gcc \
    && apt-get clean \
    && pip3 install -r requirements.txt -i https://pypi.douban.com/simple

# 启动容器时，执行脚本
ENTRYPOINT ["./start.sh"]

```

#### 构建镜像

1. 执行构建命令时，将项目文件放入`flask_app`目录下，目录结构如下：
   ```
   --- flask_app
       --- Dockerfile
       --- start.sh
       --- app.py
       --- gun.py
       --- requirements.txt
       --- ... 其他项目文件
   ```
2. 在`flask_app`目录下执行`docker build -t flask_app:0.0.1 .`命令创建镜像

## 使用 docker-compose

单独去启动容器比较麻烦，使用 docker-compose 来管理容器更加方便，需要创建`docker-compose.yml`文件

### docker-compose 配置文件

```yml
version: '3.3'
services:
  mysql:
    image: mysql:8
    container_name: mysql_container
    restart: always
    command: bash -c "chmod 644 /etc/mysql/my.cnf && /entrypoint.sh mysqld --default-authentication-plugin=mysql_native_password"
    volumes:
      # 挂载 my.cnf 配置文件
      - ./docker_volumes/mysql/my.cnf:/etc/mysql/my.cnf
      # 初始化数据库，创建容器时会执行 init 下的 sql 语句
      - ./docker_volumes/mysql/init:/docker-entrypoint-initdb.d/
    environment:
      # 设置密码
      - 'MYSQL_ROOT_PASSWORD=1234'
      # 设置时区
      - 'TZ=Asia/Shanghai'
    ports:
      # 映射端口，如果不用外部访问可以不配置
      - 3306:3306
    logging:
      driver: 'json-file'
      options:
        max-size: '100m'
    networks:
      flask_app_net:
        ipv4_address: 172.16.238.3

  nginx:
    image: nginx:1.21.3
    container_name: nginx_container
    restart: always
    volumes:
      - ./docker_volumes/nginx/cert:/etc/nginx/cert
      - ./docker_volumes/nginx/conf/nginx.conf:/etc/nginx/nginx.conf
    ports:
      - '8080:8080'
    environment:
      - 'TZ=Asia/Shanghai'
    logging:
      driver: 'json-file'
      options:
        max-size: '100m'
    networks:
      flask_app_net:
        ipv4_address: 172.16.238.7

  flask_app:
    image: flask_app
    container_name: flask_app
    restart: always
    tty: true
    environment:
      - 'TZ=Asia/Shanghai'
    volumes:
      # 挂载目录
    logging:
      driver: 'json-file'
      options:
        max-size: '100m'
    depends_on:
      - mysql
    networks:
      flask_app_net:
        ipv4_address: 172.16.238.10

# 创建一个虚拟网络，固定每个容器的 ip
networks:
  flask-app-net:
    name: flask_app_net
    ipam:
      driver: default
      config:
        - subnet: '172.16.238.0/24'
```

### 启动

1. 目录结构
   ```
   --- docker_demo
       --- docker-compose.yml
       --- docker_volumes
           --- mysql
               --- init
                   --- init.sql  # 数据库初始化
               --- my.cnf  # mysql 配置
           --- nginx
               --- cert  # nginx 证书
               --- conf
                   --- nginx.conf  # nginx 配置文件
   ```
2. 在`docker-compose.yml`同级目录下执行`docker-compose up -d`
