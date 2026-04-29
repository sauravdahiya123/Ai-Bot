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

import base64


def company_pdf_list(request):
    pdfs = CompanyPDF.objects.filter(user__auth_user=request.user).order_by('-uploaded_at')
    return render(request, "customer/company_pdf_list.html", {"pdfs": pdfs})


def customer_setting(request):
    dashboard_user = User.objects.get(auth_user=request.user)
    bot = CustomerBot.objects.filter(customer=dashboard_user).first()

    encoded = base64.urlsafe_b64encode(f"user_{dashboard_user.id}".encode()).decode()
    encoded_id = encoded.rstrip("=")
    return render(request, "customer/settings.html", {

        "bot":bot,
        "user_id":encoded_id,
        "remaining":dashboard_user.requests_limit - dashboard_user.used_requests  ,
        "user":dashboard_user,
        'remaning_blance':dashboard_user.balance
    })


from django.shortcuts import render ,  get_object_or_404
from dashboard.models import Visitor
from django.core.paginator import Paginator

def visitor_list(request):
    search = request.GET.get('search')
    bot_id = request.GET.get('bot_id')

    visitors = Visitor.objects.filter(
        bot__customer__auth_user=request.user
    ).order_by('-created_at')

    if bot_id:
        visitors = visitors.filter(bot_id=bot_id)

    if search:
        visitors = visitors.filter(
            name__icontains=search
        ) | visitors.filter(
            email__icontains=search
        ) | visitors.filter(
            phone__icontains=search
        )

    paginator = Paginator(visitors, 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'customer/visitor_list.html', {
        'page_obj': page_obj
    })


# DELETE (AJAX)
def delete_visitor(request, id):
    visitor = get_object_or_404(Visitor, id=id)
    visitor.delete()
    return JsonResponse({'status': 'success'})


@login_required
def chatqa_list(request):
    search = request.GET.get('search')
    url_id = request.GET.get('url_id')

    # 🔐 Only current user data
    qas = ChatQA.objects.filter(customer__auth_user=request.user.id).order_by('-created_at')

    # 🔎 Filter by URL
    if url_id:
        qas = qas.filter(url_id=url_id)

    # 🔍 Search
    if search:
        qas = qas.filter(
            Q(question__icontains=search) |
            Q(answer__icontains=search)
        )

    # 📄 Pagination
    paginator = Paginator(qas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'customer/chatqa_list.html', {
        'page_obj': page_obj
    })


# ❌ Delete
def delete_chatqa(request, id):
    qa = get_object_or_404(ChatQA, id=id, customer__auth_user=request.user.id)
    qa.delete()
    return JsonResponse({'status': 'success'})


@login_required
def update_bot_language(request):
    if request.method == "POST":
        data = json.loads(request.body)

        bot_id = data.get('bot_id')
        language = data.get('language')

        try:
            bot = CustomerBot.objects.get(id=bot_id, customer__auth_user=request.user)
            bot.language = language
            bot.save()

            return JsonResponse({"status": "success"})
        except CustomerBot.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Bot not found"})

    return JsonResponse({"status": "error"})


def get_bot_language(bot_id):
    from .models import CustomerBot
    try:
        bot = CustomerBot.objects.get(id=bot_id)
        return bot.language
    except:
        return 'en'
    

from django.db.models import Q


@login_required
def chat_history_view(request):
    bot_id = request.GET.get('bot_id')
    visitor_id = request.GET.get('visitor_id')
    search = request.GET.get('search')

    one_day_ago = timezone.now() - timedelta(days=1)

    chats = ChatHistory.objects.filter(
        created_at__gte=one_day_ago,
        session__bot__customer__auth_user=request.user
    )

    # 🔎 Filters
    if bot_id:
        chats = chats.filter(session__bot_id=bot_id)

    if visitor_id:
        chats = chats.filter(session__visitor_id__icontains=visitor_id)

    if search:
        chats = chats.filter(
            Q(question__icontains=search) |
            Q(answer__icontains=search)
        )

    chats = chats.select_related('session', 'session__bot').order_by('-created_at')

    # 📄 Pagination
    paginator = Paginator(chats, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 🔗 bots for dropdown
    bots = CustomerBot.objects.filter(customer__auth_user=request.user)

    return render(request, 'customer/chat_history.html', {
        'page_obj': page_obj,
        'bots': bots
    })


@login_required
def update_bot_settings(request):
    if request.method == "POST":
        bot_id = request.POST.get("bot_id")

        try:
            bot = CustomerBot.objects.get(
                id=bot_id,
                customer__auth_user=request.user
            )

            bot.name = request.POST.get("name")
            bot.welcome_message = request.POST.get("welcome_message")

            if request.FILES.get("bot_image"):
                bot.bot_image = request.FILES.get("bot_image")

            bot.save()

            return JsonResponse({"status": "success"})

        except CustomerBot.DoesNotExist:
            return JsonResponse({"status": "error"})

    return JsonResponse({"status": "error"})

from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
# def update_bot_theme(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             print("data",data)
#             bot_id = data.get("bot_id")
#             theme_color = data.get("theme_color")

#             if not bot_id:
#                 return JsonResponse({
#                     "status": "error",
#                     "message": "bot_id missing"
#                 })

#             # ✅ FIXED MODEL HERE
#             bot = CustomerBot.objects.get(id=bot_id)

#             bot.theme_color = theme_color
#             bot.save()

#             return JsonResponse({
#                 "status": "success",
#                 "message": "Theme updated successfully",
#                 "theme_color": theme_color
#             })

#         except CustomerBot.DoesNotExist:
#             return JsonResponse({
#                 "status": "error",
#                 "message": "Bot not found"
#             })

#         except Exception as e:
#             return JsonResponse({
#                 "status": "error",
#                 "message": str(e)
#             })

#     return JsonResponse({
#         "status": "error",
#         "message": "Invalid request method"
#     })



def update_bot_settings2(request, bot_id):
    if request.method == "POST":
        data = json.loads(request.body)

        bot = CustomerBot.objects.get(id=bot_id)

        bot.language = data.get("language", bot.language)
        bot.theme_color = data.get("theme_color", bot.theme_color)
        bot.sales_prompt_after = data.get("sales_prompt_after", bot.sales_prompt_after)

        bot.save()

        return JsonResponse({"status": "success"})
    