import streamlit as st
import pandas as pd
from supabase import create_client
import theme  # استدعاء ملف التنسيق المركزي لتوحيد الهوية والخطوط واتجاه RTL

# إعدادات الصفحة المستقلة
st.set_page_config(
    page_title="لوحة إدارة موضوعات القرآن", page_icon="📖", layout="wide"
)

# تطبيق التنسيق الموحد وإضافة زر العودة للرئيسية
theme.apply_custom_theme()
theme.add_home_button()


# الاتصال بقاعدة بيانات Supabase
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


supabase = init_supabase()

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

st.title("📖 لوحة التحكم المستقلة لإدارة وتصحيح موضوعات القرآن الكريم")
st.markdown("---")


# جلب البيانات من Supabase
def fetch_topics():
    response = supabase.table("quran_topics").select("*").order("id").execute()
    return pd.DataFrame(response.data)


df_topics = fetch_topics()

# تبويبات الإدارة الشاملة
tab1, tab2, tab3 = st.tabs(
    ["📊 عرض وإدارة وتعديل السجلات", "➕ إضافة سجل جديد", "📂 رفع ملف أكسل"]
)

with tab1:
    st.subheader("عرض كافة السجلات المسجلة في القاعدة")
    if df_topics.empty:
        st.info("لا توجد سجلات مسجلة حالياً.")
    else:
        # شريط بحث أو فلترة بسيطة
        search_term = st.text_input("🔍 ابحث في العناوين أو أسماء السور:", "")
        filtered_df = df_topics
        if search_term:
            filtered_df = df_topics[
                df_topics["topic_sub_category"].str.contains(search_term, na=False)
                | df_topics["surah_name_ar"].str.contains(search_term, na=False)
                | df_topics["topic_heading"].str.contains(search_term, na=False)
            ]

        st.dataframe(filtered_df, use_container_width=True)

        st.markdown("---")
        st.subheader("🛠️ تعديل أو حذف سجل محدد")

        selected_id = st.selectbox(
            "اختر رقم السجل (ID) للتعديل أو الحذف:",
            options=df_topics["id"].tolist() if not df_topics.empty else [],
        )

        if selected_id:
            record_row = df_topics[df_topics["id"] == selected_id].iloc[0]

            with st.form("edit_delete_form"):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    e_main_chapter = st.text_input(
                        "الباب الرئيسي", record_row["main_chapter"]
                    )
                    e_section_name = st.text_input("الفصل", record_row["section_name"])
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
                    e_surah_num = st.selectbox(
                        "رقم السورة",
                        options=list(SURAH_NAMES_AR.keys()),
                        index=(
                            list(SURAH_NAMES_AR.keys()).index(
                                int(record_row["surah_number"])
                            )
                            if int(record_row["surah_number"]) in SURAH_NAMES_AR
                            else 0
                        ),
                        format_func=lambda x: f"{x} - {SURAH_NAMES_AR[x]}",
                    )
                    e_ayah_num = st.number_input(
                        "رقم الآية",
                        min_value=1,
                        max_value=300,
                        value=int(record_row["start_ayah"]),
                    )
                    e_page_desc = st.text_input(
                        "الوصف / رقم الصفحة", record_row["topic_description"]
                    )

                col_btn1, col_btn2 = st.columns(2)
                update_submitted = col_btn1.form_submit_button("💾 تحديث السجل المحدد")
                delete_submitted = col_btn2.form_submit_button(
                    "🗑️ حذف السجل المحدد", type="primary"
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

with tab2:
    st.subheader("➕ إضافة سجل جديد تفاعلياً (بأتمتة جلب الوصف خلف الكواليس)")

    if not df_topics.empty:
        existing_main_chapters = sorted(
            df_topics["main_chapter"].dropna().unique().tolist()
        )
        existing_sections = sorted(df_topics["section_name"].dropna().unique().tolist())
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

    # اختيار السورة ورقم الآية في أعلى الصفحة
    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        surah_num = st.selectbox(
            "اختر السورة",
            options=list(SURAH_NAMES_AR.keys()),
            format_func=lambda x: f"{x} - {SURAH_NAMES_AR[x]}",
            key="add_surah",
        )
    with col_s2:
        ayah_num = st.number_input(
            "رقم الآية", min_value=1, max_value=300, value=1, key="add_ayah"
        )

    # جلب وصف الصفحة آلياً خلف الكواليس من جدول full_quran الثابت
    auto_description = "إضافة يدوية"
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
                auto_description = f"مرجع من صفحة الكتيب رقم {raw_page_num}"
    except Exception as e:
        pass

    st.markdown("---")

    with st.form("smart_insert_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 🏛️ المستويات الهرمية العليا")
            mc_options = existing_main_chapters + ["➕ إضافة بيان جديد..."]
            mc_choice = st.selectbox("الباب الرئيسي", options=mc_options)
            main_chapter = (
                st.text_input(
                    "أدخل اسم الباب الرئيسي الجديد", "الباب الأول: أركان الإسلام"
                )
                if mc_choice == "➕ إضافة بيان جديد..."
                else mc_choice
            )

            sec_options = existing_sections + ["➕ إضافة بيان جديد..."]
            sec_choice = st.selectbox("الفصل", options=sec_options)
            section_name = (
                st.text_input("أدخل اسم الفصل الجديد", "الفصل الأول: التوحيد")
                if sec_choice == "➕ إضافة بيان جديد..."
                else sec_choice
            )

            th_options = existing_headings + ["➕ إضافة بيان جديد..."]
            th_choice = st.selectbox("العنوان الرئيسي", options=th_options)
            topic_heading = (
                st.text_input("أدخل العنوان الرئيسي الجديد", "أولاً: توحيد الله")
                if th_choice == "➕ إضافة بيان جديد..."
                else th_choice
            )

        with col2:
            st.markdown("##### 📂 التصنيفات والمراجع")
            tc_options = existing_categories + ["➕ إضافة بيان جديد..."]
            tc_choice = st.selectbox("التصنيف", options=tc_options)
            topic_category = (
                st.text_input("أدخل التصنيف الجديد", "التوحيد والعقيدة")
                if tc_choice == "➕ إضافة بيان جديد..."
                else tc_choice
            )

            tsc_options = existing_sub_categories + ["➕ إضافة بيان جديد..."]
            tsc_choice = st.selectbox("العنوان الفرعي", options=tsc_options)
            topic_sub_category = (
                st.text_input("أدخل العنوان الفرعي الجديد", "1- وجوده تعالى...")
                if tsc_choice == "➕ إضافة بيان جديد..."
                else tsc_choice
            )

            custom_note = st.text_input(
                "ملاحظات إضافية على الوصف (اختياري)", "", key="optional_note"
            )

        submitted = st.form_submit_button("💾 حفظ وإضافة السجل الجديد لقاعدة البيانات")
        if submitted:
            try:
                final_description = auto_description
                if custom_note.strip():
                    final_description += f" - {custom_note.strip()}"

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
                    "topic_description": final_description,
                }
                supabase.table("quran_topics").insert([payload]).execute()
                st.success("✅ تم حفظ السجل الجديد بنجاح في Supabase!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء الحفظ: {e}")

