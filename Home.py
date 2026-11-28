import os
import streamlit as st
import theme
from database import supabase
from postgrest.types import CountMethod

# إعدادات الصفحة الرئيسية
st.set_page_config(
    page_title="المصحف الشريف - مشروع المصحف الإلكتروني",
    page_icon="📖",
    layout="wide",
)

# تطبيق التنسيق المركزي الموحد
theme.apply_custom_theme()

# ==============================================================================
# التنسيق البصري الموحد للصفحة الرئيسية
# ==============================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700&display=swap');

    .home-hero-box {
        background: linear-gradient(135deg, rgba(27, 77, 62, 0.12) 0%, rgba(212, 175, 55, 0.14) 100%);
        border: 1px solid rgba(212, 175, 55, 0.50);
        border-right: 6px solid #1B4D3E;
        border-radius: 16px;
        padding: 24px 30px;
        margin-bottom: 18px;
        text-align: center;
        font-family: 'Cairo', sans-serif;
    }
    .home-hero-title {
        color: #1B4D3E;
        font-size: 2.05rem;
        font-weight: 700;
        margin: 0 0 8px 0;
    }
    .home-hero-sub {
        color: #4A5568;
        font-size: 1.05rem;
        margin: 0;
    }
    .home-kpi-card {
        background: #FFFFFF;
        border: 1px solid #E6E2D6;
        border-top: 4px solid #D4AF37;
        border-radius: 12px;
        padding: 12px 14px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        font-family: 'Cairo', sans-serif;
    }
    .home-kpi-label {
        color: #666666;
        font-size: 0.88rem;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .home-kpi-val {
        color: #1B4D3E;
        font-size: 1.55rem;
        font-weight: 700;
    }
    .gate-card {
        background: #FCFBF7;
        border: 1px solid #E5DFD0;
        border-right: 5px solid #1B4D3E;
        border-radius: 12px;
        padding: 16px 18px 12px 18px;
        margin-bottom: 8px;
        min-height: 128px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        direction: rtl;
        text-align: right;
        font-family: 'Cairo', sans-serif;
    }
    .gate-card-title {
        color: #1B4D3E;
        font-size: 1.12rem;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .gate-card-desc {
        color: #555555;
        font-size: 0.90rem;
        line-height: 1.65;
        margin: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=120)
def fetch_home_kpis():
    """جلب المؤشرات الإجمالية السريعة للواجهة الرئيسية من Supabase"""
    stats = {
        "ayahs": 6236,
        "surahs": 114,
        "topics": 0,
        "roots": 0,
    }
    try:
        r_topics = (
            supabase.table("quran_topics")
            .select("id", count=CountMethod.exact)
            .limit(1)
            .execute()
        )
        if r_topics.count is not None:
            stats["topics"] = r_topics.count
    except Exception:
        pass

    try:
        r_roots = (
            supabase.table("smart_root_topics")
            .select("id", count=CountMethod.exact)
            .limit(1)
            .execute()
        )
        if r_roots.count is not None:
            stats["roots"] = r_roots.count
    except Exception:
        pass

    return stats


# الترويسة البصرية الرئيسية
st.markdown(
    """
    <div class="home-hero-box">
        <div class="home-hero-title">📖 النظام التحليلي الشامل لتدبر القرآن العظيم والبحث الذكي</div>
        <p class="home-hero-sub">منصة رقمية أكاديمية متكاملة لتدبر سور وآيات القرآن الكريم بالرسم العثماني الأصلي، مدعومة بقاعدة بيانات سحابية موحدة</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# بطاقات المؤشرات السريعة
home_stats = fetch_home_kpis()
k1, k2, k3, k4 = st.columns(4)
kpi_items = [
    (k1, "آيات المصحف الشريف", f"{home_stats['ayahs']:,} آية"),
    (k2, "سور القرآن الكريم", f"{home_stats['surahs']} سورة"),
    (k3, "سجلات الفهرس الهرمي", f"{home_stats['topics']:,} سجل"),
    (k4, "سجلات أرشيف الجذور", f"{home_stats['roots']:,} سجل"),
]
for col_box, lbl, val in kpi_items:
    with col_box:
        st.markdown(
            f"""
            <div class="home-kpi-card">
                <div class="home-kpi-label">{lbl}</div>
                <div class="home-kpi-val">{val}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

# زر تحميل دليل المُتدبّر
col_space, col_dl_btn, col_right_space = st.columns([1.5, 2, 1.5])
with col_dl_btn:
    pdf_filename = "دليل_المتدبر_للقرآن_الكريم.pdf"
    if os.path.exists(pdf_filename):
        with open(pdf_filename, "rb") as f:
            pdf_data = f.read()
        st.download_button(
            label="📥 تحميل دليل المُتدبّر الشامل (PDF)",
            data=pdf_data,
            file_name="دليل_المتدبر_للقرآن_الكريم.pdf",
            mime="application/pdf",
            width="stretch",
        )
    else:
        st.info("ℹ️ ملف دليل المتدبر (PDF) غير مرفق حالياً في المجلد الجذري.")

st.markdown("---")
st.markdown(
    "<h3 style='text-align: center; color: #1B4D3E; margin-bottom: 4px;'>🎯 بوابات المنصة التفاعلية الثمانية</h3>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #666666; font-size: 14px; margin-bottom: 18px;'>اختر البوابة المطلوبة للانتقال المباشر، ويمكنك العودة لهذه الشاشة في أي وقت عبر زر «🏠 الرئيسية» أعلى كل بوابة.</p>",
    unsafe_allow_html=True,
)

# تعريف البوابات الثمانية المرقمة المطابقة تماماً لمجلد pages/
GATES = [
    {
        "title": "1️⃣ المصحف المصور والتلاوة",
        "desc": "استعراض صفحات المصحف الشريف الـ 604 بالرسم العثماني الدقيق للتلاوة والحفظ والمراجعة.",
        "btn": "انتقل إلى المصحف المصور 👈",
        "path": "pages/1_📖_المصحف_المصور.py",
        "key": "btn_gate_1",
    },
    {
        "title": "2️⃣ المعمارية البصرية والمفاهيمية",
        "desc": "الخريطة البنيوية الشاملة للطبقات الخمس والمحاور الـ 24 والعقد الـ 96 وفق قاعدة نفي الترادف.",
        "btn": "انتقل إلى المعمارية المفاهيمية 👈",
        "path": "pages/2_🧭_المعمارية_المفاهيمية.py",
        "key": "btn_gate_2",
    },
    {
        "title": "3️⃣ معمارية المجموعات الثمانية",
        "desc": "الخريطة الهرمية الشاملة للمجموعات الثمانية والسور الـ 114 ومقاصدها وبنائها المقطعي.",
        "btn": "انتقل إلى المجموعات الثمانية 👈",
        "path": "pages/3_🏛️_معمارية_المجموعات_الثمانية.py",
        "key": "btn_gate_3",
    },
    {
        "title": "4️⃣ الإحصاءات والرسوم البيانية",
        "desc": "لوحة المؤشرات التحليلية والرسوم البيانية التفاعلية وإدارة بيانات الحصر الموضوعي.",
        "btn": "انتقل إلى الإحصاءات والرسوم 👈",
        "path": "pages/4_📊_الإحصاءات_والرسوم_البيانية.py",
        "key": "btn_gate_4",
    },
    {
        "title": "5️⃣ الآيات المحورية والمتشابهات",
        "desc": "استكشاف الآيات الجامعة للمفاهيم، تقاطع مفهومين داخل الآية، والمتشابه اللفظي في كامل المصحف.",
        "btn": "انتقل إلى الآيات المحورية 👈",
        "path": "pages/5_🔗_الآيات_المحورية_والمتشابهات.py",
        "key": "btn_gate_5",
    },
    {
        "title": "6️⃣ الفهرس الهرمي الموضوعي",
        "desc": "التصنيف الموضوعي المتدرج ذو الـ 5 مستويات (الباب ⬅ الفصل ⬅ العنوان) وإدارة السجلات.",
        "btn": "انتقل إلى الفهرس الهرمي 👈",
        "path": "pages/6_🗂️_الفهرس_الهرمي_الموضوعي.py",
        "key": "btn_gate_6",
    },
    {
        "title": "7️⃣ الاستكشاف الذكي للجذور",
        "desc": "استخراج مشتقات الجذور اللغوية وتلوينها بالعثماني، أرشيف الجذور، والمرصد المعجمي الشامل.",
        "btn": "انتقل إلى استكشاف الجذور 👈",
        "path": "pages/7_🔎_الاستكشاف_الذكي_للجذور.py",
        "key": "btn_gate_7",
    },
    {
        "title": "8️⃣ أرشيف الحفظ والتدبر",
        "desc": "لوحة متابعة وإدارة رحلتك القرآنية في حفظ وتدبر الآيات الكريمة وتسجيل المراجعات والخواطر.",
        "btn": "انتقل إلى أرشيف التدبر 👈",
        "path": "pages/8_🎯_أرشيف_الحفظ_والتدبر.py",
        "key": "btn_gate_8",
    },
]

# عرض البطاقات في صفوف متوازنة (3 بطاقات في الصفين الأول والثاني، وبطاقتان في الصف الثالث)
for row_start in range(0, len(GATES), 3):
    row_items = GATES[row_start : row_start + 3]
    cols = st.columns(len(row_items))
    for col_widget, gate in zip(cols, row_items):
        with col_widget:
            st.markdown(
                f"""
                <div class="gate-card">
                    <div class="gate-card-title">{gate['title']}</div>
                    <p class="gate-card-desc">{gate['desc']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(gate["btn"], key=gate["key"], width="stretch"):
                st.switch_page(gate["path"])
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #7A5C00; font-size: 13px;'>💡 للانتقال بين البوابات، استخدم زر «🏠 الرئيسية» الثابت أعلى كل بوابة للعودة السريعة إلى هذه اللوحة.</p>",
    unsafe_allow_html=True,
)
