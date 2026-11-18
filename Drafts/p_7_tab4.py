import streamlit as st
import pandas as pd
from theme import apply_custom_theme, add_home_button
from database import convert_df_to_excel, supabase  # الاستيراد المركزي المعتمد

# إعدادات الصفحة التجريبية للتبويب الرابع
st.set_page_config(
    page_title="التبويب الرابع: الفهرس الهرمي الموضوعي", page_icon="📖", layout="wide"
)

# تطبيق التنسيق المركزي الموحد واتجاه RTL وزر الرئيسية
apply_custom_theme()
add_home_button()

st.title("📖 الفهرس الهرمي الموضوعي للآيات والمقاصد (التبويب الرابع)")
st.markdown(
    "<p style='text-align: center; color: #666666;'>استكشاف موضوعات القرآن الكريم ومقاصده عبر التسلسل الهرمي المعتمد (الباب، الفصل، العنوان) من قاعدة بيانات Supabase.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")


# جلب بيانات العرض الموحد (v_quran_topics_with_ayahs) للاستكشاف الهرمي
@st.cache_data(ttl=60)
def fetch_topics_view():
    try:
        response = supabase.table("v_quran_topics_with_ayahs").select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء جلب البيانات: {e}")
        return pd.DataFrame()


with st.spinner("جاري جلب الفهرس الهرمي والموضوعات من قاعدة البيانات..."):
    df_view = fetch_topics_view()

if df_view.empty:
    st.warning("⚠️ لا توجد بيانات متاحة في العرض (v_quran_topics_with_ayahs) حالياً.")
else:
    st.info(
        "💡 **دليل الاستكشاف الهرمي:** حدد المستويات الهرمية من القوائم أدناه أفقياً لتصفية واستعراض الموضوعات والآيات المرتبطة بها."
    )

    # الأعمدة الهرمية المعربة في العرض
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        m_opts = ["الكل"] + sorted(
            df_view["main_chapter_name"].dropna().unique().tolist()
        )
        sel_m = st.selectbox("🏛️ الباب الرئيسي", options=m_opts, key="t4_main")

    df_t4_1 = df_view.copy()
    if sel_m != "الكل":
        df_t4_1 = df_t4_1[df_t4_1["main_chapter_name"] == sel_m]

    with c2:
        s_opts = ["الكل"] + sorted(df_t4_1["section_name"].dropna().unique().tolist())
        sel_s = st.selectbox("📂 الفصل", options=s_opts, key="t4_sec")

    df_t4_2 = df_t4_1.copy()
    if sel_s != "الكل":
        df_t4_2 = df_t4_2[df_t4_2["section_name"] == sel_s]

    with c3:
        h_opts = ["الكل"] + sorted(
            df_t4_2["topic_heading_name"].dropna().unique().tolist()
        )
        sel_h = st.selectbox("📑 العنوان الرئيسي", options=h_opts, key="t4_head")

    df_t4_3 = df_t4_2.copy()
    if sel_h != "الكل":
        df_t4_3 = df_t4_3[df_t4_3["topic_heading_name"] == sel_h]

    with c4:
        cat_opts = ["الكل"] + sorted(
            df_t4_3["topic_category_name"].dropna().unique().tolist()
        )
        sel_cat = st.selectbox("📌 التصنيف", options=cat_opts, key="t4_cat")

    df_t4_4 = df_t4_3.copy()
    if sel_cat != "الكل":
        df_t4_4 = df_t4_4[df_t4_4["topic_category_name"] == sel_cat]

    with c5:
        sub_opts = ["الكل"] + sorted(
            df_t4_4["topic_sub_category_name"].dropna().unique().tolist()
        )
        sel_sub = st.selectbox("🔖 العنوان الفرعي", options=sub_opts, key="t4_sub")

    st.markdown("---")

    # تصفية البيانات النهائية بناءً على اختيارات الباحث
    df_res_t4 = df_view.copy()
    if sel_m != "الكل":
        df_res_t4 = df_res_t4[df_res_t4["main_chapter_name"] == sel_m]
    if sel_s != "الكل":
        df_res_t4 = df_res_t4[df_res_t4["section_name"] == sel_s]
    if sel_h != "الكل":
        df_res_t4 = df_res_t4[df_res_t4["topic_heading_name"] == sel_h]
    if sel_cat != "الكل":
        df_res_t4 = df_res_t4[df_res_t4["topic_category_name"] == sel_cat]
    if sel_sub != "الكل":
        df_res_t4 = df_res_t4[df_res_t4["topic_sub_category_name"] == sel_sub]

    st.subheader(f"📊 نتائج البحث الهرمي الموضوعي (إجمالي السجلات: {len(df_res_t4)})")

    if df_res_t4.empty:
        st.warning("⚠️ لا توجد نتائج مطابقة لهذه الخيارات الهرمية.")
    else:
        # تجهيز جدول العرض المعرب
        rename_map_t4 = {
            "main_chapter_name": "الباب الرئيسي",
            "section_name": "الفصل",
            "topic_heading_name": "العنوان الرئيسي",
            "topic_category_name": "التصنيف",
            "topic_sub_category_name": "العنوان الفرعي",
            "surah_number": "رقم السورة",
            "surah_name": "اسم السورة",
            "start_ayah": "رقم الآية",
            "page_number": "رقم الصفحة",
            "ayah_text": "منطوق الآية الكريمة",
        }
        valid_r4 = {k: v for k, v in rename_map_t4.items() if k in df_res_t4.columns}
        df_disp_t4 = df_res_t4[list(valid_r4.keys())].rename(columns=valid_r4)

        st.dataframe(df_disp_t4, use_container_width=True, hide_index=True)

        # زر التصدير المركزي لملف Excel
        excel_data_t4 = convert_df_to_excel(
            df_disp_t4, sheet_name="Hierarchical_Topic_Index"
        )

        col_btn, _ = st.columns([2, 5])
        with col_btn:
            st.download_button(
                label="📥 تصدير تقرير الفهرس الهرمي إلى Excel",
                data=excel_data_t4,
                file_name="Hierarchical_Topic_Index_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="dl_t4_excel",
            )
