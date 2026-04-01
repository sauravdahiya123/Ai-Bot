# chat/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from dashboard.models import ChatSession, ChatHistory
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta

def customer_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('customer_dashboard')
        else:
            messages.error(request, "Invalid email or password")

    return render(request, "customer/login.html")


@login_required(login_url='customer_login')
def customer_dashboard(request):
    # Total users
    auth_user = request.user
    from dashboard.models import  User,CustomerBot
    dashboard_user = User.objects.filter(auth_user=auth_user).first()
    user_id = dashboard_user.id
    print("dashboard_user",dashboard_user.id)
    bot = CustomerBot.objects.filter(customer=dashboard_user).first()

    total_users = ChatSession.objects.filter(bot=bot).values('visitor_id').distinct().count()

    # Total chats
    total_chats = ChatHistory.objects.filter(session__bot=bot).count()

    # Chats today
    today = timezone.now().date()
    chats_today = ChatHistory.objects.filter(
        session__bot=bot,
        created_at__date=today
    ).count()

    # Daily chat counts (last 7 days)
    last_7_days = timezone.now().date() - timedelta(days=6)
    daily_chats_qs = (
        ChatHistory.objects.filter(
            session__bot=bot,
            created_at__date__gte=last_7_days
        )
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    chat_dates = [str(entry['date']) for entry in daily_chats_qs]
    chat_counts = [entry['count'] for entry in daily_chats_qs]
    dashboard_user = User.objects.get(auth_user=request.user)
    bot = CustomerBot.objects.filter(customer=dashboard_user).first()


    return render(request, "customer/dashboard.html", {
        "total_users": total_users,
        "total_chats": total_chats,
        "chats_today": chats_today,
        "chat_dates": chat_dates,
        "chat_counts": chat_counts,
        "bot":bot
    })
@login_required
def customer_logout(request):
    logout(request)
    return redirect('customer_login')

from dashboard.models import *
from django.http import JsonResponse
import json
@login_required
def toggle_store_data(request):
    if request.method == "POST":
        data = json.loads(request.body)
        status = data.get("status")

        dashboard_user = User.objects.get(auth_user=request.user)
        bot = CustomerBot.objects.filter(customer=dashboard_user).first()

        if bot:
            bot.store_data = status
            bot.save()

            return JsonResponse({
                "status": "success",
                "store_data": bot.store_data
            })

    return JsonResponse({"status": "error"})