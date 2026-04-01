from django.urls import path
from . import views

urlpatterns = [
    path("add-url/", views.add_url_page,name="add_url_page"),
    path("update-usage/", views.update_usage),
    path('save-chat/', views.save_chat, name='save_chat'),
    path("save-visitor/", views.save_visitor,name='save_visitor'),
]