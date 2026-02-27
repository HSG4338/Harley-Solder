@echo off
title HARLEY SOLDER v1
cd /d "%~dp0"

echo.
echo  Starting Harley Solder v1...
echo  If this window closes immediately, check error.log
echo.

python main.py

if errorlevel 1 (
    echo.
    echo  !! HARLEY SOLDER CRASHED — see error.log for details
    echo.
    pause
)
