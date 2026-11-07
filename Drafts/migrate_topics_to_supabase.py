import re
import os
from supabase import create_client
import streamlit as st  # سنعتمد على أسرار الاتصال المخزنة لديك

# 1. قاموس أسماء السور لتعبئة اسم السورة بالعربية تلقائياً بناءً على رقمها
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
    66: "التسريم",
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
    92: "اللَيل",
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


def parse_and_prepare_records(category, sub_category, reference_text, description=""):
    """
    دالة لتحليل النص وإنشاء قائمة السجلات الجاهزة للإدخال في Supabase
    """
    records = []
    cleaned_text = reference_text.strip()
    segments = re.split(r"\s*-\s*", cleaned_text)
    current_surah = None

    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue

        if "/" in segment:
            parts = segment.split("/")
            current_surah = parts[0].strip()
            ayahs_part = parts[1].strip()
        else:
            ayahs_part = segment

        ayah_numbers = re.findall(r"\d+", ayahs_part)

        for ayah in ayah_numbers:
            if current_surah:
                s_num = int(current_surah)
                a_num = int(ayah)
                s_name = SURAH_NAMES_AR.get(s_num, "غير محدد")

                records.append(
                    {
                        "topic_category": category,
                        "topic_sub_category": sub_category,
                        "surah_number": s_num,
                        "surah_name_ar": s_name,
                        "start_ayah": a_num,
                        "end_ayah": a_num,
                        "topic_description": description,
                    }
                )

    return records


# --- 🚀 عملية الترحيل التجريبية السحابية ---
if __name__ == "__main__":
    try:
        # الاتصال بقاعدة البيانات عبر أسرار التطبيق
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        supabase = create_client(url, key)

        print("🔗 تم الاتصال بقاعدة بيانات Supabase بنجاح لترحيل البيانات...")

        # عينة بيانات حقيقية تمثل بنداً من الفهرس (مثل: توحيد الألوهية)
        sample_category = "الألوهية"
        sample_sub_category = "وجوده تعالى وقيام الكافر وبيان العاقبة"
        sample_ref = "2/28 و 29 و 164"
        sample_desc = "استدلال على الوحدانية وعظمة الخالق"

        # تحليل النص واستخراج السجلات
        generated_rows = parse_and_prepare_records(
            sample_category, sample_sub_category, sample_ref, sample_desc
        )

        print(f"📦 تم تحليل العينة بنجاح وإعداد {len(generated_rows)} سجل للإرسال.")

        # إرسال السجلات إلى جدول quran_topics في Supabase
        response = supabase.table("quran_topics").insert(generated_rows).execute()

        print("✅ تم رفع وتخزين البيانات في Supabase بنجاح تام!")
        print("البيانات المرسلة:", response.data)

    except Exception as e:
        print(f"❌ حدث خطأ أثناء الاتصال أو الإرسال: {e}")
