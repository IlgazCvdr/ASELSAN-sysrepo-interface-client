# netopeer_project/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('interface_manager.urls')),  # Include your app’s URLs
]
