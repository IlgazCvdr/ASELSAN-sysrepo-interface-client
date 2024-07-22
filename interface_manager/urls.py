# interface_manager/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('connect/', views.connect, name='connect'),
    path('create-interface/', views.create_interface, name='create_interface'),
    path('network-interfaces/', views.get_network_interfaces, name='network_interfaces'),
]
