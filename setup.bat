@echo off
echo ========================================
echo  Image Colorization App - Setup Script
echo ========================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.7+ from python.org
    pause
    exit /b 1
)

echo.
echo Installing required packages...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies!
    echo Try running: python -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo To run the application, type:
echo   python pseudo_color_app_enhanced.py
echo.
echo (Or use: python pseudo_color_app.py for the original version)
echo.
pause


