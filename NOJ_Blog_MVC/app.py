from flask import Flask, request, jsonify
from flask import render_template, url_for, redirect
from schemata import *
from mongoengine import *
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_bcrypt import Bcrypt
import model
import json

app = Flask(__name__)
app.secret_key = 'IReallySuck'

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.objects(userid=user_id).first()

@app.route('/')
def index():
    return render_template('home.html', posts_list=model.show_all_posts())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        connect('ProjectDb')
        newUser = User(
            userid = len(User.objects()) + 1,
            account = request.form.get('account'),
            password = bcrypt.generate_password_hash( request.form.get('password') ),
            nickname = request.form.get('nickname')
        )
        if User.objects(account=newUser.account).count() != 0:
            err = "The account has been used!"
            return render_template('home.html', err=err)
        else:
            newUser.save()
            return redirect( url_for('login') )
    else:
        return render_template('register.html')

@app.route('/login', methods=['GET', "POST"])
def login():
    if request.method == 'POST':
        connect('ProjectDb')
        account = request.form.get('account')
        password = request.form.get('password')
        user = User.objects(account=account).first()
        is_author = bcrypt.check_password_hash(user.password, password)
        if is_author:
            login_user(user)
            posts_list = model.get_posts_by_user(user)
            return render_template('profile.html', user=user, posts_list=posts_list, is_author=True)
        else:
            err = 'Username or Password Error'
            posts_list = model.show_all_posts()
            render_template('home.html', posts_list=posts_list, err=err)
    else:
        return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    err = "Log out!"
    posts_list = model.show_all_posts()
    return render_template('home.html', err=err, posts_list=posts_list)

@app.route('/addpost', methods=['GET', 'POST'])
@login_required
def addpost():
    if request.method == 'GET':
        return render_template('addpost.html')
    else: 
        connect('ProjectDb')
        newPost = BlogPost(
            postid = len(BlogPost.objects) + 1,
            author = current_user(),
            title = request.form.get('title'),
            content = request.form.get('content'),
            isPublic = request.form.get('isPublic')
        )
        if model.get_post_by_id(postid).first():
            flash("Please try it latter.")
        else:
            newPost.save()
        flash('Success!')

@app.route('/posts/edit/<int:pid>', methods=['GET', 'POST'])
@login_required
def edit_post(pid):
    post = model.get_post_by_id(pid)
    if current_user() == post.author:
        post.update(
            title = request.form.get('title'),
            content = request.form.get('content'),
            isPublic = request.form.get('isPublic')
        )
        return "Success"
    else:
        return "Permission denied."


@app.route('/posts/delete/<int:pid>')
@login_required
def delete_post(pid):
    model.delete_post(pid)
    posts_list = model.get_posts_by_user( current_user() )
    return render_template('profile.html', user=current_user(), posts_list=posts_list, is_author=True)

@app.route('/posts/<int:pid>')
def full_post_page(pid):
    post = model.get_post_by_id(pid).first()
    if(post.postid):
        return render_template('full_post_page.html', post=post )
    else:
        return 'The post is not found.'

@app.route('/profile/<account>')
def show_profile(account):
    user = model.get_user_by_account( account ).first()
    posts_list = model.get_public_posts_by_user(user)

    if user:
        return render_template('profile.html', user=user, posts_list=posts_list, is_author=False)
    else:
        return 'User not found'

if __name__ == '__main__':
    app.run(debug=True, port=8080)