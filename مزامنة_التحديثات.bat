@echo off
echo ==============================================
echo [Hotel PMS] Auto Sync to Github/Render...
echo ==============================================

set PATH=%PATH%;C:\Program Files\Git\cmd

git add .
git commit -m "Auto-update from local machine: %date% %time%"
git push origin main

echo.
echo ==============================================
echo SUCCESS! Your changes have been pushed.
echo The website will update in a few seconds.
echo ==============================================
pause
