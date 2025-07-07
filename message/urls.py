from django.urls import path
from . import views

urlpatterns = [
    path('create_message/',views.create_message),
    path('update_message/<int:messageID>/',views.update_message),
    path('delete_message/<int:messageID>/',views.delete_message),
    path('list_threads/',views.list_threads),
    path('get_thread/<int:threadID>/',views.get_thread),
    path('search/',views.search),
]