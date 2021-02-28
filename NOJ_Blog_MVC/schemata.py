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

    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self): 
        return str(self.id)   

class BlogPost(Document):
    postid = IntField(required=True)
    title = StringField(required=True, max_length=200)
    author = StringField(max_length=20, required=True)
    update_time = DateTimeField(default=datetime.datetime.utcnow)
    tags = ListField( StringField(max_length=50) )
    content = StringField(required=True)
    isPublic = BooleanField(required=True)

BlogPost.objects.all().delete()
post1 = BlogPost(
    postid = 1,
    title = 'test1',
    author= 'RobertLiu',
    content = 'Test1',
    isPublic = True
)   
post2 = BlogPost(
    postid = 2,
    title = 'test2',
    author= 'RobertLiu',
    content = 'lorem30',
    isPublic = False
)

post1.save()
post2.save()

print( len(User.objects()) )
user = User.objects.all()
print("All users:")
for users in user:
    print( 'Account:' + users.account + ',Password:' + users.password + ", UserId: " + str(users.userid) )
print("Posts count: " + str(BlogPost.objects.count()) )

