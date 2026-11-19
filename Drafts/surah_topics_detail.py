import os
import re
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

# 1. تحميل متغيرات البيئة (SUPABASE_URL و SUPABASE_KEY)
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "❌ تأكد من وجود SUPABASE_URL و SUPABASE_KEY في ملف .env أو متغيرات البيئة."
    )

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def find_column(df: pd.DataFrame, keywords: list[str]) -> str | None:
    """بحث مرن عن اسم العمود بغض النظر عن الهمزات أو المسافات الزائدة."""
    normalized_cols = {
        col: re.sub(r"\s+", " ", str(col).replace("إ", "ا").replace("أ", "ا")).strip()
        for col in df.columns
    }
    for kw in keywords:
        norm_kw = re.sub(r"\s+", " ", kw.replace("إ", "ا").replace("أ", "ا")).strip()
        for orig_col, norm_col in normalized_cols.items():
            if norm_kw in norm_col:
                return orig_col
    return None


def migrate_surah_topics_detail(excel_path: str = "موضوعات كل سورة بالقرآن_2.xlsx"):
    if not os.path.exists(excel_path):
        fallback_path = "موضوعات كل سورة بالقرآن.xlsx"
        if os.path.exists(fallback_path):
            excel_path = fallback_path
        else:
            raise FileNotFoundError(
                f"❌ لم يتم العثور على الملف: {excel_path} في مجلد المشروع الحالي."
            )

    print(f"📂 جاري قراءة الملف: {excel_path}")
    xls = pd.ExcelFile(excel_path)
    df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])

    col_surah_num = find_column(df, ["كود السورة", "رقم السورة", "surah_number"])
    col_surah_name = find_column(df, ["اسم السورة", "إسم السورة", "surah_name"])
    col_total_ayahs = find_column(df, ["عدد الآيات", "total_ayahs"])
    col_start_page = find_column(df, ["بداية السورة", "start_page", "رقم الصفحة"])
    col_half_code = find_column(df, ["كود النصف", "half_code"])
    col_quarter_code = find_column(df, ["كود الربع", "quarter_code"])
    col_group_id = find_column(df, ["كود المجموعة", "رقم المجموعة", "group_id"])
    col_detail = find_column(
        df, ["تفاصيل الموضوعات", "تفاصيل الموضوع", "topic_detail", "الموضوع"]
    )

    required = {
        "كود السورة": col_surah_num,
        "اسم السورة": col_surah_name,
        "تفاصيل الموضوعات": col_detail,
    }
    missing = [k for k, v in required.items() if v is None]
    if missing:
        raise KeyError(
            f"❌ الأعمدة التالية غير موجودة في الملف: {missing} | الأعمدة المتاحة: {df.columns.tolist()}"
        )

    # توضيح للمحلل الساكن أن الأعمدة الإلزامية متوفرة بعد التحقق أعلاه.
    assert col_surah_num is not None
    assert col_surah_name is not None
    assert col_detail is not None

    # تعبئة الحقول التعريفية للسورة في حال وجود سطر ناقص البيانات
    fill_cols = [
        c
        for c in [
            col_surah_num,
            col_surah_name,
            col_total_ayahs,
            col_start_page,
            col_half_code,
            col_quarter_code,
            col_group_id,
        ]
        if c is not None
    ]
    df[fill_cols] = df[fill_cols].ffill()

    # استبعاد الصفوف الخالية تماماً من نص الموضوع
    df = df[df[col_detail].notna() & (df[col_detail].astype(str).str.strip() != "")]

    records = []
    current_order = 1
    prev_surah = None

    for _, row in df.iterrows():
        surah_num = int(float(row[col_surah_num]))
        surah_name = str(row[col_surah_name]).strip()
        detail_text = str(row[col_detail]).strip()

        if surah_num != prev_surah:
            current_order = 1
            prev_surah = surah_num

        # استخراج ترتيب الموضوع إن بدأ برقم متبوع بشرطة أو نقطة (مثل "1-" أو "2.")
        match = re.match(r"^\s*(\d+)\s*[-–.]", detail_text)
        if match:
            topic_ord = int(match.group(1))
            current_order = topic_ord + 1
        else:
            topic_ord = current_order
            current_order += 1

        records.append(
            {
                "surah_number": surah_num,
                "surah_name": surah_name,
                "total_ayahs": (
                    int(float(row[col_total_ayahs]))
                    if col_total_ayahs and pd.notna(row[col_total_ayahs])
                    else None
                ),
                "start_page": (
                    int(float(row[col_start_page]))
                    if col_start_page and pd.notna(row[col_start_page])
                    else None
                ),
                "half_code": (
                    int(float(row[col_half_code]))
                    if col_half_code and pd.notna(row[col_half_code])
                    else None
                ),
                "quarter_code": (
                    int(float(row[col_quarter_code]))
                    if col_quarter_code and pd.notna(row[col_quarter_code])
                    else None
                ),
                "group_id": (
                    int(float(row[col_group_id]))
                    if col_group_id and pd.notna(row[col_group_id])
                    else None
                ),
                "topic_order": topic_ord,
                "topic_detail": detail_text,
            }
        )

    # حذف السجلات السابقة في الجدول إن وُجدت لمنع التكرار عند إعادة التشغيل
    supabase.table("surah_topics_detail").delete().neq("id", 0).execute()

    # إدراج البيانات على دفعات (100 سجل لكل دفعة)
    batch_size = 100
    for start_idx in range(0, len(records), batch_size):
        batch = records[start_idx : start_idx + batch_size]
        supabase.table("surah_topics_detail").insert(batch).execute()
        print(
            f"✅ تم إدراج الدفعة {(start_idx // batch_size) + 1} ({len(batch)} سجل)"
        )

    # تقرير تحقق نهائي من قاعدة البيانات
    verify_resp = (
        supabase.table("surah_topics_detail")
        .select("id, surah_number")
        .execute()
    )
    inserted_rows = verify_resp.data if verify_resp.data else []
    unique_surahs = {r["surah_number"] for r in inserted_rows}

    print("-" * 55)
    print(f"🎉 اكتمل الترحيل بنجاح إلى جدول surah_topics_detail!")
    print(f"📊 إجمالي السجلات المرحّلة في القاعدة: {len(inserted_rows)}")
    print(f"📖 إجمالي السور المغطاة: {len(unique_surahs)} سورة")
    print("-" * 55)


if __name__ == "__main__":
    migrate_surah_topics_detail()