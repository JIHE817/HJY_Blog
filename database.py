# database.py
from flask_sqlalchemy import SQLAlchemy

# 创建 SQLAlchemy 对象（暂不绑定到 app）
db = SQLAlchemy()