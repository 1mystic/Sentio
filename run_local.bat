@echo off
echo ============================================
echo   SENTIO LOCAL DEV RUNNER
echo ============================================
echo.
echo Starting FastAPI backend on :8000 ...
echo Starting Vue frontend on :5173 ...
echo.
echo Wait ~8s for backend ML model warmup, then open:
echo   http://localhost:5173
echo.
echo Close this window to stop both servers.
echo ============================================

:: Start backend in its own window (excludes .venv and __pycache__ from reload watcher)
start "Sentio Backend :8000" cmd /k "cd /d %~dp0sentio-api && .\.venv\Scripts\activate && uvicorn main:app --reload --port 8000 --reload-exclude .venv --reload-exclude __pycache__ --reload-exclude models"

:: Small pause to let backend start
timeout /t 2 /nobreak >nul

:: Start frontend in its own window
start "Sentio Frontend :5173" cmd /k "cd /d %~dp0 && npm run dev"

echo Both servers launched in separate windows.
pause
