import streamlit as st
import pandas as pd
from theme import apply_custom_theme, add_home_button
from database import convert_df_to_excel, supabase  # الاستيراد المركزي المعتمد

# إعدادات الصفحة الموحدة المعتمدة
st.set_page_config(
    page_title="منصة البحث الثلاثية الشاملة والمقاصد", page_icon="🔍", layout="wide"
)

# تطبيق التنسيق المركزي الموحد واتجاه RTL وزر الرئيسية
apply_custom_theme()
add_home_button()


# دالة مساعدة لعكس ترتيب الأعمدة بصرياً (RTL) للعرض دون المساس بالجدول الأصلي
def prepare_rtl_display_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    return df.iloc[:, ::-1].copy()


st.title("🔍 منصة البحث الشاملة ومقاصد القرآن الكريم")
st.markdown(
    "<p style='text-align: center; color: #666666;'>المنصة المتكاملة لإدارة الموضوعات، استكشاف الآيات المتشابهات كلياً، التحليل التلقائي للمقاطع، والفهرس الهرمي الموضوعي (معربة بالكامل وعبر Supabase).</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# جدول أسماء السور العربية المعتمد
SURAH_NAMES_AR = {
    1: "الفاتحة",
    2: "البقرة",
    3: "آل عمران",
    4: "النساء",
    5: "المائدة",
    6: "الأنعام",
    7: "الأعراف",
    8: "الأنفال",
    9: "التوبة",
    10: "يونس",
    11: "هود",
    12: "يوسف",
    13: "الرعد",
    14: "إبراهيم",
    15: "الحجر",
    16: "النحل",
    17: "الإسراء",
    18: "الكهف",
    19: "مريم",
    20: "طه",
    21: "الأنبياء",
    22: "الحج",
    23: "المؤمنون",
    24: "النور",
    25: "الفرقان",
    26: "الشعراء",
    27: "النمل",
    28: "القصص",
    29: "العنكبوت",
    30: "الروم",
    31: "لقمان",
    32: "السجدة",
    33: "الأحزاب",
    34: "سبأ",
    35: "فاطر",
    36: "يس",
    37: "الصافات",
    38: "ص",
    39: "الزمر",
    40: "غافر",
    41: "فصلت",
    42: "الشورى",
    43: "الزخرف",
    44: "الدخان",
    45: "الجاثية",
    46: "الأحقاف",
    47: "محمد",
    48: "الفتح",
    49: "الحجرات",
    50: "ق",
    51: "الذاريات",
    52: "الطور",
    53: "النجم",
    54: "القمر",
    55: "الرحمن",
    56: "الواقعة",
    57: "الحديد",
    58: "المجادلة",
    59: "الحشر",
    60: "الممتحنة",
    61: "الصف",
    62: "الجمعة",
    63: "المنافقون",
    64: "التغابن",
    65: "الطلاق",
    66: "التحريم",
    67: "الملك",
    68: "القلم",
    69: "الحاقة",
    70: "المعارج",
    71: "نوح",
    72: "الجن",
    73: "المزمل",
    74: "المدثر",
    75: "القيامة",
    76: "الإنسان",
    77: "المرسلات",
    78: "النبأ",
    79: "النازعات",
    80: "عبس",
    81: "التكوير",
    82: "الانفطار",
    83: "المطففين",
    84: "الانشقاق",
    85: "البروج",
    86: "الطارق",
    87: "الأعلى",
    88: "الغاشية",
    89: "الفجر",
    90: "البلد",
    91: "الشمس",
    92: "الليل",
    93: "الضحى",
    94: "الشرح",
    95: "التين",
    96: "العلق",
    97: "القدر",
    98: "البينة",
    99: "الزلزلة",
    100: "العاديات",
    101: "القارعة",
    102: "التكاثر",
    103: "العصر",
    104: "الهمزة",
    105: "الفيل",
    106: "قريش",
    107: "الماعون",
    108: "الكوثر",
    109: "الكافرون",
    110: "النصر",
    111: "المسد",
    112: "الإخلاص",
    113: "الفلق",
    114: "الناس",
}


# جلب بيانات الموضوعات للتبويب الأول
@st.cache_data(ttl=30)
def fetch_topics():
    try:
        response = supabase.table("quran_topics").select("*").order("id").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            rename_map = {
                "id": "رقم السجل",
                "main_chapter": "الباب الرئيسي",
                "section_name": "الفصل",
                "topic_heading": "العنوان الرئيسي",
                "topic_category": "التصنيف",
                "topic_sub_category": "العنوان الفرعي",
                "surah_number": "رقم السورة",
                "surah_name_ar": "اسم السورة",
                "start_ayah": "رقم الآية",
                "topic_description": "رقم الصفحة",
            }
            valid_cols = [k for k in rename_map.keys() if k in df.columns]
            valid_map = {k: rename_map[k] for k in valid_cols}
            df_display = df[valid_cols].rename(columns=valid_map)
            return df, df_display
        return pd.DataFrame(), pd.DataFrame()
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame()


# جلب كامل المصحف للتبويب الثاني والثالث
@st.cache_data(ttl=60)
def fetch_all_full_quran():
    try:
        all_data = []
        batch_size = 1000
        start = 0
        while True:
            response = (
                supabase.table("full_quran")
                .select("surah_number, surah_name, ayah_number, ayah_text, page_number")
                .range(start, start + batch_size - 1)
                .execute()
            )
            batch = response.data if response.data else []
            if not batch:
                break
            all_data.extend(batch)
            if len(batch) < batch_size:
                break
            start += batch_size
        return pd.DataFrame(all_data) if all_data else pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()


# جلب الفهرس الهرمي للتبويب الرابع
@st.cache_data(ttl=60)
def fetch_topics_view():
    try:
        response = supabase.table("v_quran_topics_with_ayahs").select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()


# تقسيم المنصة إلى 4 تبويبات رئيسية
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📖 إدارة وموضوعات القرآن (التبويب 1)",
        "🔄 الآيات المتشابهات كلياً (التبويب 2)",
        "🧩 المقاطع المشتركة تلقائياً (التبويب 3)",
        "🏛️ الفهرس الهرمي الموضوعي (التبويب 4)",
    ]
)

