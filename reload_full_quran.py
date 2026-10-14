import os
import pandas as pd
from supabase import Client, create_client
import toml

# الاتصال بقاعدة البيانات
try:
    secrets = toml.load(".streamlit/secrets.toml")
    url = secrets.get("SUPABASE_URL")
    key = secrets.get("SUPABASE_KEY")
except:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

if not isinstance(url, str) or not isinstance(key, str):
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be configured as strings.")

supabase: Client = create_client(url, key)


def reload_quran_database():
    print("🧹 الخطوة الأولى: جاري تفريغ جدول full_quran بالكامل...")
    try:
        supabase.table("full_quran").delete().gt("id", 0).execute()
        print("✅ تم تفريغ الجدول بنجاح.")
    except Exception as e:
        print(f"ملاحظة أثناء التفريغ: {e}")

    # قراءة الملف المعتمد لاستخلاص الآيات والنصوص بدقة قياسية
    file_name = "الكلمة بالقرآن بالمنطوق بنصف و ربع و المجموعة مع اسم السورة.xlsx"
    print(f"📁 جاري قراءة الملف المعتمد: {file_name}")

    df = pd.read_excel(file_name, sheet_name=0)

    # استخلاص جميع الآيات الفريدة المتوفرة في الملف مع بياناتها الصحيحة
    valid_rows = df.dropna(subset=["إسم السورة", "رقم الآية", "منطوق الآية"])

    quran_records = []
    seen_ayahs = set()

    for idx, row in valid_rows.iterrows():
        surah_name = str(row["إسم السورة"]).strip()
        ayah_num = int(row["رقم الآية"])
        ayah_text = str(row["منطوق الآية"]).strip()
        surah_num = int(row["مسلسل السورة"]) if pd.notna(row.get("مسلسل السورة")) else 1

        identifier = (surah_name, ayah_num)
        if identifier not in seen_ayahs:
            seen_ayahs.add(identifier)
            quran_records.append(
                {
                    "surah_number": surah_num,
                    "surah_name": surah_name,
                    "ayah_number": ayah_num,
                    "ayah_text": ayah_text,
                    "juz": 1,  # القيمة الافتراضية أو يمكن تحديثها
                    "page_number": 1,  # القيمة الافتراضية
                }
            )

    print(f"✨ تم تجهيز {len(quran_records)} آية فريدة بدقة قياسية.")

    # رفع السجلات الجديدة إلى جدول full_quran على دفعات
    print("🚀 جاري رفع البيانات الجديدة إلى جدول full_quran...")
    batch_size = 200
    for i in range(0, len(quran_records), batch_size):
        batch = quran_records[i : i + batch_size]
        supabase.table("full_quran").insert(batch).execute()
        print(f"تم رفع الدفعة: {i} إلى {min(i + batch_size, len(quran_records))}")

    print(
        "🎉 مبروك! تم إعادة تحميل جدول full_quran بالكامل وأصبح جاهزاً ومطابقاً للبحث الدقيق."
    )


if __name__ == "__main__":
    reload_quran_database()
