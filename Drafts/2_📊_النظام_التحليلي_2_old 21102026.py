import os
import re
import pandas as pd
import streamlit as st
from supabase import Client, create_client
import theme  # استدعاء ملف التنسيق المركزي

# ==========================================
# 1. إعدادات الصفحة والتصميم الجمالي التكيفي
# ==========================================
st.set_page_config(
    page_title="تجربة النظام التحليلي المطور",
    page_icon="📖",
    layout="wide",
)

# تطبيق التنسيق المركزي
theme.apply_custom_theme()

st.markdown(
    """
    <style>
        .main-header {
            text-align: center; 
            color: #F1C40F !important;
            font-weight: bold;
        }
        .quran-ayah {
            font-size: 20px;
            color: #F1C40F;
            font-family: 'Amiri', serif;
            line-height: 1.6;
        }
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 2. الاتصال الآمن بقاعدة بيانات Supabase
# ==========================================
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
        "❌ خطأ: لم يتم العثور على مفاتيح الاتصال بـ Supabase في متغيرات البيئة أو"
        " الأسرار."
    )
    st.stop()

supabase: Client = create_client(url, key)


# ==========================================
# 3. الدوال المساعدة للتطبيع الذكي والبحث المتقدم (محدثة لدعم المقاطع)
# ==========================================
@st.cache_data
def load_surah_group_mapping():
    mapping_file = "ملف ربط المجموعات الثمانبة بالسور.xlsx"
    if os.path.exists(mapping_file):
        df_map = pd.read_excel(mapping_file, sheet_name=0)
        mapping = {}
        for _, row in df_map.iterrows():
            s_name = str(row["إسم السورة"]).strip()
            g_num = int(row["رقم المجموعة"])
            mapping[s_name] = g_num
        return mapping
    return {}


surah_group_map = load_surah_group_mapping()


def normalize_arabic(text):
    """توحيد شامل للهمزات والياءات وإزالة التشكيل والعلامات القرآنية"""
    if not text:
        return ""
    text = re.sub(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]", "", text)
    text = re.sub(r"[إأآٱ]", "ا", text)
    text = re.sub(r"[ىي]", "ي", text)
    return text.strip()


def is_match_query(query, plain_txt, uthmani_txt):
    """
    التحقق من التطابق سواء كان البحث كلمة مفردة أو عبارة/مقطع مكون من عدة كلمات.
    """
    norm_query = normalize_arabic(query)
    norm_plain = normalize_arabic(plain_txt)
    norm_uthmani = normalize_arabic(uthmani_txt)

    # إذا كان البحث يحتوي على مسافة (أي عبارة أو مقطع من عدة كلمات)
    if " " in norm_query:
        # البحث عن العبارة كجزء متصل داخل النص المجرد أو النص العثماني
        return (norm_query in norm_plain) or (norm_query in norm_uthmani)
    else:
        # إذا كانت كلمة مفردة، نتحقق من استقلاليتها ككلمة تامة
        words_plain = re.findall(r"[\u0600-\u06FF]+", norm_plain)
        words_uthmani = re.findall(r"[\u0600-\u06FF]+", norm_uthmani)
        return (norm_query in words_plain) or (norm_query in words_uthmani)


# ==========================================
# 4. واجهة النظام التحليلي التجريبي
# ==========================================
st.markdown(
    "<h1 class='main-header'>📊 شاشة تجربة النظام التحليلي (بحث مطور للمقاطع"
    " والكلمات)</h1>",
    unsafe_allow_html=True,
)
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🔍 البحث والتدبر الذكي",
        "📊 البحث التحليلي والموضوعي",
        "📖 استعراض السور والمقاصد",
        "📈 تقرير الكلمات المحصورة",
    ]
)

# داخل التبويب الأول (البحث والتدبر الذكي) في ملف test أو النظام التحليلي:
with tab1:
    st.subheader(
        "البحث الفوري المتكامل (يدعم الكلمة المفردة أو المقطع المتعدد الكلمات)"
    )
    search_query = st.text_input(
        "أدخل الكلمة أو العبارة بدقة (مثل: استوى، استوى على، الحميد):",
        placeholder="اكتب الكلمة أو العبارة هنا...",
        key="search_input_test_v3",
    )

    if "test_search_results" not in st.session_state:
        st.session_state.test_search_results = {"hsor": [], "quran": []}
    if "test_searched_word" not in st.session_state:
        st.session_state.test_searched_word = ""

    col_s1, col_s2 = st.columns([1, 5])
    with col_s1:
        search_button = st.button("🔍 بحث شامل دقيق", key="btn_t1_search_test_v3")

    norm_target = ""
    if search_button and search_query:
        with st.spinner("جاري البحث اللغوي الدقيق في المصحف..."):
            raw_query = search_query.strip()
            st.session_state.test_searched_word = raw_query
            norm_target = normalize_arabic(raw_query)

            # 1. البحث في الحصر المعتمد
            resp_hsor = supabase.table("ayah_group_relations").select("*").execute()
            all_hsor = resp_hsor.data if resp_hsor.data else []

            hsor_results = []
            for r in all_hsor:
                w = str(r.get("topic_or_keyword", "")).strip()
                norm_w = normalize_arabic(w)
                if " " in raw_query:
                    if norm_target in norm_w:
                        hsor_results.append(r)
                else:
                    words_in_w = re.findall(r"[\u0600-\u06FF]+", norm_w)
                    if norm_target in words_in_w or norm_target == norm_w:
                        hsor_results.append(r)

            for item in hsor_results:
                s_name = str(item.get("surah_name", "")).strip()
                item["_group_id"] = surah_group_map.get(s_name, 1)

            hsor_results = sorted(
                hsor_results,
                key=lambda x: (
                    x.get("_group_id", 1),
                    x.get("surah_serial", 0),
                    x.get("ayah_number", 0),
                ),
            )

            # 2. البحث الدقيق في المصحف الشامل (بدعم العبارات والكلمات المفردة)
            if " " in raw_query:
                # إذا كانت عبارة متعددة الكلمات (مثل: استوى على)، نبحث مباشرة عن احتوائها في النص المجرد
                quran_res = (
                    supabase.table("full_quran")
                    .select("*")
                    .ilike("plain_ayah_text", f"%{raw_query}%")
                    .execute()
                )
            else:
                # إذا كانت كلمة مفردة، ندعم تبديل التاء المربوطة والمفتوحة
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

            raw_quran_data = quran_res.data if quran_res.data else []

            quran_results = []
            for q in raw_quran_data:
                plain_txt = q.get("plain_ayah_text", "")
                uthmani_txt = q.get("ayah_text", "")
                if " " in raw_query:
                    # للتأكد التام من احتواء النص المجرد على العبارة
                    if raw_query in plain_txt or norm_target in normalize_arabic(
                        plain_txt
                    ):
                        quran_results.append(q)
                else:
                    if is_match_query(raw_query, plain_txt, uthmani_txt):
                        quran_results.append(q)

            quran_results = sorted(
                quran_results,
                key=lambda x: (x.get("surah_number", 0), x.get("ayah_number", 0)),
            )

            st.session_state.test_search_results = {
                "hsor": hsor_results,
                "quran": quran_results,
            }

    # عرض النتائج...
    res_quran = st.session_state.test_search_results.get("quran", [])
    current_word = st.session_state.test_searched_word

    if current_word:
        st.markdown(f"### 🌍 نتائج البحث لـ: '{current_word}'")
        if res_quran:
            st.success(f"✅ تم العثور على {len(res_quran)} آية مطابقة لبحثك بدقة تامة!")
            for idx, row in enumerate(res_quran, 1):
                surah_name = row["surah_name"]
                surah_num = row["surah_number"]
                ayah_num = row["ayah_number"]
                ayah_text = row["ayah_text"]
                st.markdown(
                    f"""
              <div style='background-color: #34495E; padding: 10px; border-radius: 6px; margin-top: 10px;'>
                  <p class='quran-ayah'>{idx}. {ayah_text}</p>
                  <p style='font-size: 13px; color: #ECF0F1;'>📖 سورة: <b>{surah_name} (رقم {surah_num})</b> | آية رقم: <b>{ayah_num}</b></p>
              </div>
              """,
                    unsafe_allow_html=True,
                )
        else:
            st.warning(f"❌ لم يتم العثور على أي نتائج مطابقة لـ: '{current_word}'.")

    res_hsor = st.session_state.test_search_results.get("hsor", [])
    res_quran = st.session_state.test_search_results.get("quran", [])
    current_word = st.session_state.test_searched_word

    if current_word:
        if res_hsor:
            st.success(
                f"✅ تم العثور على {len(res_hsor)} نتيجة مطابقة في **حصرك المعتمد**"
                f" لـ: '{current_word}'"
            )
            for idx, row in enumerate(res_hsor, 1):
                word = row.get("topic_or_keyword", "-")
                g_id = row.get("_group_id", 1)
                notes = row.get("notes", "-")
                surah = row.get("surah_name", "-")
                surah_num = row.get("surah_serial", "-")
                ayah = row.get("ayah_number", "-")
                text = row.get("ayah_text", "")
                st.markdown(
                    f"""
            <div style='background-color: #2C3E50; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-right: 5px solid #27AE60;'>
                <p style='font-size: 18px; font-weight: bold; color: #F1C40F;'>{idx}. النتيجة: {word}</p>
                <p class='quran-ayah'>{text}</p>
                <p style='font-size: 14px; color: #ECF0F1; margin: 5px 0;'>📖 سورة: <b>{surah} (رقم {surah_num})</b> | آية رقم: <b>{ayah}</b> | 🏷️ المجموعة: <b>{g_id}</b></p>
                <p style='font-size: 15px; color: #BDC3C7;'>💡 المقصد: <b>{notes}</b></p>
            </div>
            """,
                    unsafe_allow_html=True,
                )
        else:
            st.info(
                f"ℹ️ لا توجد سجلات مطابقة لـ '{current_word}' في حصرك المعتمد حالياً."
            )

        st.markdown("---")
        st.markdown(
            f"### 🌍 استكشاف المصحف الشامل لـ: '{current_word}' (مرتبة حسب ترتيب"
            " المصحف)"
        )

        if res_quran:
            st.success(
                f"تم العثور على {len(res_quran)} آية في **المصحف الشامل** تطابق"
                f" بحثك '{current_word}'."
            )
            for idx, row in enumerate(res_quran, 1):
                surah_name = row["surah_name"]
                surah_num = row["surah_number"]
                ayah_num = row["ayah_number"]
                ayah_text = row["ayah_text"]
                st.markdown(
                    f"""
              <div style='background-color: #34495E; padding: 10px; border-radius: 6px; margin-top: 10px;'>
                  <p class='quran-ayah'>{idx}. {ayah_text}</p>
                  <p style='font-size: 13px; color: #ECF0F1;'>📖 سورة: <b>{surah_name} (رقم {surah_num})</b> | آية رقم: <b>{ayah_num}</b></p>
              </div>
              """,
                    unsafe_allow_html=True,
                )
        else:
            st.warning(
                f"❌ لم يتم العثور على أي نتائج في المصحف الشامل لـ: '{current_word}'."
            )

# باقي التبويبات (2، 3، 4) تعمل بشكل طبيعي كما في النسخة الأصلية
with tab2:
    st.info("التبويب الثاني يعمل بنفس الإعدادات السابقة.")
with tab3:
    st.info("التبويب الثالث يعمل بنفس الإعدادات السابقة.")
with tab4:
    st.info("التبويب الرابع يعمل بنفس الإعدادات السابقة.")
