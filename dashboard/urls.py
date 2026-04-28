from django.urls import path
from . import views

urlpatterns = [
    path("add-url/", views.add_url_page,name="add_url_page"),
    path("update-usage/", views.update_usage, name="update_usage"),
    path('save-chat/', views.save_chat, name='save_chat'),
    path("save-visitor/", views.save_visitor,name='save_visitor'),
    path("get-qa/", views.get_qa,name='get_qa'),
    path("ai-chatbot/", views.ai_chatbot_view, name="ai_chatbot"),
    path("voice-ask/", views.voice_ask, name="voice_ask"),
    path("upload-pdf/", views.upload_pdf, name="upload_pdf"),
]