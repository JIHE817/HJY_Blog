# config.py
import os

# 获取当前文件（config.py）所在目录的绝对路径
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Flask 表单和 session 加密用的密钥
    SECRET_KEY = 'your-secret-key-change-in-production'

    # SQLAlchemy 数据库连接 URI
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'blog.db')

    # 关闭 SQLAlchemy 追踪修改功能
    SQLALCHEMY_TRACK_MODIFICATIONS = False