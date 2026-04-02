@echo off
chcp 65001 >nul
echo ==============================================
echo 🚀 جاري فحص التحديثات في الكود ومزامنتها مع السحابة...
echo ==============================================

set PATH=%PATH%;C:\Program Files\Git\cmd

git add .
git commit -m "Auto-update from local machine: %date% %time%"
git push origin main

echo.
echo ==============================================
echo ✅ تمت المزامنة بنجاح! سيتم تحديث موقع Streamlit خلال ثوانٍ.
echo ==============================================
pause
