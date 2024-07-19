# interface_manager/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('connect/', views.connect, name='connect'),
    path('create_interface/', views.create_interface, name='create_interface'),
]
