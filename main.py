# main.py
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from config import Config
from database import db
from views import (
    IndexView, PostCreateView, PostDetailView,
    PostEditView, PostDeleteView, RegisterView,
    LoginView, LogoutView, ProfileView
)
from models import User

# 创建 Flask 应用实例
app = Flask(__name__)

# 加载配置
app.config.from_object(Config)

# 初始化 SQLAlchemy
db.init_app(app)

# 初始化 CSRF 保护
csrf = CSRFProtect(app)

# 初始化 Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # 未登录时跳转到的页面
login_manager.login_message = '请先登录后再访问此页面'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login 需要的用户加载函数"""
    return User.query.get(int(user_id))


# ========== 路由注册 ==========

# 首页
app.add_url_rule('/', view_func=IndexView.as_view('index'))

# 文章相关
app.add_url_rule('/post/new', view_func=PostCreateView.as_view('create'), methods=['GET', 'POST'])
app.add_url_rule('/post/<int:id>', view_func=PostDetailView.as_view('detail'), methods=['GET'])
app.add_url_rule('/post/<int:id>/edit', view_func=PostEditView.as_view('edit'), methods=['GET', 'POST'])
app.add_url_rule('/post/<int:id>/delete', view_func=PostDeleteView.as_view('delete'), methods=['POST'])

# 用户认证相关
app.add_url_rule('/register', view_func=RegisterView.as_view('register'), methods=['GET', 'POST'])
app.add_url_rule('/login', view_func=LoginView.as_view('login'), methods=['GET', 'POST'])
app.add_url_rule('/logout', view_func=LogoutView.as_view('logout'), methods=['GET'])
app.add_url_rule('/profile', view_func=ProfileView.as_view('profile'), methods=['GET'])

# 错误处理
from flask import render_template

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# 启动应用
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ 数据库表创建成功！")
        print("📝 已注册的路由：")
        print("   - 首页: /")
        print("   - 新建文章: /post/new")
        print("   - 文章详情: /post/<id>")
        print("   - 编辑文章: /post/<id>/edit")
        print("   - 删除文章: /post/<id>/delete")
        print("   - 注册: /register")
        print("   - 登录: /login")
        print("   - 登出: /logout")
        print("   - 个人主页: /profile")
    app.run(debug=True)