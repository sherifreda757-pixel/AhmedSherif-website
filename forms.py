from flask_wtf import FlaskForm
from wtforms import StringField, URLField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditor, CKEditorField

class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = URLField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

class SignupForm(FlaskForm):
    name = StringField(label = 'your name', validators=[DataRequired()])
    password = PasswordField(label = 'password', validators = [DataRequired()])
    email = StringField(label = 'email', validators = [DataRequired(), Email()])
    submit = SubmitField(label = 'signup')

class LoginForm(FlaskForm):
    password = PasswordField(label = 'password', validators = [DataRequired()])
    email = StringField(label = 'email', validators = [DataRequired(), Email()])
    submit = SubmitField(label = 'login')

class CommentForm(FlaskForm):
    comment = CKEditorField("your comment", validators = [DataRequired()])
    submit = SubmitField('publish')