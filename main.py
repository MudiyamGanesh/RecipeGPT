import os
import json
import base64
from datetime import datetime
from typing import List, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from recipe import create_recipegpt_chain

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RECENTS_DIR = "recents"
IMAGES_DIR = "images"

os.makedirs(RECENTS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# Global chain (single user app)
qa_chain = create_recipegpt_chain()
current_chat_file = None
messages = []

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str

@app.get("/api/images")
def get_images():
    supported = (".png", ".jpg", ".jpeg", ".webp")
    images = []
    for f in sorted(os.listdir(IMAGES_DIR)):
        if f.lower().endswith(supported):
            img_path = os.path.join(IMAGES_DIR, f)
            with open(img_path, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode()
                images.append(f"data:image/png;base64,{encoded}")
    return {"images": images}

@app.get("/api/recents")
def get_recents():
    files = [f for f in os.listdir(RECENTS_DIR) if f.endswith(".json")]
    files.sort(reverse=True)
    recents = []
    for f in files:
        try:
            with open(os.path.join(RECENTS_DIR, f), "r", encoding="utf-8") as file:
                data = json.load(file)
                title = data.get("title", f)
                recents.append({"id": f, "title": title})
        except Exception:
            continue
    return {"recents": recents}

def generate_chat_title(first_message):
    title = first_message.strip().replace("\n", " ")
    if len(title) > 40:
        title = title[:40] + "..."
    return title or "Untitled Chat"

def save_current_conversation():
    global current_chat_file, messages
    if not messages:
        return

    conversation = []
    i = 0
    while i < len(messages) - 1:
        if messages[i]["role"] == "user" and messages[i + 1]["role"] == "assistant":
            conversation.append({
                "user": messages[i]["content"],
                "assistant": messages[i + 1]["content"],
            })
            i += 2
        else:
            i += 1

    if not conversation:
        return

    if current_chat_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        title = generate_chat_title(conversation[0]["user"])
        safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "_")
        filename = f"{timestamp}_{safe_title}.json"
        current_chat_file = filename

    data = {
        "timestamp": datetime.now().isoformat(),
        "title": generate_chat_title(conversation[0]["user"]),
        "conversation": conversation,
    }

    with open(os.path.join(RECENTS_DIR, current_chat_file), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.post("/api/chat")
def chat(req: ChatRequest):
    global messages
    prompt = req.message
    messages.append({"role": "user", "content": prompt})
    
    try:
        result = qa_chain.invoke({"question": prompt})
        answer = result.get("answer", "No response generated.")
    except Exception as e:
        answer = f"Error: {e}"

    messages.append({"role": "assistant", "content": answer})
    save_current_conversation()
    
    return {"answer": answer}

@app.post("/api/chat/new")
def new_chat():
    global qa_chain, current_chat_file, messages
    save_current_conversation()
    messages = []
    qa_chain.memory.clear()
    current_chat_file = None
    return {"status": "ok"}

@app.get("/api/chat/{chat_id}")
def load_chat(chat_id: str):
    global qa_chain, current_chat_file, messages
    save_current_conversation()
    
    file_path = os.path.join(RECENTS_DIR, chat_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Chat not found")
        
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    conversation = data.get("conversation", [])
    messages = []
    qa_chain.memory.clear()
    
    for turn in conversation:
        user_msg = turn["user"]
        ai_msg = turn["assistant"]
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": ai_msg})
        qa_chain.memory.chat_memory.add_user_message(user_msg)
        qa_chain.memory.chat_memory.add_ai_message(ai_msg)
        
    current_chat_file = chat_id
    return {"messages": messages, "title": data.get("title")}

@app.delete("/api/chat/{chat_id}")
def delete_chat(chat_id: str):
    global current_chat_file, messages, qa_chain
    file_path = os.path.join(RECENTS_DIR, chat_id)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    if current_chat_file == chat_id:
        messages = []
        qa_chain.memory.clear()
        current_chat_file = None
        
    return {"status": "ok"}

# Run with: uvicorn main:app --reload
