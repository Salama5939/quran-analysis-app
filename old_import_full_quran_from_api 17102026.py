import os
import requests
import streamlit as st
from supabase import Client, create_client

# الاتصال بقاعدة البيانات باستخدام أسرار secrets.toml
url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("❌ خطأ: لم يتم العثور على مفاتيح الاتصال بـ Supabase.")
    exit()

supabase: Client = create_client(url, key)


def import_quran_verses():
    print("جاري جلب الآيات القرآنية المدققة من المصدر المعتمد...")

    try:
        # استخدام API موثق لجلب القرآن الكريم كاملاً بالرسم العثماني/الإملائي المعتمد
        response = requests.get(
            "http://api.alquran.cloud/v1/quran/quran-uthmani"
        )  # أو quran-simple
        data = response.json()

        if data.get("code") == 200:
            surahs_list = data["data"]["surahs"]
            all_verses = []

            for surah in surahs_list:
                surah_num = surah["number"]
                surah_name = surah["name"]
                # تنظيف اسم السورة (إزالة كلمة سورة إن وجدت لتكون مطابقة لجدول السور)
                for ayah in surah["ayahs"]:
                    verse_record = {
                        "surah_number": surah_num,
                        "surah_name": surah["englishName"],  # أو الاسم العربي
                        "ayah_number": ayah["numberInSurah"],
                        "ayah_text": ayah["text"],
                        "juz": ayah["juz"],
                        "page_number": ayah["page"],
                    }
                    all_verses.append(verse_record)

            # للحصول على الاسم العربي الدقيق للسور من جدول surahs الموجود لديك مسبقاً
            surah_names_map = {}
            res_surahs = supabase.table("surahs").select("*").execute()
            if res_surahs.data:
                for s in res_surahs.data:
                    surah_names_map[s["surah_number"]] = s["name_arabic"]

            # تحديث الاسم العربي لكل آية بناءً على جدول السور المعتمد لديك
            for v in all_verses:
                s_num = v["surah_number"]
                if s_num in surah_names_map:
                    v["surah_name"] = surah_names_map[s_num]

            print(f"✅ تم تجهيز {len(all_verses)} آية. جاري رفعها إلى Supabase...")

            # رفع البيانات على دفعات (Batch Insert) لتجنب الضغط
            batch_size = 200
            for i in range(0, len(all_verses), batch_size):
                batch = all_verses[i : i + batch_size]
                supabase.table("full_quran").insert(batch).execute()
                print(
                    f"تم رفع الدفعة من الآيات: {i} إلى"
                    f" {min(i + batch_size, len(all_verses))}"
                )

            print(
                "🎉 مبروك! تم رفع المصحف الشامل كاملأً (6236 آية) إلى جدول full_quran"
                " بنجاح."
            )

        else:
            print("❌ فشل في جلب البيانات من المصدر.")

    except Exception as e:
        print(f"❌ حدث خطأ أثناء جلب أو رفع آيات القرآن: {e}")


if __name__ == "__main__":
    import_quran_verses()
