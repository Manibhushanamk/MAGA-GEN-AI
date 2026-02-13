# Constructive Builder Demo

## Prerequisites

- Python 3.8+
- Node.js 18+

## Quick Start

### 1. Backend

Open a terminal in the root directory:

```bash
# Install dependencies (if not already)
pip install fastapi uvicorn google-generativeai openai networkx

# Run Server
uvicorn backend.main:app --reload --port 8000
```

### 2. Frontend

Open a new terminal in the `frontend` directory:

```bash
cd frontend

# Install dependencies (if unexpected failure)
npm install

# Run Frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Features

- **Cost Engine**: Real-time calculation of Labor, Material, Overhead.
- **Scheduler**: Forward pass scheduling.
- **LLM Integration**: Executive summary via Gemini/Groq.
- **Risk Analysis**: Monte Carlo simulation (P50/P80).
