import razorpay
from django.conf import settings
from django.http import JsonResponse
from .models import User, Payment , Visitor , ChatQA
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


# # create order
# def create_order(request, user_id):
#     user = User.objects.get(id=user_id)

#     amount = 1000 * 100  # ₹1000

#     order = client.order.create({
#         "amount": amount,
#         "currency": "INR",
#         "payment_capture": "1"
#     })

#     Payment.objects.create(
#         user=user,
#         amount=1000,
#         razorpay_order_id=order["id"]
#     )

#     return JsonResponse({
#         "order_id": order["id"],
#         "key": settings.RAZORPAY_KEY_ID
#     })


# # verify payment
# def verify_payment(request):
#     data = request.POST

#     try:
#         client.utility.verify_payment_signature({
#             'razorpay_order_id': data['razorpay_order_id'],
#             'razorpay_payment_id': data['razorpay_payment_id'],
#             'razorpay_signature': data['razorpay_signature']
#         })

#         payment = Payment.objects.get(razorpay_order_id=data['razorpay_order_id'])
#         payment.razorpay_payment_id = data['razorpay_payment_id']
#         payment.status = "paid"
#         payment.save()

#         # 🔥 PLAN UPGRADE
#         user = payment.user
#         user.requests_limit += 10000
#         user.save()

#         return JsonResponse({"status": "success"})

#     except:
#         return JsonResponse({"status": "failed"})
    

from django.http import JsonResponse
from .models import User
import json

def verify_user(request):
    try:
        body = json.loads(request.body)
        api_key = body.get("api_key")

        user = User.objects.filter(api_key=api_key).first()

        if not user:
            return JsonResponse({"status": False})

        if not user.is_active:
            return JsonResponse({"status": False, "msg": "blocked"})

        return JsonResponse({
            "status": True,
            "user_id": user.id,
            "limit": user.requests_limit,
            "used": user.used_requests
        })

    except:
        return JsonResponse({"status": False})

from .models import User, UserURL
    

import json
import requests
from django.http import JsonResponse
from .models import User, UserURL

# 🔥 FastAPI URL
FASTAPI_CRAWL = "http://backbotv1.borgdesk.com/crawl"
# def add_url(request):
#     body = json.loads(request.body)

#     api_key = body.get("api_key")
#     urls = body.get("urls", [])

#     user = User.objects.filter(api_key=api_key).first()

#     if not user:
#         return JsonResponse({"status": False, "msg": "Invalid user"})

#     # ✅ STEP 1: DB me save karo
#     for url in urls:
#         UserURL.objects.create(user=user, url=url, status="pending")

#     # ✅ STEP 2: FastAPI ko call karo (🔥 IMPORTANT)
#     requests.post(FASTAPI_CRAWL, json={
#         "user_id": str(user.id),
#         "urls": urls
#     })

#     return JsonResponse({"status": True, "msg": "URL added & crawling started"})

@login_required(login_url="login")
def add_url_page(request):
    users = User.objects.all()
    print("users",users)
    msg = ""
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        url_input = request.POST.get("url")

        user = User.objects.get(id=user_id)

        # 🔥 split by comma
        urls = [u.strip() for u in url_input.split(",") if u.strip()]

        # ✅ DB me sab save karo
        for url in urls:
            UserURL.objects.create(user=user, url=url)

        # FastAPI call
        requests.post(FASTAPI_CRAWL, json={
            "user_id": str(user.id),
            "urls": [url]
        })
        msg = "Urls Saved Succesfully !"
        # return redirect("/add-url-page/")

    return render(request, "add_url.html", {"users": users, "msg": msg})

def get_urls(request):
    api_key = request.GET.get("api_key")

    user = User.objects.filter(api_key=api_key).first()

    if not user:
        return JsonResponse({"status": False})

    urls = list(UserURL.objects.filter(user=user).values("url", "status"))

    return JsonResponse({"status": True, "data": urls})


