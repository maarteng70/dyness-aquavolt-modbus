@echo off
cd /d "C:\dev\dyeness_av"
git tag -d v2026.11.6
echo Tag deleted locally
git push origin :refs/tags/v2026.11.6
echo Tag pushed (deleted) remotely