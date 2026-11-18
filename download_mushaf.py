import os
import requests


def download_mushaf_pages():
    output_dir = "mushaf_pages"
    os.makedirs(output_dir, exist_ok=True)

    # نموذج رابط مباشر لصور المصحف (مثال من مستودعات المطورين المفتوحة)
    base_url = "https://raw.githubusercontent.com/quran/quran_android/master/app/src/main/assets/pages/page{}.png"

    print("جاري بدء تحميل صفحات المصحف الشريف (604 صفحة)...")

    for page_num in range(1, 605):
        # تنسيق الرقم ليصبح من ثلاث منازل مثل 001.png أو عبر رقم الصفحة المباشر حسب المصدر
        file_name = f"{page_num:03d}.png"
        file_path = os.path.join(output_dir, file_name)

        if not os.path.exists(file_path):
            # رابط افتراضي أو معدل حسب الدقة المطلوبة
            url = f"https://quranimages.b-cdn.net/page{page_num:03d}.png"  # أو المصدر البديل
            # للتبسيط يمكن استخدام روابط GitHub الرسمية للصور
            formatted_url = f"https://raw.githubusercontent.com/quran/quran_android/v3.6.3/res/drawable-hdpi/page{page_num}.png"  # مثال

            try:
                # محاولة الجلب
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    print(f"تم تحميل الصفحة: {file_name}")
                else:
                    print(
                        f"تعذر تحميل الصفحة {page_num}, رمز الاستجابة: {response.status_code}"
                    )
            except Exception as e:
                print(f"خطأ في تحميل الصفحة {page_num}: {e}")
        else:
            print(f"الصفحة موجودة مسبقاً: {file_name}")


if __name__ == "__main__":
    download_mushaf_pages()
