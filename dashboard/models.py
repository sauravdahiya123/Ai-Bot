from django.db import models
from django.contrib.auth.models import User as AuthUser

class User(models.Model):
    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    api_key = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    requests_limit = models.IntegerField(default=1000)
    used_requests = models.IntegerField(default=0)

    def __str__(self):
        return self.email


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    razorpay_order_id = models.CharField(max_length=200)
    razorpay_payment_id = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=50, default="created")
    created_at = models.DateTimeField(auto_now_add=True)



class UserURL(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="urls")
    url = models.URLField()
    status = models.CharField(max_length=20, default="pending")  # pending, done
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.url}"
    


class CompanyPDF(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="company_pdfs/")
    uploaded_at = models.DateTimeField(auto_now_add=True)


import json

class CustomerBot(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)  # Customer who owns the bot
    name = models.CharField(max_length=100)  # Bot name
    created_at = models.DateTimeField(auto_now_add=True)
    store_data = models.BooleanField(default=True)  # 🔥 NEW FIELD
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('hinglish', 'Hinglish'),
    ]
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    bot_image = models.ImageField(upload_to='bot_images/', null=True, blank=True)
    welcome_message = models.TextField(default="Hi 👋 How can I help you?")
    theme_color = models.CharField(max_length=20, default="#0d6efd")


    def __str__(self):
        return f"{self.name} - {self.customer.email}"

class ChatSession(models.Model):
    bot = models.ForeignKey(CustomerBot, on_delete=models.CASCADE)
    visitor_id = models.CharField(max_length=100)  # Unique identifier for website visitor
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Session {self.id} - {self.visitor_id}"

class ChatHistory(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    question = models.TextField()
    answer = models.TextField()
    source_urls = models.TextField(null=True, blank=True)  # JSON array of URLs
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=200)

    def get_source_urls(self):
        if self.source_urls:
            return json.loads(self.source_urls)
        return []

    def __str__(self):
        return f"Q: {self.question[:30]}..."
    


class Visitor(models.Model):
    bot = models.ForeignKey(CustomerBot, on_delete=models.CASCADE)
    visitor_id = models.CharField(max_length=100)

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    message = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    


class ChatQA(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)  # Customer who owns the bot
    url = models.ForeignKey(UserURL, on_delete=models.CASCADE, null=True, blank=True)  # 🔥 connection
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question[:50]