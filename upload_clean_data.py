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

if not isinstance(url, str) or not url.strip():
    raise ValueError("SUPABASE_URL must be configured as a non-empty string.")
if not isinstance(key, str) or not key.strip():
    raise ValueError("SUPABASE_KEY must be configured as a non-empty string.")

supabase: Client = create_client(url, key)


def process_and_upload():
    file_name = "الكلمة بالقرآن بالمنطوق بنصف و ربع و المجموعة مع اسم السورة.xlsx"
    print(f"جاري قراءة الملف الأساسي المعتمد: {file_name}")

    df = pd.read_excel(file_name, sheet_name=0)

    cleaned_rows = []
    current_word = None

    for idx, row in df.iterrows():
        if pd.notna(row.get("الكلمة")):
            current_word = str(row["الكلمة"]).strip()
        elif pd.notna(row.get("إسم السورة")) and pd.notna(row.get("منطوق الآية")):
            if current_word:
                surah_name = str(row["إسم السورة"]).strip()
                ayah_num = int(row["رقم الآية"]) if pd.notna(row["رقم الآية"]) else 0
                ayah_text = str(row["منطوق الآية"]).strip()
                surah_num = (
                    int(row["مسلسل السورة"]) if pd.notna(row.get("مسلسل السورة")) else 1
                )

                notes = f"سورة {surah_name} | آية رقم: {ayah_num} | النص: {ayah_text}"

                cleaned_rows.append(
                    {
                        "topic_or_keyword": current_word,
                        "frequency_count": 1,
                        "group_id": 1,
                        "notes": notes,
                        "source_file": file_name,  # 📌 تسجيل اسم الملف المصدري لمعرفته بوضوح
                    }
                )

    df_clean = pd.DataFrame(cleaned_rows)
    # إزالة التكرار الداخلي إن وجد في الملف
    df_clean = df_clean.drop_duplicates(subset=["topic_or_keyword", "notes"])

    records = df_clean.to_dict(orient="records")
    print(f"تم إعداد {len(records)} سجلاً فريداً ونظيفاً.")

    # 1. تفريغ جدول ayah_group_relations بالكامل لحذف أي بيانات قديمة أو مكررة
    print("🧹 جاري مسح وتفريغ الجدول القديم في Supabase لضمان النقاء التام...")
    try:
        supabase.table("ayah_group_relations").delete().neq("id", 0).execute()
    except Exception as e:
        print(f"ملاحظة أثناء الحذف (يمكن تجاهلها إذا كان الجدول فارغاً): {e}")

    # 2. رفع البيانات الجديدة على دفعات
    print("🚀 جاري رفع البيانات الجديدة...")
    batch_size = 200
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        supabase.table("ayah_group_relations").insert(batch).execute()
        print(f"تم رفع الدفعة: {i} إلى {min(i + batch_size, len(records))}")

    print("🎉 مبروك! تم تحديث وتنظيف القاعدة بالكامل والبيانات خالية من أي تكرار.")


if __name__ == "__main__":
    process_and_upload()
