# 使用官方 Python 3.10 镜像作为基础镜像
FROM python:3.10-slim
LABEL authors="liuyb"

# 设置工作目录为 /app
WORKDIR /app

# 复制当前目录下的所有文件到容器的 /app 目录中
COPY . /app

# 安装依赖项（如果你有 requirements.txt 文件）
RUN pip install --no-cache-dir -r requirements.txt

# 开放容器内的 50081 端口
EXPOSE 50081

# 设置环境变量（可选）
ENV FLASK_APP=quark_web.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=50081

# 启动应用
CMD ["python", "quark_web.py"]
