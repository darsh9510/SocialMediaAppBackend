from django.urls import path
from . import views

urlpatterns = [
    path('signup/',views.signup),
    path('otp_login/',views.login_otp),
    path('verify_otp_login/',views.verify_otp),
    path('logout/',views.log_out),
    path('forgot_password/',views.forgot_password),
    path('update_forgot_password/',views.update_forgot_password),
    path('update_password/',views.update_password),
    path('update_profile/',views.update_profile),
    path('follow/<int:userID>/',views.follow),
    path('unfollow/<int:userID>/',views.unfollow),
    path('decide_follow_request/',views.decide_follow_request),
    path('block_user/<int:userID>/',views.block_user),
    path('unblock_user/<int:userID>/',views.unblock_user),
    path('blocked_users_list/',views.blocked_users_list),
    path('user/<int:userID>/',views.get_user),
    path('get_user_posts/<int:userID>/',views.get_user_posts),
    path('get_user_comments/<int:userID>/',views.get_user_comments),
    path('get_all_users/',views.get_all_users),
    path('get_loggedin_user/',views.get_loggedin_user),
    path('list_followers/<int:userID>/',views.list_followers),
    path('list_followings/<int:userID>/',views.list_followings),
    path('delete_user/',views.delete_user),
    path('search/',views.search),
]