# chat/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.customer_login, name='customer_login'),
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('logout/', views.customer_logout, name='customer_logout'),
]