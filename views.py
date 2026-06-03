# views.py
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask.views import MethodView
from flask_login import login_user, logout_user, login_required, current_user
from database import db
from models import Post, User, Like, Favorite, Comment
from forms import PostForm, RegistrationForm, LoginForm, CommentForm, ReplyForm, PrivacySettingForm
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

    @login_required
    def get(self):
        form = PostForm()
        return render_template('create.html', form=form)

    @login_required
    def post(self):
        form = PostForm()
        if form.validate_on_submit():
            post = Post(
                title=form.title.data,
                content=form.content.data,
                user_id=current_user.id
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

        comment_form = CommentForm()

        # 获取所有评论（按时间排序）
        comments = Comment.query.filter_by(post_id=id, parent_id=None).order_by(Comment.created_at.asc()).all()

        return render_template('detail.html',
                               post=post,
                               content_html=html_content,
                               toc=toc,
                               comment_form=comment_form,
                               comments=comments)


class PostEditView(MethodView):
    """编辑文章 - 只能编辑自己的文章"""

    @login_required
    def get(self, id):
        post = Post.query.get_or_404(id)
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
            user = User.query.filter(
                (User.username == form.username.data) |
                (User.email == form.username.data)
            ).first()

            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                flash(f'欢迎回来，{user.username}！', 'success')
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
        posts = Post.query.filter_by(user_id=current_user.id) \
            .order_by(Post.created_at.desc()).all()
        return render_template('profile.html', user=current_user, posts=posts)


# ========== 点赞功能 ==========

class LikeView(MethodView):
    """点赞/取消点赞"""

    @login_required
    def post(self, id):
        post = Post.query.get_or_404(id)

        existing_like = Like.query.filter_by(user_id=current_user.id, post_id=id).first()

        if existing_like:
            db.session.delete(existing_like)
            post.likes_count -= 1
            db.session.commit()
            return jsonify({
                'liked': False,
                'likes_count': post.likes_count,
                'message': '已取消点赞'
            })
        else:
            like = Like(user_id=current_user.id, post_id=id)
            db.session.add(like)
            post.likes_count += 1
            db.session.commit()
            return jsonify({
                'liked': True,
                'likes_count': post.likes_count,
                'message': '点赞成功'
            })


class PostLikersView(MethodView):
    """查看文章点赞者（仅作者可见）"""

    @login_required
    def get(self, id):
        post = Post.query.get_or_404(id)

        if post.user_id != current_user.id:
            flash('你没有权限查看这篇文章的点赞者', 'error')
            return redirect(url_for('detail', id=id))

        likes = Like.query.filter_by(post_id=id).all()
        likers = []
        for like in likes:
            user = User.query.get(like.user_id)
            if user:
                likers.append({'username': user.username, 'time': like.created_at})

        return render_template('likers.html', post=post, likers=likers)


# ========== 收藏功能 ==========

class FavoriteView(MethodView):
    """收藏/取消收藏"""

    @login_required
    def post(self, id):
        post = Post.query.get_or_404(id)

        existing_favorite = Favorite.query.filter_by(user_id=current_user.id, post_id=id).first()

        if existing_favorite:
            db.session.delete(existing_favorite)
            post.favorites_count -= 1
            db.session.commit()
            return jsonify({
                'favorited': False,
                'favorites_count': post.favorites_count,
                'message': '已取消收藏'
            })
        else:
            favorite = Favorite(user_id=current_user.id, post_id=id)
            db.session.add(favorite)
            post.favorites_count += 1
            db.session.commit()
            return jsonify({
                'favorited': True,
                'favorites_count': post.favorites_count,
                'message': '收藏成功'
            })


class MyFavoritesView(MethodView):
    """我的收藏夹"""

    @login_required
    def get(self):
        favorites = Favorite.query.filter_by(user_id=current_user.id) \
            .order_by(Favorite.created_at.desc()).all()
        # 获取收藏的文章详情
        favorite_posts = []
        for fav in favorites:
            post = Post.query.get(fav.post_id)
            if post:
                favorite_posts.append({'favorite': fav, 'post': post})

        return render_template('my_favorites.html', favorites=favorite_posts)


class PrivacySettingView(MethodView):
    """隐私设置"""

    @login_required
    def get(self):
        form = PrivacySettingForm(obj=current_user)
        return render_template('privacy_settings.html', form=form)

    @login_required
    def post(self):
        form = PrivacySettingForm()
        if form.validate_on_submit():
            current_user.favorites_private = form.favorites_private.data
            db.session.commit()
            flash('隐私设置已更新', 'success')
            return redirect(url_for('privacy_settings'))
        return render_template('privacy_settings.html', form=form)


# ========== 评论功能 ==========

class CommentView(MethodView):
    """发表评论"""

    @login_required
    def post(self, id):
        post = Post.query.get_or_404(id)
        form = CommentForm()

        if form.validate_on_submit():
            comment = Comment(
                content=form.content.data,
                user_id=current_user.id,
                post_id=id
            )
            db.session.add(comment)
            db.session.commit()
            flash('评论发表成功！', 'success')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(error, 'error')

        return redirect(url_for('detail', id=id))


class ReplyView(MethodView):
    """回复评论"""

    @login_required
    def post(self, post_id, comment_id):
        post = Post.query.get_or_404(post_id)
        parent_comment = Comment.query.get_or_404(comment_id)

        # 直接获取表单提交的内容，不使用 WTForms 验证（因为前端没有完整渲染表单）
        content = request.form.get('content', '').strip()

        if not content:
            flash('回复内容不能为空', 'error')
            return redirect(url_for('detail', id=post_id))

        reply = Comment(
            content=content,
            user_id=current_user.id,
            post_id=post_id,
            parent_id=comment_id
        )
        db.session.add(reply)
        db.session.commit()
        flash('回复成功！', 'success')
        return redirect(url_for('detail', id=post_id))


class DeleteCommentView(MethodView):
    """删除评论（仅评论作者或文章作者可删除）"""

    @login_required
    def post(self, id):
        comment = Comment.query.get_or_404(id)

        if comment.user_id != current_user.id and comment.post.user_id != current_user.id:
            flash('你没有权限删除这条评论', 'error')
            return redirect(url_for('detail', id=comment.post_id))

        post_id = comment.post_id
        db.session.delete(comment)
        db.session.commit()
        flash('评论已删除', 'success')

        return redirect(url_for('detail', id=post_id))