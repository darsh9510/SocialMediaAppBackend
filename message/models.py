from django.db import models
from user.models import User

class Message(models.Model):
    from_user = models.ForeignKey(User,on_delete=models.PROTECT,related_name='sender')
    to_user = models.ForeignKey(User,on_delete=models.PROTECT,related_name='reciever')
    content = models.CharField(max_length=1000)
    thread = models.IntegerField()
    first_sent = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    seen = models.BooleanField(default=False)
