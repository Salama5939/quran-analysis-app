import streamlit as st
import pandas as pd
from supabase import create_client

# إعدادات الصفحة المستقلة للباحث
st.set_page_config(
    page_title="منصة استكشاف وبحث موضوعات القرآن الكريم", page_icon="📖", layout="wide"
)


# الاتصال بقاعدة بيانات Supabase
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


supabase = init_supabase()

# قاموس أسماء السور
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

st.title("📖 منصة البحث الاستكشافي لموضوعات القرآن الكريم")
st.markdown("---")


# جلب بيانات الموضوعات بالكامل
@st.cache_data(ttl=60)
def fetch_all_topics():
    response = supabase.table("quran_topics").select("*").execute()
    return pd.DataFrame(response.data)


df_topics = fetch_all_topics()

if df_topics.empty:
    st.warning("⚠️ لا توجد بيانات مسجلة في جدول quran_topics حالياً.")
else:
    # تقسيم الشاشة إلى تبويبين أساسيين بناءً على قرارنا المعتمد
    tab1, tab2 = st.tabs(
        ["🏛️ البحث الهرمي الذكي (المتدرج)", "🔍 البحث الحر السريع (بالكلمات المفتاحية)"]
    )

    # ----------------------------------------------------
    # التبويب الأول: البحث الهرمي المتسلسل (أفقياً في رأس الصفحة)
    # ----------------------------------------------------
    with tab1:
        st.info(
            "💡 **دليل البحث الذكي:** يمكنك اختيار المستويات الهرمية تدريجياً من القوائم الأفقية أدناه (الباب الرئيسي ⬅️ الفصل ⬅️ العنوان الرئيسي ⬅️ التصنيف ⬅️ العنوان الفرعي)، وسيقوم النظام فوراً بتصفية النتائج وجلب منطوق الآيات الكريمة المرتبطة ورقم الصفحة من الأصل الثابت بدقة مطلقة."
        )

        # 1. الباب الرئيسي
        main_chapters = ["الكل"] + sorted(
            df_topics["main_chapter"].dropna().unique().tolist()
        )
        sel_main = st.selectbox("🏛️ الباب الرئيسي", options=main_chapters, key="h_main")

        df_filtered = df_topics.copy()
        if sel_main != "الكل":
            df_filtered = df_filtered[df_filtered["main_chapter"] == sel_main]

        # 2. الفصل
        sections = ["الكل"] + sorted(
            df_filtered["section_name"].dropna().unique().tolist()
        )
        sel_sec = st.selectbox("📂 الفصل", options=sections, key="h_sec")
        if sel_sec != "الكل":
            df_filtered = df_filtered[df_filtered["section_name"] == sel_sec]

        # 3. العنوان الرئيسي
        headings = ["الكل"] + sorted(
            df_filtered["topic_heading"].dropna().unique().tolist()
        )
        sel_head = st.selectbox("📑 العنوان الرئيسي", options=headings, key="h_head")
        if sel_head != "الكل":
            df_filtered = df_filtered[df_filtered["topic_heading"] == sel_head]

        # 4. التصنيف
        categories = ["الكل"] + sorted(
            df_filtered["topic_category"].dropna().unique().tolist()
        )
        sel_cat = st.selectbox("📌 التصنيف", options=categories, key="h_cat")
        if sel_cat != "الكل":
            df_filtered = df_filtered[df_filtered["topic_category"] == sel_cat]

        # 5. العنوان الفرعي
        sub_categories = ["الكل"] + sorted(
            df_filtered["topic_sub_category"].dropna().unique().tolist()
        )
        sel_sub = st.selectbox("🔖 العنوان الفرعي", options=sub_categories, key="h_sub")
        if sel_sub != "الكل":
            df_filtered = df_filtered[df_filtered["topic_sub_category"] == sel_sub]

        st.markdown("---")
        st.subheader(
            f"📊 نتائج البحث الهرمي (عدد السجلات المطابقة: {len(df_filtered)})"
        )

        if df_filtered.empty:
            st.warning("⚠️ لا توجد نتائج مطابقة لهذه الخيارات.")
        else:
            results_data = []
            for _, row in df_filtered.iterrows():
                s_num = int(row["surah_number"])
                a_num = int(row["start_ayah"])
                s_name = row["surah_name_ar"]

                # الجسر التقني مع full_quran لجلب منطوق الآية ورقم الصفحة الفعلي
                ayah_text = "النص غير متوفر"
                page_num = "غير محدد"
                try:
                    fq_res = (
                        supabase.table("full_quran")
                        .select("ayah_text, page_number")
                        .eq("surah_number", s_num)
                        .eq("ayah_number", a_num)
                        .execute()
                    )
                    if fq_res.data and len(fq_res.data) > 0:
                        ayah_text = fq_res.data[0].get("ayah_text", "النص غير متوفر")
                        page_num = fq_res.data[0].get("page_number", "غير محدد")
                except Exception:
                    pass

                results_data.append(
                    {
                        "الباب الرئيسي": row["main_chapter"],
                        "التصنيف الفرعي": row["topic_sub_category"],
                        "رقم السورة": s_num,
                        "اسم السورة": s_name,
                        "رقم الآية": a_num,
                        "رقم الصفحة": page_num,
                        "منطوق الآية": ayah_text,
                    }
                )

            df_results = pd.DataFrame(results_data)
            st.dataframe(df_results, use_container_width=True)

    # ----------------------------------------------------
    # التبويب الثاني: البحث الحر النصي السريع
    # ----------------------------------------------------
    with tab2:
        st.info(
            "💡 **دليل البحث الحر:** يمكنك كتابة أي كلمة مفتاحية (مثل اسم سورة، أو كلمة من العنوان، أو جزء من التصنيف) للبحث الفوري في كافة السجلات."
        )

        search_query = st.text_input(
            "🔍 أدخل كلمة البحث الحر:", "", key="free_search_input"
        )

        if search_query.strip():
            df_search = df_topics[
                df_topics["topic_sub_category"].str.contains(search_query, na=False)
                | df_topics["topic_category"].str.contains(search_query, na=False)
                | df_topics["topic_heading"].str.contains(search_query, na=False)
                | df_topics["surah_name_ar"].str.contains(search_query, na=False)
                | df_topics["main_chapter"].str.contains(search_query, na=False)
            ]

            st.subheader(
                f"📊 نتائج البحث الحر عن: '{search_query}' (عدد السجلات: {len(df_search)})"
            )

            if df_search.empty:
                st.warning("⚠️ لا توجد نتائج مطابقة لكلمة البحث.")
            else:
                search_results_data = []
                for _, row in df_search.iterrows():
                    s_num = int(row["surah_number"])
                    a_num = int(row["start_ayah"])
                    s_name = row["surah_name_ar"]

                    ayah_text = "النص غير متوفر"
                    page_num = "غير محدد"
                    try:
                        fq_res = (
                            supabase.table("full_quran")
                            .select("ayah_text, page_number")
                            .eq("surah_number", s_num)
                            .eq("ayah_number", a_num)
                            .execute()
                        )
                        if fq_res.data and len(fq_res.data) > 0:
                            ayah_text = fq_res.data[0].get(
                                "ayah_text", "النص غير متوفر"
                            )
                            page_num = fq_res.data[0].get("page_number", "غير محدد")
                    except Exception:
                        pass

                    search_results_data.append(
                        {
                            "الباب الرئيسي": row["main_chapter"],
                            "التصنيف الفرعي": row["topic_sub_category"],
                            "رقم السورة": s_num,
                            "اسم السورة": s_name,
                            "رقم الآية": a_num,
                            "رقم الصفحة": page_num,
                            "منطوق الآية": ayah_text,
                        }
                    )

                df_s_results = pd.DataFrame(search_results_data)
                st.dataframe(df_s_results, use_container_width=True)
        else:
            st.markdown(
                "_(قم برفع حقل البحث أعلاه بكتابة كلمة مفتاحية لتظهر النتائج فوراً)_"
            )
