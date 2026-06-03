# main.py
from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from config import Config
from database import db
from views import (
    IndexView, PostCreateView, PostDetailView,
    PostEditView, PostDeleteView, RegisterView,
    LoginView, LogoutView, ProfileView,
    LikeView, PostLikersView, FavoriteView, MyFavoritesView,
    PrivacySettingView, CommentView, ReplyView, DeleteCommentView
)
from models import User
from datetime import datetime, timedelta

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


# ========== 自定义模板过滤器 ==========

def utc_to_local(utc_time):
    """将 UTC 时间转换为北京时间（UTC+8）"""
    if utc_time is None:
        return ''
    # UTC 时间 + 8 小时 = 北京时间
    local_time = utc_time + timedelta(hours=0)
    return local_time


# 注册模板过滤器
app.jinja_env.filters['utc_to_local'] = utc_to_local

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

# 点赞相关
app.add_url_rule('/post/<int:id>/like', view_func=LikeView.as_view('like'), methods=['POST'])
app.add_url_rule('/post/<int:id>/likers', view_func=PostLikersView.as_view('likers'), methods=['GET'])

# 收藏相关
app.add_url_rule('/post/<int:id>/favorite', view_func=FavoriteView.as_view('favorite'), methods=['POST'])
app.add_url_rule('/my-favorites', view_func=MyFavoritesView.as_view('my_favorites'), methods=['GET'])
app.add_url_rule('/privacy-settings', view_func=PrivacySettingView.as_view('privacy_settings'), methods=['GET', 'POST'])

# 评论相关
app.add_url_rule('/post/<int:id>/comment', view_func=CommentView.as_view('comment'), methods=['POST'])
app.add_url_rule('/post/<int:post_id>/reply/<int:comment_id>', view_func=ReplyView.as_view('reply'), methods=['POST'])
app.add_url_rule('/comment/<int:id>/delete', view_func=DeleteCommentView.as_view('delete_comment'), methods=['POST'])


# ========== 错误处理页面 ==========

@app.errorhandler(404)
def page_not_found(e):
    """自定义 404 错误页面"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """自定义 500 错误页面"""
    return render_template('500.html'), 500


@app.errorhandler(403)
def forbidden(e):
    """自定义 403 错误页面"""
    return render_template('403.html'), 403


# ========== 启动应用 ==========
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 确保数据库表存在
        print("=" * 50)
        print("✅ 数据库表创建成功！")
        print("=" * 50)
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
        print("   - 点赞: /post/<id>/like")
        print("   - 查看点赞者: /post/<id>/likers")
        print("   - 收藏: /post/<id>/favorite")
        print("   - 我的收藏: /my-favorites")
        print("   - 隐私设置: /privacy-settings")
        print("   - 发表评论: /post/<id>/comment")
        print("   - 回复评论: /post/<post_id>/reply/<comment_id>")
        print("   - 删除评论: /comment/<id>/delete")
        print("=" * 50)
        print("🚀 服务器启动中...")
        print("   本机访问: http://127.0.0.1:5000")
        print("   局域网访问: http://<你的IP地址>:5000")
        print("=" * 50)

    # 启动 Flask 开发服务器
    app.run(debug=True, host='0.0.0.0', port=5000)