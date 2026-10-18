import os
import pandas as pd
import streamlit as st
from supabase import Client, create_client

st.set_page_config(
    page_title="تجربة المصحف المصور والبحث المتقدم",
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
        }
        
        .quran-ayah {
            font-family: 'Amiri', serif;
            font-size: 22px;
            color: #F1C40F;
            line-height: 1.8;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 1. الاتصال بقاعدة بيانات Supabase
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
    st.error("يرجى ضبط SUPABASE_URL و SUPABASE_KEY للاتصال بقاعدة البيانات.")
    st.stop()

supabase: Client = create_client(url, key)

# ==========================================
# 2. تحميل ملف الإكسل المساعد لصفحات السور
# ==========================================
EXCEL_FILE = "Relational TBL between Start and End Pages for each Surah.xlsx"


@st.cache_data
def load_surah_page_mapping():
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE, sheet_name=0)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    return None


df_surah_map = load_surah_page_mapping()

st.markdown(
    "<h1>🧪 شاشة تجربة المصحف المصور والبحث النصي المتقدم</h1>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ==========================================
# تقسيم الشاشة إلى تبويبين (Tab 1 & Tab 2)
# ==========================================
tab1, tab2 = st.tabs(
    [
        "📖 التبويب الأول: استعراض السورة الكاملة (SVG)",
        "🔍 التبويب الثاني: البحث واستعراض الآيات بالرسم العثماني",
    ]
)

# ------------------------------------------
# التبويب الأول: استعراض السورة الكاملة بالمصحف المصور
# ------------------------------------------
with tab1:
    st.subheader("استعراض صفحات السورة بالرسم العثماني الأصلي")

    if df_surah_map is not None:
        surah_list_t1 = df_surah_map["إسم السورة"].str.strip().tolist()
        selected_surah_t1 = st.selectbox(
            "اختر السورة الكريمة للاستعراض البصري:",
            surah_list_t1,
            key="surah_select_t1",
        )

        if st.button("تحميل وعرض السورة المختارة 🌟", key="btn_load_t1"):
            row_data = df_surah_map[
                df_surah_map["إسم السورة"].str.strip() == selected_surah_t1
            ]
            if not row_data.empty:
                start_page = int(str(row_data["رقم صفحة البداية للسورة"].values[0]))
                end_page = int(str(row_data["رقم صفحة النهاية للسورة"].values[0]))

                st.success(
                    f"✅ سورة **{selected_surah_t1}** تبدأ من الصفحة {start_page} إلى"
                    f" الصفحة {end_page}"
                )

                # عرض صفحات الـ SVG الخاصة بالسورة تباعاً
                for p in range(start_page, end_page + 1):
                    svg_filename = f"{p:03d}.svg"
                    svg_path = os.path.join("quran_svg", svg_filename)

                    if os.path.exists(svg_path):
                        with open(svg_path, "r", encoding="utf-8") as f:
                            svg_content = f.read()

                        st.markdown("---")
                        st.markdown(
                            f"<h3 style='text-align: center; color: #F1C40F;'>عرض صفحة"
                            f" المصحف رقم {p}</h3>",
                            unsafe_allow_html=True,
                        )
                        st.markdown(svg_content, unsafe_allow_html=True)
                    else:
                        st.warning(
                            f"⚠️ ملف الصفحة '{svg_filename}' غير موجود في المجلد."
                        )
            else:
                st.error("⚠️ لم يتم العثور على بيانات السورة في الملف المساعد.")
    else:
        st.error(f"❌ لم يتم العثور على ملف الإكسل المساعد '{EXCEL_FILE}'.")


# ------------------------------------------
# التبويب الثاني: البحث واستعراض الآيات بالرسم العثماني
# ------------------------------------------
with tab2:
    st.subheader("استعراض ونطاق الآيات الكريمة بالرسم العثماني من قاعدة البيانات")

    if df_surah_map is not None:
        surah_list_t2 = df_surah_map["إسم السورة"].str.strip().tolist()

        col_a1, col_a2, col_a3 = st.columns(3)
        with col_a1:
            selected_surah_t2 = st.selectbox(
                "اختر السورة:", surah_list_t2, key="surah_select_t2"
            )
        with col_a2:
            start_ayah = st.number_input(
                "من آية رقم:", min_value=1, max_value=286, value=1, key="start_ayah_t2"
            )
        with col_a3:
            end_ayah = st.number_input(
                "إلى آية رقم:", min_value=1, max_value=286, value=5, key="end_ayah_t2"
            )

        if st.button("بحث واستعراض الآيات 🔍", key="btn_search_t2"):
            if start_ayah > end_ayah:
                st.error(
                    "⚠️ خطأ: آية البداية يجب أن تكون أقل من أو مساوية لأية النهاية."
                )
            else:
                with st.spinner("جاري جلب الآيات من قاعدة البيانات..."):
                    try:
                        # استعلام مباشر من جدول full_quran لجلب الآيات المطلوبة ضمن النطاق
                        response = (
                            supabase.table("full_quran")
                            .select("ayah_number, ayah_text")
                            .eq("surah_name", selected_surah_t2)
                            .gte("ayah_number", start_ayah)
                            .lte("ayah_number", end_ayah)
                            .order("ayah_number")
                            .execute()
                        )

                        ayahs_data = response.data

                        if ayahs_data:
                            # عرض Header منسق باسم السورة ونطاق الآيات
                            st.markdown(
                                f"""
                    <div style='background-color: #1E3D59; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
                        <h2 style='color: #F1C40F; margin: 0;'>سورة {selected_surah_t2}</h2>
                        <p style='color: #ECF0F1; margin: 5px 0 0 0; font-size: 16px;'>عرض الآيات الكريمة من (الآية {start_ayah} إلى الآية {end_ayah})</p>
                    </div>
                    """,
                                unsafe_allow_html=True,
                            )

                            # تحويل البيانات إلى DataFrame وتنسيق الجدول
                            df_ayahs = pd.DataFrame(ayahs_data)
                            df_ayahs.columns = [
                                "رقم الآية",
                                "منطوق الآية بالرسم العثماني",
                            ]

                            # عرض الجدول المنسق
                            st.dataframe(
                                df_ayahs,
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "رقم الآية": st.column_config.NumberColumn(
                                        "رقم الآية", width="small", format="%d"
                                    ),
                                    "منطوق الآية بالرسم العثماني": (
                                        st.column_config.TextColumn(
                                            "منطوق الآية بالرسم العثماني", width="large"
                                        )
                                    ),
                                },
                            )
                        else:
                            st.warning(
                                "⚠️ لم يتم العثور على آيات مطابقة لهذا النطاق في قاعدة البيانات."
                            )

                    except Exception as e:
                        st.error(f"حدث خطأ أثناء الاستعلام: {e}")
    else:
        st.error(f"❌ لم يتم العثور على ملف الإكسل المساعد '{EXCEL_FILE}'.")
