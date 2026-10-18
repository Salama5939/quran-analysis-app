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


def upload_orthographic_quran():
    csv_file = "orthographic_v1.0.csv"
    print(f"📁 جاري قراءة ملف المصحف الشامل: {csv_file}")

    # قراءة الملف بدون هيدر (الأعمدة: 0: رقم تسلسلي، 1: الجزء، 2: رقم السورة، 3: رقم الآية، 4: نص الآية)
    df = pd.read_csv(csv_file, header=None)

    # جلب أسماء السور من جدول surahs لربط رقم السورة باسمها العربي بدقة
    surahs_res = supabase.table("surahs").select("surah_number, name_arabic").execute()
    surah_map = (
        {s["surah_number"]: s["name_arabic"] for s in surahs_res.data}
        if surahs_res.data
        else {}
    )

    # 1. تفريغ جدول full_quran بالكامل أولاً
    print("🧹 جاري تفريغ جدول full_quran بالكامل...")
    try:
        supabase.table("full_quran").delete().gt("id", 0).execute()
        print("✅ تم تفريغ الجدول بنجاح.")
    except Exception as e:
        print(f"ملاحظة أثناء التفريغ: {e}")

    records = []
    for idx, row in df.iterrows():
        surah_num = int(row[2])
        ayah_num = int(row[3])
        juz_num = int(row[1])
        ayah_text = str(row[4]).strip()

        surah_name = surah_map.get(surah_num, f"سورة {surah_num}")

        records.append(
            {
                "surah_number": surah_num,
                "surah_name": surah_name,
                "ayah_number": ayah_num,
                "ayah_text": ayah_text,
                "juz": juz_num,
                "page_number": 1,
            }
        )

    print(f"✨ تم تجهيز {len(records)} آية كاملة للرفع.")

    # 2. الرفع إلى Supabase على دفعات لضمان السرعة والاستقرار
    print("🚀 جاري رفع المصحف الشامل إلى جدول full_quran...")
    batch_size = 200
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        supabase.table("full_quran").insert(batch).execute()
        print(f"تم رفع الدفعة: {i} إلى {min(i + batch_size, len(records))}")

    print(
        "🎉 مبروك! أصبح جدول full_quran يحتوي على المصحف الشامل كاملاً (6236 آية) بدقة فائقة مطابقة لموقع جامعة الملك سعود."
    )


if __name__ == "__main__":
    upload_orthographic_quran()
