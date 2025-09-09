from django.db import models
from django.contrib.auth.models import User
import uuid

class ConversationSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user_language = models.CharField(max_length=50, default='English', help_text='User preferred language')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.session_id} ({self.user.email})"

class ChatMessage(models.Model):
    session = models.ForeignKey(ConversationSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=16, choices=[('user', 'User'), ('bot', 'Bot')])
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    # فیلدهای اختیاری برای ذخیره زبان (در صورت نیاز)
    detected_language = models.CharField(max_length=50, blank=True, null=True, help_text='Detected language of the message')
    original_message = models.TextField(blank=True, null=True, help_text='Original message before translation')
    translated_message = models.TextField(blank=True, null=True, help_text='Translated message')
    is_translated = models.BooleanField(default=False)  # اضافه کردن default=False

    def __str__(self):
        return f"{self.sender} said '{self.message[:24]}'"