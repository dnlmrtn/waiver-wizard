from django.urls import path
from . import views

urlpatterns = [
    path('injuries/', views.injuries, name='injured'),
    path('benefitting/', views.benefitting, name='benefitting'),
]
