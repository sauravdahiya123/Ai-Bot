import razorpay
from django.conf import settings
from django.http import JsonResponse
from .models import User, Payment , Visitor , ChatQA, CompanyPDF
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
        bot = CustomerBot.objects.filter(customer=user).first()

        if not user:
            return JsonResponse({"status": False})

        if not user.is_active:
            return JsonResponse({"status": False, "msg": "blocked"})

        return JsonResponse({
            "status": True,
            "user_id": user.id,
            "limit": user.requests_limit,
            "used": user.used_requests,
            "language": bot.language if bot else "en"   # 🔥 ADD THIS

        })

    except:
        return JsonResponse({"status": False})

from .models import User, UserURL
    

import json
import requests
from django.http import JsonResponse
from .models import User, UserURL

# 🔥 FastAPI URL
FASTAPI_CRAWL = "https://backbotv1.borgdesk.com/crawl"

# FASTAPI_CRAWL = "http://127.0.0.1:8002/crawl"





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

        try:
            res = requests.post(FASTAPI_CRAWL, json={
                "user_id": str(user.id),
                "urls": urls
            })

            print("FastAPI Response:", res.status_code, res.text)

        except Exception as e:
            print("FastAPI Error:", e)
        
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

import base64

def chatbot_page(request, encoded_id):
    try:
        encoded_id += '=' * (4 - len(encoded_id) % 4)

        decoded = base64.urlsafe_b64decode(encoded_id).decode()

        # अगर तुमने "user_4" encode किया था
        user_id = decoded.split("_")[-1]

        user = User.objects.get(id=user_id)
        print("users",user)
        bot = CustomerBot.objects.filter(customer=user).first()
        store_data = False
        if bot:
            store_data = bot.store_data

        return render(request, "chatbot.html", {
            "api_key": user.api_key,
            "bot":bot,
            "instance_id":bot.instance_id,
            "sales_prompt_after": bot.sales_prompt_after if bot else 10,
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

            if user.balance < user.cost_per_request:
                return JsonResponse({"status": "error", "msg": "Insufficient balance"})

            user.balance -= user.cost_per_request
            user.used_requests += 1
            user.save()

            return JsonResponse({
                "status": "success",
                "remaining_balance": str(user.balance)
            })

            # return JsonResponse({"status": "success", "used": user.used_requests})

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
            return redirect("user_list")  # admin panel
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


def get_bot_details(request):
    bot_id = request.GET.get("bot_id")

    try:
        bot = CustomerBot.objects.get(id=bot_id)

        return JsonResponse({
            "status": True,
            "name": bot.name,
            "image": bot.bot_image.url if bot.bot_image else "",
            "welcome_message": bot.welcome_message
        })

    except:
        return JsonResponse({"status": False})


def ai_chatbot_view(request):
    return render(request, "ai_chatbot.html")

@csrf_exempt
def voice_ask(request):
    if request.method == "POST":
        audio_file = request.FILES.get("audio_file")
        dashboard_user = User.objects.get(auth_user=request.user)

        api_key = dashboard_user.api_key

        files = {"audio_file": audio_file}
        res = requests.post("http://127.0.0.1:8001/voice-ask", files=files, data={"api_key": api_key})
        return JsonResponse(res.json())
    
FASTAPI_PDF = "https://backbotv1.borgdesk.com/upload-pdf-url"
# FASTAPI_PDF = "http://127.0.0.1:8002/upload-pdf-url"

from pydantic import BaseModel

class PDFRequest(BaseModel):
    user_id: str
    pdf_url: str
    title: str | None = None

@login_required(login_url="login")
def upload_pdf(request):
    users = User.objects.all()
    msg = ""

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        title = request.POST.get("title")
        pdf_file = request.FILES.get("pdf")

        user = User.objects.get(id=user_id)

        pdf_obj = CompanyPDF.objects.create(
            user=user,
            title=title,
            file=pdf_file
        )

        # 🔥 SEND TO FASTAPI

        print("request.build_absolute_uri(pdf_obj.file.url)",request.build_absolute_uri(pdf_obj.file.url))
        try:
            requests.post(FASTAPI_PDF, json={
                "user_id": str(user.id),
                "pdf_url": request.build_absolute_uri(pdf_obj.file.url),
                "title": title
            })
        except Exception as e:
            print("FastAPI error:", e)

        msg = "PDF uploaded & processing started!"

    return render(request, "add_pdf.html", {
        "users": users,
        "msg": msg
    })


from datetime import datetime
from django.conf import settings
import os

CHAT_MESSAGES = []

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == "POST":

        # ✅ 1. RAW BODY (full JSON)
        raw_body = request.body.decode("utf-8")

        # ✅ 2. SAVE FULL JSON FIRST
        log_path = os.path.join(settings.BASE_DIR, "webhook_log.txt")

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n===== {datetime.now()} =====\n")
            f.write(raw_body + "\n")

        # ✅ 3. NOW process data
        try:
            data = json.loads(raw_body)
        except:
            data = request.POST.dict()

        print("📩 Incoming:", data)

        # ✅ Extract fields
        message = data.get("message") or data.get("text") or ""
        phone = data.get("from") or data.get("mobile") or ""

        if phone:
            phone = phone[-10:]

        # ✅ Store in memory (chatbot use)
        CHAT_MESSAGES.append({
            "phone": phone,
            "message": message
        })

        return JsonResponse({"status": "received"})

    return JsonResponse({"error": "Invalid request"}, status=400)



# views.py

def get_messages(request):
    phone = request.GET.get("phone", "")

    if phone:
        phone = phone[-10:]  # normalize

    # ✅ sirf us number ke messages return karo
    filtered = [
        msg for msg in CHAT_MESSAGES
        if not phone or msg["phone"] == phone
    ]

    return JsonResponse(filtered, safe=False)



from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment

@csrf_exempt
def voice_chat(request):
    if request.method == "POST":

        audio_file = request.FILES.get("audio")
        api_key = request.headers.get("X-API-KEY")
        if not audio_file:
            return JsonResponse({"error": "No audio"}, status=400)

        # save webm
        webm_path = os.path.join(settings.MEDIA_ROOT, "input.webm")

        with open(webm_path, "wb+") as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        # 🔥 convert to wav
        wav_path = os.path.join(settings.MEDIA_ROOT, "input.wav")

        audio = AudioSegment.from_file(webm_path, format="webm")
        audio.export(wav_path, format="wav")

        # 🔥 speech to text
        recognizer = sr.Recognizer()

        try:
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)

        except Exception as e:
            print("Speech error:", e)
            text = ""

        print("TEXT:", text)
        import requests
        ai_res = requests.get(
            "https://backbotv1.borgdesk.com/ask",
            params={"q": text,
                                        "vistor_id": "voice-user",
                                        "api_key": api_key
                                        }
        )
        ai_data = ai_res.json()
        answer = ai_data.get("answer", "Sorry, I didn’t understand.")

        # 🔥 3. Text → MP3
        output_path = os.path.join(settings.MEDIA_ROOT, "reply.mp3")

        tts = gTTS(answer, lang="en")
        tts.save(output_path)

        audio_url = request.build_absolute_uri(settings.MEDIA_URL + "reply.mp3")

        return JsonResponse({
            "text": text,
            "reply": answer,
            "audio_url": audio_url
        })