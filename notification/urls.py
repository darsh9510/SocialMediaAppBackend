from django.urls import path
from . import views

urlpatterns = [
    path('get_notification/',views.get_notification),
]