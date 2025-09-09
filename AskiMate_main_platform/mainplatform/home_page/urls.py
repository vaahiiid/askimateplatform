from django.urls import path
from . import views

urlpatterns = [
    # صفحات عمومی
    path('', views.main_page, name='main_page'),
    path('contact/', views.contact_form, name='contact_form'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.custom_login_view, name='custom_login'),
    path('login/email/', views.email_login_view, name='email_login'),
    path('login/password/', views.password_login_view, name='password_login'),

    # چت
    path('chat/', views.redirect_to_latest_chat, name='chatbot-view'),  # میره آخرین سشن
    path('chat/new/', views.create_new_session, name='chatbot-new'),    # ساخت سشن جدید و رفتن بهش
    path('chat/<uuid:session_id>/', views.chatbot_main, name='chatbot-main'),  # نمایش سشن

    # حذف سشن
    path('chat/delete/<uuid:session_id>/', views.delete_session, name='delete-session'),
]
