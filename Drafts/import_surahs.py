import os
import pandas as pd
from supabase import Client, create_client

# الاتصال بقاعدة بيانات Supabase
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
    exit()

supabase: Client = create_client(url, key)

# قراءة ملف الإكسل المحلي
EXCEL_FILE = "Relational TBL between Start and End Pages for each Surah.xlsx"

if os.path.exists(EXCEL_FILE):
    df = pd.read_excel(EXCEL_FILE, sheet_name=0)
    df.columns = [str(c).strip() for c in df.columns]

    records = []
    for surah_serial, (_, row) in enumerate(df.iterrows(), start=1):
        surah_name = str(row["إسم السورة"]).strip()
        start_page = int(float(str(row["رقم صفحة البداية للسورة"])))
        end_page = int(float(str(row["رقم صفحة النهاية للسورة"])))

        records.append(
            {
                "surah_serial": surah_serial,
                "surah_name": surah_name,
                "start_page": start_page,
                "end_page": end_page,
            }
        )

    # إدخال السور دفعة واحدة في Supabase
    try:
        response = supabase.table("surah_pages").insert(records).execute()
        print("✅ تم رفع بيانات جميع السور وصفحاتها إلى Supabase بنجاح تام!")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء الرفع: {e}")
else:
    print(f"❌ لم يتم العثور على ملف الإكسل '{EXCEL_FILE}'.")
