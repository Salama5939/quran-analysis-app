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

    # قائمة الأعمدة التقنية المراد إخفاؤها تلقائياً أينما وجدت
    unwanted_columns = ["created_at", "updated_at", "id"]

    # إسقاط الأعمدة إن وجدت في الجدول
    df_cleaned = df.drop(
        columns=[col for col in unwanted_columns if col in df.columns], errors="ignore"
    )
    return df_cleaned
