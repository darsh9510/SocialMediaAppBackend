from django.db import models
from user.models import User

class Post(models.Model):
    poster = models.ForeignKey(User,on_delete=models.CASCADE,related_name='post_poster')
    title = models.CharField(max_length = 100)
    description = models.CharField(max_length = 1000)
    posted_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    # def __str__(self):
    #     name = self.title[:10] + '...' if len(self.title)>10 else self.title
    #     return name

class PostLike(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='postlike_post')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='postlike_user')

class Reactions(models.Model):
    choice = (('happy','Happy'),('sad','Sad'),('angry','Angry'),('celebrate','Celebrate'),('wow','Wow'),)
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='post_reaction')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_reaction')
    reaction = models.CharField(choices = choice)
