import os
import re
import io
import pandas as pd
import streamlit as st
from supabase import create_client, Client


# ==========================================
# 1. إعدادات الاتصال المركزي بـ Supabase
# ==========================================
@st.cache_resource
def init_supabase() -> Client:
    """إنشاء وتشغيل اتصال مركزي موحد مع قاعدة بيانات Supabase"""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url:
        try:
            url = st.secrets.get("SUPABASE_URL", "")
            key = st.secrets.get("SUPABASE_KEY", "")
        except Exception:
            pass

    if not url or not key:
        st.error(
            "❌ خطأ حرج: لم يتم العثور على مفاتيح الاتصال بـ Supabase في الأسرار أو البيئة."
        )
        st.stop()

    return create_client(url, key)


supabase = init_supabase()


# ==========================================
# 2. دوال معالجة النصوص واللغويات (Helper Functions)
# ==========================================
def normalize_arabic(text: str) -> str:
    """توحيد شامل للهمزات والياءات وإزالة التشكيل والعلامات القرآنية للبحث الدقيق"""
    if not isinstance(text, str) or not text:
        return ""
    text = re.sub(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]", "", text)
    text = re.sub(r"[إأآٱ]", "ا", text)
    text = re.sub(r"[ىي]", "ي", text)
    return text.strip()


def is_exact_word_match(query: str, plain_txt: str, uthmani_txt: str) -> bool:
    """التحقق من الكلمة المستقلة أو العبارة المتصلة"""
    norm_query = normalize_arabic(query)
    norm_plain = normalize_arabic(plain_txt)
    norm_uthmani = normalize_arabic(uthmani_txt)

    if " " in norm_query:
        return (norm_query in norm_plain) or (norm_query in norm_uthmani)
    else:
        words_plain = re.findall(r"[\u0600-\u06FF]+", norm_plain)
        words_uthmani = re.findall(r"[\u0600-\u06FF]+", norm_uthmani)
        return (norm_query in words_plain) or (norm_query in words_uthmani)


# ==========================================
# 3. دوال البحث والتحليل المستقرة (الاعتماد على الجدول الأصلي)
# ==========================================
def search_ayah_group_relations_stable(search_term: str) -> list:
    """البحث المستقر والمباشر في جدول ayah_group_relations الأصلي"""
    try:
        if not search_term:
            return []
        raw_query = search_term.strip()
        norm_target = normalize_arabic(raw_query)

        # 1. البحث المباشر بالتطابق التام للكلمة
        resp = (
            supabase.table("ayah_group_relations")
            .select("*")
            .eq("topic_or_keyword", raw_query)
            .execute()
        )
        results = resp.data if resp.data else []

        if not results:
            # 2. البحث الشامل في حال كانت عبارة أو جزئية
            resp_all = (
                supabase.table("ayah_group_relations")
                .select("*")
                .range(0, 9999)
                .execute()
            )
            all_data = resp_all.data if resp_all.data else []
            for r in all_data:
                w = str(r.get("topic_or_keyword", "")).strip()
                norm_w = normalize_arabic(w)
                if " " in raw_query:
                    if norm_target in norm_w:
                        results.append(r)
                else:
                    words_in_w = re.findall(r"[\u0600-\u06FF]+", norm_w)
                    if norm_target in words_in_w or norm_target == norm_w:
                        results.append(r)
        return results
    except Exception as e:
        st.error(f"❌ خطأ في بحث الحصر: {e}")
        return []


def search_full_quran_stable(search_term: str) -> list:
    """البحث المستقر في full_quran باستخدام plain_ayah_text لتجاوز التشكيل"""
    try:
        if not search_term:
            return []
        raw_query = search_term.strip()
        norm_target = normalize_arabic(raw_query)

        if " " in raw_query:
            quran_res = (
                supabase.table("full_quran")
                .select("*")
                .ilike("plain_ayah_text", f"%{raw_query}%")
                .execute()
            )
        else:
            variants = {raw_query, norm_target}
            if norm_target.endswith("ت"):
                variants.add(norm_target[:-1] + "ة")
            elif norm_target.endswith("ة"):
                variants.add(norm_target[:-1] + "ت")

            or_conditions = [f"plain_ayah_text.ilike.%{v}%" for v in variants if v]
            quran_res = (
                supabase.table("full_quran")
                .select("*")
                .or_(",".join(or_conditions))
                .execute()
            )

        raw_data = quran_res.data if quran_res.data else []
        matched_verses = []
        for q in raw_data:
            plain_txt = q.get("plain_ayah_text", "")
            uthmani_txt = q.get("ayah_text", "")
            if " " in raw_query:
                if raw_query in plain_txt or norm_target in normalize_arabic(plain_txt):
                    matched_verses.append(q)
            else:
                if is_exact_word_match(raw_query, plain_txt, uthmani_txt):
                    matched_verses.append(q)

        return sorted(
            matched_verses,
            key=lambda x: (x.get("surah_number", 0), x.get("ayah_number", 0)),
        )
    except Exception as e:
        st.error(f"❌ خطأ في بحث المصحف: {e}")
        return []


