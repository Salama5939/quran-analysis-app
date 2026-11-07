import streamlit as st
import pandas as pd
from supabase import create_client
from theme import apply_custom_theme, add_home_button
import io

# إعدادات الصفحة التجريبية الموحدة
st.set_page_config(
    page_title="منصة البحث الثلاثية الشاملة (تجريبي)", page_icon="🔍", layout="wide"
)

# تطبيق التنسيق المركزي الموحد واتجاه RTL من ملف theme.py
apply_custom_theme()


# الاتصال بقاعدة بيانات Supabase
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


supabase = init_supabase()

# زر العودة السريعة للرئيسية
add_home_button()

st.title("🔍 منصة البحث الشاملة (البحث الثلاثي المتقدم)")
st.markdown(
    "<p style='text-align: center; color: #666666;'>البحث العام في الحصر، الاستكشاف الهرمي الذكي، والبحث الحر السريع في منصة واحدة.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")


# جلب بيانات العرض الموحد (v_quran_topics_with_ayahs) للاستكشاف والبحث الحر
@st.cache_data(ttl=60)
def fetch_topics_view():
    try:
        response = supabase.table("v_quran_topics_with_ayahs").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        return pd.DataFrame()


df_view = fetch_topics_view()

# تقسيم الواجهة إلى ثلاثة تبويبات رئيسية كما اتفقنا
tab1, tab2, tab3 = st.tabs(
    [
        "📂 البحث في مجموعات الحصر (التبويب الأول)",
        "🏛️ الاستكشاف والهرمي الذكي (التبويب الثاني)",
        "🚀 البحث الحر السريع والمقاطع (التبويب الثالث)",
    ]
)

# -------------------------------------------------------------------------
# TAB 1: البحث العام في مجموعات الحصر الثمانية (ayah_group_relations) مع الأزرار الثلاثة
# -------------------------------------------------------------------------
with tab1:
    st.info(
        "💡 **دليل البحث:** ابحث بالكلمة أو العبارة في جدول ارتباطات مجموعات الحصر والآيات المرتبطة."
    )

    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        search_q1 = st.text_input(
            "أدخل الكلمة المراد البحث عنها في مجموعات الحصر:",
            placeholder="مثال: الصبر، التقوى، الجنة...",
            key="t1_input",
        )

    # الأزرار الثلاثة الاحترافية لـ Tab 1
    b1_col1, b1_col2, b1_col3, _ = st.columns([1.5, 1.5, 1.5, 5.5])
    search_btn_t1 = b1_col1.button(
        "🔍 تنفيذ البحث", type="primary", use_container_width=True, key="btn_t1_search"
    )
    clear_btn_t1 = b1_col2.button(
        "🧹 مسح الشاشة", use_container_width=True, key="btn_t1_clear"
    )

    if "t1_searched" not in st.session_state:
        st.session_state.t1_searched = False

    if clear_btn_t1:
        st.session_state.t1_searched = False
        st.rerun()

    if search_btn_t1:
        st.session_state.t1_searched = True

    if not st.session_state.t1_searched:
        st.info("👈 أدخل كلمة البحث في الحقل أعلاه ثم اضغط على زر **'تنفيذ البحث'**.")
    else:
        if search_q1.strip():
            if len(search_q1.strip()) < 2:
                st.warning("⚠️ الرجاء إدخال حرفين على الأقل للبدء في البحث.")
            else:
                with st.spinner("جاري الاستعلام في مجموعات الحصر..."):
                    try:
                        rel_resp = (
                            supabase.table("ayah_group_relations")
                            .select(
                                "surah_serial, surah_name, ayah_number, ayah_text, topic_or_keyword, group_id"
                            )
                            .ilike("topic_or_keyword", f"%{search_q1.strip()}%")
                            .execute()
                        )

                        rel_data = rel_resp.data if rel_resp.data else []
                        df_rel = pd.DataFrame(rel_data)

                        st.subheader(
                            f"📊 نتائج البحث في الحصر عن: ( {search_q1} ) - عدد السجلات: {len(df_rel)}"
                        )

                        if not df_rel.empty:
                            display_df = df_rel[
                                [
                                    "surah_serial",
                                    "surah_name",
                                    "ayah_number",
                                    "ayah_text",
                                    "topic_or_keyword",
                                    "group_id",
                                ]
                            ].copy()
                            display_df.columns = [
                                "رقم السورة",
                                "اسم السورة",
                                "رقم الآية",
                                "منطوق الآية",
                                "الكلمة / الموضوع",
                                "المجموعة",
                            ]

                            st.dataframe(
                                display_df, use_container_width=True, hide_index=True
                            )

                            # زر التصدير إلى Excel خاص بـ Tab 1
                            with b1_col3:
                                output1 = io.BytesIO()
                                with pd.ExcelWriter(
                                    output1, engine="xlsxwriter"
                                ) as writer:
                                    display_df.to_excel(
                                        writer,
                                        index=False,
                                        sheet_name="Ayah_Group_Search",
                                    )
                                excel_data1 = output1.getvalue()
                                st.download_button(
                                    label="📥 تصدير إلى Excel",
                                    data=excel_data1,
                                    file_name="Ayah_Group_Search_Results.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True,
                                    key="dl_t1",
                                )
                        else:
                            st.info(
                                "ℹ️ لم يتم العثور على نتائج مطابقة في مجموعات الحصر."
                            )
                    except Exception as e:
                        st.error(f"❌ حدث خطأ أثناء الاستعلام: {e}")
        else:
            st.warning("⚠️ الرجاء كتابة كلمة مفتاحية أولاً.")

