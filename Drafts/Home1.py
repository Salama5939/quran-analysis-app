import streamlit as st

st.set_page_config(
    page_title="النظام التحليلي الشامل للتدبر القرآني",
    page_icon="📖",
    layout="wide",
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Cairo', sans-serif;
            direction: rtl;
            text-align: right;
        }
        
        h1, h2, h3 {
            font-family: 'Amiri', serif;
            color: #F1C40F !important;
        }
        
        .hero-box {
            background-color: #1E3D59;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }
        
        .card-container {
            background-color: #2b3a4a;
            padding: 25px;
            border-radius: 12px;
            border-right: 6px solid #17B978;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            margin-bottom: 20px;
            transition: transform 0.3s ease;
        }
        
        .card-container:hover {
            transform: translateY(-5px);
        }
    </style>
""",
    unsafe_allow_html=True,
)

# --- الترحيب والواجهة الرئيسية ---
st.markdown(
    """
    <div class="hero-box">
        <h1>📖 النظام التحليلي الشامل للتدبر القرآني والإضافة الذكية</h1>
        <p style="color: #ECF0F1; font-size: 1.2rem; margin-top: 10px;">
            منصة رقمية متقدمة لتدبر سور وآيات كلمات القرآن العظيم، والاستعراض البصري بالرسم العثماني الأصلي.
        </p>
    </div>
""",
    unsafe_allow_html=True,
)

st.markdown("---")
st.subheader("🧭 اختر البوابة التفاعلية للبدء:")

# --- تصميم البطاقتين الأساسيتين بناءً على طلبك ---
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div class="card-container">
            <h3>📖 تدبر السور الكريمة (SVG)</h3>
            <p style="color: #BDC3C7;">استعراض صفحات المصحف الشريف بالرسم العثماني المتجه بدقة عالية لجودة التصفح البصري.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="card-container">
            <h3>🔍 تدبر الكلمات والآيات (النظام التحليلي)</h3>
            <p style="color: #BDC3C7;">البحث الفوري في الحصر المعتمد، استقراء المجموعات، ومقاصد السور، وتقارير الكلمات.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")
st.info(
    "💡 **إرشاد الاستخدام:** انتقل عبر القائمة الجانبية (Sidebar) إلى الصفحات"
    " الفرعية للبدء في الاستعراض."
)
