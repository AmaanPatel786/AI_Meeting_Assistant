# 📒 AI Meeting Notes Assistant

An AI-powered tool that converts raw meeting notes (text or audio) into structured summaries, action items, and ownership insights.

It helps teams turn messy discussions into clean, actionable outputs in seconds.

---

## 🏗️ Architecture

Frontend (HTML + JS)
        →
FastAPI Backend (Python)
        →
Whisper (Audio → Text)
        →
Gemini AI (Summarization)
        →
JSON Storage (data.json)
        →
History API → Frontend UI

---

## 🧠 Why this stack?

### Frontend (HTML + JS)
- Lightweight, fast to build
- No build tools needed
- Perfect for MVP speed

### FastAPI
- High performance Python backend
- Easy async handling
- Great for ML + AI integration

### Whisper
- Reliable speech-to-text model
- Works offline
- No dependency on paid APIs

### Gemini AI
- Fast, high-quality summarization
- Strong structured output capability
- Easy integration via SDK

### JSON storage
- Simple persistence for MVP
- No database overhead
- Easy debugging

---

## ⚖️ Tradeoffs

- ❌ No database (used JSON instead of PostgreSQL/MongoDB)
- ❌ No authentication system
- ❌ Limited scalability for concurrent users
- ❌ AI output sometimes requires fallback parsing

---

## 🚀 What I would improve

- Add PostgreSQL or MongoDB for scalable storage
- Add authentication (JWT / OAuth)
- Improve AI structured output with schema enforcement
- Deploy on cloud (Render / AWS / Vercel)
- Improve UI responsiveness for mobile

---

## 📌 Features

- 📝 Text-based meeting notes input
- 🎤 Audio upload → transcription
- 🧠 AI summary + action items
- 👤 Owner + priority tagging
- 📚 History tracking
- 📚 Semantic Search on past meetings

---

## ⚙️ Setup

pip install fastapi uvicorn python-multipart openai-whisper google-generativeai python-dotenv

Run backend:

uvicorn main:app --reload

Open frontend:

index.html

Run frontend:

python -m http.server 5500

---

## 📡 API

POST /summarize
Generates summary + action items.

GET /history
Returns previous meetings.
