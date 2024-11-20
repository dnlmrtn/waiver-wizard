from django.urls import path
from . import views

urlpatterns = [
    path('api/injuries/', views.injuries, name='injured'),
    path('api/benefitting/', views.benefitting, name='benefitting'),
]