def chatbot_page(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        print("users",user)
        bot = CustomerBot.objects.filter(customer=user).first()

        store_data = False
        if bot:
            store_data = bot.store_data

        return render(request, "chatbot.html", {
            "api_key": user.api_key,
            "store_data": store_data   # 🔥 important
        })
    

    except User.DoesNotExist:
        return render(request, "chatbot.html", {
            "api_key": "",
            "store_data":""
        })
    
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt   # 🔥 ADD THIS
def verify_user(request):
    body = json.loads(request.body)
    api_key = body.get("api_key")

    user = User.objects.filter(api_key=api_key).first()

    if not user or not user.is_active:
        return JsonResponse({
            "status": False,
            "msg": "Invalid user"
        })

    return JsonResponse({
        "status": True,
        "user_id": user.id,
        "limit": user.requests_limit,
        "used": user.used_requests
    })

@login_required(login_url="login")
def user_list(request):
    users = User.objects.prefetch_related('urls').all()
    return render(request, "user_list.html", {"users": users})



@csrf_exempt
def update_usage(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_id = data.get("user_id")

        try:
            user = User.objects.get(id=user_id)

            if user.used_requests >= user.requests_limit:
                return JsonResponse({"status": "error", "msg": "Limit exceeded"})

            user.used_requests += 1
            user.save()

            return JsonResponse({"status": "success", "used": user.used_requests})

        except User.DoesNotExist:
            return JsonResponse({"status": "error", "msg": "User not found"})


from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")  # admin panel
        else:
            messages.error(request, "Invalid credentials")

    return render(request, "login.html")

def admin_logout(request):
    logout(request)
    return redirect("login")

from django.db.models import Sum


@login_required(login_url="login")
def dashboard(request):
    total_users = User.objects.count()
    total_used_requests = User.objects.aggregate(total=Sum('used_requests'))['total'] or 0

    return render(request, "dashboard.html", {
        "total_users": total_users,
        "total_used_requests": total_used_requests
    })

from .models import CustomerBot, ChatSession, ChatHistory



@csrf_exempt
def save_chat(request):
    if request.method == "POST":
        data = json.loads(request.body)
        bot_id = data.get("bot_id")
        visitor_id = data.get("visitor_id")
        question = data.get("question")
        answer = data.get("answer")
        source_urls = data.get("source_urls", [])

        bot, created = CustomerBot.objects.get_or_create(
            id=bot_id,
            defaults={
                "customer_id": bot_id,   # ya request user
                "name": f"Bot {bot_id}"
            }
        )
        print("data",bot)
        # Check if session exists for this visitor
        session, created = ChatSession.objects.get_or_create(bot=bot, visitor_id=visitor_id, end_time__isnull=True)

        # Save chat history
        ChatHistory.objects.create(
            session=session,
            question=question,
            answer=answer,
            source_urls=json.dumps(source_urls)
        )

        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error", "message": "Invalid request"})



# dashboard/views.py

@csrf_exempt
def save_visitor(request):
    if request.method == "POST":
        data = json.loads(request.body)

        api_key = data.get("api_key")
        visitor_id = data.get("visitor_id")
        user = User.objects.filter(api_key=api_key).first()
        bot = CustomerBot.objects.filter(customer=user.id).first()

        
        if not bot:
            return JsonResponse({"status": "error", "message": "Invalid bot"})

        Visitor.objects.create(
            bot=bot,
            visitor_id=visitor_id,
            name=data.get("name"),
            email=data.get("email"),
            phone=data.get("phone"),
            location=data.get("location"),
            message=data.get("message")
        )

        return JsonResponse({"status": "success"})
    



@login_required
def save_qa(request):
    user = request.user

    # user ke URLs
    dashboard_user = User.objects.get(auth_user=request.user)
    urls = UserURL.objects.filter(user=dashboard_user)

    if request.method == "POST":
        url_id = request.POST.get("url_id")
        question = request.POST.get("question")
        answer = request.POST.get("answer")

        try:
            url_obj = UserURL.objects.get(id=url_id, user=dashboard_user)

            ChatQA.objects.create(
                customer=dashboard_user,
                url=url_obj,
                question=question,
                answer=answer
            )

            return redirect("save_qa")  # same page reload

        except UserURL.DoesNotExist:
            pass

    return render(request, "customer/save_qa.html", {"urls": urls})


from django.db.models import Q
def get_qa(request):
    user_id = request.GET.get("user_id")
    question = request.GET.get("question")

    results = ChatQA.objects.filter(
        customer_id=user_id
    ).filter(
        Q(question__icontains=question)
    )[:5]

    data = []
    for qa in results:
        data.append({
            "question": qa.question,
            "answer": qa.answer
        })

    return JsonResponse({"results": data})