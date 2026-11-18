import os
import pandas as pd
import streamlit as st
import theme  # استدعاء ملف التنسيق المركزي
from database import supabase, convert_df_to_excel

# 1. إعدادات الصفحة المطورة
st.set_page_config(
    page_title="منصة التناظر وموضوعات السور القرآنية",
    page_icon="🔗",
    layout="wide",
)

# تطبيق التنسيق المركزي وزر الرئيسية
theme.apply_custom_theme()
theme.add_home_button()

st.markdown(
    "<h1 style='text-align: center; color: #F1C40F;'>🔗 منصة التناظر وموضوعات السور القرآنية المتقدمة</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #666666;'>استكشاف وتحليل خريطة التناظر بين السور والمجموعات الثمانية، مع الاستعراض العميق لمقاصد وموضوعات السور.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")


# 2. قراءة ملف CSV للربط بين السور والمجموعات مع التخزين المؤقت
@st.cache_data
def load_surah_group_csv():
    csv_file = "surah_group_relations_rows.csv"
    if os.path.exists(csv_file):
        try:
            return pd.read_csv(csv_file)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


@st.cache_data(ttl=60)
def fetch_objectives_data():
    try:
        response = supabase.table("surah_objectives").select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


df_csv = load_surah_group_csv()
df_top = fetch_objectives_data()

# تقسيم العرض إلى تبويبين رئيسيين متطورين
tab1, tab2 = st.tabs(
    [
        "⚖️ أولاً: خريطة التناظر والتشابه بين السور والمجموعات",
        "📖 ثانياً: مقاصد وموضوعات السور (حسب كتاب التدبر)",
    ]
)

# ---------------------------------------------------------
# TAB 1: خريطة التناظر والتشابه بين السور والمجموعات (من ملف CSV المرفق)
# ---------------------------------------------------------
with tab1:
    st.subheader("⚖️ خريطة التناظر والتشابه بين سور القرآن والمجموعات الثمانية")
    st.markdown("استعراض منظم لجميع سور القرآن مستخرج من ملف الربط المعتمد.")

    if not df_csv.empty:
        col_f1, col_f2 = st.columns([2, 3])

        with col_f1:
            # البحث عن عمود المجموعة في الملف المرفق
            group_col_candidates = [
                c for c in df_csv.columns if "مجموعة" in c or "group" in c.lower()
            ]
            group_col_name = (
                group_col_candidates[0] if group_col_candidates else df_csv.columns[1]
            )

            available_groups = ["الكل"] + sorted(
                df_csv[group_col_name].dropna().unique().tolist()
            )

            selected_group = st.selectbox(
                "🎯 تصفية حسب المجموعة:",
                available_groups,
                key="filter_grp_t1_csv",
            )

        with col_f2:
            search_t_input = st.text_input(
                "🔍 بحث سريع برقم أو اسم السورة:",
                placeholder="اكتب اسم السورة أو رقمها...",
                key="search_tanazor_input_csv",
            )

        filtered_df_csv = df_csv.copy()

        # الفلترة حسب المجموعة
        if selected_group != "الكل":
            filtered_df_csv = filtered_df_csv[
                filtered_df_csv[group_col_name].astype(str) == str(selected_group)
            ]

        # الفلترة حسب البحث النصي
        if search_t_input.strip():
            term = search_t_input.strip()
            mask = False
            for col in filtered_df_csv.select_dtypes(
                include=["object", "int64", "float64"]
            ).columns:
                mask = mask | filtered_df_csv[col].astype(str).str.contains(
                    term, na=False
                )
            filtered_df_csv = filtered_df_csv[mask]

        filtered_df_csv = pd.DataFrame(filtered_df_csv)
        st.success(f"✅ عدد السور المعروضة مطابقة للشروط: {len(filtered_df_csv)} سورة")

        # عرض الجدول مع تحكم كامل بالعرض
        st.dataframe(
            filtered_df_csv,
            width= "stretch",
            hide_index=True,
        )

        # زر التصدير إلى Excel
        excel_bytes_t = convert_df_to_excel(
            filtered_df_csv, sheet_name="خريطة_التناظر_CSV"
        )
        col_dl1, _ = st.columns([2, 5])
        with col_dl1:
            st.download_button(
                label="📥 تصدير جدول التناظر إلى Excel",
                data=excel_bytes_t,
                file_name="Surahs_Tanazor_CSV_Map.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width= "stretch",
            )
    else:
        st.warning(
            "⚠️ تعذر قراءة ملف `surah_group_relations_rows.csv` في المجلد الرئيسي للمشروع."
        )

# ---------------------------------------------------------
# TAB 2: مقاصد وموضوعات السور
# ---------------------------------------------------------
with tab2:
    st.subheader("📖 تفاصيل مقاصد وموضوعات كل سورة من سور القرآن الكريم")
    st.markdown("مستندة إلى المصادر المعتمدة لكتاب 'تسهيل فهم وتدبر القرآن'.")

    if not df_top.empty:
        col_surah_name = (
            "surah_name" if "surah_name" in df_top.columns else df_top.columns[1]
        )
        surah_names_list = ["الكل (عرض كافة السور)"] + sorted(
            df_top[col_surah_name].dropna().unique().tolist()
        )

        col_s1, col_s2 = st.columns([2, 2])
        with col_s1:
            selected_surah_dd = st.selectbox(
                "🎯 اختر السورة للاستعراض السريع:",
                surah_names_list,
                key="surah_dropdown_topics_csv",
            )

        with col_s2:
            st.markdown("<br>", unsafe_allow_html=True)
            show_extra_cols = st.checkbox(
                "إظهار الأعمدة التقنية الإضافية",
                value=False,
                key="chk_extra_cols_csv",
            )

        filtered_df_top = df_top.copy()
        if selected_surah_dd != "الكل (عرض كافة السور)":
            filtered_df_top = filtered_df_top[
                filtered_df_top[col_surah_name].astype(str).str.strip()
                == selected_surah_dd.strip()
            ]

        cols_to_drop = []
        if not show_extra_cols:
            for c in ["id", "code", "half_code", "quarter_code", "group_code"]:
                if c in filtered_df_top.columns:
                    cols_to_drop.append(c)

        display_df_top = filtered_df_top.drop(columns=cols_to_drop, errors="ignore")

        st.success(f"✅ إجمالي السجلات المطابقة: {len(display_df_top)} سجل موضوعي")

        st.dataframe(
            display_df_top,
            width= "stretch",
            hide_index=True,
            column_config={
                col_surah_name: st.column_config.TextColumn(
                    "اسم السورة", width="medium"
                ),
                "surah_objective": st.column_config.TextColumn(
                    "مقصد السورة", width="large"
                ),
            },
        )

        excel_bytes_top = convert_df_to_excel(display_df_top, sheet_name="مقاصد_السور")
        col_dl2, _ = st.columns([2, 5])
        with col_dl2:
            st.download_button(
                label="📥 تصدير تقرير مقاصد السور إلى Excel",
                data=excel_bytes_top,
                file_name="Surahs_Objectives_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width= "stretch",
            )
    else:
        st.warning(
            "⚠️ لا توجد بيانات متاحة في جدول موضوعات السور (`surah_objectives`)."
        )
