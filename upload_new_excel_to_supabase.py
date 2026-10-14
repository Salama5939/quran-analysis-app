import os
import pandas as pd
import toml
from supabase import Client, create_client

# 1. الاتصال بـ Supabase من ملف secrets.toml أو متغيرات البيئة
try:
    secrets = toml.load(".streamlit/secrets.toml")
    url = secrets.get("SUPABASE_URL")
    key = secrets.get("SUPABASE_KEY")
except Exception:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("❌ خطأ: لم يتم العثور على مفاتيح الاتصال بـ Supabase.")

supabase: Client = create_client(url, key)

# 2. قراءة ملف الإكسل الجديد
excel_file = "ملف كود الكلمة المجموعة مسلسل الصورة رقم الآية.xlsx"
print(f"📖 جاري قراءة الملف: {excel_file} ...")
df = pd.read_excel(excel_file, sheet_name=0)

print(f"✅ تم قراءة {len(df)} صفاً بنجاح من الملف.")

# 3. تحضير البيانات لرفعها بالدفعات (Batch Insert) لتجنب الضغط على الخادم
batch_size = 100
total_rows = len(df)
success_count = 0

print("🚀 جاري بدء رفع البيانات إلى جدول ayah_group_relations في Supabase...")

for i in range(0, total_rows, batch_size):
    batch_df = df.iloc[i : i + batch_size]
    records = []

    for _, row in batch_df.iterrows():
        record = {
            "word_code": int(row["كود الكلمة"]),
            "topic_or_keyword": str(row["الكلمة"]).strip(),
            "group_id": int(row["كود المجموعة"]),
            "surah_serial": int(row["مسلسل السورة"]),
            "surah_name": str(row["إسم السورة"]).strip(),
            "ayah_number": int(row["رقم الآية"]),
            "ayah_text": str(row["منطوق الآية"]).strip(),
            "notes": str(row["تعريف المقصد"]).strip(),
            "half_code": int(row["كود النصف"]),
            "quarter_code": int(row["كود الربع"]),
            "frequency_count": 1,
        }
        records.append(record)

    try:
        # إدخال الدفعة إلى جدول ayah_group_relations
        response = supabase.table("ayah_group_relations").insert(records).execute()
        success_count += len(records)
        print(
            f" تم بنجاح رفع الدفعة: من صف {i + 1} إلى {min(i + batch_size, total_rows)}"
            f" (الإجمالي المرفوع: {success_count}/{total_rows})"
        )
    except Exception as e:
        print(f"❌ حدث خطأ في الدفعة بدءاً من الصف {i + 1}: {e}")

print(
    f"🎉 اكتمل عملية الرفع بنجاح تام! إجمالي السجلات المرفوعة:" f" {success_count} سجل."
)
