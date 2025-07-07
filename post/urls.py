from django.urls import path
from . import views

urlpatterns = [
    path('create_post/',views.create_post),
    path('update_post/<int:postID>/',views.update_post),
    path('delete_post/<int:postID>/',views.delete_post),
    path('like_unlike_post/<int:postID>/',views.like_unlike_post),
    path('post_reaction/<int:postID>/',views.post_reaction),
    path('remove_reaction/<int:postID>/',views.remove_reaction),
    path('get_post/<int:postID>/',views.get_post),
    path('get_post_reactions/<int:postID>/',views.get_post_reactions),
    path('get_post_liked_list/<int:postID>/',views.get_post_likes),
    path('get_post_comments/<int:postID>/',views.get_post_comments),
    path('list_posts/',views.list_posts),
    path('search/',views.search),
]