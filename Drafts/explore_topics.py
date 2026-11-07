import streamlit as st
import pandas as pd
from supabase import create_client
from theme import apply_custom_theme, add_home_button

# إعدادات الصفحة المستقلة للباحث
st.set_page_config(
    page_title="منصة استكشاف وبحث موضوعات القرآن الكريم", page_icon="📖", layout="wide"
)

# تطبيق التصميم الموحد والـ RTL من ملف theme.py
apply_custom_theme()


# الاتصال بقاعدة بيانات Supabase
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


supabase = init_supabase()

# زر العودة السريعة للرئيسية في أعلى الصفحة
add_home_button()

st.title("📖 منصة البحث الاستكشافي المتقدم لموضوعات القرآن الكريم")
st.markdown("---")


# جلب بيانات العرض الموحد والشامل (v_quran_topics_with_ayahs)
@st.cache_data(ttl=60)
def fetch_topics_view():
    try:
        response = supabase.table("v_quran_topics_with_ayahs").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"❌ خطأ في الاتصال بقاعدة البيانات أو جلب الـ View: {e}")
        return pd.DataFrame()


df_view = fetch_topics_view()

if df_view.empty:
    st.warning(
        "⚠️ لا توجد بيانات متاحة في العرض (v_quran_topics_with_ayahs) حالياً أو حدث خطأ في الاتصال."
    )
