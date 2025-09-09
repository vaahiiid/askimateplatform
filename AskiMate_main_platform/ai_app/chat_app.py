from fastapi import FastAPI
from contextlib import asynccontextmanager
from rasa.core.agent import Agent
import boto3
import yaml
import json
from pydantic import BaseModel
import uuid
from langdetect import detect

# -----------------------------
# Load config
with open("config.yml", "r") as config_file:
    config = yaml.safe_load(config_file)

# -----------------------------
# AWS Bedrock client setup - rely on container AWS credentials
bedrock_client = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'  # ثابت نگه می‌داریم
)

# -----------------------------
def detect_language(text: str) -> str:
    """
    Detect the language of the given text and return a string.
    - Returns "English" if detected as English.
    - For very short texts (<5 chars), defaults to "English" to avoid langdetect misfires.
    - On error, returns "Unknown".
    """
    try:
        if not isinstance(text, str) or not text.strip():
            return "Unknown"

        if len(text.strip()) < 5:
            print(f"[DEBUG] Short text detected ('{text}'), defaulting language to English")
            return "English"

        lang_code = detect(text)
        if lang_code == "en":
            return "English"
        return lang_code
    except Exception as e:
        print(f"[ERROR] Language detection failed: {e}")
        return "Unknown"

# -----------------------------
def translate_to_english(text, source_language):
    print(f"[DEBUG] translate_to_english source_language={source_language} ({type(source_language)})")
    if isinstance(source_language, str) and source_language.lower() == "english":
        return text
    prompt = f"""<|begin_of_text|>..."""
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
        return response_body.get('generation', text).strip()
    except Exception as e:
        print(f"[ERROR] translation to English failed: {e}")
        return text

def translate_from_english(text, target_language):
    print(f"[DEBUG] translate_from_english target_language={target_language} ({type(target_language)})")
    if isinstance(target_language, str) and target_language.lower() == "english":
        return text
    prompt = f"""<|begin_of_text|>..."""
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
        return response_body.get('generation', text).strip()
    except Exception as e:
        print(f"[ERROR] translation from English failed: {e}")
        return text

# -----------------------------
def format_llama_prompt(system_message, user_message, chat_history):
    prompt = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
    prompt += system_message + "<|eot_id|>"
    if chat_history:
        for msg in chat_history:
            role = msg.get('role')
            content = msg.get('content', '')
            if role == 'user':
                prompt += f"<|start_header_id|>user<|end_header_id|>\n\n{content}<|eot_id|>"
            else:
                prompt += f"<|start_header_id|>assistant<|end_header_id|>\n\n{content}<|eot_id|>"
    prompt += f"<|start_header_id|>user<|end_header_id|>\n\n{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    return prompt

# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.agent = Agent.load("models/20250724-114045-optimal-level.tar.gz")
    yield

app = FastAPI(lifespan=lifespan)

# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# -----------------------------
sessions = {}

class ChatRequest(BaseModel):
    session_id: str = None
    message: str
    history: list[dict] = []

@app.post("/chat/")
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    message = request.message
    chat_history = request.history

    user_language = detect_language(message)
    print(f"[DEBUG] Detected user_language={user_language} ({type(user_language)})\n")

    agent = app.state.agent

    if isinstance(user_language, str) and user_language.lower() != "english":
        english_message = translate_to_english(message, user_language)
        print(f"[DEBUG] english_message={english_message}\n")
        responses = await agent.handle_text(english_message, sender_id=session_id)
    else:
        english_message = message
        responses = await agent.handle_text(message, sender_id=session_id)

    answer = responses[0].get("text", "") if responses else ""
    print(f"[DEBUG] rasa text: {answer}\n")

    system_message = f"... Context:\n{answer}\n..."
    formatted_prompt = format_llama_prompt(system_message, message, chat_history)

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

        model_response = translate_from_english(english_response, user_language)
    except Exception as e:
        print(f"[ERROR] Bedrock error: {e}")
        model_response = translate_from_english("Sorry, there was an error.", user_language)

    print(f"[DEBUG] model_response: {model_response}\n")

    return {
        "session_id": session_id,
        "answer": model_response,
        "detected_language": user_language,
        "original_message": message,
        "translated_message": english_message if isinstance(user_language, str) and user_language.lower() != "english" else None
    }