# -------------------------------------------------------------------------
# TAB 2: الاستكشاف الهرمي الذكي (أفقياً في 5 أعمدة متجاورة) مع الأزرار الثلاثة
# -------------------------------------------------------------------------
with tab2:
    st.info(
        "💡 **دليل البحث الهرمي:** حدد المستويات الهرمية من القوائم أدناه أفقياً، ثم اضغط على زر **'تنفيذ البحث'**."
    )

    if df_view.empty:
        st.warning("⚠️ لا توجد بيانات متاحة في العرض (v_quran_topics_with_ayahs).")
    else:
        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            m_opts = ["الكل"] + sorted(
                df_view["main_chapter"].dropna().unique().tolist()
            )
            sel_m = st.selectbox("🏛️ الباب الرئيسي", options=m_opts, key="t2_main")

        df_t2_1 = df_view.copy()
        if sel_m != "الكل":
            df_t2_1 = df_t2_1[df_t2_1["main_chapter"] == sel_m]

        with c2:
            s_opts = ["الكل"] + sorted(
                df_t2_1["section_name"].dropna().unique().tolist()
            )
            sel_s = st.selectbox("📂 الفصل", options=s_opts, key="t2_sec")

        df_t2_2 = df_t2_1.copy()
        if sel_s != "الكل":
            df_t2_2 = df_t2_2[df_t2_2["section_name"] == sel_s]

        with c3:
            h_opts = ["الكل"] + sorted(
                df_t2_2["topic_heading"].dropna().unique().tolist()
            )
            sel_h = st.selectbox("📑 العنوان الرئيسي", options=h_opts, key="t2_head")

        df_t2_3 = df_t2_2.copy()
        if sel_h != "الكل":
            df_t2_3 = df_t2_3[df_t2_3["topic_heading"] == sel_h]

        with c4:
            cat_opts = ["الكل"] + sorted(
                df_t2_3["topic_category"].dropna().unique().tolist()
            )
            sel_cat = st.selectbox("📌 التصنيف", options=cat_opts, key="t2_cat")

        df_t2_4 = df_t2_3.copy()
        if sel_cat != "الكل":
            df_t2_4 = df_t2_4[df_t2_4["topic_category"] == sel_cat]

        with c5:
            sub_opts = ["الكل"] + sorted(
                df_t2_4["topic_sub_category"].dropna().unique().tolist()
            )
            sel_sub = st.selectbox("🔖 العنوان الفرعي", options=sub_opts, key="t2_sub")

        st.markdown("---")

        b2_col1, b2_col2, b2_col3, _ = st.columns([1.5, 1.5, 1.5, 5.5])
        search_btn_t2 = b2_col1.button(
            "🔍 تنفيذ البحث",
            type="primary",
            use_container_width=True,
            key="btn_t2_search",
        )
        clear_btn_t2 = b2_col2.button(
            "🧹 مسح الشاشة", use_container_width=True, key="btn_t2_clear"
        )

        if "t2_searched" not in st.session_state:
            st.session_state.t2_searched = False

        if clear_btn_t2:
            st.session_state.t2_searched = False
            st.rerun()

        if search_btn_t2:
            st.session_state.t2_searched = True

        if not st.session_state.t2_searched:
            st.info(
                "👈 قم باختيار المعايير من القوائم أعلاه ثم اضغط على زر **'تنفيذ البحث'**."
            )
        else:
            df_res_t2 = df_view.copy()
            if sel_m != "الكل":
                df_res_t2 = df_res_t2[df_res_t2["main_chapter"] == sel_m]
            if sel_s != "الكل":
                df_res_t2 = df_res_t2[df_res_t2["section_name"] == sel_s]
            if sel_h != "الكل":
                df_res_t2 = df_res_t2[df_res_t2["topic_heading"] == sel_h]
            if sel_cat != "الكل":
                df_res_t2 = df_res_t2[df_res_t2["topic_category"] == sel_cat]
            if sel_sub != "الكل":
                df_res_t2 = df_res_t2[df_res_t2["topic_sub_category"] == sel_sub]

            st.subheader(f"📊 نتائج البحث الهرمي (إجمالي السجلات: {len(df_res_t2)})")

            if df_res_t2.empty:
                st.warning("⚠️ لا توجد نتائج مطابقة لهذه الخيارات.")
            else:
                rename_map_t2 = {
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
                valid_r2 = {
                    k: v for k, v in rename_map_t2.items() if k in df_res_t2.columns
                }
                df_disp_t2 = df_res_t2[list(valid_r2.keys())].rename(columns=valid_r2)

                st.dataframe(df_disp_t2, use_container_width=True)

                with b2_col3:
                    output2 = io.BytesIO()
                    with pd.ExcelWriter(output2, engine="xlsxwriter") as writer:
                        df_disp_t2.to_excel(
                            writer, index=False, sheet_name="Hierarchical_Search"
                        )
                    excel_data2 = output2.getvalue()
                    st.download_button(
                        label="📥 تصدير إلى Excel",
                        data=excel_data2,
                        file_name="Hierarchical_Search_Results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key="dl_t2",
                    )

# -------------------------------------------------------------------------
# TAB 3: البحث الحر السريع والمقاطع (كن فيكون، إلخ) مع التصدير
# -------------------------------------------------------------------------
with tab3:
    st.info(
        "💡 **دليل البحث الحر:** ابحث بأي كلمة أو مقطع (مثل: 'كن فيكون' أو 'بديع السماوات') في كافة السجلات والموضوعات."
    )

    fc1, fc2, fc3 = st.columns([3, 1, 1])
    with fc1:
        free_q = st.text_input(
            "🔍 أدخل كلمة أو مقطع البحث الحر:",
            placeholder="اكتب هنا...",
            key="t3_input",
        )

    with fc2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_btn_t3 = st.button(
            "🚀 بحث حر", type="primary", use_container_width=True, key="btn_t3_search"
        )

    with fc3:
        st.markdown("<br>", unsafe_allow_html=True)
        clear_btn_t3 = st.button("🧹 مسح", use_container_width=True, key="btn_t3_clear")

    if "t3_searched" not in st.session_state:
        st.session_state.t3_searched = False

    if clear_btn_t3:
        st.session_state.t3_searched = False
        st.rerun()

    if search_btn_t3:
        st.session_state.t3_searched = True

    if not st.session_state.t3_searched:
        st.info("👈 أدخل مصطلح البحث واضغط على زر **'بحث حر'**.")
    else:
        if free_q.strip() and not df_view.empty:
            q_str = free_q.strip()
            mask = False
            for col in df_view.select_dtypes(include=["object"]).columns:
                mask = mask | df_view[col].str.contains(q_str, na=False)

            df_free = df_view[mask]

            st.subheader(
                f"📊 نتائج البحث الحر عن: '{q_str}' (عدد السجلات: {len(df_free)})"
            )

            if df_free.empty:
                st.warning("⚠️ لا توجد نتائج مطابقة لمصطلح البحث الحر.")
            else:
                rename_map_t3 = {
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
                valid_r3 = {
                    k: v for k, v in rename_map_t3.items() if k in df_free.columns
                }
                df_disp_t3 = pd.DataFrame(df_free.loc[:, list(valid_r3.keys())]).copy()
                df_disp_t3.columns = list(valid_r3.values())

                st.dataframe(df_disp_t3, use_container_width=True)

                output3 = io.BytesIO()
                with pd.ExcelWriter(output3, engine="xlsxwriter") as writer:
                    df_disp_t3.to_excel(writer, index=False, sheet_name="Free_Search")
                excel_data3 = output3.getvalue()

                st.download_button(
                    label="📥 تصدير نتائج البحث الحر إلى Excel",
                    data=excel_data3,
                    file_name="Free_Search_Results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="dl_t3",
                )
        else:
            st.warning("⚠️ الرجاء إدخال كلمة أو مقطع للبحث.")
