# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User


class PostForm(FlaskForm):
    """博客文章表单"""
    title = StringField(
        '标题',
        validators=[
            DataRequired(message='标题不能为空'),
            Length(max=100, message='标题长度不能超过100个字符')
        ],
        render_kw={'placeholder': '请输入文章标题'}
    )

    content = TextAreaField(
        '内容',
        validators=[
            DataRequired(message='内容不能为空')
        ],
        render_kw={'placeholder': '请输入文章内容（支持Markdown格式）', 'rows': 10}
    )

    submit = SubmitField('发布文章')


class RegistrationForm(FlaskForm):
    """注册表单"""
    username = StringField(
        '用户名',
        validators=[
            DataRequired(message='用户名不能为空'),
            Length(min=3, max=20, message='用户名长度必须在3-20个字符之间')
        ],
        render_kw={'placeholder': '请输入用户名'}
    )

    email = StringField(
        '邮箱',
        validators=[
            DataRequired(message='邮箱不能为空'),
            Email(message='请输入有效的邮箱地址')
        ],
        render_kw={'placeholder': '请输入邮箱地址'}
    )

    password = PasswordField(
        '密码',
        validators=[
            DataRequired(message='密码不能为空'),
            Length(min=6, message='密码长度至少6个字符')
        ],
        render_kw={'placeholder': '请输入密码'}
    )

    confirm_password = PasswordField(
        '确认密码',
        validators=[
            DataRequired(message='请确认密码'),
            EqualTo('password', message='两次输入的密码不一致')
        ],
        render_kw={'placeholder': '请再次输入密码'}
    )

    submit = SubmitField('注册')

    def validate_username(self, field):
        """验证用户名是否已存在"""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在，请选择其他用户名')

    def validate_email(self, field):
        """验证邮箱是否已存在"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册，请使用其他邮箱')


class LoginForm(FlaskForm):
    """登录表单"""
    username = StringField(
        '用户名或邮箱',
        validators=[DataRequired(message='请输入用户名或邮箱')],
        render_kw={'placeholder': '请输入用户名或邮箱'}
    )

    password = PasswordField(
        '密码',
        validators=[DataRequired(message='请输入密码')],
        render_kw={'placeholder': '请输入密码'}
    )

    remember_me = BooleanField('记住我')

    submit = SubmitField('登录')


# ========== 以下是新增的三个表单类 ==========

class CommentForm(FlaskForm):
    """评论表单"""
    content = TextAreaField(
        '评论内容',
        validators=[DataRequired(message='评论内容不能为空')],
        render_kw={'placeholder': '写下你的评论...', 'rows': 3}
    )
    submit = SubmitField('发表评论')


class ReplyForm(FlaskForm):
    """回复表单"""
    content = TextAreaField(
        '回复内容',
        validators=[DataRequired(message='回复内容不能为空')],
        render_kw={'placeholder': '写下你的回复...', 'rows': 2}
    )
    submit = SubmitField('回复')


class PrivacySettingForm(FlaskForm):
    """隐私设置表单"""
    favorites_private = BooleanField('收藏夹仅自己可见')
    submit = SubmitField('保存设置')