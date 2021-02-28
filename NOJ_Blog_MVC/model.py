from mongoengine import *
from schemata import *
import datetime

connect('ProjectDb')

def delete_post(pid):
    return BlogPost.objects(postid=pid).first().delete()

def show_all_posts():
    return BlogPost.objects(isPublic=True)

def get_public_posts_by_user(user):
    return BlogPost.objects(author=user.account, isPublic=True)

def get_posts_by_user(user):
    return BlogPost.objects(author=user.account)

def get_post_by_id(pid):
    return BlogPost.objects(postid=pid).first()

def get_user_by_account(account):
    return User.objects(account=account).first()
