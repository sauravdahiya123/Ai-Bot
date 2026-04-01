# chat/urls.py
from django.urls import path
from . import views

from dashboard.views import save_qa

urlpatterns = [
    path('login/', views.customer_login, name='customer_login'),
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('logout/', views.customer_logout, name='customer_logout'),
    path('customer_setting/', views.customer_setting, name='customer_setting'),
    path('save-qa/', save_qa, name='save_qa'),

]

