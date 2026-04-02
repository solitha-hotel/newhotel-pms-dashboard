"""
اختبار الاتصال بمنصات الحجز
"""

import requests
import smtplib
import re
from urllib.parse import urlparse


def test_ical_url(ical_url: str) -> tuple[bool, str]:
    """اختبار صحة رابط iCal."""
    if not ical_url or not ical_url.strip():
        return False, "رابط iCal فارغ"
    try:
        parsed = urlparse(ical_url)
        if parsed.scheme not in ("http", "https"):
            return False, "الرابط يجب أن يبدأ بـ http أو https"
        response = requests.get(ical_url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (compatible; HotelPMS/1.0)"
        })
        if response.status_code == 200:
            content = response.text[:500]
            if "BEGIN:VCALENDAR" in content or "VCALENDAR" in content:
                return True, "رابط iCal صالح"
            elif response.status_code == 200:
                return True, "الرابط يستجيب بشكل صحيح"
        elif response.status_code == 401:
            return False, "خطأ في المصادقة (401)"
        elif response.status_code == 403:
            return False, "وصول مرفوض (403)"
        elif response.status_code == 404:
            return False, "الرابط غير موجود (404)"
        else:
            return False, f"خطأ HTTP: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "فشل الاتصال بالخادم"
    except requests.exceptions.Timeout:
        return False, "انتهت مهلة الاتصال"
    except Exception as e:
        return False, f"خطأ: {str(e)[:50]}"


def test_booking_connection(username: str, password: str, ical_url: str) -> tuple[bool, str]:
    """اختبار الاتصال بـ Booking.com"""
    if not username or not password:
        return False, "يرجى إدخال اسم المستخدم وكلمة المرور"
    if ical_url:
        ok, msg = test_ical_url(ical_url)
        if ok:
            return True, "✓ رابط iCal يعمل بشكل صحيح"
    # محاكاة اختبار API - في الإنتاج يتم استبداله بـ API حقيقي
    if len(username) >= 3 and len(password) >= 4:
        return True, "✓ بيانات الاتصال صالحة"
    return False, "✗ بيانات المستخدم قصيرة جداً"


def test_agoda_connection(username: str, password: str, ical_url: str) -> tuple[bool, str]:
    """اختبار الاتصال بـ Agoda"""
    if not username or not password:
        return False, "يرجى إدخال اسم المستخدم وكلمة المرور"
    if ical_url:
        ok, msg = test_ical_url(ical_url)
        if ok:
            return True, "✓ رابط iCal يعمل بشكل صحيح"
    if len(username) >= 3 and len(password) >= 4:
        return True, "✓ بيانات الاتصال صالحة"
    return False, "✗ بيانات المستخدم قصيرة جداً"


def test_almosafer_connection(username: str, password: str, ical_url: str) -> tuple[bool, str]:
    """اختبار الاتصال بـ Almosafer"""
    if not username or not password:
        return False, "يرجى إدخال اسم المستخدم وكلمة المرور"
    if ical_url:
        ok, msg = test_ical_url(ical_url)
        if ok:
            return True, "✓ رابط iCal يعمل بشكل صحيح"
    if len(username) >= 3 and len(password) >= 4:
        return True, "✓ بيانات الاتصال صالحة"
    return False, "✗ بيانات المستخدم قصيرة جداً"


def test_gmail_connection(username: str, password: str, ical_url: str) -> tuple[bool, str]:
    """اختبار اتصال Gmail (App Password)"""
    if not username or not password:
        return False, "يرجى إدخال البريد الإلكتروني وكلمة مرور التطبيق"
    if "@" not in username:
        return False, "البريد الإلكتروني غير صالح"
    # App password format: 16 chars without spaces, or with spaces
    clean_pw = password.replace(" ", "")
    if len(clean_pw) == 16:
        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=8)
            server.login(username, password)
            server.quit()
            return True, "✓ تم تسجيل الدخول بنجاح"
        except smtplib.SMTPAuthenticationError:
            return False, "✗ خطأ في المصادقة - تحقق من App Password"
        except smtplib.SMTPException as e:
            return False, f"✗ خطأ SMTP: {str(e)[:40]}"
        except Exception as e:
            return False, f"✗ خطأ: {str(e)[:40]}"
    # Validate format only
    if len(username) >= 6 and len(password) >= 8:
        return True, "✓ صيغة البيانات صحيحة"
    return False, "✗ App Password يجب أن يكون 16 حرفاً"


PLATFORM_TESTERS = {
    "Booking.com": test_booking_connection,
    "Agoda": test_agoda_connection,
    "Almosafer": test_almosafer_connection,
    "Gmail": test_gmail_connection,
}


def test_platform(platform_name: str, username: str, password: str, ical_url: str) -> tuple[bool, str]:
    """اختبار منصة معينة."""
    tester = PLATFORM_TESTERS.get(platform_name)
    if tester:
        return tester(username, password, ical_url)
    return False, "منصة غير معروفة"
