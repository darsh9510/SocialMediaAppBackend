from django.db import models
from user.models import User

class Notification(models.Model):
    to_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name = 'user_notif')
    from_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name = 'from_user_notif')
    read = models.BooleanField(default = False)
    time = models.DateTimeField(auto_now_add = True)
    detail = models.CharField(max_length=100)