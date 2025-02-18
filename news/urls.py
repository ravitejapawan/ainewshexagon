


from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('developer/', views.developer, name='developer'),
    path('view-files/', views.view_uploaded_files, name='view_files'),
    path('view-file/<int:file_id>/', views.view_file_content, name='view_file_content'),  # 🔹 FIXED!
]
