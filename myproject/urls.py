# project/urls.py
from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('telegram_login/', views.telegram_login, name='telegram_login'),  # Auth endpoint
    path('', views.reporting, name='reporting'),
    path('schedules/', views.schedules, name='schedules'),
    path('finances/', views.finances, name='finances'),
    path('tools/', views.tools, name='tools'),
]
