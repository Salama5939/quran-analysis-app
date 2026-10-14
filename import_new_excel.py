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


def import_hierarchical_excel(file_path):
    print("جاري قراءة ومعالجة ملف الإكسل الجديد...")

    try:
        df = pd.read_excel(file_path)

        # ملء الفراغات في أعمدة الكلمة والكود بناءً على الهيكل المتدرج (Forward Fill)
        df["كود الكلمة"] = df["كود الكلمة"].ffill()
        df["الكلمة"] = df["الكلمة"].ffill()

        # استبعاد الصفوف الفارغة التي لا تحتوي على مسلسل سورة
        clean_df = df.dropna(subset=["مسلسل السورة"]).copy()
        print(f"✅ تم تنظيف البيانات وإعداد {len(clean_df)} سجلاً للرفع.")

        records_to_insert = []
        for _, row in clean_df.iterrows():
            # جلب البيانات وتنظيفها
            word_code = row.get("كود الكلمة", "")
            word_text = str(row.get("الكلمة", ""))
            surah_name = str(row.get("إسم السورة", ""))
            ayah_num = row.get("رقم الآية", 0)
            ayah_text = str(row.get("منطوق الآية", ""))

            record = {
                "topic_or_keyword": word_text,
                "frequency_count": 1,
                "notes": f"كود الكلمة: {word_code} | سورة: {surah_name} | آية: {ayah_num}",
                "group_id": 1,  # مجموعة افتراضية ويمكن تحديثها أو ربطها لاحقاً
            }

            # إذا كان جدولك في Supabase يحتوي على حقل لنص الآية أو ملاحظات، يتم دمجه هنا
            # سنضع منطوق الآية في الحقول المتاحة لضمان ظهورها عند البحث
            record["notes"] = (
                f"الكلمة: {word_text} | السورة: {surah_name} (آية {ayah_num})"
            )

            records_to_insert.append(record)

        # رفع البيانات على دفعات (Batch Insert) لتجنب الضغط
        batch_size = 100
        for i in range(0, len(records_to_insert), batch_size):
            batch = records_to_insert[i : i + batch_size]
            supabase.table("ayah_group_relations").insert(batch).execute()
            print(
                f"تم رفع الدفعة من {i} إلى {min(i + batch_size, len(records_to_insert))}"
                " بنجاح..."
            )

        print("🎉 مبروك! تم دمج ورفع بيانات الملف الجديد بنجاح إلى Supabase.")

    except Exception as e:
        print(f"❌ حدث خطأ أثناء معالجة أو رفع الملف: {e}")


if __name__ == "__main__":
    file_name = "الكلمة بالقرآن بالمنطوق بنصف و ربع و المجموعة مع اسم السورة.xlsx"
    if os.path.exists(file_name):
        import_hierarchical_excel(file_name)
    else:
        print(f"❌ الملف غير موجود في المسار الحالي: {file_name}")
