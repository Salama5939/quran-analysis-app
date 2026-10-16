import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="تجربة المصحف المصور بالملف المساعد", page_icon="📖", layout="wide"
)

st.markdown(
    """
    <style>
        html, body, [class*="css"] {
            font-family: 'Cairo', sans-serif;
            direction: rtl;
            text-align: right;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 1. تحميل ملف ربط السور بصفحات البداية والنهاية
# ==========================================
EXCEL_FILE = "Relational TBL between Start and End Pages for each Surah.xlsx"


@st.cache_data
def load_surah_page_mapping():
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE, sheet_name=0)
        # تنظيف أسماء الأعمدة لإزالة أي مسافات زائدة
        df.columns = [str(c).strip() for c in df.columns]
        return df
    return None


df_surah_map = load_surah_page_mapping()

st.markdown(
    "<h1>🧪 شاشة تجربة المصحف المصور (باستخدام ملف الإكسل المساعد)</h1>",
    unsafe_allow_html=True,
)

if df_surah_map is not None:
    # استخراج قائمة أسماء السور بدقة من ملف الإكسل
    surah_list = df_surah_map["إسم السورة"].str.strip().tolist()

    # اختيار السورة
    selected_surah = st.selectbox("اختر السورة الكريمة:", surah_list)

    # جلب صفحة البداية والنهاية لهذه السورة من الإكسل
    row_data = df_surah_map[df_surah_map["إسم السورة"].str.strip() == selected_surah]

    if not row_data.empty:
        surah_start_page = int(
            float(str(row_data["رقم صفحة البداية للسورة"].values[0]))
        )
        surah_end_page = int(float(str(row_data["رقم صفحة النهاية للسورة"].values[0])))
        total_ayahs = int(float(str(row_data["عدد الآيات"].values[0])))

        st.info(
            f"📖 سورة **{selected_surah}** تبدأ من **الصفحة {surah_start_page}** إلى"
            f" **الصفحة {surah_end_page}** (عدد آياتها: {total_ayahs} آية)"
        )

        # إدخال نطاق الآيات للتوضيح
        col1, col2 = st.columns(2)
        with col1:
            start_ayah = st.number_input(
                "من آية رقم:", min_value=1, max_value=max(1, total_ayahs), value=1
            )
        with col2:
            end_ayah = st.number_input(
                "إلى آية رقم:",
                min_value=1,
                max_value=max(1, total_ayahs),
                value=min(5, total_ayahs),
            )

        if st.button("عرض صفحات المصحف المطلوبة 🌟"):
            if start_ayah > end_ayah:
                st.error(
                    "⚠️ خطأ: آية البداية يجب أن تكون أقل من أو مساوية لأية النهاية."
                )
            else:
                # كمبدأ أساسي دقيق: سنعرض صفحات السورة أو الصفحات المرتبطة
                # (يمكننا استخدام صفحة البداية والنهاية الخاصة بالسورة كبداية عرض)
                st.success(
                    f"✅ جاري عرض صفحات سورة {selected_surah} (من الصفحة"
                    f" {surah_start_page} إلى {surah_end_page})"
                )

                # عرض الصفحات تباعاً من مجلد quran_svg
                for p in range(surah_start_page, surah_end_page + 1):
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
        st.error("⚠️ لم يتم العثور على بيانات هذه السورة في ملف الإكسل.")
else:
    st.error(
        f"❌ لم يتم العثور على ملف الإكسل '{EXCEL_FILE}' في مجلد المشروع. تأكد من"
        " وضعه بجانب ملفات التطبيق."
    )
