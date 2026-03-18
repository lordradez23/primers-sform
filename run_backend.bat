
@echo off
echo Starting PrimersGPT Backend...
cd backend
..\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
