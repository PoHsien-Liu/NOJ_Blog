from flask import Flask, request, jsonify
from flask import render_template, url_for, redirect
from schemata import *
from mongoengine import *
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
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
    if User.objects(userid=user_id) is not None:
        curr_user = User.objects(userid=user_id).first()
        curr_user.id = user_id
    return curr_user

@app.route('/')
def index():
    if current_user.is_anonymous:
        NotLogin = True
        account = "None"
    else:
        NotLogin = False
        account = current_user.account
    return render_template('home.html', posts_list=model.show_all_posts(), NotLogin=NotLogin, account=account)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        connect('ProjectDb')
        newUser = User(
            userid = len(User.objects()) + 1,
            account = request.form.get('account'),
            password = generate_password_hash( request.form.get('password') ),
            nickname = request.form.get('nickname')
        )
        if User.objects(account=newUser.account).count() != 0:
            return model.show_error("The account has been used!")
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
        user = model.get_user_by_account(account)
        is_author = check_password_hash(user.password, password)
        if is_author:
            curr_user = user
            curr_user.id = user.userid
            login_user(curr_user)
            posts_list = model.get_posts_by_user(current_user)
            return redirect( url_for('show_profile', account=current_user.account) )
        else:
            return model.show_error("Account or Password error, pls try again!")
            
    else:
        return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    err = "Log out!"
    posts_list = model.show_all_posts()
    return redirect( url_for('index') )

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == "POST":
        if current_user:
            user = current_user
            user.update(
                userid = user.userid,
                account = user.account,
                nickname = request.form.get('nickname'),
                password = user.password
            )
            return modle.show_error("Sucess!")    
        else:
            return model.show_error("fuck")
    elif request.method == "GET":
        return render_template('editprofile.html', ori_nickname=current_user.nickname)

@app.route('/addpost', methods=['GET', 'POST'])
@login_required
def addpost():
    if request.method == 'GET':
        return render_template('addpost.html')
    else: 
        string_to_boolean = lambda string: string=='True'
        connect('ProjectDb')
        orderPost = BlogPost.objects.order_by('-postid')
        if orderPost:
            pid = orderPost.first().postid + 1
        else: 
            pid = 1
        newPost = BlogPost(
            postid =  pid,
            author = current_user.account,
            title = request.form.get('title'),
            content = request.form.get('content'),
            isPublic = string_to_boolean( request.form.get('isPublic') )
        )
        newPost.save()
        posts_list = model.get_posts_by_user(current_user)
        return redirect( url_for('show_profile', account=current_user.account) )

@app.route('/posts/edit/<int:pid>', methods=['GET', 'POST'])
@login_required
def edit_post(pid):
    if request.method == 'GET':
        post = model.get_post_by_id(pid)
        return render_template('editpost.html', ori_title=post.title, ori_content=post.content)
    else:
        post = model.get_post_by_id(pid)
        if current_user == post.author:
            post.update(
                postid = post.id,
                title = request.form.get('title'),
                content = request.form.get('content'),
                isPublic = string_to_boolean( request.form.get('isPublic') ),
                author = post.author
            )     
            return model.show_error("Sucess")
        else:
            return model.show_error("Permisson Denied")
        
@app.route('/posts/delete/<int:pid>')
@login_required
def delete_post(pid):
    model.delete_post(pid)
    posts_list = model.get_posts_by_user( current_user )
    return render_template('profile.html', user=current_user, posts_list=posts_list, is_author=True)

@app.route('/posts/<int:pid>')
def full_post_page(pid):
    post = model.get_post_by_id(pid)
    if post:
        return render_template('full_post_page.html', post=post )
    else:
        return model.show_error("The post is not found.")

@app.route('/profile/<account>')
def show_profile(account):
    user = model.get_user_by_account( account )
    if user:
        if current_user.is_authenticated and current_user.account == user.account:
            is_author = True
            posts_list = model.get_posts_by_user(user)
        else:
            is_author = False
            posts_list = model.get_public_posts_by_user(user)
        return render_template('profile.html', user=user, posts_list=posts_list, is_author=is_author)
    else:
        return model.show_error("User not found!")

if __name__ == '__main__':
    app.run(debug=True, port=5000)