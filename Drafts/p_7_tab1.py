import streamlit as st
import pandas as pd
from theme import apply_custom_theme, add_home_button
from database import supabase  # الاتصال المركزي المعتمد

# إعدادات الصفحة التجريبية للتبويب الأول
st.set_page_config(
    page_title="التبويب الأول: لوحة إدارة موضوعات القرآن", page_icon="📖", layout="wide"
)

# تطبيق التنسيق المركزي الموحد واتجاه RTL وزر الرئيسية
apply_custom_theme()
add_home_button()

st.title("📖 لوحة إدارة وتصحيح موضوعات القرآن الكريم (التبويب الأول)")
st.markdown(
    "<p style='text-align: center; color: #666666;'>إدارة وعرض وتعديل وحذف وإضافة موضوعات القرآن الكريم مباشرة في قاعدة بيانات Supabase باللغة العربية (بدون أي ملفات إكسل).</p>",
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


# جلب بيانات الموضوعات من Supabase وتعريب أعمدة العرض
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
            valid_map = {k: v for k, v in rename_map.items() if k in df.columns}
            df_display = df.rename(columns=valid_map)
            return df, df_display
        return pd.DataFrame(), pd.DataFrame()
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء جلب الموضوعات: {e}")
        return pd.DataFrame(), pd.DataFrame()


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
            "🔍 ابحث في العناوين الفرعية أو أسماء السور أو العناوين الرئيسية:",
            "",
            key="search_topics_t1",
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

        st.dataframe(filtered_df_disp, use_container_width=True, hide_index=True)

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

                    # تعديل حقل رقم الصفحة ليقبل القيمة الصريحة
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
    st.subheader(
        "➕ إضافة سجل موضوع جديد مباشر في قاعدة البيانات (مع جلب رقم الصفحة تلقائياً)"
    )

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

    # أتمتة جلب رقم الصفحة الصريح من جدول full_quran في Supabase
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
            mc_choice = st.selectbox("الباب الرئيسي", options=mc_options, key="mc_c")
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
            th_choice = st.selectbox("العنوان الرئيسي", options=th_options, key="th_c")
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
                    "أدخل العنوان الفرعي الجديد", "1- وجوده تعالى...", key="tsc_t"
                )
                if tsc_choice == "➕ إضافة بيان جديد..."
                else tsc_choice
            )

            # حقل رقم الصفحة ليحفظ الرقم الصريح فقط
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
