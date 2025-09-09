from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

class ChatRequest(BaseModel):
    session_id: str
    message: str
    history: List[Dict[str, str]]

class ChatResponse(BaseModel):
    reply: str

@app.post("/chat/", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):

    ai_output = f"AI says: I got your message '{req.message}' and see {len(req.history)} messages in history."
    return ChatResponse(reply=ai_output)