with tab3:
    st.subheader("📂 رفع ملف أكسل (تحديث شامل)")
    uploaded_file = st.file_uploader("اختر ملف الأكسل (xlsx)", type=["xlsx"])

    if uploaded_file is not None:
        df_preview = pd.read_excel(uploaded_file)
        st.success(f"تم قراءة الملف بنجاح! إجمالي السجلات: {len(df_preview)}")
        st.dataframe(df_preview.head(10))

        if st.button("🚀 اعتماد وترحيل البيانات إلى Supabase"):
            try:
                records = []
                for _, row in df_preview.iterrows():
                    s_num = int(row.get("surah_number", row.get("رقم السورة", 1)))
                    a_num = int(
                        row.get(
                            "start_ayah", row.get("رقم الآية", row.get("رقم الاية", 1))
                        )
                    )

                    main_ch = str(row.get("main_chapter", "الباب الأول: أركان الإسلام"))
                    sec_name = str(row.get("section_name", "الفصل الأول: التوحيد"))
                    t_heading = str(row.get("topic_heading", "أولاً: توحيد الله"))
                    t_cat = str(row.get("topic_category", "التوحيد والعقيدة"))
                    t_sub_cat = str(
                        row.get(
                            "topic_sub_category",
                            "1- وجوده تعالى وقيامه وكفر البيان والمالية",
                        )
                    )
                    t_desc = str(row.get("topic_description", "مرجع محدث"))

                    s_name = SURAH_NAMES_AR.get(s_num, "غير محدد")

                    records.append(
                        {
                            "main_chapter": main_ch,
                            "section_name": sec_name,
                            "topic_heading": t_heading,
                            "topic_category": t_cat,
                            "topic_sub_category": t_sub_cat,
                            "surah_number": s_num,
                            "surah_name_ar": s_name,
                            "start_ayah": a_num,
                            "end_ayah": a_num,
                            "topic_description": t_desc,
                        }
                    )

                supabase.table("quran_topics").delete().neq("id", 0).execute()

                batch_size = 100
                for i in range(0, len(records), batch_size):
                    batch = records[i : i + batch_size]
                    supabase.table("quran_topics").insert(batch).execute()

                st.success(f"✅ تم ترحيل {len(records)} سجلاً بنجاح تام إلى Supabase!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء الترحيل: {e}")
