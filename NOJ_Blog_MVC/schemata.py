from mongoengine import *
from flask_login import UserMixin
import datetime

connect('ProjectDb')

class User(Document, UserMixin):
    userid = IntField(required=True)
    account = StringField(max_length=20, required=True)
    password = StringField(required=True)
    nickname = StringField(max_length=20, default=account)
    blogPostList = ListField()

class BlogPost(Document):
    postid = IntField(required=True)
    title = StringField(required=True, max_length=200)
    author = StringField(max_length=20, required=True)
    update_time = DateTimeField(default=datetime.datetime.utcnow)
    tags = ListField( StringField(max_length=50) )
    content = StringField(required=True)
    isPublic = BooleanField(required=True)


users = User.objects.all()
print("All users:")
for user in users:
    print( 'Account:' + user.account + ',Password:' + user.password + ", UserId: " + str(user.userid) )
print("All posts:")
posts = BlogPost.objects.all()
for post in posts:
    print( 'PostId:' + str(post.postid) + ', Author:' + post.author + ", Content: " + post.content )


