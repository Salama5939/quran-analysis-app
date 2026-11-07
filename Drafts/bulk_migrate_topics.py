import re
from supabase import create_client
import streamlit as st

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


def parse_and_prepare_hierarchical_records(
    hierarchy_data, reference_text, description=""
):
    records = []
    cleaned_text = reference_text.strip()

    # 1. التقسيم الصارم بناءً على الشرطة '-' لاعتبار كل جزء وحدة مرجعية مستقلة تماماً
    segments = re.split(r"\s*-\s*", cleaned_text)

    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue

        current_surah = None
        ayahs_part = ""

        # 2. التحقق من وجود الفاصل المائل '/' داخل الوحدة المستقلة
        if "/" in segment:
            parts = segment.split("/")
            # القاعدة الدقيقة: اليمين هو رقم السورة، واليسار هو أرقام الآيات
            current_surah = parts[0].strip()  # اليمين = رقم السورة
            ayahs_part = parts[1].strip()  # اليسار = أرقام الآيات
        else:
            # في حال عدم وجود '/' ضمن المقطع (احتياطياً)، يتم تجاوزه أو ربطه إن وجد سياق
            ayahs_part = segment

        # استخراج كافة أرقام الآيات الواردة في هذا المقطع المستقل فقط
        ayah_numbers = re.findall(r"\d+", ayahs_part)

        if current_surah and ayah_numbers:
            s_num = int(current_surah)
            s_name = SURAH_NAMES_AR.get(s_num, "غير محدد")

            for ayah in ayah_numbers:
                a_num = int(ayah)
                records.append(
                    {
                        "main_chapter": hierarchy_data.get("main_chapter"),
                        "section_name": hierarchy_data.get("section_name"),
                        "topic_heading": hierarchy_data.get("topic_heading"),
                        "topic_category": hierarchy_data.get("topic_category", "عام"),
                        "topic_sub_category": hierarchy_data.get("topic_sub_category"),
                        "surah_number": s_num,
                        "surah_name_ar": s_name,
                        "start_ayah": a_num,
                        "end_ayah": a_num,
                        "topic_description": description,
                    }
                )

    return records


if __name__ == "__main__":
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        supabase = create_client(url, key)

        # تفريغ الجدول أولاً لضمان نظافة البيانات تماماً
        supabase.table("quran_topics").delete().neq("id", 0).execute()
        print("🗑️ تم تفريغ جدول quran_topics بنجاح لإعادة البناء.")

        # بيانات الصفحة الثانية (موضوعات التوحيد والعقيدة)
        page_two_data = [
            {
                "main_chapter": "الباب الأول: أركان الإسلام",
                "section_name": "الفصل الأول: التوحيد",
                "topic_heading": "أولاً: توحيد الله",
                "topic_category": "التوحيد والعقيدة",
                "topic_sub_category": "1- وجوده تعالى وقيامه وكفر البيان والمالية",
                "reference_text": "2/28 و 29 و 164 - 3/18 و 190 - 6/10 - 7/11 - 10/31 - 22/6 و 7 و 50 - 23/11 و 79 و 80 - 27/60 و 64 - 30/27 و 40 - 35/3 - 40/12 - 43/9",
                "description": "دلائل وجود الله تعالى ووحدانيته في القرآن الكريم",
            },
            {
                "main_chapter": "الباب الأول: أركان الإسلام",
                "section_name": "الفصل الأول: التوحيد",
                "topic_heading": "أولاً: توحيد الله",
                "topic_category": "التوحيد والعقيدة",
                "topic_sub_category": "2- وحدانيته تعالى",
                "reference_text": "2/21 و 22 و 29 و 107 - 3/18 و 26 - 6/19 - 7/158 - 9/31 - 10/68 - 16/3 - 17/42 - 21/22 - 23/91 - 25/3 - 28/68 - 35/40 - 39/4 - 42/11",
                "description": "استدلال على انفراد الله بالربوبية والألوهية",
            },
        ]

        all_generated_rows = []
        for item in page_two_data:
            rows = parse_and_prepare_hierarchical_records(
                item, item["reference_text"], item["description"]
            )
            all_generated_rows.extend(rows)

        response = supabase.table("quran_topics").insert(all_generated_rows).execute()
        print(
            f"✅ تم ترحيل الصفحة الثانية بالمعمارية الجديدة الصارمة بنجاح! إجمالي السجلات: {len(all_generated_rows)}"
        )

    except Exception as e:
        print(f"❌ حدث خطأ أثناء الترحيل: {e}")
