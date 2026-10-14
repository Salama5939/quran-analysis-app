import os
import pandas as pd
import toml
from supabase import Client, create_client

# الاتصال بـ Supabase من ملف secrets.toml أو متغيرات البيئة
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

# قراءة ملف الإكسل الخاص بمقاصد السور
excel_file = "تفاصيل مقاصدمن السور بالربط ما بين السور و المجموعات الثمانية.xlsx"
print(f"📖 جاري قراءة الملف: {excel_file} ...")
df = pd.read_excel(excel_file, sheet_name="Sheet1")

print(f"✅ تم قراءة {len(df)} صفاً (سورة) بنجاح من الملف.")

# تجهيز البيانات للإدخال
records = []
for _, row in df.iterrows():
    record = {
        "surah_number": int(row["م"]),
        "surah_name": str(row["إسم السورة"]).strip(),
        "group_id": int(row["كود المجموعة"]),
        "surah_objective": str(row["تفاصيل مقاصد المجموعات الثمانى من السور"]).strip(),
    }
    records.append(record)

try:
    # إدخال السجلات إلى جدول surah_objectives
    response = supabase.table("surah_objectives").insert(records).execute()
    print(
        f"🎉 تم بنجاح رفع جميع مقاصد السور ({len(records)} سورة) إلى جدول"
        " surah_objectives في Supabase!"
    )
except Exception as e:
    print(f"❌ حدث خطأ أثناء رفع البيانات: {e}")
