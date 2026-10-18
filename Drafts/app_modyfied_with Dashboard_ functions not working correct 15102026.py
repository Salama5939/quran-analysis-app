import os
import pandas as pd
import streamlit as st
from supabase import Client, create_client

# ==========================================
# 1. إعدادات الصفحة والتصميم الجمالي التكيفي
# ==========================================
st.set_page_config(
    page_title="النظام التحليلي للتدبر القرآني",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# تنسيقات CSS متوافقة تلقائياً مع Dark Mode و Light Mode وتضمن وضوح العناوين
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Cairo', sans-serif;
            direction: rtl;
            text-align: right;
        }
        
        /* عناوين واضحة وبارزة تتكيف مع الثيم (فاتح/داكن) */
        h1, h2, h3, h4 {
            font-family: 'Amiri', serif;
            font-weight: 700;
        }
        
        /* بطاقات عرض احترافية */
        .card-box {
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-right: 5px solid #17B978;
            margin-bottom: 20px;
        }
        
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 2. الاتصال بقاعدة بيانات Supabase بأمان
# ==========================================
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url:
    try:
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "")
    except Exception:
        pass

if not url or not key:
    st.error("❌ خطأ: لم يتم العثور على مفاتيح الاتصال بـ Supabase.")
    st.stop()

supabase: Client = create_client(url, key)


# ==========================================
# 3. دوال جلب البيانات مرتبة حسب المصحف
# ==========================================
@st.cache_data
def load_surah_list_ordered():
    # قائمة السور مرتبة بدقة حسب الترتيب المصحفي الصحيح (من 1 إلى 114) لسهولة البحث
    return [
        "الفاتحة",
        "البقرة",
        "آل عمران",
        "النساء",
        "المائدة",
        "الأنعام",
        "الأعراف",
        "الأنفال",
        "التوبة",
        "يونس",
        "هود",
        "يوسف",
        "الرعد",
        "إبراهيم",
        "الحجر",
        "النحل",
        "الإسراء",
        "الكهف",
        "مريم",
        "طه",
        "الأنبياء",
        "الحج",
        "المؤمنون",
        "النور",
        "الفرقان",
        "الشعراء",
        "النمل",
        "القصص",
        "العنكبوت",
        "الروم",
        "لقمان",
        "السجدة",
        "الأحزاب",
        "سبأ",
        "فاطر",
        "يس",
        "الصافات",
        "ص",
        "الزمر",
        "غافر",
        "فصلت",
        "الشورى",
        "الزخرف",
        "الدخان",
        "الجاثية",
        "الأحقاف",
        "محمد",
        "الفتح",
        "الحجرات",
        "ق",
        "الذاريات",
        "الطور",
        "النجم",
        "القمر",
        "الرحمن",
        "الواقعة",
        "الحديد",
        "المجادلة",
        "الحشر",
        "الممتحنة",
        "الصف",
        "الجمعة",
        "المنافقون",
        "التغابن",
        "الطلاق",
        "التحريم",
        "الملك",
        "القلم",
        "الحاقة",
        "المعارج",
        "نوح",
        "الجن",
        "المزمل",
        "المدثر",
        "القيامة",
        "الإنسان",
        "المرسلات",
        "النبأ",
        "النازعات",
        "عبس",
        "التكوير",
        "الانفطار",
        "المطففين",
        "الانشقاق",
        "البروج",
        "الطارق",
        "الأعلى",
        "الغاشية",
        "الفجر",
        "البلد",
        "الشمس",
        "الليل",
        "الضحى",
        "الشرح",
        "التين",
        "العلق",
        "القدر",
        "البينة",
        "الزلزلة",
        "العاديات",
        "القارعة",
        "التكاثر",
        "العصر",
        "الهمزة",
        "الفيل",
        "قريش",
        "الماعون",
        "الكوثر",
        "الكافرون",
        "النصر",
        "المسد",
        "الإخلاص",
        "الفلق",
        "الناس",
    ]


# ==========================================
# 4. القائمة الجانبية (Dashboard Sidebar)
# ==========================================
st.sidebar.markdown(
    "<h2 style='text-align: center;'>📖 تدبر القرآن</h2>", unsafe_allow_html=True
)
st.sidebar.markdown("---")

app_mode = st.sidebar.radio(
    "🧭 التنقل في النظام:",
    [
        "🏠 الرئيسية ولوحة التحكم",
        "🔍 النظام التحليلي والبحث",
        "📖 المصحف المصور التفاعلي",
    ],
)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **نصيحة إرشادية:** استخدم المصحف المصور للاطلاع على الرسم العثماني الأصلي"
    " بجودة عالية متجهة (SVG)."
)


