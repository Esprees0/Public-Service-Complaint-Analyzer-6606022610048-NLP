import streamlit as st
import re
import pandas as pd
from pythainlp.tokenize import word_tokenize


PHONE_PATTERN = r'(?<!\d)0\d{2}[- ]?\d{3}[- ]?\d{4}(?!\d)'

# =========================
# Page Configuration
# =========================

st.set_page_config(
    page_title="ระบบวิเคราะห์ข้อความร้องเรียน",
    page_icon="📢",
    layout="wide"
)

# =========================
# Theme / Styling
# =========================
# ใช้ "TH Sarabun" ซึ่งเป็นแบบอักษรราชการไทยตามมติคณะรัฐมนตรี
# เป็นฟอนต์หลัก ให้บรรยากาศน่าเชื่อถือแบบหน่วยงานภาครัฐ
# และ "Prompt" สำหรับหัวข้อ/ตัวเลขเด่น

# =========================
# Theme / Styling (FIXED)
# =========================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&family=Prompt:wght@500;600;700&display=swap');

    :root {
        --navy: #0F2A4A;
        --navy-light: #1B4B7A;
        --teal: #0E7C7B;
        --paper: #F6F4EF;
        --ink: #1F2A33;
        --high: #C0392B;
        --medium: #B7791F;
        --low: #1E8449;
    }

    /* 1. บังคับตั้งค่าฟอนต์และสีข้อความพื้นฐานทั้งหมด */
    html, body, [class*="css"], .stMarkdown, p, div, label, span {
        font-family: 'Sarabun', sans-serif;
        color: var(--ink) !important;
    }

    .stApp {
        background-color: var(--paper) !important;
    }

    h1, h2, h3, h4, h5, h6, .hero-title {
        font-family: 'Prompt', sans-serif !important;
        color: var(--navy) !important;
    }

    /* ซ่อนหัวเรื่องมาตรฐานของ Streamlit */
    div[data-testid="stAppViewContainer"] .block-container {
        padding-top: 1.5rem;
    }

    /* 2. ปรับแต่ง Hero Banner */
    .hero-band {
        background: linear-gradient(120deg, var(--navy) 0%, var(--navy-light) 100%);
        border-radius: 14px;
        padding: 2rem 2.2rem;
        margin-bottom: 1.6rem;
        box-shadow: 0 6px 20px rgba(15, 42, 74, 0.18);
    }

    .hero-eyebrow {
        color: #9FD8D6 !important;
        font-family: 'Prompt', sans-serif;
        font-size: 0.8rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }

    .hero-title {
        color: #FFFFFF !important;
        font-size: 2rem;
        font-weight: 700;
        margin: 0 0 0.6rem 0;
        line-height: 1.25;
    }

    .hero-desc {
        color: #DCE7F0 !important;
        font-size: 1rem;
        line-height: 1.6;
        max-width: 720px;
        margin: 0;
    }

    /* 3. ปรับแต่ง Section Card & Text Area ให้เห็นตัวอักษรชัดเจน */
    .section-card {
        background: #FFFFFF;
        border: 1px solid #E4DFD3;
        border-radius: 12px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 8px rgba(15, 42, 74, 0.04);
    }

    .section-label {
        font-family: 'Prompt', sans-serif;
        font-weight: 600;
        font-size: 1.05rem;
        color: var(--navy) !important;
        margin-bottom: 0.8rem;
    }

    /* แก้ไขช่องกรอกข้อความ (st.text_area) */
    .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: var(--ink) !important;
        border: 1px solid #CCCCCC !important;
        border-radius: 8px;
    }

    .stTextArea textarea:focus {
        border-color: var(--teal) !important;
    }

    /* 4. ปรับแต่ง Metric Cards */
    .metric-card {
        border-radius: 12px;
        padding: 1.1rem 1.2rem;
        border-left: 5px solid var(--teal);
        background: #FFFFFF;
        box-shadow: 0 2px 8px rgba(15, 42, 74, 0.05);
        height: 100%;
    }

    .metric-card .label {
        font-size: 0.8rem;
        color: #6B7684 !important;
        letter-spacing: 0.03em;
    }

    .metric-card .value {
        font-family: 'Prompt', sans-serif;
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--navy) !important;
        margin-top: 0.15rem;
    }

    .metric-card.urgency-high { border-left-color: var(--high); }
    .metric-card.urgency-high .value { color: var(--high) !important; }
    .metric-card.urgency-medium { border-left-color: var(--medium); }
    .metric-card.urgency-medium .value { color: var(--medium) !important; }
    .metric-card.urgency-low { border-left-color: var(--low); }
    .metric-card.urgency-low .value { color: var(--low) !important; }

    /* 5. ปรับแต่ง Chips */
    .chip {
        display: inline-block;
        font-family: 'Sarabun', sans-serif;
        font-size: 0.88rem;
        background: #EAF3F1;
        color: var(--navy) !important;
        border: 1px solid #D3E4E1;
        border-radius: 999px;
        padding: 0.25rem 0.7rem;
        margin: 0.15rem 0.25rem 0.15rem 0;
    }

    .keyword-chip {
        background: #FBEAE8;
        color: var(--high) !important;
        border: 1px solid #F1CFC9;
    }

    /* 6. ปรับแต่ง Table ของ Streamlit ให้พื้นหลังขาว ตัวอักษรเข้ม */
    [data-testid="stTable"] table {
        background-color: #FFFFFF !important;
        color: var(--ink) !important;
        border-radius: 8px;
    }
    
    [data-testid="stTable"] th, [data-testid="stTable"] td {
        color: var(--ink) !important;
        border-color: #E4DFD3 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="hero-band">
        <div class="hero-eyebrow">ระบบสำหรับหน่วยงานบริการสาธารณะ</div>
        <div class="hero-title">📢 ระบบวิเคราะห์ข้อความร้องเรียนบริการสาธารณะ</div>
        <p class="hero-desc">
            วิเคราะห์ข้อความร้องเรียนภาษาไทยด้วยเทคนิค NLP
            เพื่อจำแนกประเภทปัญหา สกัดสถานที่ วิเคราะห์ความเร่งด่วน
            และลบข้อมูลส่วนบุคคลก่อนนำไปใช้งานต่อ
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# Functions
# =========================

def clean_text(text):
    """ลบข้อมูลส่วนบุคคล เช่น เบอร์โทร Email และ URL"""

    # ลบ Markdown link เช่น [email](mailto:email@example.com)
    text = re.sub(
        r'\[([^\]]+)\]\(mailto:[^)]+\)',
        '[EMAIL]',
        text
    )

    # ลบ Email ปกติ
    text = re.sub(
        r'[\w\.-]+@[\w\.-]+\.\w+',
        '[EMAIL]',
        text
    )

    # ลบ URL
    text = re.sub(
        r'https?://\S+|www\.\S+',
        '[URL]',
        text
    )

    # ลบเบอร์โทรทั้งแบบ 0812345678
    # และ 081-234-5678
    text = re.sub(
        PHONE_PATTERN,
        '[PHONE]',
        text
    )

    return text


def tokenize_text(text):
    """ตัดคำภาษาไทย"""

    tokens = word_tokenize(
        text,
        engine="newmm"
    )

    return [
        token for token in tokens
        if token.strip()
    ]


def identify_topic(text):
    """จำแนกประเภทปัญหา"""

    topics = {
        "ไฟฟ้าสาธารณะ": [
            "ไฟ",
            "ไฟฟ้า",
            "ไฟถนน",
            "เสาไฟ",
            "หลอดไฟ"
        ],

        "ถนนและการจราจร": [
            "ถนน",
            "หลุม",
            "บ่อ",
            "จราจร",
            "รถติด",
            "สัญญาณไฟ",
            "ทางเท้า"
        ],

        "น้ำประปา": [
            "น้ำ",
            "น้ำประปา",
            "ประปา",
            "ท่อแตก",
            "น้ำไม่ไหล",
            "น้ำขุ่น"
        ],

        "ขยะและสิ่งแวดล้อม": [
            "ขยะ",
            "ถังขยะ",
            "เหม็น",
            "มลพิษ",
            "น้ำเสีย",
            "สกปรก"
        ],

        "ความปลอดภัย": [
            "อันตราย",
            "อาชญากรรม",
            "ขโมย",
            "โจร",
            "ทะเลาะ",
            "ความปลอดภัย"
        ]
    }

    scores = {}

    for topic, keywords in topics.items():

        score = 0

        for keyword in keywords:

            if keyword in text:
                score += 1

        scores[topic] = score

    best_topic = max(
        scores,
        key=scores.get
    )

    if scores[best_topic] == 0:
        return "อื่น ๆ"

    return best_topic


def detect_urgency(text):
    """วิเคราะห์ระดับความเร่งด่วน"""

    high_keywords = [
        "ไฟดูด",
        "ไฟช็อต",
        "ไฟฟ้าช็อต",
        "สายไฟขาด",
        "สายไฟตก",
        "สายไฟต่ำ",
        "สายไฟทอดต่ำ",
        "สายไฟห้อย",
        "ไฟไหม้",
        "อุบัติเหตุ",
        "ผู้บาดเจ็บ",
        "คนเจ็บ",
        "เสี่ยงชีวิต",
        "อันตราย",
        "ฉุกเฉิน",
        "กลัวโดนไฟดูด",
        "กลัวไฟดูด"
    ]

    medium_keywords = [
        "หลายวัน",
        "หลายเดือน",
        "นานแล้ว",
        "เดือดร้อน",
        "รบกวน",
        "เสีย",
        "ชำรุด",
        "ไม่ทำงาน",
        "ไม่ไหล",
        "ขัดข้อง"
    ]

    # ตรวจระดับสูงก่อน
    found_high = [
        keyword
        for keyword in high_keywords
        if keyword in text
    ]

    if found_high:
        return "🔴 สูง", found_high

    # ตรวจระดับปานกลาง
    found_medium = [
        keyword
        for keyword in medium_keywords
        if keyword in text
    ]

    if found_medium:
        return "🟡 ปานกลาง", found_medium

    return "🟢 ต่ำ", []


def extract_phone(text):
    """ค้นหาเบอร์โทรศัพท์ทั้งแบบมีขีดและไม่มีขีด"""

    phones = re.findall(
        PHONE_PATTERN,
        text
    )

    return phones


def extract_location(text):
    """
    สกัดสถานที่จากข้อความร้องเรียนภาษาไทย
    ใช้ Rule-based Information Extraction
    """

    # --------------------------------
    # รูปแบบสถานที่ที่พบบ่อย
    # --------------------------------

    patterns = [

        # หน้าปากซอย / หลังปากซอย
        r'(หน้าปากซอย|หลังปากซอย|บริเวณปากซอย|ตรงปากซอย)',

        # ซอย + ชื่อ + เลข
        # เช่น ซอยสุขุมวิท 21
        # เช่น ซอยลาดพร้าว 101
        r'(ซอย[ก-๙A-Za-z]+(?:\s*\d+)?(?:/\d+)?)',

        # ถนน + ชื่อ + เลข
        # เช่น ถนนสุขุมวิท
        # เช่น ถนนพหลโยธิน 24
        r'(ถนน[ก-๙A-Za-z]+(?:\s*\d+)?(?:/\d+)?)',

        # สถานที่ทั่วไป
        r'(มหาวิทยาลัย[ก-๙A-Za-z0-9]*)',
        r'(โรงเรียน[ก-๙A-Za-z0-9]*)',
        r'(ตลาด[ก-๙A-Za-z0-9]*)',
        r'(โรงพยาบาล[ก-๙A-Za-z0-9]*)',
        r'(สถานีรถไฟ[ก-๙A-Za-z0-9]*)',
        r'(สถานีตำรวจ[ก-๙A-Za-z0-9]*)',
        r'(สถานีขนส่ง[ก-๙A-Za-z0-9]*)',
        r'(สวนสาธารณะ[ก-๙A-Za-z0-9]*)',
        r'(ชุมชน[ก-๙A-Za-z0-9]*)',
        r'(หมู่บ้าน[ก-๙A-Za-z0-9]*)',

        # ร้าน / ห้าง
        r'(ร้านสะดวกซื้อ[ก-๙A-Za-z0-9]*)',
        r'(ห้าง[ก-๙A-Za-z0-9]*)',
    ]

    candidates = []

    # --------------------------------
    # ค้นหา Location Candidate
    # --------------------------------

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        for match in matches:

            if isinstance(match, tuple):
                location = match[0]
            else:
                location = match

            location = location.strip()

            if location:
                candidates.append(location)

    # --------------------------------
    # รูปแบบ Prefix + Location
    # เช่น
    # หน้ามหาวิทยาลัย
    # หน้าตลาด
    # ใกล้โรงพยาบาล
    # แถวตลาด
    # --------------------------------

    prefix_patterns = [

        r'(หน้ามหาวิทยาลัย)',
        r'(หน้าตลาด)',
        r'(หน้าโรงเรียน)',
        r'(หน้าโรงพยาบาล)',
        r'(หน้าสถานีรถไฟ)',
        r'(หน้าสถานีตำรวจ)',
        r'(หน้าร้านสะดวกซื้อ)',

        r'(ใกล้มหาวิทยาลัย)',
        r'(ใกล้ตลาด)',
        r'(ใกล้โรงเรียน)',
        r'(ใกล้โรงพยาบาล)',

        r'(แถวม หาวิทยาลัย)',
        r'(แถวมหาวิทยาลัย)',
        r'(แถวตลาด)',
        r'(แถวโรงเรียน)',
        r'(แถวโรงพยาบาล)',
    ]

    for pattern in prefix_patterns:

        matches = re.findall(
            pattern,
            text
        )

        candidates.extend(matches)

    # --------------------------------
    # ทำความสะอาด
    # --------------------------------

    cleaned = []

    for location in candidates:

        location = location.strip(
            " ,.!?;:，。！？"
        )

        if location and location not in cleaned:

            cleaned.append(location)

    # --------------------------------
    # ไม่มีสถานที่
    # --------------------------------

    if not cleaned:

        return "ไม่พบสถานที่"

    # --------------------------------
    # ให้คะแนน Candidate
    # --------------------------------

    def score(location):

        score = 0

        # รูปแบบที่มีความชัดเจน
        if "ซอย" in location:
            score += 10

        if "ถนน" in location:
            score += 10

        if "ปากซอย" in location:
            score += 12

        if "ตลาด" in location:
            score += 8

        if "มหาวิทยาลัย" in location:
            score += 8

        if "โรงเรียน" in location:
            score += 8

        if "โรงพยาบาล" in location:
            score += 8

        # มีเลขสถานที่
        if re.search(r'\d+', location):
            score += 5

        # Prefix
        if location.startswith(
            ("หน้า", "หลัง", "ใกล้", "แถว", "บริเวณ")
        ):
            score += 3

        return score

    # เรียงจากคะแนนมากไปน้อย
    cleaned.sort(
        key=score,
        reverse=True
    )

    return cleaned[0]


# =========================
# Input
# =========================

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-label">📝 กรุณากรอกข้อความร้องเรียน</div>', unsafe_allow_html=True)

default_text = (
    "ไฟถนนหน้ามหาวิทยาลัยเสียมาหลายวันแล้ว "
    "ตอนกลางคืนมืดมาก อันตรายสำหรับนักศึกษา "
    "สามารถติดต่อได้ที่ 0812345678"
)

text = st.text_area(
    "ข้อความร้องเรียน",
    value=default_text,
    height=150,
    label_visibility="collapsed"
)


analyze = st.button(
    "🔍 วิเคราะห์ข้อความ",
    type="primary"
)
st.markdown('</div>', unsafe_allow_html=True)


# =========================
# Analysis
# =========================

if analyze:

    if not text.strip():

        st.warning("กรุณากรอกข้อความก่อนวิเคราะห์")

    else:

        # Cleansing
        cleaned = clean_text(text)

        # Tokenization
        tokens = tokenize_text(text)

        # Topic
        topic = identify_topic(text)

        # Urgency
        urgency, urgency_keywords = detect_urgency(text)

        # Location
        location = extract_location(text)

        # Phone
        phones = extract_phone(text)


        # กำหนดคลาสสีของการ์ดตามระดับความเร่งด่วน
        if "สูง" in urgency:
            urgency_class = "urgency-high"
        elif "ปานกลาง" in urgency:
            urgency_class = "urgency-medium"
        else:
            urgency_class = "urgency-low"

        st.markdown('<div class="section-label" style="margin-top:0.4rem;">📊 ผลการวิเคราะห์</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="label">ประเภทปัญหา</div>
                    <div class="value">{topic}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div class="metric-card {urgency_class}">
                    <div class="label">ความเร่งด่วน</div>
                    <div class="value">{urgency}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="label">สถานที่</div>
                    <div class="value">{location}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.write("")


        # =========================
        # Extracted Information
        # =========================

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">🔎 ข้อมูลที่สกัดได้</div>', unsafe_allow_html=True)

        data = {
            "ข้อมูล": [
                "ประเภทปัญหา",
                "สถานที่",
                "ระดับความเร่งด่วน",
                "เบอร์โทรศัพท์"
            ],

            "ผลลัพธ์": [
                topic,
                location,
                urgency,
                ", ".join(phones)
                if phones
                else "ไม่พบ"
            ]
        }

        df = pd.DataFrame(data)

        st.table(df)

        if urgency_keywords:
            st.markdown(
                '<div class="label" style="font-size:0.82rem;color:#6B7684;margin-bottom:0.3rem;">'
                'คำสำคัญที่พบ (ความเร่งด่วน)</div>',
                unsafe_allow_html=True
            )
            chips_html = "".join(
                f'<span class="chip keyword-chip">{kw}</span>'
                for kw in urgency_keywords
            )
            st.markdown(chips_html, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


        # =========================
        # Tokenization
        # =========================

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">✂️ Tokenization</div>', unsafe_allow_html=True)

        st.markdown(
            f'<div class="label" style="font-size:0.85rem;color:#6B7684;margin-bottom:0.6rem;">'
            f'จำนวนคำ: <strong style="color:var(--navy);">{len(tokens)}</strong></div>',
            unsafe_allow_html=True
        )

        tokens_html = "".join(
            f'<span class="chip">{token}</span>' for token in tokens
        )
        st.markdown(tokens_html, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


        # =========================
        # Cleansing
        # =========================

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">🧹 Regex & Cleansing</div>', unsafe_allow_html=True)

        st.write("ข้อความต้นฉบับ")

        st.info(text)

        st.write("ข้อความหลังลบข้อมูลส่วนบุคคล")

        st.success(cleaned)

        st.markdown('</div>', unsafe_allow_html=True)


        # =========================
        # Explanation
        # =========================

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">💡 เทคนิค NLP ที่ใช้</div>', unsafe_allow_html=True)

        st.markdown(
            """
            **1. Regex & Cleansing**  
            ใช้ Regular Expression ตรวจหาและซ่อนข้อมูลส่วนบุคคล
            เช่น เบอร์โทรศัพท์ Email และ URL

            **2. Tokenization**  
            ใช้ PyThaiNLP สำหรับตัดข้อความภาษาไทยออกเป็นคำ

            **3. Topic Identification**  
            ใช้ Keyword Matching เพื่อจำแนกประเภทปัญหา

            **4. Information Extraction**  
            สกัดข้อมูลสถานที่และเบอร์โทรศัพท์จากข้อความ

            **5. Urgency Classification**  
            วิเคราะห์คำสำคัญเพื่อจัดระดับความเร่งด่วน
            """
        )

        st.markdown('</div>', unsafe_allow_html=True)