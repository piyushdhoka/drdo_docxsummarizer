Document Summarizer — quick start (Windows PowerShell)

This repository contains a Streamlit UI and a FastAPI backend for summarizing documents.

Quick checklist
- Create a Python virtual environment (recommended)
- Install dependencies from `requirements.txt`
- Start both services (Streamlit UI + FastAPI)

Setup (PowerShell)

1. Create and activate venv

   python -m venv venv
   .\venv\Scripts\Activate.ps1

2. Upgrade pip and install requirements

   python -m pip install --upgrade pip
   pip install -r requirements.txt

3. Start services (uses `start_services.bat`)

   .\start_services.bat

Manual runs (if you prefer)

- Start Streamlit UI:

  .\venv\Scripts\Activate.ps1
  streamlit run app.py

- Start FastAPI server:

  .\venv\Scripts\Activate.ps1
  uvicorn fastapi_app:app --reload --host 0.0.0.0 --port 8000

