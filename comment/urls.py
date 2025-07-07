from django.urls import path
from . import views

urlpatterns = [
    path('create_comment/',views.create_comment),
    path('update_comment/<int:commentID>/',views.update_comment),
    path('delete_comment/<int:commentID>/',views.delete_comment),
    path('reply_comment/<int:commentID>/',views.reply_comment),
    path('like_unlike_comment/<int:commentID>/',views.like_unlike_comment),
    path('get_comment/<int:commentID>/',views.get_comment),
    path('search/',views.search),
]