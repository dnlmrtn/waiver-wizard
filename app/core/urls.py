from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='base'),
    path('home/', views.home, name='home'),
    path('login', views.login, name='login')
]
