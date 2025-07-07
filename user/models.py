from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    date_joined = models.DateTimeField(null = True, blank = True)
    login_time = models.DateTimeField(null = True, blank = True)
    logout_time = models.DateTimeField(null = True, blank = True)
    last_login = models.DateTimeField(null = True, blank = True)
    bio = models.CharField(max_length=200)
    otp = models.CharField(max_length=6,null=True,blank=True)

    def __str__(self):
        return self.username
    
    def get_data(self):
        data = {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'bio': self.bio,
        }
        return data


class UserRelation(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    followers = models.ManyToManyField(User,related_name='user_followers')
    following = models.ManyToManyField(User,related_name='user_following')
    blocked_users = models.ManyToManyField(User,related_name='user_blocked')

    def __str__ (self):
        return self.user.username
