import os
import pandas as pd
import streamlit as st
from supabase import Client, create_client

# الاتصال بقاعدة البيانات باستخدام أسرار secrets.toml
url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("❌ خطأ: لم يتم العثور على مفاتيح الاتصال بـ Supabase.")
    exit()

supabase: Client = create_client(url, key)


def safe_int(value, field_name):
    if value is None or pd.isna(value):
        raise ValueError(f"قيمة الحقل '{field_name}' فارغة أو غير صالحة.")

    if isinstance(value, str):
        value = value.strip().replace(",", "")
        if not value:
            raise ValueError(f"قيمة الحقل '{field_name}' فارغة أو غير صالحة.")

    return int(value)


def import_surahs(file_path):
    print("جاري قراءة ملف أسماء السور...")

    try:
        df = pd.read_excel(file_path, sheet_name="Sheet1")
        print(f"✅ تم العثور على {len(df)} سورة في الملف.")

        surahs_data = []
        for _, row in df.iterrows():
            surah = {
                "surah_number": safe_int(row.get("م"), "م"),
                "name_arabic": str(row.get("إسم السورة") or "").strip(),
                "total_ayahs": safe_int(row.get("عدد الآيات"), "عدد الآيات"),
                "revelation_type": "مكية/مدنية",  # قيمة افتراضية يمكن تحديثها لاحقاً
            }
            surahs_data.append(surah)

        # رفع البيانات إلى جدول surahs دفعة واحدة
        response = supabase.table("surahs").upsert(surahs_data).execute()
        print("🎉 مبروك! تم رفع قائمة السور بالكامل إلى جدول surahs في Supabase.")

    except Exception as e:
        print(f"❌ حدث خطأ أثناء رفع السور: {e}")


if __name__ == "__main__":
    surah_file = "أسماء السور.xlsx"
    if os.path.exists(surah_file):
        import_surahs(surah_file)
    else:
        print(f"❌ ملف أسماء السور غير موجود في المسار الحالي: {surah_file}")
