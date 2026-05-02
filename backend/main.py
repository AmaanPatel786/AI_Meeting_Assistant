from fastapi import FastAPI, UploadFile, Form, Query, File
from fastapi.middleware.cors import CORSMiddleware

import whisper
import json
import os
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

from sentence_transformers import SentenceTransformer
import numpy as np

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================
# GEMINI SETUP
# =====================
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY missing in environment")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")

# =====================
# WHISPER
# =====================
whisper_model = whisper.load_model("base")

# =====================
# 🧠 SEMANTIC MODEL
# =====================
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text: str):
    """Generate semantic embedding vector"""
    return embedding_model.encode(text).tolist()


# =====================
# STORAGE
# =====================
DB_FILE = "data.json"


def save_to_db(data):
    try:
        with open(DB_FILE, "r") as f:
            db = json.load(f)
    except Exception:
        db = []

    db.append(data)

    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)


def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


# =====================
# TAGGING ENGINE
# =====================
def extract_tags(text: str):
    text = text.lower()

    tag_map = {
        "Performance": ["slow", "lag", "latency", "performance"],
        "Bug": ["bug", "error", "issue", "crash", "fail"],
        "Client": ["client", "customer", "stakeholder"],
        "Engineering": ["backend", "api", "deploy", "server"],
        "Frontend": ["ui", "ux", "design", "frontend"],
        "Operations": ["process", "workflow", "approval"],
        "Product": ["feature", "requirement", "scope"]
    }

    tags = set()

    for tag, keywords in tag_map.items():
        if any(k in text for k in keywords):
            tags.add(tag)

    return list(tags) if tags else ["General"]


# =====================
# SAFE JSON PARSER (Gemini protection)
# =====================
def safe_json_parse(text: str):
    try:
        # try direct JSON
        return json.loads(text)
    except:
        pass

    try:
        # extract JSON block if model adds noise
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start:end+1])
    except:
        pass

    return {
        "summary": text,
        "action_items": []
    }


# =====================
# AI FUNCTION
# =====================
def generate_summary(text, participants):
    try:
        prompt = f"""
You are an AI Meeting Assistant.

Return ONLY valid JSON:

{{
  "summary": "short 2-3 line summary",
  "action_items": [
    {{
      "task": "string",
      "owner": "string",
      "priority": "High | Medium | Low"
    }}
  ]
}}

Rules:
- No markdown
- No extra text
- Output must be valid JSON only

Meeting Notes:
{text}

Participants:
{participants}
"""

        response = model.generate_content(prompt)
        raw = response.text.strip()

        return safe_json_parse(raw)

    except Exception as e:
        print("AI ERROR:", e)
        return {
            "summary": text[:200],
            "action_items": []
        }


# =====================
# COSINE SIMILARITY
# =====================
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)

    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0

    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# =====================
# API: SUMMARIZE
# =====================
@app.post("/summarize")
async def summarize(
    title: str = Form(...),
    notes: str = Form(""),
    participants: str = Form(""),
    file: UploadFile | None = File(None)
):
    text = notes

    # 🎤 AUDIO → TEXT
    if file is not None and file.filename:
        audio_path = f"temp_{file.filename}"

        with open(audio_path, "wb") as f:
            f.write(await file.read())

        try:
            result = whisper_model.transcribe(audio_path)
            text = result.get("text", "")
        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)

    output = generate_summary(text, participants)

    # 🏷️ TAGGING
    for item in output.get("action_items", []):
        task_text = item.get("task", "")
        item["tags"] = extract_tags(task_text + " " + text)

    # 🧠 EMBEDDING
    embedding = get_embedding(output.get("summary", ""))

    record = {
        "title": title,
        "participants": participants,
        "input_text": text,
        "summary": output.get("summary", ""),
        "action_items": output.get("action_items", []),
        "timestamp": str(datetime.now()),
        "embedding": embedding
    }

    save_to_db(record)

    return record


# =====================
# HISTORY
# =====================
@app.get("/history")
def history():
    return load_db()


@app.delete("/history")
def clear_history():
    with open(DB_FILE, "w") as f:
        json.dump([], f)
    return {"message": "cleared"}


# =====================
# 🔍 SEMANTIC SEARCH
# =====================
@app.get("/search")
def search(q: str = Query(...)):
    db = load_db()

    query_vec = get_embedding(q)
    results = []

    for item in db:
        if "embedding" not in item:
            continue

        score = cosine_similarity(query_vec, item["embedding"])

        results.append({
            "title": item.get("title", ""),
            "summary": item.get("summary", ""),
            "score": score
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:5]