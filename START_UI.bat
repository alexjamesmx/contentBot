@echo off
echo ================================
echo ContentBot Pro UI - Starting...
echo ================================
echo.

REM Check if running in correct directory
if not exist "app.py" (
    echo ERROR: app.py not found!
    echo Please run this script from the ContentBot root directory.
    pause
    exit /b 1
)

echo [1/2] Starting Flask Backend...
echo.
start "ContentBot Backend" cmd /k "python app.py"

echo [2/2] Starting React Frontend...
echo.
echo Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak >nul

cd contentbot-ui
start "ContentBot Frontend" cmd /k "npm run dev"

echo.
echo ================================
echo ContentBot Pro UI Started!
echo ================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo Open http://localhost:5173 in your browser
echo.
echo Press any key to close this window (servers will keep running)
pause >nul
