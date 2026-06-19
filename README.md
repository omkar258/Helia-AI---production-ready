# 🌟 Helia AI – Intelligent Mental Well-being Assistant

<div align="center">

![Helia AI](https://img.shields.io/badge/Helia_AI-Mental_Wellbeing-7c3aed?style=for-the-badge&logo=sparkles)
![Next.js](https://img.shields.io/badge/Next.js-16-black?style=flat-square&logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql)
![Llama](https://img.shields.io/badge/Llama_3.1-Ollama-blue?style=flat-square)

*An AI-powered mental health companion with empathetic conversations, mood tracking, journaling, and personalized wellness plans.*

</div>

> ⚠️ **Important Disclaimer**: Helia AI is NOT a substitute for professional mental health care. If you are in crisis, please contact emergency services or a crisis helpline immediately.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Database Schema](#-database-schema)
- [Project Structure](#-project-structure)
- [Deployment](#-deployment)
- [Testing](#-testing)

---

## ✨ Features

### 🤖 AI Conversations
- Empathetic, context-aware conversations powered by Llama 3.1 via Ollama
- RAG-augmented responses using mental health knowledge base
- Personalized memory across sessions

### 🎯 Emotion & Sentiment Analysis
- Real-time emotion detection (joy, sadness, anger, fear, surprise, etc.)
- Sentiment scoring (-1.0 to 1.0) on every interaction
- Historical emotion analytics and distribution charts

### 📔 AI Journaling
- Free-form journaling with AI-powered analysis
- Automatic mood tagging and emotion detection
- Pattern recognition across entries

### 📊 Mood Tracking
- Visual mood logger with emoji-based scoring (1-10)
- Contributing factors tracking (work, sleep, exercise, etc.)
- Trend charts over 7/30/90 day periods

### 💚 Wellness Plans
- Personalized recommendations based on mood data
- AI-generated wellness plans (anxiety, stress, sleep, etc.)
- Progress tracking with milestones

### 🚨 Crisis Detection
- Two-stage detection: regex keyword matching + AI analysis
- Immediate safety resources and crisis hotline information
- Conversation flagging for crisis events

### 📈 Analytics Dashboard
- Overview stats (conversations, entries, logs, streak)
- Mood trend area charts and emotion radar charts
- Weekly reports with AI-generated insights

### 🎨 Premium UI/UX
- Dark/Light mode with smooth transitions
- Glassmorphism design with gradient accents
- Responsive layout (mobile → desktop)
- Micro-animations with Framer Motion

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS 4 |
| **Backend** | FastAPI 0.115, Python 3.11, Async SQLAlchemy |
| **Database** | PostgreSQL 16, Alembic (migrations) |
| **AI/ML** | Llama 3.1 (Ollama), sentence-transformers, FAISS |
| **Auth** | JWT (access + refresh tokens), bcrypt |
| **UI** | Recharts, Lucide React, Framer Motion, next-themes |
| **Infra** | Docker, Docker Compose |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                │
│  ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌─────────┐  │
│  │ Landing  │ │   Chat   │ │Dashboard│ │ Journal │  │
│  └────┬─────┘ └────┬─────┘ └────┬────┘ └────┬────┘  │
│       └─────────────┼───────────┼───────────┘        │
│                     │    REST API                    │
└─────────────────────┼────────────────────────────────┘
                      │
┌─────────────────────┼────────────────────────────────┐
│                Backend (FastAPI)                      │
│  ┌──────────┐  ┌───────────┐  ┌──────────────────┐   │
│  │ Auth     │  │ AI Engine │  │ RAG Service      │   │
│  │ Service  │  │ (Ollama)  │  │ (FAISS+MiniLM)   │   │
│  └──────────┘  └───────────┘  └──────────────────┘   │
│  ┌──────────┐  ┌───────────┐  ┌──────────────────┐   │
│  │ Emotion  │  │ Crisis    │  │ Wellness         │   │
│  │ Service  │  │ Detector  │  │ Recommender      │   │
│  └──────────┘  └───────────┘  └──────────────────┘   │
└──────────────────────┬───────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
     ┌────┴─────┐ ┌───┴────┐ ┌────┴─────┐
     │PostgreSQL│ │ Ollama │ │  FAISS   │
     │    DB    │ │ Server │ │  Index   │
     └──────────┘ └────────┘ └──────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** 20+ and **npm**
- **Python** 3.11+
- **PostgreSQL** 16+
- **Ollama** installed ([ollama.com](https://ollama.com))

### Option 1: Docker (Recommended)

```bash
# Clone and navigate
cd mental_well_being_chatbot

# Copy env file
cp .env.example .env

# Start all services
docker compose up --build

# Pull Llama 3.1 model (in a new terminal)
docker exec -it helia-ollama ollama pull llama3.1
```

Access: Frontend → `http://localhost:3000` | API Docs → `http://localhost:8000/docs`

### Option 2: Local Development

#### 1. Start PostgreSQL & Ollama
```bash
# Start Ollama and pull model
ollama serve
ollama pull llama3.1
```

#### 2. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and edit .env
cp ../.env.example .env

# Run server
uvicorn app.main:app --reload --port 8000
```

#### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 📡 API Documentation

Once running, visit `http://localhost:8000/docs` for interactive Swagger docs.

### Key Endpoints

| Category | Endpoint | Method | Description |
|----------|----------|--------|-------------|
| Auth | `/api/v1/auth/register` | POST | Register |
| Auth | `/api/v1/auth/login` | POST | Login |
| Chat | `/api/v1/chat/message` | POST | Send message |
| Journal | `/api/v1/journal/entries` | GET/POST | CRUD entries |
| Journal | `/api/v1/journal/analyze` | POST | AI analysis |
| Mood | `/api/v1/mood/log` | POST | Log mood |
| Mood | `/api/v1/mood/trends` | GET | Get trends |
| Wellness | `/api/v1/wellness/recommendations` | GET | Get recs |
| Dashboard | `/api/v1/dashboard/overview` | GET | Stats |

---

## 💾 Database Schema

- **users** – Authentication, profile, preferences
- **conversations** – Chat history with emotion/sentiment metadata
- **journal_entries** – User journals with AI analysis
- **mood_logs** – Mood scores, emotions, contributing factors
- **wellness_plans** – Goals, recommendations, progress
- **user_memories** – Personalized AI context

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend build check
cd frontend
npm run build
```

---

## 📦 Deployment

### Option 1: Vercel (Frontend) + Hugging Face Spaces (Backend) — *Recommended, Free (Full RAG)*

Since Hugging Face Spaces provides **16 GB RAM** for free, you can run the full PyTorch + SentenceTransformers RAG system without Out-Of-Memory (OOM) errors.

#### Backend → Hugging Face Spaces

1. Go to **[huggingface.co/spaces](https://huggingface.co/spaces)** and click **Create new Space**.
2. Name your space (e.g., `helia-backend`) and select **Docker** as the SDK.
3. Choose the **Blank** template (default).
4. Keep it **Public** (required for Vercel to access the API).
5. Once created, go to the Space **Settings** page and add your **Variables and Secrets**:
   - Add Secret: `GROQ_API_KEY` → your Groq API key
   - Add Variable: `FRONTEND_URL` → your Vercel URL (e.g., `https://helia-ai.vercel.app`)
   - Add Variable: `CORS_ORIGINS_STR` → same as FRONTEND_URL
   - Add Variable: `DISABLE_RAG` → `false` (to enable full RAG features)
6. Clone the space repository locally or push your existing git repo directly to the Hugging Face space remote URL.

*Note: Hugging Face automatically detects the `backend/Dockerfile` if you configure the Space's entry directory or push the backend directly.*

#### Frontend → Vercel

1. Go to [vercel.com](https://vercel.com) → **Add New Project**
2. Import your GitHub repo, set **Root Directory** to `frontend`
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL` → `https://<your-username>-<your-space-name>.hf.space/api/v1`
4. Deploy! Frontend will be live at `https://your-app.vercel.app`


### Option 2: Docker Compose (Self-hosted)

```bash
# Copy and edit environment variables
cp .env.example .env
# Edit .env with your GROQ_API_KEY and JWT_SECRET_KEY

# Start all services
docker compose up --build -d

# View logs
docker compose logs -f
```

Access: Frontend → `http://localhost:3000` | API → `http://localhost:8000/docs`

### Production Checklist
- [x] Groq API key configured
- [ ] Change `JWT_SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=false`
- [ ] Use strong `POSTGRES_PASSWORD`
- [ ] Configure proper CORS origins (`CORS_ORIGINS_STR`)
- [ ] Set up SSL/TLS termination (handled by Vercel/Render)
- [ ] Set up database backups (Render provides automated backups on paid plans)

---

## 📄 License

MIT License. Built with ❤️ for mental well-being.
