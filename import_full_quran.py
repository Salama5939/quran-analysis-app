import os
import pandas as pd
from supabase import Client, create_client

# ==========================================
# 1. إعدادات الاتصال بـ Supabase
# ==========================================
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url:
    try:
        import streamlit as st

        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "")
    except Exception:
        pass

if not url or not key:
    print("❌ خطأ: لم يتم العثور على مفاتيح الاتصال بـ Supabase.")
    exit(1)

supabase: Client = create_client(url, key)

# ==========================================
# 2. قراءة ملف الإكسل المحدث الكامل
# ==========================================
EXCEL_FILENAME = "Full_quran.xlsx"

if not os.path.exists(EXCEL_FILENAME):
    print(f"❌ خطأ: لم يتم العثور على ملف الإكسل '{EXCEL_FILENAME}' في المجلد.")
    exit(1)

print(f"📂 جاري قراءة ملف الإكسل '{EXCEL_FILENAME}'...")
df = pd.read_excel(EXCEL_FILENAME, sheet_name=0)

# تنظيف أسماء الأعمدة والفراغات
df.columns = [str(c).strip() for c in df.columns]
df = df.where(pd.notnull(df), None)

print(f"📊 تم قراءة عدد {len(df)} صف بنجاح من الملف.")

# ==========================================
# 3. تفريغ جدول full_quran تماماً من السجلات القديمة
# ==========================================
print("🗑️ جاري تفريغ ومحو جميع السجلات القديمة من جدول `full_quran` في" " Supabase...")
try:
    supabase.table("full_quran").delete().gt("id", 0).execute()
    print("✅ تم تفريغ الجدول بنجاح تام.")
except Exception as e:
    print(f"⚠️ تنبيه أثناء الحذف: {e}")

# ==========================================
# 4. إعداد وتجهيز البيانات الجديدة (بما فيها plain_ayah_text)
# ==========================================
records = []
for _, row in df.iterrows():
    record = {
        "id": int(row["id"]) if row.get("id") is not None else None,
        "surah_number": (
            int(row["surah_number"]) if row.get("surah_number") is not None else 0
        ),
        "surah_name": (
            str(row["surah_name"]).strip() if row.get("surah_name") is not None else ""
        ),
        "ayah_number": (
            int(row["ayah_number"]) if row.get("ayah_number") is not None else 0
        ),
        "ayah_text": (
            str(row["ayah_text"]).strip() if row.get("ayah_text") is not None else ""
        ),
        "plain_ayah_text": (
            str(row["plain_ayah_text"]).strip()
            if row.get("plain_ayah_text") is not None
            else ""
        ),
        "juz": int(row["juz"]) if row.get("juz") is not None else 1,
        "page_number": (
            int(row["page_number"]) if row.get("page_number") is not None else 1
        ),
    }
    records.append(record)

# ==========================================
# 5. عملية الرفع على دفعات نظيفة (Batch Insert)
# ==========================================
print(
    "🚀 جاري البدء في إدخال البيانات النقية مع العمود الصافي إلى جدول"
    " `full_quran`..."
)

batch_size = 500
total_records = len(records)

for i in range(0, total_records, batch_size):
    batch = records[i : i + batch_size]
    try:
        response = supabase.table("full_quran").insert(batch).execute()
        print(
            f"✅ تم بنجاح إدخال الدفعة من السجل {i + 1} إلى"
            f" {min(i + batch_size, total_records)}"
        )
    except Exception as e:
        print(f"❌ حدث خطأ أثناء إدخال الدفعة عند السجل {i + 1}: {e}")

print("🎉 تمت عملية استيراد وتحديث جدول المصحف الشريف بالكامل بنجاح تام!")
