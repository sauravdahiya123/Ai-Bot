from django.contrib import admin
from .models import User, Payment ,UserURL

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "api_key", "is_active", "used_requests", "requests_limit")
    list_editable = ("is_active",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "status", "created_at")



@admin.register(UserURL)
class URLAdmin(admin.ModelAdmin):
    list_display = ("user", "url", "status", "created_at")
    