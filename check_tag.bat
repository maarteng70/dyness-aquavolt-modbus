@echo off
cd /d "C:\dev\dyeness_av"
git tag -l v2026.11.6
if %ERRORLEVEL% equ 0 (
    echo Tag v2026.11.6 exists
) else (
    echo Tag v2026.11.6 does not exist
)