import uuid
from .models import Conversation

def generate_session_id():
    return str(uuid.uuid4())  # You can customize if needed

def start_new_conversation(user, title=""):
    session_id = generate_session_id()
    conversation = Conversation.objects.create(
        session_id=session_id,
        user=user,
        title=title,
        messages=[]
    )
    return conversation

def get_user_conversations(user):
    return Conversation.objects.filter(user=user).order_by('-updated_at')

def get_conversation_by_session(user, session_id):
    try:
        return Conversation.objects.get(user=user, session_id=session_id)
    except Conversation.DoesNotExist:
        return None

def add_message(conversation, sender, text):
    from django.utils import timezone
    message = {
        'sender': sender,
        'text': text,
        'timestamp': timezone.now().isoformat(),
    }
    conversation.messages.append(message)
    conversation.save()
