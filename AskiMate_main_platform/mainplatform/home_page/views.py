import logging
import os
import requests
import traceback
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import ConversationSession, ChatMessage
import json
import requests
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from .models import ConversationSession, ChatMessage
logger = logging.getLogger(__name__)
AI_APP_URL = os.getenv("AI_API_URL", "https://askimate-ai-app.onrender.com/chat")


def main_page(request):
    if request.method == "POST":
        full_name = request.POST.get('fullName', '').strip()
        email = request.POST.get('email', '').strip().lower()

        if full_name and email:
            if User.objects.filter(email=email).exists():
                messages.error(request, "You have already joined the waiting list before.")
                return redirect('main_page')

            subject = "Welcome to AskiMate Waiting List!"
            message = (
                f"Hello {full_name},"
                f"Thank you for joining the AskiMate waiting list!"
                f"Best regards,The AskiMate Team"
            )

            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
                messages.success(request, "Thank you for joining the waiting list! A confirmation email has been sent.")
            except Exception as e:
                logger.warning(f"Email not sent to {email}: {e}")
                messages.warning(request, "You joined the waiting list, but we couldn't send the confirmation email.")

            return redirect('main_page')
        else:
            messages.error(request, "Please fill in all fields.")

    return render(request, 'home_page/main_page.html')


def contact_form(request):
    if request.method == 'POST':
        name = request.POST.get('contact_name', '').strip()
        email = request.POST.get('contact_email', '').strip()
        message = request.POST.get('contact_message', '').strip()

        if not (name and email and message):
            messages.error(request, "All fields are required.")
            return redirect('main_page')

        full_message = f"Name: {name}Email: {email}Message:{message}"

        try:
            send_mail(
                subject="New Contact Form Submission",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['askimatetest@gmail.com'],
                fail_silently=False,
            )

            user_subject = "We received your message at AskiMate!"
            user_message = (
                f"Hi {name},"
                f"Thanks for reaching out to us!"
                f"Your message:{message}"f"Best,AskiMate Team"
            )

            send_mail(
                subject=user_subject,
                message=user_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, "Your message has been sent successfully.")
        except Exception as e:
            logger.error(f"Error sending contact form email: {e}")
            messages.error(request, "Something went wrong. Please try again later.")

        return redirect('main_page')

    return redirect('main_page')


def signup_view(request):
    error = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not (email and username and password):
            error = 'All fields are required.'
        elif User.objects.filter(username=username).exists():
            error = 'Username already exists.'
        elif User.objects.filter(email=email).exists():
            error = 'Email already registered.'
        else:
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                auth_user = authenticate(request, username=username, password=password)
                if auth_user is not None:
                    login(request, auth_user)
                    messages.success(request, 'Registration successful! You are now logged in.')
                    return redirect('custom_login')
                else:
                    error = 'Authentication failed after registration.'
            except Exception as e:
                logger.error(f"User registration error: {e}")
                error = 'There was a problem creating your account.'

    return render(request, 'home_page/signup.html', {'error': error})


def custom_login_view(request):
    return render(request, 'home_page/login.html')


def email_login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        if not email:
            messages.error(request, 'Please enter your email.')
            return redirect('custom_login')
        request.session['login_email'] = email
        return redirect('password_login')
    return redirect('custom_login')


def password_login_view(request):
    email = request.session.get('login_email')
    if not email:
        return redirect('custom_login')

    error = None
    if request.method == 'POST':
        password = request.POST.get('password', '').strip()
        if not password:
            error = 'Please enter your password.'
        else:
            user = User.objects.filter(email=email).first()
            if not user:
                error = 'No user found with this email.'
            else:
                auth_user = authenticate(request, username=user.username, password=password)
                if auth_user is not None:
                    login(request, auth_user)
                    messages.success(request, f'Welcome back, {user.username}!')

                    last_session = ConversationSession.objects.filter(user=user).order_by('-created_at').first()
                    if last_session:
                        return redirect(f"{reverse('chatbot-main', kwargs={'session_id': last_session.session_id})}?from_login=1")
                    else:
                        return redirect(f"{reverse('chatbot-new')}?from_login=1")
                else:
                    error = 'Password incorrect.'
    return render(request, 'home_page/password.html', {'email': email, 'error': error})


