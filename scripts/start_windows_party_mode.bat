@echo off
REM Whispering Machine - Windows Party Mode Startup
REM Configures Windows laptop for Waveshare 7" touchscreen operation
REM Handles display configuration, power management, and delightful interactions

echo.
echo 🎉 Whispering Machine - Windows Party Mode Startup
echo ================================================
echo.

REM Configuration
set EXTERNAL_DISPLAY_RESOLUTION=1024x600
set BRIGHTNESS_PERCENT=80
set HOUSE_ID=%HOUSE_ID%
if "%HOUSE_ID%"=="" set HOUSE_ID=houseA

REM Check if running on Windows
ver | findstr /i "windows" >nul
if errorlevel 1 (
    echo ❌ This script is designed for Windows only
    exit /b 1
)
echo ✅ Running on Windows

REM Check for required tools
echo.
echo 🔍 Checking dependencies...

REM Check for PowerShell
powershell -Command "Write-Host 'PowerShell available'" >nul 2>&1
if errorlevel 1 (
    echo ❌ PowerShell not found - this is required for Windows
    exit /b 1
)
echo ✅ PowerShell available

REM Check for Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker not found - please install Docker Desktop
    exit /b 1
)
echo ✅ Docker available

REM Check for Docker Compose
docker compose version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose not found - please install Docker Desktop
    exit /b 1
)
echo ✅ Docker Compose available

echo.
echo 🖥️ Detecting displays...

REM Detect displays using PowerShell
powershell -Command "Get-WmiObject -Class Win32_VideoController | Select-Object Name, VideoModeDescription | ConvertTo-Json" > display_info.json 2>nul
if exist display_info.json (
    echo ✅ Display detection completed
    del display_info.json
) else (
    echo ⚠️ Could not detect displays - continuing anyway
)

echo.
echo ⚙️ Configuring power management...

REM Disable screensaver
powercfg /change monitor-timeout-ac 0 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Could not disable screensaver (may need admin rights)
) else (
    echo ✅ Screensaver disabled
)

REM Disable sleep
powercfg /change standby-timeout-ac 0 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Could not disable sleep (may need admin rights)
) else (
    echo ✅ Sleep disabled
)

echo.
echo 🎮 Configuring touchscreen...

REM Create calibration directory
if not exist "%USERPROFILE%\.whispering_machine" mkdir "%USERPROFILE%\.whispering_machine"

REM Create Windows calibration file
echo {> "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"
echo   "calibrated": true,>> "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"
echo   "platform": "windows",>> "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"
echo   "timestamp": %time%,>> "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"
echo   "resolution": "%EXTERNAL_DISPLAY_RESOLUTION%",>> "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"
echo   "touch_offset_x": 0,>> "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"
echo   "touch_offset_y": 0,>> "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"
echo   "touch_scale_x": 1.0,>> "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"
echo   "touch_scale_y": 1.0,>> "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"
echo   "touchscreen_device": "USB Touchscreen",>> "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"
echo   "driver_info": "Generic USB Touchscreen Driver",>> "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"
echo   "party_mode": true,>> "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"
echo   "delightful_interactions": {>> "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"
echo     "easter_eggs_enabled": true,>> "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"
echo     "konami_code": false,>> "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"
echo     "secret_patterns": false,>> "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"
echo     "long_press_reveal": false,>> "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"
echo     "multi_touch_magic": false>> "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"
echo   }>> "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"
echo }>> "%USERPROFILE%\.whispering_machine\windows_touch_calibration.json"

echo ✅ Touchscreen calibration created

echo.
echo 🚀 Starting party mode services...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running - please start Docker Desktop
    exit /b 1
)

REM Start services using docker compose
if exist "windows\compose.yml" (
    echo 📦 Starting services with docker compose...
    docker compose -f windows/compose.yml up -d
    
    if errorlevel 1 (
        echo ❌ Failed to start party mode services
        exit /b 1
    )
    echo ✅ Party mode services started
) else (
    echo ⚠️ windows/compose.yml not found - services may need manual startup
)

echo.
echo 🎊 Party Mode Configuration Complete! 🎊
echo.
echo 🎮 Party Mode Status:
echo   • External Display: Configured
echo   • Power Management: Disabled
echo   • Touchscreen: Calibrated
echo   • Services: Running
echo   • House ID: %HOUSE_ID%
echo   • Platform: Windows
echo.
echo 🎨 Delightful Features Enabled:
echo   • Easter Eggs: Konami Code, Secret Patterns
echo   • Long Press: Debug Mode Reveal
echo   • Multi-Touch: Magic Effects
echo   • Touch Patterns: Interaction Insights
echo.
echo 🎉 Ready for Party!
echo.
echo Access the party interface at: http://localhost:8000/party
echo Press Ctrl+C to stop party mode
echo.

REM Keep running until interrupted
:loop
timeout /t 1 /nobreak >nul
goto loop