# ==========================================
# 5. محتوى الشاشات
# ==========================================

# --- الشاشة الأولى: الرئيسية ---
if app_mode == "🏠 الرئيسية ولوحة التحكم":
    st.markdown(
        "<h1 style='text-align: center;'>✨ النظام التحليلي للتدبر القرآني"
        " والإضافة الذكية</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; font-size: 1.1rem;'>منصة رقمية متقدمة"
        " للبحث المزدوج، التدبر الموضوعي، واستعراض صفحات المصحف الشريف بالرسم"
        " العثماني الأصلي.</p>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div class="card-box">
                <h3>🔍 بحث دقيق</h3>
                <p>بحث فوري في الحصر المعتمد واستكشاف شامل للآيات والكلمات.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="card-box">
                <h3>📊 استقراء وتدبر</h3>
                <p>استنتاج تلقائي للمجموعات، استعراض السور، ومقاصد الآيات.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
            <div class="card-box">
                <h3>📖 مصحف SVG تفاعلي</h3>
                <p>تصفح صفحات المصحف العثماني بالبحث المباشر عن السورة ورقم"
        " الآية.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# --- الشاشة الثانية: النظام التحليلي والبحث ---
elif app_mode == "🔍 النظام التحليلي والبحث":
    st.markdown("<h1>🔍 النظام التحليلي والبحث الموضوعي</h1>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "البحث الفوري والتدبر",
            "البحث التحليلي والموضوعي",
            "استعراض السور والمقاصد",
            "تقرير الكلمات المحصورة",
        ]
    )

    with tab1:
        st.subheader("البحث الفوري أولاً في الحصر المعتمد")
        search_query = st.text_input(
            "أدخل الكلمة أو العبارة بدقة (مثل: العليم، الغفار، سنن):",
            placeholder="... اكتب الكلمة هنا",
            key="search_input_main",
        )
        if search_query:
            st.info(f"جاري البحث عن: {search_query} ...")

    with tab2:
        st.subheader("البحث التحليلي والموضوعي")
        st.write("مساحة مخصصة للتحليلات المتقدمة وربط الآيات والمجموعات.")

    with tab3:
        st.subheader("استعراض السور والمقاصد")
        st.write("استعراض هيكلي للسور ومقاصدها الكلية.")

    with tab4:
        st.subheader("تقرير الكلمات المحصورة")
        st.write("تقارير إحصائية دقيقة للكلمات المحصورة في القرآن الكريم.")


# --- الشاشة الثالثة: المصحف المصور التفاعلي ---
elif app_mode == "📖 المصحف المصور التفاعلي":
    st.markdown(
        "<h1>📖 المصحف المصور التفاعلي (SVG V1.01)</h1>", unsafe_allow_html=True
    )
    st.markdown(
        "<p>اختر السورة ورقم الآية لينتقلك النظام فوراً إلى صفحة المصحف المطابقة"
        " بدقة.</p>",
        unsafe_allow_html=True,
    )

    surah_list = load_surah_list_ordered()

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        selected_surah = st.selectbox(
            "اختر السورة الكريمة (مرتبة حسب المصحف):", surah_list
        )
    with col_s2:
        selected_ayah = st.number_input(
            "أدخل رقم الآية:", min_value=1, max_value=286, value=1
        )

    if st.button("عرض الصفحة في المصحف 🌟", use_container_width=True):
        target_page = 1  # افتراضي افتتاحي

        try:
            db_query = (
                supabase.table("full_quran")
                .select("page_number")
                .eq("surah_name", selected_surah)
                .eq("ayah_number", selected_ayah)
                .execute()
            )
            if db_query.data and len(db_query.data) > 0:
                target_page = db_query.data[0].get("page_number", 1)
        except Exception:
            pass

        st.success(
            f"✅ تم تحديد الآية {selected_ayah} من سورة {selected_surah} (تقع في"
            f" الصفحة رقم {target_page})"
        )

        # مطابقة اسم الملف بالصيغة الصحيحة ثلاثية الأرقام (مثل 001.svg)
        svg_filename = f"{target_page:03d}.svg"
        svg_path = os.path.join("quran_svg", svg_filename)

        if os.path.exists(svg_path):
            with open(svg_path, "r", encoding="utf-8") as f:
                svg_content = f.read()

            st.markdown("---")
            st.markdown(
                f"<h3 style='text-align: center;'>عرض صفحة المصحف رقم"
                f" {target_page}</h3>",
                unsafe_allow_html=True,
            )
            st.markdown(svg_content, unsafe_allow_html=True)
        else:
            st.warning(
                f"⚠️ ملف الصفحة '{svg_filename}' غير موجود حالياً في مجلد `quran_svg`."
            )
