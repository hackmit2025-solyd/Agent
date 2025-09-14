@echo off
echo 🏥 Healthcare Agent Chat System
echo ================================
echo.

echo 🚀 Starting servers...
start "Flask Server" python app.py
start "Database Service" python mock_database_service.py

echo.
echo ⏳ Waiting for servers to start...
timeout /t 5 /nobreak > nul

echo.
echo 💬 Launching Patient Chat Interface...
python patient_chat.py

echo.
echo 👋 Chat session ended.
pause
