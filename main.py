from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import os

# الاستيراد من ملفات المشروع الخفية
import database as db
import connection_tester as tester

app = FastAPI(title="Hotel PMS Dashboard")

# تحميل الواجهة والأصول الثابتة
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# تهيئة قاعدة البيانات عند بدء التطبيق
db.init_db()

# نماذج البيانات لـ Pydantic
class ConnectionRequest(BaseModel):
    platform_name: str
    username: str
    password: str
    ical_url: str

@app.get("/")
async def serve_dashboard(request: Request):
    """عرض صفحة لوحة التحكم الرئيسية."""
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/statuses")
async def get_all_statuses():
    """الحصول على جميع بيانات المنصات لعرضها في البطاقات."""
    data = db.load_all_statuses()
    return JSONResponse(status_code=200, content=data)

@app.post("/api/save_and_test")
async def test_and_save_connection(payload: ConnectionRequest):
    """اختبار الاتصال بالمنصة وحفظ النتيجة في قاعدة البيانات."""
    # فحص الاتصال باستخدام الوحدة السابقة
    result = tester.test_platform(
        payload.platform_name, 
        payload.username, 
        payload.password, 
        payload.ical_url
    )
    
    # حفظ الإعدادات في قاعدة البيانات الآمنة (Encrypted SQLite)
    db.save_credentials(
        payload.platform_name,
        payload.username,
        payload.password,
        payload.ical_url
    )
    
    # تحديث الحالة بناءً على النتيجة
    db.update_connection_status(payload.platform_name, result["success"])
    
    return JSONResponse(content={
        "success": result["success"],
        "message": result["message"]
    })

if __name__ == "__main__":
    # هذا يسمح للبرنامج بالعمل على الخوادم السحابية مثل Render 
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
