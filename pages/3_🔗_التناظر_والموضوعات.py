import os
import pandas as pd
import streamlit as st
import theme  # استدعاء ملف التنسيق المركزي

# 1. إعدادات الصفحة التجريبية الثالثة
st.set_page_config(
    page_title="تجربة التناظر وموضوعات السور",
    page_icon="🔗",
    layout="wide",
)

# تطبيق التنسيق المركزي
theme.apply_custom_theme()

# تنسيق إضافي لتكبير الخط داخل الجداول لتسهيل القراءة
st.markdown(
    """
    <style>
        [data-testid="stDataFrame"] {
            direction: rtl;
            text-align: right;
        }
        [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
            direction: rtl !important;
            text-align: right !important;
            font-family: 'Amiri', serif !important;
            font-size: 18px !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    "<h1 style='text-align: center; color: #F1C40F;'>🔗 شاشة تجربة جداول التناظر"
    " وموضوعات السور القرآنية</h1>",
    unsafe_allow_html=True,
)
st.markdown("---")

FILE_TANAZOR = "جدول التناظر و التشابة بين سور القرآن و المجموعات الثمانية.xlsx"
FILE_TOPICS = "موضوعات كل سورة بالقرآن.xlsx"


# 2. دالة لقراءة الملفين مع التخزين المؤقت
@st.cache_data
def load_new_files():
    df_tanazor = None
    df_topics = None

    if os.path.exists(FILE_TANAZOR):
        df_tanazor = pd.read_excel(
            FILE_TANAZOR, sheet_name="جدول التناظر سور و مجموعات"
        )

    if os.path.exists(FILE_TOPICS):
        df_topics = pd.read_excel(FILE_TOPICS, sheet_name="موضوعات كل السور بالقرآن")

    return df_tanazor, df_topics


df_t, df_top = load_new_files()

if df_t is not None or df_top is not None:
    # تقسيم العرض إلى تبويبين رئيسيين
    tab1, tab2 = st.tabs(
        [
            "⚖️ أولاً: جدول التناظر والتشابه بين السور والمجموعات",
            "📖 ثانياً: موضوعات السور (حسب كتاب التدبر)",
        ]
    )

    # --- التبويب الأول: جدول التناظر والمجموعات ---
    with tab1:
        st.subheader(
            "خريطة التناظر والتشابه بين سور القرآن والمجموعات الثمانية ونصف القرآن"
        )
        st.markdown(
            "<p style='color: #BDC3C7;'>استعراض منظم لجميع سور القرآن الـ 114 مع"
            " أكواد المجموعات ونصف القرآن والمجموعات المتناظرة.</p>",
            unsafe_allow_html=True,
        )

        if df_t is not None:
            selected_group = st.selectbox(
                "تصفية حسب المجموعة الثمانية:",
                ["الكل", 1, 2, 3, 4, 5, 6, 7, 8],
                key="filter_grp_t1",
            )

            filtered_df_t = df_t
            if selected_group != "الكل":
                filtered_df_t = df_t[
                    df_t["كود المجموعة (1-8)"].astype(str) == str(selected_group)
                ]

            st.success(f"✅ عدد السور المعروضة: {len(filtered_df_t)} سورة")
            st.dataframe(filtered_df_t, use_container_width=True, hide_index=True)
        else:
            st.error(f"❌ تعذر العثور على الملف: '{FILE_TANAZOR}'")

    # --- التبويب الثاني: موضوعات السور ---
    with tab2:
        st.subheader("تفاصيل موضوعات كل سورة من سور القرآن الكريم")
        st.markdown(
            "<p style='color: #BDC3C7;'>مستندة إلى كتاب 'تسهيل فهم وتدبر القرآن' لفضيلة"
            " الدكتور عدلي الخطيب.</p>",
            unsafe_allow_html=True,
        )

        if df_top is not None:
            col_surah_name = (
                "إسم السورة" if "إسم السورة" in df_top.columns else df_top.columns[1]
            )
            surah_names_list = ["الكل (عرض كافة السور)"] + list(
                df_top[col_surah_name].dropna().unique()
            )

            col_s1, col_s2 = st.columns([2, 2])
            with col_s1:
                selected_surah_dd = st.selectbox(
                    "اختر السورة للاستعراض السريع:",
                    surah_names_list,
                    key="surah_dropdown_topics",
                )

            with col_s2:
                show_extra_cols = st.checkbox(
                    "إظهار الأعمدة التقنية الإضافية (كود النصف، الربع، المجموعة)",
                    value=False,
                    key="chk_extra_cols",
                )

            filtered_df_top = df_top
            if selected_surah_dd != "الكل (عرض كافة السور)":
                filtered_df_top = df_top[
                    df_top[col_surah_name].astype(str).str.strip()
                    == selected_surah_dd.strip()
                ]

            cols_to_drop = []
            if not show_extra_cols:
                for c in [
                    "م",
                    "كود النصف",
                    "كود الربع ",
                    "كود المجموعة",
                    "كود السورة",
                ]:
                    if c in filtered_df_top.columns:
                        cols_to_drop.append(c)

            display_df = filtered_df_top.drop(columns=cols_to_drop, errors="ignore")

            st.success(f"✅ إجمالي السجلات المطابقة: {len(display_df)} سجل موضوعي")

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    col_surah_name: st.column_config.TextColumn(
                        "اسم السورة", width="medium"
                    ),
                },
            )
        else:
            st.error(f"❌ تعذر العثور على الملف: '{FILE_TOPICS}'")

else:
    st.error("❌ تعذر العثور على ملفات الإكسل الجديدة في المجلد الرئيسي للمشروع.")
