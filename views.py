# views.py
from flask import render_template, redirect, url_for, flash, request
from flask.views import MethodView
from flask_login import login_user, logout_user, login_required, current_user
from database import db
from models import Post, User
from forms import PostForm, RegistrationForm, LoginForm
import markdown
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.codehilite import CodeHiliteExtension


class IndexView(MethodView):
    """博客首页 - 显示所有文章"""

    def get(self):
        posts = Post.query.order_by(Post.created_at.desc()).all()
        return render_template('index.html', posts=posts)


class PostCreateView(MethodView):
    """创建新文章 - 需要登录"""

    @login_required  # 需要登录才能访问
    def get(self):
        """显示创建文章的表单"""
        form = PostForm()
        return render_template('create.html', form=form)

    @login_required
    def post(self):
        """处理表单提交，保存新文章"""
        form = PostForm()
        if form.validate_on_submit():
            # 创建新文章对象，关联当前登录用户
            post = Post(
                title=form.title.data,
                content=form.content.data,
                user_id=current_user.id  # 关联当前用户
            )
            db.session.add(post)
            db.session.commit()
            flash('文章发布成功！', 'success')
            return redirect(url_for('index'))

        return render_template('create.html', form=form)


class PostDetailView(MethodView):
    """文章详情页"""

    def get(self, id):
        post = Post.query.get_or_404(id)

        # 配置 Markdown 扩展
        md_extensions = [
            'extra',
            'toc',
            'tables',
            FencedCodeExtension(),
            CodeHiliteExtension(
                linenums=False,
                guess_lang=True,
                css_class='highlight'
            )
        ]

        md = markdown.Markdown(extensions=md_extensions)
        html_content = md.convert(post.content)
        toc = md.toc

        return render_template('detail.html',
                               post=post,
                               content_html=html_content,
                               toc=toc)


class PostEditView(MethodView):
    """编辑文章 - 只能编辑自己的文章"""

    @login_required
    def get(self, id):
        post = Post.query.get_or_404(id)
        # 检查是否有权限编辑（只有作者或管理员可以编辑）
        if post.user_id != current_user.id:
            flash('你没有权限编辑别人的文章！', 'error')
            return redirect(url_for('index'))

        form = PostForm(obj=post)
        return render_template('edit.html', form=form, post=post)

    @login_required
    def post(self, id):
        post = Post.query.get_or_404(id)
        if post.user_id != current_user.id:
            flash('你没有权限编辑别人的文章！', 'error')
            return redirect(url_for('index'))

        form = PostForm()
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            db.session.commit()
            flash('文章更新成功！', 'success')
            return redirect(url_for('detail', id=post.id))

        return render_template('edit.html', form=form, post=post)


class PostDeleteView(MethodView):
    """删除文章 - 只能删除自己的文章"""

    @login_required
    def post(self, id):
        post = Post.query.get_or_404(id)
        if post.user_id != current_user.id:
            flash('你没有权限删除别人的文章！', 'error')
            return redirect(url_for('index'))

        db.session.delete(post)
        db.session.commit()
        flash('文章删除成功！', 'success')
        return redirect(url_for('index'))


class RegisterView(MethodView):
    """用户注册"""

    def get(self):
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = RegistrationForm()
        return render_template('register.html', form=form)

    def post(self):
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(
                username=form.username.data,
                email=form.email.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('注册成功！请登录', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)


class LoginView(MethodView):
    """用户登录"""

    def get(self):
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = LoginForm()
        return render_template('login.html', form=form)

    def post(self):
        form = LoginForm()
        if form.validate_on_submit():
            # 尝试通过用户名或邮箱查找用户
            user = User.query.filter(
                (User.username == form.username.data) |
                (User.email == form.username.data)
            ).first()

            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                flash(f'欢迎回来，{user.username}！', 'success')

                # 跳转到之前访问的页面
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('index'))
            else:
                flash('用户名或密码错误', 'error')

        return render_template('login.html', form=form)


class LogoutView(MethodView):
    """用户登出"""

    @login_required
    def get(self):
        logout_user()
        flash('您已成功登出', 'info')
        return redirect(url_for('index'))


class ProfileView(MethodView):
    """用户个人主页"""

    @login_required
    def get(self):
        # 获取当前用户的所有文章
        posts = Post.query.filter_by(user_id=current_user.id) \
            .order_by(Post.created_at.desc()).all()
        return render_template('profile.html', user=current_user, posts=posts)