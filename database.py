"""
قاعدة البيانات - تخزين آمن لبيانات الاعتماد باستخدام SQLite والتشفير
"""

import sqlite3
import os
import base64
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

load_dotenv()

DB_PATH = "hotel_pms.db"
KEY_FILE = ".secret.key"


def _get_or_create_key() -> bytes:
    """الحصول على مفتاح التشفير أو إنشاء مفتاح جديد."""
    # البحث في متغيرات البيئة (للنشر على Render)
    env_key = os.getenv("ENCRYPTION_KEY")
    if env_key:
        return env_key.encode()
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        return key


def _get_cipher() -> Fernet:
    """الحصول على كائن التشفير."""
    key = _get_or_create_key()
    return Fernet(key)


def encrypt_password(password: str) -> str:
    """تشفير كلمة المرور."""
    if not password:
        return ""
    cipher = _get_cipher()
    return cipher.encrypt(password.encode()).decode()


def decrypt_password(encrypted: str) -> str:
    """فك تشفير كلمة المرور."""
    if not encrypted:
        return ""
    try:
        cipher = _get_cipher()
        return cipher.decrypt(encrypted.encode()).decode()
    except Exception:
        return ""


def init_db():
    """تهيئة قاعدة البيانات وإنشاء الجداول."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS platform_credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform_name TEXT UNIQUE NOT NULL,
            username TEXT,
            password_encrypted TEXT,
            ical_url TEXT,
            is_connected INTEGER DEFAULT 0,
            last_tested TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_credentials(platform_name: str, username: str, password: str, ical_url: str):
    """حفظ بيانات الاعتماد بشكل آمن."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    encrypted_pw = encrypt_password(password)
    cursor.execute("""
        INSERT INTO platform_credentials (platform_name, username, password_encrypted, ical_url, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(platform_name) DO UPDATE SET
            username = excluded.username,
            password_encrypted = excluded.password_encrypted,
            ical_url = excluded.ical_url,
            updated_at = CURRENT_TIMESTAMP
    """, (platform_name, username, encrypted_pw, ical_url))
    conn.commit()
    conn.close()


def load_credentials(platform_name: str) -> dict:
    """تحميل بيانات الاعتماد."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, password_encrypted, ical_url, is_connected, last_tested FROM platform_credentials WHERE platform_name = ?",
        (platform_name,)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "username": row[0] or "",
            "password": decrypt_password(row[1]) if row[1] else "",
            "ical_url": row[2] or "",
            "is_connected": bool(row[3]),
            "last_tested": row[4] or "",
        }
    return {"username": "", "password": "", "ical_url": "", "is_connected": False, "last_tested": ""}


def update_connection_status(platform_name: str, is_connected: bool):
    """تحديث حالة الاتصال."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE platform_credentials
        SET is_connected = ?, last_tested = CURRENT_TIMESTAMP
        WHERE platform_name = ?
    """, (1 if is_connected else 0, platform_name))
    conn.commit()
    conn.close()


def load_all_statuses() -> dict:
    """تحميل حالة الاتصال لجميع المنصات."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT platform_name, is_connected, last_tested FROM platform_credentials")
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: {"is_connected": bool(row[1]), "last_tested": row[2] or ""} for row in rows}