# ==========================================
# 4. دوال مساعدة عامة
# ==========================================
def get_or_create_word_code(keyword):
    """التحقق هل الكلمة مسجلة مسبقاً لجلب الـ word_code الخاص بها، أو إنشاء جديد"""
    try:
        res = (
            supabase.table("ayah_group_relations")
            .select("word_code")
            .eq("topic_or_keyword", keyword)
            .limit(1)
            .execute()
        )
        data = res.data
        if data and len(data) > 0 and data[0].get("word_code"):
            return int(data[0].get("word_code"))

        res_max = (
            supabase.table("ayah_group_relations")
            .select("word_code")
            .order("word_code", desc=True)
            .limit(1)
            .execute()
        )
        max_data = res_max.data
        if max_data and len(max_data) > 0:
            max_code = max_data[0].get("word_code", 0)
            return int(max_code) + 1
    except Exception:
        pass
    return 1


def convert_df_to_excel(
    df: pd.DataFrame, sheet_name: str = "التقرير_التحليلي"
) -> bytes:
    """دالة مركزية لتصدير أي DataFrame إلى ملف Excel احترافي"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()


def clean_dataframe_for_display(df: pd.DataFrame) -> pd.DataFrame:
    """دالة مركزية لتنظيف أي DataFrame من الأعمدة التقنية الخلفية غير الضرورية للباحث مثل created_at"""
    if df is None or df.empty:
        return df

    unwanted_columns = ["created_at", "updated_at", "id"]
    df_cleaned = df.drop(
        columns=[col for col in unwanted_columns if col in df.columns], errors="ignore"
    )
    return df_cleaned


@st.cache_data(ttl=3600)
def fetch_all_supabase_rows(
    table_name: str,
    select_cols: str = "*",
    order_col: str = "id",
    batch_size: int = 1000,
) -> list:
    """
    جلب جميع الصفوف من أي جدول أو View في Supabase بنظام الدفعات (Pagination)
    لتجاوز حد الـ 1000 صف الافتراضي في واجهة PostgREST.
    """
    all_rows = []
    offset = 0

    while True:
        res = (
            supabase.table(table_name)
            .select(select_cols)
            .order(order_col)
            .range(offset, offset + batch_size - 1)
            .execute()
        )
        batch = res.data if res.data else []
        all_rows.extend(batch)
        if len(batch) < batch_size:
            break
        offset += batch_size

    return all_rows


# ==========================================
# 5. التمييز البصري للرسم العثماني والأرشفة التدبرية
# ==========================================
def highlight_uthmani_keyword(uthmani_text: str, query: str) -> str:
    """
    تمييز الكلمة أو العبارة المبحوث عنها ومشتقاتها العثمانية داخل نص الآية
    بصيغة Streamlit Markdown الأصلية (:blue[**«الكلمة»**]) بدقة لغوية تمنع
    تلوين الكلمات القصيرة المتداخلة عشوائياً (مثل تداخل 'ما' داخل 'الماء' أو 'لما').
    """
    if not uthmani_text or not query or not query.strip():
        return uthmani_text or ""

    def _deep_norm(s: str) -> str:
        s_clean = str(s).replace("آ", "اا")
        base = normalize_arabic(s_clean)
        return re.sub(r"[ءئؤ]", "ا", base)

    norm_q = _deep_norm(query.strip())
    if not norm_q:
        return uthmani_text

    # استبعاد حروف الجر/النفي المكونة من حرفين من التطابق الجزئي داخل كلمات أخرى
    stop_short_words = {
        "ما",
        "لا",
        "في",
        "من",
        "عن",
        "ان",
        "او",
        "قد",
        "بل",
        "اذ",
        "يا",
    }

    q_words = [w for w in re.findall(r"[\u0600-\u06FF]+", norm_q) if len(w) >= 2]
    exact_short_words = {w for w in q_words if w in stop_short_words}
    core_variants = {w for w in q_words if w not in stop_short_words}

    if len(norm_q) >= 3 and norm_q not in stop_short_words:
        core_variants.add(norm_q)

    # معالجة صيغ النداء العثماني المتصل مثل: يَا أَيُّهَا -> يايها
    if "يا" in q_words and "ايها" in q_words:
        core_variants.add("يايها")

    # معالجة صيغ أفعل التفضيل/الماضي مثل: أظلم (اظلم) -> يشمل جذر (ظلم)
    for w in list(core_variants):
        if len(w) >= 4 and w.startswith("ا"):
            core_variants.add(w[1:])

    tokens = re.split(r"(\s+)", str(uthmani_text))
    highlighted_tokens = []

    for tok in tokens:
        if not tok.strip():
            highlighted_tokens.append(tok)
            continue

        norm_tok = _deep_norm(tok)
        clean_tok_letters = re.sub(r"[^\u0600-\u06FF]", "", norm_tok)

        # 1. الكلمات القصيرة جداً (مثل: ما، لا، في) تُطابق فقط ككلمة مستقلة أو مسبوقة بواو/فاء (وما، فلا)
        short_matched = any(
            clean_tok_letters == sw or clean_tok_letters in {f"و{sw}", f"ف{sw}"}
            for sw in exact_short_words
        )

        # 2. الكلمات الأساسية (3 أحرف فأكثر) تُطابق الكلمة ومشتقاتها وسوابقها العثمانية
        core_matched = any(v in clean_tok_letters for v in core_variants if len(v) >= 3)

        if short_matched or core_matched:
            highlighted_tokens.append(f":blue[**«{tok}»**]")
        else:
            highlighted_tokens.append(tok)

    return "".join(highlighted_tokens)


def save_ayah_to_memorization_archive(
    surah_serial: int,
    surah_name: str,
    ayah_number: int,
    ayah_text: str,
    status_label: str = "تدبر مقاصدي - المجموعات الثمانية",
) -> tuple[bool, str]:
    """
    حفظ آية في جدول user_memorization_archive (الصفحة 8) مع منع التكرار.
    تُرجع (True/False, رسالة توضيحية).
    """
    try:
        existing = (
            supabase.table("user_memorization_archive")
            .select("id, memorization_status")
            .eq("surah_serial", int(surah_serial))
            .eq("ayah_number", int(ayah_number))
            .limit(1)
            .execute()
        )
        if existing.data and len(existing.data) > 0:
            return (
                False,
                f"ℹ️ الآية ({surah_name}: {ayah_number}) مسجلة مسبقاً في أرشيفك بحالة: «{existing.data[0].get('memorization_status', '')}».",
            )

        payload = {
            "surah_serial": int(surah_serial),
            "surah_name": str(surah_name).strip(),
            "ayah_number": int(ayah_number),
            "ayah_text": str(ayah_text).strip(),
            "memorization_status": str(status_label).strip(),
        }
        supabase.table("user_memorization_archive").insert(payload).execute()
        return (
            True,
            f"✅ تم ترحيل الآية ({surah_name}: {ayah_number}) إلى أرشيف الحفظ والتدبر (الصفحة 8) بنجاح!",
        )
    except Exception as e:
        return (False, f"❌ تعذّر الحفظ في الأرشيف: {e}")


def save_keyword_bulk_to_relations(
    keyword: str,
    ayah_records: list[dict],
    surah_to_group_map: dict,
    custom_note: str = "",
) -> tuple[bool, str]:
    """
    حفظ كلمة أو مفهوم جديد (أو آيات إضافية لمفهوم قائم) دفعة واحدة في جدول ayah_group_relations
    بمطابقة كاملة لجميع الحقول الإلزامية في الجدول (بما في ذلك half_code و quarter_code و ayah_text و surah_serial).
    """
    clean_kw = str(keyword).strip()
    if not clean_kw or not ayah_records:
        return (False, "⚠️ لا توجد آيات صالحة للحفظ.")

    try:
        word_code = get_or_create_word_code(clean_kw)

        # 1. جلب السجلات المسجلة مسبقاً لهذا المفهوم لمنع التكرار
        existing_res = (
            supabase.table("ayah_group_relations")
            .select("surah_serial, ayah_number")
            .eq("topic_or_keyword", clean_kw)
            .range(0, 9999)
            .execute()
        )
        existing_pairs = {
            (int(r["surah_serial"]), int(r["ayah_number"]))
            for r in (existing_res.data or [])
            if r.get("surah_serial") is not None and r.get("ayah_number") is not None
        }

        # 2. جلب أكواد النصف والربع والمجموعة من السجلات المرجعية في قاعدة البيانات لكل سورة
        surah_codes_res = (
            supabase.table("ayah_group_relations")
            .select("surah_serial, group_id, half_code, quarter_code")
            .range(0, 9999)
            .execute()
        )
        surah_codes_map = {}
        for sc in surah_codes_res.data or []:
            s_ser = sc.get("surah_serial")
            if s_ser is not None and int(s_ser) not in surah_codes_map:
                surah_codes_map[int(s_ser)] = {
                    "group_id": int(sc.get("group_id") or 1),
                    "half_code": int(sc.get("half_code") or 0),
                    "quarter_code": int(sc.get("quarter_code") or 0),
                }

        norm_kw = normalize_arabic(clean_kw)
        payload_rows = []

        for rec in ayah_records:
            s_num = int(rec["surah_number"])
            s_name = str(rec.get("surah_name", "")).strip()
            a_num = int(rec["ayah_number"])
            raw_ayah_text = str(
                rec.get("ayah_text") or rec.get("plain_ayah_text") or ""
            ).strip()

            if (s_num, a_num) in existing_pairs or not raw_ayah_text:
                continue

            g_id_map, g_obj = surah_to_group_map.get(s_num, (1, ""))
            codes_info = surah_codes_map.get(s_num, {})
            final_group_id = int(codes_info.get("group_id") or g_id_map or 1)
            half_c = int(codes_info.get("half_code", 0))
            quarter_c = int(codes_info.get("quarter_code", 0))

            plain_txt = normalize_arabic(
                str(rec.get("plain_ayah_text") or raw_ayah_text)
            )
            freq_cnt = plain_txt.split().count(norm_kw) if norm_kw else 1
            freq_cnt = max(1, int(freq_cnt))

            note_val = str(custom_note).strip() if str(custom_note).strip() else g_obj

            payload_rows.append(
                {
                    "word_code": int(word_code),
                    "topic_or_keyword": clean_kw,
                    "group_id": final_group_id,
                    "surah_serial": s_num,
                    "surah_name": s_name,
                    "ayah_number": a_num,
                    "ayah_text": raw_ayah_text,
                    "notes": note_val,
                    "half_code": half_c,
                    "quarter_code": quarter_c,
                    "frequency_count": freq_cnt,
                }
            )
            existing_pairs.add((s_num, a_num))

        if not payload_rows:
            return (
                False,
                f"ℹ️ جميع الآيات المطابقة للمفهوم «{clean_kw}» مسجلة مسبقاً في ملف الحصر.",
            )

        batch_size = 200
        for i in range(0, len(payload_rows), batch_size):
            supabase.table("ayah_group_relations").insert(
                payload_rows[i : i + batch_size]
            ).execute()

        return (
            True,
            f"✅ تم اعتماد وحفظ المفهوم «{clean_kw}» بعدد ({len(payload_rows)}) آية جديدة في ملف الحصر بنجاح (كود المفهوم: {word_code})!",
        )
    except Exception as e:
        return (False, f"❌ تعذّر حفظ المفهوم في قاعدة البيانات: {e}")


# ==========================================
# 6. خدمات الصوتيات وتنقية العرض وتأسيس مستندات Word (RTL)
# ==========================================
def clean_arabic_display(text: str) -> str:
    """تصحيح أخطاء التشكيل الطباعية الشائعة مثل (للهّ / الل هّ) أثناء العرض"""
    if not text:
        return ""
    s = str(text)
    s = re.sub(r"الل\s+هّ?", "الله", s)
    s = s.replace("للهّ", "لله").replace("اللهّ", "الله")
    return s.strip()


def get_everyayah_audio_url(
    surah_num: int, ayah_num: int, reciter: str = "MaherAlMuaiqly128kbps"
) -> str:
    """بناء رابط التلاوة الصوتية عبر EveryAyah (الافتراضي: الشيخ ماهر المعيقلي)"""
    return f"https://everyayah.com/data/{reciter}/{int(surah_num):03d}{int(ayah_num):03d}.mp3"


def init_rtl_docx():
    """إنشاء مستند Word جديد مع دوال مساعدة جاهزة للكتابة العربية من اليمين لليسار (RTL)"""
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    doc = Document()

    def set_p_rtl(paragraph, align=WD_ALIGN_PARAGRAPH.RIGHT):
        paragraph.alignment = align
        pPr = paragraph._p.get_or_add_pPr()
        pPr.append(OxmlElement("w:bidi"))

    def set_tbl_rtl(table):
        tblPr = table._tbl.tblPr
        tblPr.append(OxmlElement("w:bidiVisual"))

    def add_run_rtl(
        paragraph,
        text: str,
        font_name: str = "Arial",
        size_pt: int = 12,
        bold: bool = False,
        color_rgb=None,
    ):
        run = paragraph.add_run(str(text))
        run.font.name = font_name
        run.font.size = Pt(size_pt)
        run.bold = bold
        if color_rgb:
            run.font.color.rgb = RGBColor(*color_rgb)
        rPr = run._r.get_or_add_rPr()
        rFonts = OxmlElement("w:rFonts")
        rFonts.set(qn("w:cs"), font_name)
        rPr.append(rFonts)
        rPr.append(OxmlElement("w:rtl"))
        return run

    return doc, set_p_rtl, set_tbl_rtl, add_run_rtl, WD_ALIGN_PARAGRAPH
