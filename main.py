from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy 
from flask_ckeditor import CKEditor
from flask_ckeditor.utils import cleanify
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, current_user, UserMixin, login_required
from forms import LoginForm, SignupForm, CreatePostForm, CommentForm
from email_sender import send_me_an_email
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import hashlib, os

app = Flask(__name__)
bootstrap = Bootstrap5(app)
ckeditor = CKEditor(app)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "dev-secret-key") 
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///blogss.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


class Post(db.Model):

    __tablename__=  'blog_posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False, unique = True)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    body = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(500)) 
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    author = db.relationship('User', back_populates = 'posts', lazy = True)
    comments = db.relationship('Comment', back_populates = 'post', lazy = True, cascade='all, delete-orphan')

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class User (UserMixin, db.Model):

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(250), nullable = False)
    password = db.Column(db.String(250), nullable = False)
    email = db.Column(db.String(250), nullable = False, unique = True)
    posts = db.relationship('Post', back_populates = 'author', lazy = True)
    comments = db.relationship('Comment', back_populates = 'commenter', lazy =True)

class Comment (db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.Text, nullable=False)
    commenter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    commenter = db.relationship('User', back_populates = 'comments', lazy = True)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable = False)
    post = db.relationship('Post', back_populates = 'comments', lazy = True)
    def gravatar_url(self, size=30):
        return gravatar_url(self.commenter.email, size)

with app.app_context():
    db.create_all()

def admin_only(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            abort (403)
        if current_user.id != 1:
            abort(403)
        else:
            return func(*args, **kwargs)     
    return wrapped

def gravatar_url(email, size = 30):
    email = email.strip().lower()
    # email = email.encode()
    email = hashlib.md5(email.encode()).hexdigest()
    return f"https://www.gravatar.com/avatar/{email}?s={size}"

@app.route('/')
def register():
    if current_user.is_authenticated:
        return redirect (url_for('index'))
    else:
     return render_template('register.html')

@login_manager.user_loader
def user_loader(id):
    return User.query.get(id)


@app.route('/posts')
@login_required
def index():
    posts = Post.query.all()
    return render_template('index.html' , posts = posts, no_of_posts = len(posts))

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/post/<int:id>')
@login_required
def post(id):
    return render_template('post.html', post = Post.query.get(id))

@app.route( '/contact', methods  = ['POST', 'GET'] )
def contact():
    
    if request.method == 'POST':
        data = request.form
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        message = data.get('message')
        send_me_an_email(name = name, email = email, phone = phone, message = message)
        return render_template('contact.html', msg_sent=True)
    return render_template('contact.html', msg_sent=False)


@app.route('/form-entry', methods = ['POST'])
def receive_data():
    data = request.form
    return f"<h1>Successfully send your message!</h1><br>email: {data.get('email')}<br>name: {data.get('name')}<br>phone: {data.get('phone')}"


@app.route('/new_post', methods = ['POST', 'GET'])
@login_required
@admin_only
def create_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        date = datetime.now().strftime("%B %d, %Y")
        new_post = Post(
            title = form.title.data,
            subtitle = form.subtitle.data,
            body = cleanify(form.body.data),
            # author = current_user,    ممكن تستخدم دي والي تحتها او ممكن تستخدم دي او الي تحتها نفس النتيجة
            author_id = current_user.id,
            image = form.img_url.data,
            date = date, 
        )
        # ممكن تضيف دي بدل author_id وهو هيضيف author_id لوحده 
        # current_user.posts.append(new_post)
        db.session.add(new_post)
        db.session.commit()
        return redirect (url_for('index'))
    return render_template('add.html', form = form, is_edit = False)


@app.route('/edit-post/<int:id>', methods = ['POST', 'GET'])
@login_required
@admin_only
def edit_post(id):
    post = Post.query.get(id)
    form = CreatePostForm(
        title = post.title,
        subtitle = post.subtitle,
        img_url = post.image,
        body = post.body
    )
    if form.validate_on_submit():
        post.title = form.title.data
        post.subtitle = form.subtitle.data
        post.body = form.body.data
        post.image  = form.img_url.data
        db.session.commit()
        return redirect(url_for('post', id = post.id))
    return render_template('add.html', form = form, is_edit = True)


@app.route('/delete/<int:id>')
@admin_only
def delete(id):
    del_post = Post.query.get(id)
    db.session.delete(del_post)
    db.session.commit()
    return redirect(url_for('index'))
    

@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email = form.email.data).first()
        if existing_user:
            flash('this user already exists', 'danger')
            return redirect(url_for('login'))
        new_user = User(email = form.email.data, name = form.name.data, password = generate_password_hash(form.password.data))
        db.session.add(new_user)
        db.session.commit()
        flash('signed-up successfully! now go to login', 'success')
        return redirect (url_for('register'))
    return render_template('signup.html', form = form)


@app.route('/login', methods = ['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('logged-in successfully!')
            return redirect (url_for('index'))
        else:
            flash('the email or the password is wrong, else you do not have an account and need to signup first.', 'danger')
            return redirect(url_for('login'))

    return render_template('signup.html', form = form)


@app.route('/logout')
def logout():
    logout_user()
    flash ('you are logged out')
    return redirect(url_for('register'))


@app.route('/comment/<int:post_id>', methods = ['POST', 'GET'])
@login_required
def comment(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        new_comment=  Comment(
            text = cleanify(form.comment.data),
            commenter = current_user,
            post_id = post_id
        )
        db.session.add(new_comment)
        db.session.commit()
        flash('comment added successfully!', 'success')
        return redirect (url_for('post', id = post_id))
    return render_template('signup.html', form = form)
    

@app.route('/delete-comment/<int:id>')
@admin_only
def delete_comment(id):
    del_com = Comment.query.get(id)
    print(del_com.text)
    post_id = del_com.post_id
    db.session.delete(del_com)
    db.session.commit()
    flash('comment deleted successfully!', 'success')
    return redirect(url_for('post', id = post_id))
    




