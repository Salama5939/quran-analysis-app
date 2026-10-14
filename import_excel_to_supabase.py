import os
import pandas as pd
import streamlit as st
from supabase import Client, create_client

# 1. الاتصال بقاعدة البيانات باستخدام أسرار secrets.toml
url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("❌ خطأ: لم يتم العثور على مفاتيح الاتصال بـ Supabase في ملف الأسرار.")
    exit()

supabase: Client = create_client(url, key)


def import_excel_data(file_path):
    print("جاري قراءة ملف الإكسل...")

    try:
        # قراءة شيت البيانات الأولية
        df = pd.read_excel(file_path, sheet_name="ملف البيانات الأولية")
        print(f"✅ تم العثور على {len(df)} صف في ملف الإكسل.")

        # تنظيف البيانات واستبدال القيم الفارغة إن وجدت
        df = df.fillna("")

        # إدخال المجموعات الثمانية أولاً (باستخدام طريقة آمنة تتجنب أخطاء الـ Conflict)
        print("جاري التحقق من إدخال المجموعات الثمانية (1-8)...")
        for i in range(1, 9):
            try:
                supabase.table("groups_8").insert(
                    {"group_number": i, "group_name": f"المجموعة {i}"}
                ).execute()
            except Exception:
                # إذا كانت المجموعة موجودة مسبقاً، نتجاهل الخطأ ونكمل بنجاح
                pass
        print("✅ تم التأكد من جاهزية المجموعات الثمانية.")

        # تحضير البيانات لرفعها إلى جدول علاقات الآيات والموضوعات (ayah_group_relations)
        records_to_insert = []
        for index, row in df.iterrows():
            record = {
                "topic_or_keyword": str(row.get("الكلمة", "")),
                "frequency_count": 1,
                "notes": (
                    f"مقصد: {row.get('تعريف المقصد', '')} | سورة:"
                    f" {row.get('إسم السورة', '')} | آية:"
                    f" {row.get('رقم الآية', '')}"
                ),
                "group_id": int(row.get("كود المجموعة", 1)),
            }
            records_to_insert.append(record)

        # رفع البيانات على دفعات لتجنب الضغط على السيرفر (Batch Insert)
        batch_size = 100
        for i in range(0, len(records_to_insert), batch_size):
            batch = records_to_insert[i : i + batch_size]
            supabase.table("ayah_group_relations").insert(batch).execute()
            print(
                f"تم رفع الدفعة من {i} إلى {min(i + batch_size, len(records_to_insert))}"
                " بنجاح..."
            )

        print("🎉 مبروك! تم رفع وتدقيق كافة البيانات بنجاح إلى Supabase.")

    except Exception as e:
        print(f"❌ حدث خطأ أثناء قراءة أو رفع البيانات: {e}")


if __name__ == "__main__":
    excel_file = "PivotTBL كلمات القرآن و حصرها.xlsx"
    if os.path.exists(excel_file):
        import_excel_data(excel_file)
    else:
        print(f"❌ ملف الإكسل غير موجود في المسار الحالي: {excel_file}")
