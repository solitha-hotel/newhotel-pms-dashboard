"""
نظام إدارة الفندق - ربط منصات الحجز
Hotel PMS - Booking Platforms Integration Manager
"""

import streamlit as st
import time
from datetime import datetime
from database import init_db, save_credentials, load_credentials, update_connection_status, load_all_statuses
from connection_tester import test_platform

# ───────────────────────────────────────────────
# إعداد الصفحة
# ───────────────────────────────────────────────
st.set_page_config(
    page_title="نظام إدارة الفندق - منصات الحجز",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ───────────────────────────────────────────────
# CSS مخصص - تصميم احترافي RTL
# ───────────────────────────────────────────────
st.markdown("""
<style>
/* ======= Google Fonts ======= */
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;800&family=Tajawal:wght@300;400;500;700&display=swap');

/* ======= Global RTL & Font ======= */
* {
    direction: rtl !important;
    text-align: right !important;
    font-family: 'Cairo', 'Tajawal', 'Segoe UI', Arial, sans-serif !important;
}

html, body, [class*="css"] {
    background: linear-gradient(135deg, #0f0c29 0%, #1a1040 40%, #24243e 100%) !important;
    color: #e8e8f0 !important;
}

/* ======= Main Header ======= */
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f64f59 100%);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    text-align: center !important;
    box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
    animation: shimmer 4s infinite;
}
@keyframes shimmer {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
.main-header h1 {
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    color: white !important;
    margin: 0 !important;
    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    text-align: center !important;
}
.main-header p {
    color: rgba(255,255,255,0.85) !important;
    font-size: 1rem !important;
    margin: 0.5rem 0 0 0 !important;
    text-align: center !important;
}

/* ======= Platform Cards ======= */
.platform-card {
    background: linear-gradient(145deg, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0.03) 100%);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 1.8rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.platform-card::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 4px;
    height: 100%;
    border-radius: 0 20px 20px 0;
}
.platform-card.booking::after { background: linear-gradient(180deg, #003580, #0071c2); }
.platform-card.agoda::after { background: linear-gradient(180deg, #e5424d, #ff6b6b); }
.platform-card.almosafer::after { background: linear-gradient(180deg, #00a651, #00d166); }
.platform-card.gmail::after { background: linear-gradient(180deg, #ea4335, #fbbc04); }

.platform-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 45px rgba(0,0,0,0.4);
    border-color: rgba(255,255,255,0.2);
}

/* ======= Card Header ======= */
.card-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 1.2rem;
    flex-direction: row-reverse;
    justify-content: flex-end;
}
.platform-icon {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    flex-shrink: 0;
}
.icon-booking { background: linear-gradient(135deg, #003580, #0071c2); }
.icon-agoda   { background: linear-gradient(135deg, #e5424d, #ff6b6b); }
.icon-almosafer { background: linear-gradient(135deg, #00a651, #00d166); }
.icon-gmail   { background: linear-gradient(135deg, #ea4335, #fbbc04); }

.platform-title {
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    margin: 0 !important;
}
.platform-subtitle {
    font-size: 0.78rem !important;
    color: rgba(255,255,255,0.55) !important;
    margin: 0 !important;
}

/* ======= Status Badges ======= */
.status-connected {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: linear-gradient(135deg, rgba(0, 200, 100, 0.2), rgba(0, 200, 100, 0.1));
    border: 1px solid rgba(0, 200, 100, 0.4);
    color: #00e676 !important;
    padding: 0.4rem 1rem;
    border-radius: 50px;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    text-align: center !important;
    direction: rtl !important;
}
.status-disconnected {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: linear-gradient(135deg, rgba(255, 60, 60, 0.2), rgba(255, 60, 60, 0.1));
    border: 1px solid rgba(255, 60, 60, 0.4);
    color: #ff5252 !important;
    padding: 0.4rem 1rem;
    border-radius: 50px;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    text-align: center !important;
    direction: rtl !important;
}
.status-pending {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: linear-gradient(135deg, rgba(255, 180, 0, 0.2), rgba(255, 180, 0, 0.1));
    border: 1px solid rgba(255, 180, 0, 0.4);
    color: #ffd740 !important;
    padding: 0.4rem 1rem;
    border-radius: 50px;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    text-align: center !important;
    direction: rtl !important;
}

/* ======= Stats Row ======= */
.stats-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}
.stat-card {
    flex: 1;
    min-width: 140px;
    background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.2rem;
    text-align: center !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}
.stat-number {
    font-size: 2rem !important;
    font-weight: 800 !important;
    text-align: center !important;
    display: block;
    line-height: 1;
}
.stat-label {
    font-size: 0.78rem !important;
    color: rgba(255,255,255,0.6) !important;
    text-align: center !important;
    margin-top: 0.3rem !important;
    display: block;
}
.stat-connected .stat-number { color: #00e676 !important; }
.stat-disconnected .stat-number { color: #ff5252 !important; }
.stat-total .stat-number { color: #7c83fd !important; }
.stat-pending .stat-number { color: #ffd740 !important; }

/* ======= Divider ======= */
.section-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    margin: 1rem 0;
}

/* ======= Sidebar ======= */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1040 0%, #0f0c29 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
}
[data-testid="stSidebar"] * {
    color: #e8e8f0 !important;
}
.sidebar-brand {
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 16px;
    padding: 1.2rem;
    text-align: center !important;
    margin-bottom: 1.5rem;
}
.sidebar-brand h2 {
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    color: white !important;
    margin: 0 !important;
    text-align: center !important;
}
.sidebar-brand p {
    font-size: 0.75rem !important;
    color: rgba(255,255,255,0.7) !important;
    margin: 0.3rem 0 0 0 !important;
    text-align: center !important;
}
.sidebar-section {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
    border: 1px solid rgba(255,255,255,0.08);
}
.sidebar-section-title {
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    color: rgba(255,255,255,0.45) !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.8rem !important;
    text-align: right !important;
}

/* ======= Inputs ======= */
.stTextInput input, .stTextInput textarea {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    color: #e8e8f0 !important;
    direction: ltr !important;
    text-align: left !important;
}
.stTextInput input:focus {
    border-color: #7c83fd !important;
    box-shadow: 0 0 0 2px rgba(124, 131, 253, 0.2) !important;
}
.stTextInput label {
    color: rgba(255,255,255,0.8) !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
}

/* ======= Buttons ======= */
.stButton button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.5rem !important;
    font-family: 'Cairo', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    width: 100% !important;
}
.stButton button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5) !important;
}
.stButton button:active {
    transform: translateY(0) !important;
}

/* ======= Expander ======= */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
    margin-bottom: 0.8rem !important;
}
[data-testid="stExpander"] summary {
    color: #e8e8f0 !important;
    font-weight: 600 !important;
}

/* ======= Info / Warning / Success Alerts ======= */
.custom-alert {
    padding: 0.9rem 1.2rem;
    border-radius: 12px;
    font-size: 0.88rem !important;
    margin: 0.5rem 0;
    font-weight: 500 !important;
    direction: rtl !important;
    text-align: right !important;
}
.alert-info {
    background: rgba(124, 131, 253, 0.15);
    border: 1px solid rgba(124, 131, 253, 0.3);
    color: #a5b4fc !important;
}
.alert-warning {
    background: rgba(255, 215, 0, 0.1);
    border: 1px solid rgba(255, 215, 0, 0.3);
    color: #fde68a !important;
}
.alert-success {
    background: rgba(0, 230, 118, 0.1);
    border: 1px solid rgba(0, 230, 118, 0.3);
    color: #6ee7b7 !important;
}

/* ======= Tabs ======= */
[data-testid="stTabs"] button {
    color: rgba(255,255,255,0.6) !important;
    font-family: 'Cairo', sans-serif !important;
    font-weight: 600 !important;
    background: transparent !important;
    border: none !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #7c83fd !important;
    border-bottom: 2px solid #7c83fd !important;
}

/* ======= Spinner ======= */
.stSpinner > div {
    border-color: #7c83fd !important;
}

/* ======= Scrollbar ======= */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.05); }
::-webkit-scrollbar-thumb { background: rgba(124, 131, 253, 0.5); border-radius: 3px; }

/* ======= Last Tested ======= */
.last-tested {
    font-size: 0.72rem !important;
    color: rgba(255,255,255,0.4) !important;
    text-align: right !important;
    margin-top: 0.3rem !important;
}

/* ======= Footer ======= */
.footer {
    text-align: center !important;
    padding: 2rem 0 1rem;
    color: rgba(255,255,255,0.3) !important;
    font-size: 0.78rem !important;
}

/* ======= Hide Streamlit branding ======= */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ───────────────────────────────────────────────
# تهيئة قاعدة البيانات
# ───────────────────────────────────────────────
init_db()

# ───────────────────────────────────────────────
# إعداد بيانات المنصات
# ───────────────────────────────────────────────
PLATFORMS = [
    {
        "key": "Booking.com",
        "name": "Booking.com",
        "name_ar": "بوكينج",
        "desc": "منصة الحجز العالمية",
        "icon": "🔵",
        "emoji": "🌐",
        "css_class": "booking",
        "icon_class": "icon-booking",
        "color": "#0071c2",
        "favicon_url": "https://www.booking.com/favicon.ico",
        "has_ical": True,
        "username_label": "اسم المستخدم / Property ID",
        "password_label": "كلمة المرور / API Key",
        "ical_label": "رابط iCal للتقويم",
        "ical_placeholder": "https://ical.booking.com/v1/export?t=...",
    },
    {
        "key": "Agoda",
        "name": "Agoda",
        "name_ar": "أجودا",
        "desc": "منصة الحجز الآسيوية",
        "icon": "🔴",
        "emoji": "✈️",
        "css_class": "agoda",
        "icon_class": "icon-agoda",
        "color": "#e5424d",
        "favicon_url": "https://www.agoda.com/favicon.ico",
        "has_ical": True,
        "username_label": "Hotel ID / اسم المستخدم",
        "password_label": "API Key / كلمة المرور",
        "ical_label": "رابط iCal للتقويم",
        "ical_placeholder": "https://ical.agoda.com/...",
    },
    {
        "key": "Almosafer",
        "name": "Almosafer",
        "name_ar": "المسافر",
        "desc": "منصة الحجز السعودية",
        "icon": "🟢",
        "emoji": "🕌",
        "css_class": "almosafer",
        "icon_class": "icon-almosafer",
        "color": "#00a651",
        "favicon_url": "https://www.almosafer.com/favicon.ico",
        "has_ical": True,
        "username_label": "اسم المستخدم / Partner ID",
        "password_label": "كلمة المرور / API Secret",
        "ical_label": "رابط iCal للتقويم",
        "ical_placeholder": "https://www.almosafer.com/ical/...",
    },
    {
        "key": "Gmail",
        "name": "Gmail",
        "name_ar": "جيميل",
        "desc": "الإشعارات والبريد الإلكتروني",
        "icon": "📧",
        "emoji": "📩",
        "css_class": "gmail",
        "icon_class": "icon-gmail",
        "color": "#ea4335",
        "favicon_url": "https://www.google.com/favicon.ico",
        "has_ical": False,
        "username_label": "البريد الإلكتروني (Gmail)",
        "password_label": "كلمة مرور التطبيق (App Password)",
        "ical_label": None,
        "ical_placeholder": None,
    },
]

# ───────────────────────────────────────────────
# حالة الجلسة
# ───────────────────────────────────────────────
if "connection_results" not in st.session_state:
    st.session_state.connection_results = {}
if "testing" not in st.session_state:
    st.session_state.testing = False


def get_status_html(platform_key: str) -> str:
    """الحصول على HTML لمؤشر الحالة."""
    all_status = load_all_statuses()
    result = st.session_state.connection_results.get(platform_key)
    db_status = all_status.get(platform_key, {})

    if result is not None:
        connected, msg = result
        if connected:
            return f'<span class="status-connected">🟢 {msg}</span>'
        else:
            return f'<span class="status-disconnected">🔴 {msg}</span>'
    elif db_status:
        if db_status.get("is_connected"):
            last = db_status.get("last_tested", "")
            return f'<span class="status-connected">🟢 متصل</span>'
        elif db_status.get("last_tested"):
            return f'<span class="status-disconnected">🔴 غير متصل</span>'
    return '<span class="status-pending">⚪ لم يُختبر بعد</span>'


# ───────────────────────────────────────────────
# SIDEBAR
# ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h2>🏨 Hotel PMS</h2>
        <p>نظام إدارة منصات الحجز</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="sidebar-section-title">⚙️ إعدادات المنصات</p>', unsafe_allow_html=True)

    # تخزين مؤقت لبيانات الإدخال
    platform_inputs = {}

    for platform in PLATFORMS:
        key = platform["key"]
        creds = load_credentials(key)

        with st.expander(f"{platform['icon']} {platform['name_ar']} ({platform['name']})", expanded=False):
            username = st.text_input(
                platform["username_label"],
                value=creds["username"],
                key=f"user_{key}",
                placeholder=f"أدخل {platform['username_label']}",
            )
            password = st.text_input(
                platform["password_label"],
                value=creds["password"],
                key=f"pass_{key}",
                type="password",
                placeholder="••••••••",
            )
            if platform["has_ical"]:
                ical_url = st.text_input(
                    platform["ical_label"],
                    value=creds["ical_url"],
                    key=f"ical_{key}",
                    placeholder=platform["ical_placeholder"],
                )
            else:
                ical_url = ""
                st.markdown(
                    '<div class="custom-alert alert-info">💡 Gmail يستخدم App Password للمصادقة الآمنة</div>',
                    unsafe_allow_html=True
                )

            platform_inputs[key] = {
                "username": username,
                "password": password,
                "ical_url": ical_url,
            }

    st.markdown("<br>", unsafe_allow_html=True)

    # ── زر حفظ واختبار الاتصال ──
    save_test = st.button(
        "💾 حفظ واختبار الاتصال",
        key="save_test_btn",
        use_container_width=True,
    )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ── معلومات إضافية ──
    st.markdown("""
    <div class="sidebar-section">
        <p class="sidebar-section-title">🔒 الأمان</p>
        <div class="custom-alert alert-success">✅ كلمات المرور مشفرة بـ AES-256 Fernet</div>
        <div class="custom-alert alert-info" style="margin-top:0.5rem">💾 التخزين: SQLite محلي</div>
    </div>
    """, unsafe_allow_html=True)

    now = datetime.now().strftime("%Y/%m/%d %H:%M")
    st.markdown(f"""
    <div class="sidebar-section">
        <p class="sidebar-section-title">📅 معلومات النظام</p>
        <div style="font-size:0.78rem; color:rgba(255,255,255,0.5); text-align:right">
            <div>🕐 {now}</div>
            <div style="margin-top:0.3rem">🗄️ hotel_pms.db</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ───────────────────────────────────────────────
# معالجة الحفظ والاختبار
# ───────────────────────────────────────────────
if save_test:
    st.session_state.connection_results = {}
    results_temp = {}

    progress_placeholder = st.empty()
    progress_placeholder.markdown(
        '<div class="custom-alert alert-info">⏳ جاري حفظ البيانات واختبار الاتصال بجميع المنصات...</div>',
        unsafe_allow_html=True,
    )

    for i, platform in enumerate(PLATFORMS):
        key = platform["key"]
        data = platform_inputs[key]

        # حفظ البيانات
        save_credentials(key, data["username"], data["password"], data["ical_url"])

        # اختبار الاتصال
        if data["username"] or data["ical_url"]:
            connected, msg = test_platform(key, data["username"], data["password"], data["ical_url"])
        else:
            connected, msg = False, "لم يتم إدخال بيانات"

        results_temp[key] = (connected, msg)
        update_connection_status(key, connected)
        time.sleep(0.3)

    st.session_state.connection_results = results_temp
    progress_placeholder.empty()
    st.rerun()


# ───────────────────────────────────────────────
# MAIN CONTENT - Header
# ───────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🏨 مركز تحكم منصات الحجز</h1>
    <p>إدارة وربط جميع منصات الحجز من مكان واحد</p>
</div>
""", unsafe_allow_html=True)


# ───────────────────────────────────────────────
# STATS ROW
# ───────────────────────────────────────────────
all_status = load_all_statuses()
total = len(PLATFORMS)
connected_count = sum(1 for p in PLATFORMS if all_status.get(p["key"], {}).get("is_connected"))
disconnected_count = sum(1 for p in PLATFORMS if p["key"] in all_status and not all_status[p["key"]].get("is_connected"))
not_tested = total - len(all_status)

if st.session_state.connection_results:
    connected_count = sum(1 for v in st.session_state.connection_results.values() if v[0])
    disconnected_count = sum(1 for v in st.session_state.connection_results.values() if not v[0])

st.markdown(f"""
<div class="stats-row">
    <div class="stat-card stat-total">
        <span class="stat-number">4</span>
        <span class="stat-label">إجمالي المنصات</span>
    </div>
    <div class="stat-card stat-connected">
        <span class="stat-number">{connected_count}</span>
        <span class="stat-label">متصل</span>
    </div>
    <div class="stat-card stat-disconnected">
        <span class="stat-number">{disconnected_count}</span>
        <span class="stat-label">غير متصل</span>
    </div>
    <div class="stat-card stat-pending">
        <span class="stat-number">{total - connected_count - disconnected_count}</span>
        <span class="stat-label">لم يُختبر</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ───────────────────────────────────────────────
# بطاقات المنصات - دالة مساعدة لبناء HTML
# ───────────────────────────────────────────────
def build_card_html(platform: dict, status_html: str, last_tested: str) -> str:
    """بناء HTML للبطاقة بشكل نظيف."""
    border_colors = {
        "booking":   "linear-gradient(180deg,#003580,#0071c2)",
        "agoda":     "linear-gradient(180deg,#e5424d,#ff6b6b)",
        "almosafer": "linear-gradient(180deg,#00a651,#00d166)",
        "gmail":     "linear-gradient(180deg,#ea4335,#fbbc04)",
    }
    icon_bgs = {
        "booking":   "linear-gradient(135deg,#003580,#0071c2)",
        "agoda":     "linear-gradient(135deg,#e5424d,#ff6b6b)",
        "almosafer": "linear-gradient(135deg,#00a651,#00d166)",
        "gmail":     "linear-gradient(135deg,#ea4335,#fbbc04)",
    }
    cls = platform["css_class"]
    border_grad = border_colors.get(cls, "#555")
    icon_bg     = icon_bgs.get(cls, "#444")
    name_ar     = platform["name_ar"]
    name_en     = platform["name"]
    desc        = platform["desc"]
    icon        = platform["icon"]
    emoji       = platform["emoji"]

    last_html = ""
    if last_tested:
        last_html = (
            "<div style='font-size:0.7rem;color:rgba(255,255,255,0.35);"
            "margin-top:0.4rem;direction:rtl;'>🕐 آخر اختبار: " + last_tested + "</div>"
        )

    html = (
        "<div style='"
        "background:linear-gradient(145deg,rgba(255,255,255,0.07),rgba(255,255,255,0.03));"
        "border:1px solid rgba(255,255,255,0.12);border-radius:20px;"
        "padding:1.6rem;margin-bottom:1.5rem;"
        "box-shadow:0 8px 32px rgba(0,0,0,0.3);position:relative;overflow:hidden;'>"

        # شريط اللون الجانبي
        "<div style='position:absolute;top:0;right:0;width:5px;height:100%;"
        "background:" + border_grad + ";border-radius:0 20px 20px 0;'></div>"

        # رأس البطاقة - نستخدم table layout لتجنب مشاكل flex+RTL
        "<table style='width:100%;border-collapse:collapse;margin-bottom:0.9rem;'><tr>"
        "<td style='vertical-align:middle;padding:0;text-align:right;width:100%;'>"
        "<div style='font-size:1.08rem;font-weight:800;color:#ffffff;"
        "font-family:Cairo,Tajawal,sans-serif;line-height:1.3;'>"
        + emoji + "&nbsp;" + name_ar +
        "</div>"
        "<div style='font-size:0.74rem;color:rgba(255,255,255,0.48);"
        "font-family:Cairo,Tajawal,sans-serif;margin-top:3px;'>"
        + name_en + " &mdash; " + desc +
        "</div>"
        "</td>"
        "<td style='vertical-align:middle;padding:0;padding-right:10px;'>"
        "<div style='width:46px;height:46px;border-radius:13px;"
        "background:" + icon_bg + ";"
        "display:flex;align-items:center;justify-content:center;"
        "font-size:1.4rem;flex-shrink:0;'>" + icon + "</div>"
        "</td>"
        "</tr></table>"

        # خط فاصل
        "<div style='height:1px;background:linear-gradient("
        "90deg,transparent,rgba(255,255,255,0.18),transparent);margin:0 0 0.85rem;'></div>"

        # مؤشر الحالة
        "<div style='text-align:right;'>"
        + status_html
        + last_html
        + "</div></div>"
    )
    return html


st.markdown("### 🔗 حالة الاتصال بالمنصات")

# رسم البطاقات في صفين
for row_start in range(0, len(PLATFORMS), 2):
    row_platforms = PLATFORMS[row_start:row_start+2]
    cols = st.columns(len(row_platforms), gap="large")
    for col_idx, platform in enumerate(row_platforms):
        key = platform["key"]
        all_status_data = load_all_statuses()
        db_info = all_status_data.get(key, {})
        status_html = get_status_html(key)
        last_tested = db_info.get("last_tested", "")

        with cols[col_idx]:
            card_html = build_card_html(platform, status_html, last_tested)
            st.markdown(card_html, unsafe_allow_html=True)


# ───────────────────────────────────────────────
# قسم التعليمات
# ───────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 📋 دليل الإعداد السريع")

with st.expander("🔵 كيفية إعداد Booking.com", expanded=False):
    st.markdown("""
    **خطوات الربط مع Booking.com:**
    
    1. **تسجيل الدخول** إلى [Extranet Booking.com](https://account.booking.com)
    2. انتقل إلى **Property Settings → Channel Manager**
    3. احصل على **Property ID** من الإعدادات
    4. لرابط iCal: اذهب إلى **Calendar → Export Calendar → Copy iCal Link**
    5. أدخل البيانات في الـ Sidebar وانقر **حفظ واختبار الاتصال**
    """)

with st.expander("🔴 كيفية إعداد Agoda", expanded=False):
    st.markdown("""
    **خطوات الربط مع Agoda:**
    
    1. **تسجيل الدخول** إلى [Agoda YCS](https://ycs.agoda.com)
    2. انتقل إلى **Settings → API Integration**
    3. احصل على **Hotel ID و API Key**
    4. لرابط iCal: من **Calendar → iCal Export**
    5. أدخل البيانات وانقر **حفظ واختبار الاتصال**
    """)

with st.expander("🟢 كيفية إعداد Almosafer", expanded=False):
    st.markdown("""
    **خطوات الربط مع المسافر (Almosafer):**
    
    1. تواصل مع فريق الشركاء على [almosafer.com](https://www.almosafer.com)
    2. احصل على **Partner ID** و **API Secret**
    3. اطلب رابط **iCal الخاص** بالعقار
    4. أدخل البيانات وانقر **حفظ واختبار الاتصال**
    """)

with st.expander("📧 كيفية إعداد Gmail (App Password)", expanded=False):
    st.markdown("""
    **خطوات تفعيل App Password في Gmail:**
    
    1. اذهب إلى [myaccount.google.com](https://myaccount.google.com)
    2. انتقل إلى **Security → 2-Step Verification** (يجب تفعيله أولاً)
    3. ارجع إلى **Security → App passwords**
    4. اختر **Mail** كتطبيق و **Other** كجهاز، ثم انقر **Generate**
    5. انسخ كلمة المرور المكونة من **16 حرفاً**
    6. أدخل Gmail الخاص بك وكلمة المرور المولّدة
    
    > ⚠️ **مهم:** لا تستخدم كلمة مرور Gmail العادية — استخدم App Password فقط
    """)


# ───────────────────────────────────────────────
# Footer
# ───────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
    🏨 Hotel PMS — نظام إدارة منصات الحجز &nbsp;|&nbsp; 
    🔒 مشفر ومحمي &nbsp;|&nbsp;
    📅 {datetime.now().strftime("%Y")}
</div>
""", unsafe_allow_html=True)