# ---------------------------------------------------------
# TAB 1: لوحة الإدارة وتصحيح الموضوعات
# ---------------------------------------------------------
with tab1:
    df_topics, df_topics_display = fetch_topics()
    sub_tab1, sub_tab2 = st.tabs(
        ["📊 عرض، بحث، وتعديل السجلات الحالية", "➕ إضافة سجل موضوع جديد مباشر"]
    )

    with sub_tab1:
        st.subheader("عرض كافة السجلات المسجلة في قاعدة البيانات")
        if df_topics.empty:
            st.info("لا توجد سجلات مسجلة حالياً في جدول quran_topics.")
        else:
            search_term = st.text_input(
                "🔍 ابحث في العناوين أو أسماء السور:", "", key="search_topics_t1"
            )
            filtered_df_disp = df_topics_display
            if search_term:
                mask = filtered_df_disp.apply(
                    lambda row: row.astype(str)
                    .str.contains(search_term, case=False, na=False)
                    .any(),
                    axis=1,
                )
                filtered_df_disp = filtered_df_disp[mask]

            rtl_topics_disp = prepare_rtl_display_df(filtered_df_disp)
            st.dataframe(rtl_topics_disp, use_container_width=True, hide_index=True)
            st.markdown("---")
            st.subheader("🛠️ تعديل أو حذف سجل محدد من القاعدة")

            selected_id = st.selectbox(
                "اختر رقم السجل للتعديل أو الحذف:",
                options=df_topics["id"].tolist() if not df_topics.empty else [],
                key="sel_id_edit",
            )

            if selected_id:
                record_row = df_topics[df_topics["id"] == selected_id].iloc[0]
                with st.form("edit_delete_form_t1"):
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        e_main_chapter = st.text_input(
                            "الباب الرئيسي", record_row["main_chapter"]
                        )
                        e_section_name = st.text_input(
                            "الفصل", record_row["section_name"]
                        )
                        e_topic_heading = st.text_input(
                            "العنوان الرئيسي", record_row["topic_heading"]
                        )
                        e_topic_category = st.text_input(
                            "التصنيف", record_row["topic_category"]
                        )
                    with col_e2:
                        e_topic_sub_category = st.text_input(
                            "العنوان الفرعي", record_row["topic_sub_category"]
                        )
                        current_surah_num = (
                            int(record_row["surah_number"])
                            if pd.notna(record_row["surah_number"])
                            else 1
                        )
                        e_surah_num = st.selectbox(
                            "رقم السورة",
                            options=list(SURAH_NAMES_AR.keys()),
                            index=(
                                list(SURAH_NAMES_AR.keys()).index(current_surah_num)
                                if current_surah_num in SURAH_NAMES_AR
                                else 0
                            ),
                            format_func=lambda x: f"{x} - {SURAH_NAMES_AR[x]}",
                            key="edit_surah_num",
                        )
                        e_ayah_num = st.number_input(
                            "رقم الآية",
                            min_value=1,
                            max_value=300,
                            value=(
                                int(record_row["start_ayah"])
                                if pd.notna(record_row["start_ayah"])
                                else 1
                            ),
                            key="edit_ayah_num",
                        )
                        current_desc = (
                            str(record_row["topic_description"])
                            if pd.notna(record_row["topic_description"])
                            else ""
                        )
                        e_page_desc = st.text_input("رقم الصفحة", current_desc)

                    col_btn1, col_btn2 = st.columns(2)
                    update_submitted = col_btn1.form_submit_button(
                        "💾 تحديث السجل المحدد في القاعدة"
                    )
                    delete_submitted = col_btn2.form_submit_button(
                        "🗑️ حذف السجل المحدد من القاعدة", type="primary"
                    )

                    if update_submitted:
                        try:
                            updated_payload = {
                                "main_chapter": e_main_chapter,
                                "section_name": e_section_name,
                                "topic_heading": e_topic_heading,
                                "topic_category": e_topic_category,
                                "topic_sub_category": e_topic_sub_category,
                                "surah_number": e_surah_num,
                                "surah_name_ar": SURAH_NAMES_AR.get(
                                    e_surah_num, "غير محدد"
                                ),
                                "start_ayah": int(e_ayah_num),
                                "end_ayah": int(e_ayah_num),
                                "topic_description": e_page_desc,
                            }
                            supabase.table("quran_topics").update(updated_payload).eq(
                                "id", selected_id
                            ).execute()
                            st.success(f"✅ تم تحديث السجل رقم {selected_id} بنجاح!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ حدث خطأ أثناء التحديث: {e}")

                    if delete_submitted:
                        try:
                            supabase.table("quran_topics").delete().eq(
                                "id", selected_id
                            ).execute()
                            st.success(f"🗑️ تم حذف السجل رقم {selected_id} بنجاح!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ حدث خطأ أثناء الحذف: {e}")

    with sub_tab2:
        st.subheader("➕ إضافة سجل موضوع جديد مباشر في قاعدة البيانات")
        if not df_topics.empty:
            existing_main_chapters = sorted(
                df_topics["main_chapter"].dropna().unique().tolist()
            )
            existing_sections = sorted(
                df_topics["section_name"].dropna().unique().tolist()
            )
            existing_headings = sorted(
                df_topics["topic_heading"].dropna().unique().tolist()
            )
            existing_categories = sorted(
                df_topics["topic_category"].dropna().unique().tolist()
            )
            existing_sub_categories = sorted(
                df_topics["topic_sub_category"].dropna().unique().tolist()
            )
        else:
            (
                existing_main_chapters,
                existing_sections,
                existing_headings,
                existing_categories,
                existing_sub_categories,
            ) = ([], [], [], [], [])

        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            surah_num = st.selectbox(
                "اختر السورة",
                options=list(SURAH_NAMES_AR.keys()),
                format_func=lambda x: f"{x} - {SURAH_NAMES_AR[x]}",
                key="add_surah_t1",
            )
        with col_s2:
            ayah_num = st.number_input(
                "رقم الآية", min_value=1, max_value=300, value=1, key="add_ayah_t1"
            )

        auto_page_val = ""
        try:
            fq_response = (
                supabase.table("full_quran")
                .select("page_number")
                .eq("surah_number", surah_num)
                .eq("ayah_number", ayah_num)
                .execute()
            )
            if fq_response.data and len(fq_response.data) > 0:
                raw_page_num = fq_response.data[0].get("page_number")
                if raw_page_num is not None:
                    auto_page_val = str(raw_page_num)
        except Exception:
            pass

        st.markdown("---")
        with st.form("smart_insert_form_t1"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("##### 🏛️ المستويات الهرمية العليا")
                mc_options = existing_main_chapters + ["➕ إضافة بيان جديد..."]
                mc_choice = st.selectbox(
                    "الباب الرئيسي", options=mc_options, key="mc_c"
                )
                main_chapter = (
                    st.text_input(
                        "أدخل اسم الباب الرئيسي الجديد",
                        "الباب الأول: أركان الإسلام",
                        key="mc_t",
                    )
                    if mc_choice == "➕ إضافة بيان جديد..."
                    else mc_choice
                )

                sec_options = existing_sections + ["➕ إضافة بيان جديد..."]
                sec_choice = st.selectbox("الفصل", options=sec_options, key="sec_c")
                section_name = (
                    st.text_input(
                        "أدخل اسم الفصل الجديد", "الفصل الأول: التوحيد", key="sec_t"
                    )
                    if sec_choice == "➕ إضافة بيان جديد..."
                    else sec_choice
                )

                th_options = existing_headings + ["➕ إضافة بيان جديد..."]
                th_choice = st.selectbox(
                    "العنوان الرئيسي", options=th_options, key="th_c"
                )
                topic_heading = (
                    st.text_input(
                        "أدخل العنوان الرئيسي الجديد", "أولاً: توحيد الله", key="th_t"
                    )
                    if th_choice == "➕ إضافة بيان جديد..."
                    else th_choice
                )

            with col2:
                st.markdown("##### 📂 التصنيفات ورقم الصفحة")
                tc_options = existing_categories + ["➕ إضافة بيان جديد..."]
                tc_choice = st.selectbox("التصنيف", options=tc_options, key="tc_c")
                topic_category = (
                    st.text_input("أدخل التصنيف الجديد", "التوحيد والعقيدة", key="tc_t")
                    if tc_choice == "➕ إضافة بيان جديد..."
                    else tc_choice
                )

                tsc_options = existing_sub_categories + ["➕ إضافة بيان جديد..."]
                tsc_choice = st.selectbox(
                    "العنوان الفرعي", options=tsc_options, key="tsc_c"
                )
                topic_sub_category = (
                    st.text_input(
                        "أدخل العنوان الفرعي الجديد",
                        "1- وحدانيته تعالى...",
                        key="tsc_t",
                    )
                    if tsc_choice == "➕ إضافة بيان جديد..."
                    else tsc_choice
                )

                page_desc = st.text_input(
                    "رقم الصفحة", auto_page_val, key="page_desc_input"
                )

            submitted = st.form_submit_button(
                "💾 حفظ وإضافة السجل الجديد لقاعدة بيانات Supabase"
            )
            if submitted:
                try:
                    payload = {
                        "main_chapter": main_chapter,
                        "section_name": section_name,
                        "topic_heading": topic_heading,
                        "topic_category": topic_category,
                        "topic_sub_category": topic_sub_category,
                        "surah_number": surah_num,
                        "surah_name_ar": SURAH_NAMES_AR.get(surah_num, "غير محدد"),
                        "start_ayah": int(ayah_num),
                        "end_ayah": int(ayah_num),
                        "topic_description": page_desc.strip(),
                    }
                    supabase.table("quran_topics").insert([payload]).execute()
                    st.success("✅ تم حفظ السجل الجديد بنجاح مباشر في Supabase!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء الحفظ: {e}")

# ---------------------------------------------------------
# TAB 2: استكشاف الآيات المتشابهات كلياً
# ---------------------------------------------------------
with tab2:
    st.subheader("🔄 استكشاف ومقارنة الآيات المتشابهات كلياً في كامل المصحف")
    df_quran_t2 = fetch_all_full_quran()

    if df_quran_t2.empty:
        st.warning("⚠️ لا توجد بيانات متاحة في جدول full_quran حالياً.")
    else:

        @st.cache_data
        def find_exact_duplicates(df):
            df["clean_text"] = df["ayah_text"].str.strip()
            grouped = df.groupby("clean_text").filter(lambda x: len(x) > 1)
            if grouped.empty:
                return pd.DataFrame()
            return grouped.sort_values(by=["clean_text", "surah_number", "ayah_number"])

        df_exact = find_exact_duplicates(df_quran_t2)

        if df_exact.empty:
            st.info("ℹ️ لم يتم العثور على آيات متطابقة نصياً بالكامل.")
        else:
            col_m1, col_m2 = st.columns(2)
            col_m1.metric(
                "عدد النصوص المتشابهة (المجموعات)",
                f"{df_exact['clean_text'].nunique()} نص",
            )
            col_m2.metric(
                "إجمالي الآيات الواقعة في التشابه الكلي", f"{len(df_exact)} آية"
            )
            st.markdown("---")

            display_exact_df = df_exact[
                [
                    "surah_number",
                    "surah_name",
                    "ayah_number",
                    "ayah_text",
                    "page_number",
                ]
            ].copy()
            display_exact_df.columns = [
                "رقم السورة",
                "اسم السورة",
                "رقم الآية",
                "منطوق الآية الكريمة",
                "رقم الصفحة",
            ]
            rtl_exact_df = prepare_rtl_display_df(display_exact_df)
            st.dataframe(rtl_exact_df, use_container_width=True, hide_index=True)

            excel_data_exact = convert_df_to_excel(
                display_exact_df, sheet_name="Exact_Mutashabihahat"
            )
            col_btn, _ = st.columns([2, 5])
            with col_btn:
                st.download_button(
                    label="📥 تصدير تقرير الآيات المتشابهات كلياً إلى Excel",
                    data=excel_data_exact,
                    file_name="Exact_Mutashabihahat_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="dl_exact_excel_main",
                )

# ---------------------------------------------------------
# TAB 3: الاستخراج التلقائي للمقاطع المشتركة
# ---------------------------------------------------------
with tab3:
    st.subheader("🧩 الاستخراج التلقائي للمقاطع المشتركة جزئياً داخل الآيات")
    df_quran_t3 = fetch_all_full_quran()

    if df_quran_t3.empty:
        st.warning("⚠️ لا توجد بيانات متاحة في جدول full_quran حالياً.")
    else:
        col_opt1, _ = st.columns([2, 2])
        with col_opt1:
            ngram_size = st.slider(
                "اختر عدد الكلمات المتتالية في المقطع المشترك:",
                min_value=2,
                max_value=5,
                value=3,
                key="slider_ngram_main",
            )

        @st.cache_data
        def extract_shared_snippets(df, n=3):
            records = []
            for _, row in df.iterrows():
                words = row["ayah_text"].split()
                if len(words) >= n:
                    for i in range(len(words) - n + 1):
                        snippet = " ".join(words[i : i + n])
                        records.append(
                            {
                                "snippet": snippet,
                                "surah_number": row["surah_number"],
                                "surah_name": row["surah_name"],
                                "ayah_number": row["ayah_number"],
                                "ayah_text": row["ayah_text"],
                                "page_number": row["page_number"],
                            }
                        )
            if not records:
                return pd.DataFrame()
            snippet_df = pd.DataFrame(records)
            counts = snippet_df.groupby("snippet")["ayah_text"].nunique().reset_index()
            repeated_snippets = counts[counts["ayah_text"] > 1]["snippet"]
            filtered_result = snippet_df[snippet_df["snippet"].isin(repeated_snippets)]
            return filtered_result.sort_values(
                by=["snippet", "surah_number", "ayah_number"]
            )

        df_snippets = extract_shared_snippets(df_quran_t3, n=ngram_size)

        if df_snippets.empty:
            st.info("ℹ️ لم يتم العثور على مقاطع متشابهة متكررة بهذه الشروط.")
        else:
            col_m1, col_m2 = st.columns(2)
            col_m1.metric(
                "عدد المقاطع المشتركة المستخرجة",
                f"{df_snippets['snippet'].nunique()} مقطع",
            )
            col_m2.metric("إجمالي مواضع الورود في المصحف", f"{len(df_snippets)} موضع")
            st.markdown("---")

            display_snippet_df = df_snippets[
                [
                    "snippet",
                    "surah_number",
                    "surah_name",
                    "ayah_number",
                    "ayah_text",
                    "page_number",
                ]
            ].copy()
            display_snippet_df.columns = [
                "المقطع المشترك المستخرج",
                "رقم السورة",
                "اسم السورة",
                "رقم الآية",
                "منطوق الآية الكريمة",
                "رقم الصفحة",
            ]
            rtl_snippet_df = prepare_rtl_display_df(display_snippet_df)
            st.dataframe(rtl_snippet_df, use_container_width=True, hide_index=True)

            excel_data_snippets = convert_df_to_excel(
                display_snippet_df, sheet_name="Automatic_Snippet_Analysis"
            )
            col_btn, _ = st.columns([2, 5])
            with col_btn:
                st.download_button(
                    label="📥 تصدير تقرير المقاطع المستخرجة تلقائياً إلى Excel",
                    data=excel_data_snippets,
                    file_name=f"Automatic_Snippets_{ngram_size}_words.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="dl_snippet_auto_excel_main",
                )

# ---------------------------------------------------------
# TAB 4: الفهرس الهرمي الموضوعي
# ---------------------------------------------------------
with tab4:
    st.subheader("📖 الفهرس الهرمي الموضوعي للآيات والمقاصد")
    df_view = fetch_topics_view()

    if df_view.empty:
        st.warning(
            "⚠️ لا توجد بيانات متاحة في العرض (v_quran_topics_with_ayahs) حالياً."
        )
    else:
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            m_opts = ["الكل"] + sorted(
                df_view["main_chapter_name"].dropna().unique().tolist()
            )
            sel_m = st.selectbox("🏛️ الباب الرئيسي", options=m_opts, key="t4_main_main")

        df_t4_1 = df_view.copy()
        if sel_m != "الكل":
            df_t4_1 = df_t4_1[df_t4_1["main_chapter_name"] == sel_m]

        with c2:
            s_opts = ["الكل"] + sorted(
                df_t4_1["section_name"].dropna().unique().tolist()
            )
            sel_s = st.selectbox("📂 الفصل", options=s_opts, key="t4_sec_main")

        df_t4_2 = df_t4_1.copy()
        if sel_s != "الكل":
            df_t4_2 = df_t4_2[df_t4_2["section_name"] == sel_s]

        with c3:
            h_opts = ["الكل"] + sorted(
                df_t4_2["topic_heading_name"].dropna().unique().tolist()
            )
            sel_h = st.selectbox(
                "📑 العنوان الرئيسي", options=h_opts, key="t4_head_main"
            )

        df_t4_3 = df_t4_2.copy()
        if sel_h != "الكل":
            df_t4_3 = df_t4_3[df_t4_3["topic_heading_name"] == sel_h]

        with c4:
            cat_opts = ["الكل"] + sorted(
                df_t4_3["topic_category_name"].dropna().unique().tolist()
            )
            sel_cat = st.selectbox("📌 التصنيف", options=cat_opts, key="t4_cat_main")

        df_t4_4 = df_t4_3.copy()
        if sel_cat != "الكل":
            df_t4_4 = df_t4_4[df_t4_4["topic_category_name"] == sel_cat]

        with c5:
            sub_opts = ["الكل"] + sorted(
                df_t4_4["topic_sub_category_name"].dropna().unique().tolist()
            )
            sel_sub = st.selectbox(
                "🔖 العنوان الفرعي", options=sub_opts, key="t4_sub_main"
            )

        st.markdown("---")
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

        st.subheader(f"📊 نتائج الفهرس الهرمي (إجمالي السجلات: {len(df_res_t4)})")

        if df_res_t4.empty:
            st.warning("⚠️ لا توجد نتائج مطابقة لهذه الخيارات.")
        else:
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
            valid_r4 = {
                k: v for k, v in rename_map_t4.items() if k in df_res_t4.columns
            }
            df_disp_t4 = df_res_t4[list(valid_r4.keys())].rename(columns=valid_r4)
            rtl_t4_df = prepare_rtl_display_df(df_disp_t4)

            st.dataframe(rtl_t4_df, use_container_width=True, hide_index=True)

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
                    key="dl_t4_excel_main",
                )
