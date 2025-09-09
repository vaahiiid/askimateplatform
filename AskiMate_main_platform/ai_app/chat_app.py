# chat_app.py - Fixed version with detected_language in response

from fastapi import FastAPI
from contextlib import asynccontextmanager
from rasa.core.agent import Agent
import boto3
import yaml
import json
import re


with open("config.yml", "r") as config_file:
    config = yaml.safe_load(config_file)

# AWS Bedrock client setup
bedrock_client = boto3.client(
    'bedrock-runtime',
    region_name=config['AWS']['region'],
    aws_access_key_id=config['AWS']['access_key_id'],
    aws_secret_access_key=config['AWS']['secret_access_key']
)

def detect_language(text):
    """تشخیص زبان متن ورودی"""
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a language detection expert. Detect the language of the given text and respond with ONLY the language name in English (e.g., "English", "Persian", "Arabic", "French", "Spanish", "German", etc.). If the text contains multiple languages, identify the dominant language. Be very accurate in your detection.

<|eot_id|><|start_header_id|>user<|end_header_id|>

{text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

    try:
        request_body = {
            "prompt": prompt,
            "max_gen_len": 50,
            "temperature": 0.1,
            "top_p": 0.9
        }
        
        response = bedrock_client.invoke_model(
            modelId=config['AWS']['model_id'],
            body=json.dumps(request_body),
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        detected_language = response_body.get('generation', 'English').strip()
        
        return detected_language
        
    except Exception as e:
        print(f"Error in language detection: {e}")
        return "English"  # پیش‌فرض انگلیسی

def translate_to_english(text, source_language):
    """ترجمه متن از زبان مبدا به انگلیسی"""
    if source_language.lower() == "english":
        return text
    
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a professional translator. Translate the following {source_language} text to English accurately. Maintain the original meaning, context, and intent. If there are any spelling errors or typos in the source text, correct them during translation. Provide ONLY the English translation without any additional text or explanation.

<|eot_id|><|start_header_id|>user<|end_header_id|>

{text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

    try:
        request_body = {
            "prompt": prompt,
            "max_gen_len": 500,
            "temperature": 0.2,
            "top_p": 0.9
        }
        
        response = bedrock_client.invoke_model(
            modelId=config['AWS']['model_id'],
            body=json.dumps(request_body),
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        translated_text = response_body.get('generation', text).strip()
        
        return translated_text
        
    except Exception as e:
        print(f"Error in translation to English: {e}")
        return text

def translate_from_english(text, target_language):
    """ترجمه متن از انگلیسی به زبان هدف"""
    if target_language.lower() == "english":
        return text
    
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a professional translator. Translate the following English text to {target_language} accurately. Maintain the original meaning, context, and intent. Make sure the translation is natural and fluent in {target_language}. Provide ONLY the {target_language} translation without any additional text or explanation.

<|eot_id|><|start_header_id|>user<|end_header_id|>

{text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

    try:
        request_body = {
            "prompt": prompt,
            "max_gen_len": 500,
            "temperature": 0.2,
            "top_p": 0.9
        }
        
        response = bedrock_client.invoke_model(
            modelId=config['AWS']['model_id'],
            body=json.dumps(request_body),
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        translated_text = response_body.get('generation', text).strip()
        
        return translated_text
        
    except Exception as e:
        print(f"Error in translation from English: {e}")
        return text

def format_llama_prompt(system_message, user_message, chat_history):
    """Format prompt according to Llama 3.1 chat template"""
    prompt = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
    prompt += system_message
    prompt += "<|eot_id|>"
    
    # Add conversation history
    if chat_history and isinstance(chat_history, list):
        for msg in chat_history:
            if isinstance(msg, dict):
                if msg.get('role') == 'user':
                    prompt += "<|start_header_id|>user<|end_header_id|>\n\n"
                    prompt += msg.get('content', '')
                    prompt += "<|eot_id|>"
                elif msg.get('role') == 'bot' or msg.get('role') == 'assistant':
                    prompt += "<|start_header_id|>assistant<|end_header_id|>\n\n"
                    prompt += msg.get('content', '')
                    prompt += "<|eot_id|>"
    
    # Current user message
    prompt += "<|start_header_id|>user<|end_header_id|>\n\n"
    prompt += user_message
    prompt += "<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    
    return prompt

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the Rasa agent/model at app startup
    app.state.agent = Agent.load("models/20250724-114045-optimal-level.tar.gz")
    yield
    # Put any shutdown/cleanup code here if needed

app = FastAPI(lifespan=lifespan)

# Now access the agent via app.state.agent in your route
from pydantic import BaseModel
import uuid

sessions = {}

class ChatRequest(BaseModel):
    session_id: str = None
    message: str
    history: list[dict] = []

@app.post("/chat/")
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id
    message = request.message
    chat_history = request.history
    print('chat_history: \n', chat_history)

    # مرحله 1: تشخیص زبان پیام کاربر
    user_language = detect_language(message)
    print(f"Detected language: {user_language}")

    # مرحله 2: ترجمه پیام به انگلیسی (در صورت لزوم)
    english_message = translate_to_english(message, user_language)
    print(f"English message: {english_message}")

    # مرحله 3: ترجمه تاریخچه چت به انگلیسی برای پردازش
    english_history = []
    if chat_history:
        for msg in chat_history:
            if isinstance(msg, dict):
                content = msg.get('content', '')
                role = msg.get('role', '')
                
                if role == 'user':
                    # ترجمه پیام‌های کاربر به انگلیسی
                    msg_language = detect_language(content)
                    english_content = translate_to_english(content, msg_language)
                    english_history.append({"role": "user", "content": english_content})
                else:
                    # پیام‌های بات احتمالاً قبلاً ترجمه شده‌اند، پس آنها را همان‌طور نگه می‌داریم
                    english_history.append({"role": "bot", "content": content})

    # Access the loaded Agent via app.state
    agent = app.state.agent

    responses = await agent.handle_text(
        english_message,
        sender_id=session_id
    )

    answer = responses[0].get("text", "") if responses else ""
    print(f"Rasa response (English): {answer}")
    
    system_message = f"""
You are AskiMate, a super friendly, cool, approachable AI assistant who helps students with everything about studying abroad—especially the UK and Europe.

**Behavior:**
- If users greet you ("hi", "hey", "hello"), thank you, ask how you are, wish you well (etc): respond naturally, warmly, and conversationally—just like a supportive friend would.
- If users express feelings (happy, sad, worried, excited): respond supportively, show empathy, and use casual, relatable, and uplifting language.
- For those general/introduction moments, it's okay to be informal, fun, or use emojis as long as it's kind and inclusive.
- For ALL other queries, base your answers entirely on the information given in Context (below), and if the information is not in the Context, say so politely.
- The conversation history (conversation session) is also placed below, if you do not find the answer from context then please check the conversation history.

**Important:**
- Never invent your own name or personal story—always use the name, details, and identity from Context.
- For questions not about studying abroad or about illegal/inappropriate topics, politely explain your area of expertise but stay friendly and open.
- You are allowed to answer general chit-chat and emotional/rapport-building messages as a real assistant would.
- Always check the chat history to find the relevant information of the session.

**Context for this conversation:**
{answer}

**Student's Question:**
{english_message}

**Conversation history:**
{english_history}

Respond in a friendly and engaging tone—as AskiMate!
    """
    
    # Format prompt for Llama 3.1
    formatted_prompt = format_llama_prompt(system_message, english_message, english_history)
    
    print("Formatted prompt:", formatted_prompt[:200] + "..." if len(formatted_prompt) > 200 else formatted_prompt)

    print("Sending request to AWS Bedrock...")
    model_response = ""
    
    try:
        request_body = {
            "prompt": formatted_prompt,
            "max_gen_len": 500,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        response = bedrock_client.invoke_model(
            modelId=config['AWS']['model_id'],
            body=json.dumps(request_body),
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        english_response = response_body.get('generation', '')
        print(f"AI response (English): {english_response}")
        
        # مرحله 4: ترجمه پاسخ به زبان اصلی کاربر
        model_response = translate_from_english(english_response, user_language)
        print(f"Final response ({user_language}): {model_response}")
        
        print("Completed receiving response from AWS Bedrock.")
        
    except json.JSONDecodeError as e:
        print(f"\nError decoding JSON: {e}")
        error_msg = "Sorry, there was an error processing your request."
        model_response = translate_from_english(error_msg, user_language)
        user_language = "English"  # fallback language

    except Exception as e:
        print(f"\nAn unexpected error occurred with AWS Bedrock: {e}")
        error_msg = "Sorry, there was an error connecting to the service."
        model_response = translate_from_english(error_msg, user_language)
        user_language = "English"  # fallback language

    # اضافه کردن detected_language به پاسخ
    return {
        "session_id": session_id,
        "answer": model_response,
        "detected_language": user_language,  # این خط مهم است!
        "original_message": message,
        "translated_message": english_message if user_language.lower() != "english" else None
    }