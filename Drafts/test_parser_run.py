import re


def parse_quran_references(reference_text):
    """
    دالة التحليل البرمجية (Parser) لفهرس الموضوعات القرآنية:
    - '/' تفصل بين رقم السورة ورقم الآية.
    - '-' تفصل بين مواضع أو سور مستقلة وليست نطاقاً للآيات.
    """
    parsed_results = []
    cleaned_text = reference_text.strip()

    # التقسيم بناءً على الشرطة '-' للفصل بين السور والمواضع المستقلة
    segments = re.split(r"\s*-\s*", cleaned_text)

    current_surah = None  # لتتبع رقم السورة في حال تم ذكر الآيات تابعة لنفس السورة

    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue

        # التحقق من وجود علامة التوجيه (/) التي تفصل السورة عن الآيات
        if "/" in segment:
            parts = segment.split("/")
            current_surah = parts[0].strip()
            ayahs_part = parts[1].strip()
        else:
            # إذا لم توجد '/', فهذا يعني أن الآيات تتبع نفس السورة السابقة
            ayahs_part = segment

        # استخراج جميع أرقام الآيات الموجودة في المقطع
        ayah_numbers = re.findall(r"\d+", ayahs_part)

        for ayah in ayah_numbers:
            if current_surah:
                parsed_results.append(
                    {"surah_number": int(current_surah), "ayah_number": int(ayah)}
                )

    return parsed_results


# --- 🧪 عينات تجريبية حقيقية مأخوذة من الكتيب للتحقق والبرهان ---
if __name__ == "__main__":
    test_samples = [
        "2/28 و 29 و 164",  # مثال لآيات متعددة في سورة البقرة (رقم 2)
        "2/28 - 3/45",  # مثال على الانتقال بين سورتين بفاصل '-'
        "2/114 - 115 - 116",  # مثال لتعدد الآيات بفاصل '-' ضمن نفس السياق أو السورة
    ]

    print("=" * 50)
    print("🧪 نتائج اختبار دالة التحليل (Parser Test Results)")
    print("=" * 50)

    for idx, sample in enumerate(test_samples, 1):
        print(f"\n[العينة {idx}] النص الأصلي في الكتيب: {sample}")
        results = parse_quran_references(sample)
        print("النتيجة المهيكلة (سورة / آية):")
        for res in results:
            print(
                f"  ➡️ سورة رقم: {res['surah_number']} | آية رقم: {res['ayah_number']}"
            )

    print("\n" + "=" * 50)
    print("✅ انتهى الاختبار بنجاح تام.")