from django.db import models
from user.models import User
from post.models import Post

class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='post_comment')
    poster = models.ForeignKey(User,on_delete=models.CASCADE,related_name='comment_poster')
    content = models.CharField(max_length=1000)
    commented_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)
    parent = models.ForeignKey('self',on_delete=models.PROTECT,related_name='parent_comment',related_query_name='child_comment',null=True,blank=True)

class CommentLike(models.Model):
    comment = models.ForeignKey(Comment,on_delete=models.CASCADE,related_name='comment_object')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_object')