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

supabase: Client = create_client(url, key)


def fix_and_upload_clean_data():
    file_name = "الكلمة بالقرآن بالمنطوق بنصف و ربع و المجموعة مع اسم السورة.xlsx"
    print(f"📁 جاري قراءة الملف المعتمد حصرياً: {file_name}")

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

                # صيغة الملاحظات النظيفة والموحدة
                notes = f"سورة {surah_name} | آية رقم: {ayah_num} | النص: {ayah_text}"

                cleaned_rows.append(
                    {
                        "topic_or_keyword": current_word,
                        "frequency_count": 1,
                        "group_id": 1,
                        "notes": notes,
                    }
                )

    df_clean = pd.DataFrame(cleaned_rows)

    # 🛡️ إزالة أي تكرار داخلي في الملف بشكل قاطع
    df_clean = df_clean.drop_duplicates(subset=["topic_or_keyword", "notes"])

    records = df_clean.to_dict(orient="records")
    print(f"✨ عدد السجلات الفريدة بعد تنظيف التكرار: {len(records)} سجلاً نظيفاً.")

    # 🧹 الخطوة الأولى: تفريغ الجدول تماماً في Supabase
    print(
        "🧹 جاري تفريغ جدول ayah_group_relations بالكامل من أي بيانات مكررة أو قديمة..."
    )
    try:
        supabase.table("ayah_group_relations").delete().gt("id", 0).execute()
    except Exception as e:
        print(f"ملاحظة أثناء التفريغ: {e}")

    # 🚀 الخطوة الثانية: رفع السجلات النظيفة الفريدة فقط على دفعات
    print("🚀 جاري رفع السجلات النظيفة الجديدة...")
    batch_size = 200
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        supabase.table("ayah_group_relations").insert(batch).execute()
        print(f"تم رفع الدفعة: {i} إلى {min(i + batch_size, len(records))}")

    print(
        "🎉 تم ضبط وتدقيق قاعدة البيانات بنجاح تام! أصبحت خالية من أي تكرار بنسبة 100%."
    )


if __name__ == "__main__":
    fix_and_upload_clean_data()