else:
    # خريطة إعادة تسمية الأعمدة لتكون عربية وواضحة للباحث
    rename_map = {
        "main_chapter": "الباب الرئيسي",
        "section_name": "الفصل",
        "topic_heading": "العنوان الرئيسي",
        "topic_category": "التصنيف",
        "topic_sub_category": "العنوان الفرعي",
        "surah_number": "رقم السورة",
        "surah_name_ar": "اسم السورة",
        "start_ayah": "رقم الآية",
        "page_number": "رقم الصفحة",
        "ayah_text": "منطوق الآية الكريمة",
    }

    # التقسيم إلى تبويبين أساسيين بناءً على التصميم المعتمد
    tab1, tab2 = st.tabs(
        ["🏛️ البحث الهرمي الذكي (المتدرج)", "🔍 البحث الحر السريع (بالكلمات المفتاحية)"]
    )

    # -------------------------------------------------------------------------
    # التبويب الأول: البحث الهرمي الذكي (أفقياً في 5 أعمدة متجاورة في رأس الصفحة)
    # -------------------------------------------------------------------------
    with tab1:
        st.info(
            "💡 **دليل البحث الذكي:** يمكنك اختيار التصنيفات الهرمية تدريجياً من القوائم الأفقية أدناه، ثم الضغط على زر **'تنفيذ البحث'** لعرض النتائج وجلب الآيات الكريمة ورقم الصفحة من المصدر الموحد بدقة متناهية."
        )

        # توزيع الفلاتر الخمسة أفقياً في نفس السطر عبر st.columns(5)
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            main_options = ["الكل"] + sorted(
                df_view["main_chapter"].dropna().unique().tolist()
            )
            sel_main = st.selectbox(
                "🏛️ الباب الرئيسي", options=main_options, key="h_main"
            )

        df_f1 = df_view.copy()
        if sel_main != "الكل":
            df_f1 = df_f1[df_f1["main_chapter"] == sel_main]

        with col2:
            sec_options = ["الكل"] + sorted(
                df_f1["section_name"].dropna().unique().tolist()
            )
            sel_sec = st.selectbox("📂 الفصل", options=sec_options, key="h_sec")

        df_f2 = df_f1.copy()
        if sel_sec != "الكل":
            df_f2 = df_f2[df_f2["section_name"] == sel_sec]

        with col3:
            head_options = ["الكل"] + sorted(
                df_f2["topic_heading"].dropna().unique().tolist()
            )
            sel_head = st.selectbox(
                "📑 العنوان الرئيسي", options=head_options, key="h_head"
            )

        df_f3 = df_f2.copy()
        if sel_head != "الكل":
            df_f3 = df_f3[df_f3["topic_heading"] == sel_head]

        with col4:
            cat_options = ["الكل"] + sorted(
                df_f3["topic_category"].dropna().unique().tolist()
            )
            sel_cat = st.selectbox("📌 التصنيف", options=cat_options, key="h_cat")

        df_f4 = df_f3.copy()
        if sel_cat != "الكل":
            df_f4 = df_f4[df_f4["topic_category"] == sel_cat]

        with col5:
            sub_options = ["الكل"] + sorted(
                df_f4["topic_sub_category"].dropna().unique().tolist()
            )
            sel_sub = st.selectbox(
                "🔖 العنوان الفرعي", options=sub_options, key="h_sub"
            )

        st.markdown("---")

        # الأزرار الثلاثة التنفيذية للتحكم بالبحث والتنظيف
        b_col1, b_col2, b_col3, _ = st.columns([1.5, 1.5, 1.5, 5])

        search_clicked = b_col1.button(
            "🔍 تنفيذ البحث", type="primary", width="stretch"
        )
        clear_clicked = b_col2.button("🧹 مسح الشاشة", width="stretch")

        if "hierarchical_searched" not in st.session_state:
            st.session_state.hierarchical_searched = False

        if clear_clicked:
            st.session_state.hierarchical_searched = False
            st.rerun()

        if search_clicked:
            st.session_state.hierarchical_searched = True

        if not st.session_state.hierarchical_searched:
            st.info(
                "👈 الشاشة جاهزة ونظيفة. يرجى اختيار المعايير المطلوبة من الأعمدة أعلاه ثم الضغط على زر **'تنفيذ البحث'**."
            )
        else:
            df_result = df_view.copy()
            if sel_main != "الكل":
                df_result = df_result[df_result["main_chapter"] == sel_main]
            if sel_sec != "الكل":
                df_result = df_result[df_result["section_name"] == sel_sec]
            if sel_head != "الكل":
                df_result = df_result[df_result["topic_heading"] == sel_head]
            if sel_cat != "الكل":
                df_result = df_result[df_result["topic_category"] == sel_cat]
            if sel_sub != "الكل":
                df_result = df_result[df_result["topic_sub_category"] == sel_sub]

            st.subheader(
                f"📊 نتائج البحث الهرمي (إجمالي السجلات المطابقة: {len(df_result)})"
            )

            if df_result.empty:
                st.warning("⚠️ لا توجد نتائج مطابقة لهذه الخيارات.")
            else:
                valid_rename = {
                    k: v for k, v in rename_map.items() if k in df_result.columns
                }
                df_display = df_result[list(valid_rename.keys())].rename(
                    columns=valid_rename
                )

                st.dataframe(df_display, width="stretch")

                with b_col3:
                    try:
                        import io

                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                            df_display.to_excel(
                                writer, index=False, sheet_name="Quran_Topics_Search"
                            )
                        excel_data = output.getvalue()

                        st.download_button(
                            label="📥 تصدير إلى Excel",
                            data=excel_data,
                            file_name="Quran_Topics_Search_Results.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            width="stretch",
                        )
                    except Exception:
                        pass

    # -------------------------------------------------------------------------
    # التبويب الثاني: البحث الحر السريع (بالكلمات المفتاحية)
    # -------------------------------------------------------------------------
    with tab2:
        st.info(
            "💡 **دليل البحث الحر:** قم بكتابة أي كلمة مفتاحية (اسم سورة، كلمة من العنوان، أو جزء من التصنيف) للبحث الفوري في كافة السجلات بضربة واحدة."
        )

        f_col1, f_col2 = st.columns([3, 1])
        with f_col1:
            free_query = st.text_input(
                "🔍 أدخل كلمة البحث الحر:",
                "",
                key="free_query_input",
                placeholder="اكتب كلمة مفتاحية هنا...",
            )

        with f_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            free_search_btn = st.button("🚀 بحث حر", type="primary", width="stretch")

        if free_search_btn and free_query.strip():
            q = free_query.strip()
            mask = False
            for col in df_view.select_dtypes(include=["object"]).columns:
                mask = mask | df_view[col].str.contains(q, na=False)

            df_free = df_view[mask]

            st.subheader(f"📊 نتائج البحث الحر عن: '{q}' (عدد السجلات: {len(df_free)})")

            if df_free.empty:
                st.warning("⚠️ لا توجد نتائج مطابقة لكلمة البحث الحر.")
            else:
                valid_rename_f = {
                    k: v for k, v in rename_map.items() if k in df_free.columns
                }
                if valid_rename_f:
                    df_f_display = df_free.loc[:, list(valid_rename_f.keys())].copy()
                    df_f_display.columns = [
                        valid_rename_f[col] for col in df_f_display.columns
                    ]
                else:
                    df_f_display = df_free.copy()

                st.dataframe(df_f_display, width="stretch")
        else:
            st.markdown(
                "_(قم بإدخال الكلمة المفتاحية واضغط على زر 'بحث حر' لتظهر النتائج)_"
            )
