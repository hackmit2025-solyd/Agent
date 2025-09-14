@echo off
echo 🏥 Starting Healthcare Agent System...
echo.

echo 🚀 Starting Flask Server...
start "Flask Server" python app.py

echo 🗄️ Starting Database Service...
start "Database Service" python mock_database_service.py

echo.
echo ✅ Servers starting...
echo 📡 Flask API: http://localhost:8080
echo 🗄️ Database: http://localhost:3000
echo.
echo 🌐 Opening Frontend Demo...
start frontend_demo.html

echo.
echo 🎉 System Ready!
echo Press any key to run tests...
pause > nul

echo.
echo 🧪 Running Tests...
python COMPLETE_DEMO.py

echo.
echo ✅ All done! Check the browser for the frontend demo.
pause