@csrf_exempt
def chatbot_view(request, session_id=None):
    sessions = ConversationSession.objects.filter(user=request.user).order_by('-created_at')
    last_session = sessions.first()

    if session_id:
        active_session = get_object_or_404(ConversationSession, user=request.user, session_id=session_id)
        messages_qs = ChatMessage.objects.filter(session=active_session).order_by('timestamp')
    else:
        active_session, messages_qs = None, None

    if not request.session.get('modal_shown', False):
        show_modal = True
        request.session['modal_shown'] = True
    else:
        show_modal = False

    context = {
        "sessions": sessions,
        "active_session": active_session,
        "messages": messages_qs,
        "last_session": last_session,
        "show_modal": show_modal,
    }
    return render(request, "home_page/chat.html", context)


@login_required
def redirect_to_latest_chat(request):
    user = request.user
    last_session = ConversationSession.objects.filter(user=user).order_by('-created_at').first()
    if last_session:
        return redirect('chatbot-main', session_id=last_session.session_id)
    return redirect('chatbot-new')


AI_APP_URL = "http://ai_app:8000/chat"  # آدرس سرویس FastAPI

@login_required
@csrf_exempt  # یا حذف و استفاده از CSRF token هدر
def chatbot_main(request, session_id):
    active_session = get_object_or_404(
        ConversationSession,
        session_id=session_id,
        user=request.user
    )

    if request.method == "POST":
        try:
            body_data = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        user_text = body_data.get("message", "").strip()
        ai_reply = None
        detected_language = None

        if not user_text:
            return JsonResponse({"error": "Empty message"}, status=400)

        # ثبت پیام کاربر
        user_message = ChatMessage.objects.create(
            session=active_session,
            sender="user",
            message=user_text,
            detected_language="Unknown",
            original_message=user_text
        )

        # ساخت history برای AI
        history = [
            {"role": "user" if m.sender == "user" else "bot", "content": m.message}
            for m in ChatMessage.objects.filter(session=active_session).order_by("timestamp")
        ]
        payload = {
            "session_id": str(active_session.session_id),
            "message": user_text,
            "history": history
        }

        try:
            resp = requests.post(AI_APP_URL, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()

            ai_reply = data.get("answer", "No reply")
            detected_language = data.get("detected_language", "English")

            # آپدیت پیام کاربر با زبان شناسایی‌شده
            user_message.detected_language = detected_language
            user_message.save()

            # ثبت جواب AI
            ChatMessage.objects.create(
                session=active_session,
                sender="bot",
                message=ai_reply,
                detected_language=detected_language,
                original_message=ai_reply
            )
        except Exception as e:
            ai_reply = f"[Error] {str(e)}"

        return JsonResponse({
            "ai_reply": ai_reply,
            "user_message": user_text,
            "detected_language": detected_language
        })

    # GET → لود صفحه چت
    sessions = ConversationSession.objects.filter(user=request.user).order_by("-created_at")
    messages_qs = ChatMessage.objects.filter(session=active_session).order_by("timestamp")
    return render(request, "home_page/chat.html", {
        "sessions": sessions,
        "active_session": active_session,
        "messages": messages_qs
    })


@csrf_exempt
def create_new_session(request):
    user = request.user
    # ایجاد سشن جدید با زبان پیش‌فرض
    session = ConversationSession.objects.create(
        user=user,
        user_language='English'  # زبان پیش‌فرض
    )
    return redirect('chatbot-main', session_id=session.session_id)


@csrf_exempt
def delete_session(request, session_id):
    session = get_object_or_404(ConversationSession, user=request.user, session_id=session_id)
    session.delete()

    # بعد حذف، به آخرین جلسه موجود برگرد
    last_session = ConversationSession.objects.filter(user=request.user).order_by('-created_at').first()
    if last_session:
        return redirect('chatbot-main', session_id=last_session.session_id)
    else:
        return redirect('chatbot-new')


@csrf_exempt
def chatbot_new(request):
    # ایجاد جلسه جدید با زبان پیش‌فرض
    new_session = ConversationSession.objects.create(
        user=request.user,
        user_language='English'  # زبان پیش‌فرض
    )

    return redirect('chatbot-main', session_id=new_session.session_id)
