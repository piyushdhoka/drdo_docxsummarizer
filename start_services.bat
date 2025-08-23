@echo off
echo Starting Document Summarizer Services...
echo.

REM Activate virtual environment and start Streamlit
echo Starting Streamlit UI...
start "Streamlit UI" cmd /k "cd /d %~dp0 && venv\Scripts\activate && streamlit run app.py"

REM Wait a moment for Streamlit to start
timeout /t 3 /nobreak >nul

REM Activate virtual environment and start FastAPI
echo Starting FastAPI API...
start "FastAPI API" cmd /k "cd /d %~dp0 && venv\Scripts\activate && uvicorn fastapi_app:app --reload --host 0.0.0.0 --port 8000"

echo.
echo Services are starting...
echo.
echo Streamlit UI: http://localhost:8501 (or 8502)
echo FastAPI: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to close this window...
pause >nul
