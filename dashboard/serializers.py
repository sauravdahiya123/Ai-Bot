# chat/serializers.py
from rest_framework import serializers
from .models import ChatHistory, ChatSession

class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        fields = '__all__'

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatHistorySerializer(many=True, read_only=True)
    class Meta:
        model = ChatSession
        fields = '__all__'