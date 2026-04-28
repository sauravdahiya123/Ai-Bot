# chat/urls.py
from django.urls import path
from . import views

from dashboard.views import save_qa

urlpatterns = [
    path('', views.customer_login, name='customer_login'),
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('logout/', views.customer_logout, name='customer_logout'),
    path('customer_setting/', views.customer_setting, name='customer_setting'),
    path('save-qa/', save_qa, name='save_qa'),
    path('visitors/', views.visitor_list, name='visitor_list'),
    path('visitors/delete/<int:id>/', views.delete_visitor, name='delete_visitor'),
    path('chatqa/', views.chatqa_list, name='chatqa_list'),
    path('chatqa/delete/<int:id>/', views.delete_chatqa, name='delete_chatqa'),
    path('update-bot-language/', views.update_bot_language, name='update_bot_language'),
    path('chat-history/', views.chat_history_view, name='chat_history'),
    path('update-bot-settings/', views.update_bot_settings, name='update_bot_settings'),
    path('update-bot-settings2/<int:bot_id>/', views.update_bot_settings2, name='update_bot_settings2'),

]

