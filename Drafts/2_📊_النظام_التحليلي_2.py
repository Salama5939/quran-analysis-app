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
    page_title="النظام التحليلي للتدبر القرآني (المطور)",
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
# 3. الدوال المساعدة للتطبيع الذكي والبحث
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


def is_exact_word_match(query, plain_txt, uthmani_txt):
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
# 4. واجهة النظام التحليلي
# ==========================================
st.markdown(
    "<h1 class='main-header'>📊 النظام التحليلي والبحث الموضوعي</h1>",
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

# التبويب الأول: البحث والتدبر الذكي (المدمج والشامل)
with tab1:
    st.subheader(
        "البحث الفوري المتكامل في الحصر المعتمد والمصحف الشامل (يدعم الكلمات"
        " والمقاطع)"
    )
    search_query = st.text_input(
        "أدخل الكلمة أو العبارة بدقة (مثل: استوى، استوى على، الحميد):",
        placeholder="اكتب هنا...",
        key="search_input_final",
    )

    if "search_results" not in st.session_state:
        st.session_state.search_results = {"hsor": [], "quran": []}
    if "searched_word" not in st.session_state:
        st.session_state.searched_word = ""
    if "success_message" not in st.session_state:
        st.session_state.success_message = ""

    col_s1, col_s2 = st.columns([1, 5])
    with col_s1:
        search_button = st.button("🔍 بحث شامل", key="btn_t1_search_final")

    if search_button and search_query:
        with st.spinner("جاري البحث اللغوي الدقيق في الحصر والمصحف..."):
            raw_query = search_query.strip()
            st.session_state.searched_word = raw_query
            st.session_state.success_message = ""
            norm_target = normalize_arabic(raw_query)

            # 1. البحث في الحصر المعتمد (ayah_group_relations)
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

            # 2. البحث في المصحف الشامل (full_quran) مع دعم العبارات والكلمات
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

            raw_quran_data = quran_res.data if quran_res.data else []

            quran_results = []
            for q in raw_quran_data:
                plain_txt = q.get("plain_ayah_text", "")
                uthmani_txt = q.get("ayah_text", "")
                if " " in raw_query:
                    if raw_query in plain_txt or norm_target in normalize_arabic(
                        plain_txt
                    ):
                        quran_results.append(q)
                else:
                    if is_exact_word_match(raw_query, plain_txt, uthmani_txt):
                        quran_results.append(q)

            quran_results = sorted(
                quran_results,
                key=lambda x: (x.get("surah_number", 0), x.get("ayah_number", 0)),
            )

            st.session_state.search_results = {
                "hsor": hsor_results,
                "quran": quran_results,
            }

    if st.session_state.success_message:
        st.success(st.session_state.success_message)
        if st.button("🔄 البحث عن كلمة جديدة أخرى", type="primary"):
            st.session_state.search_results = {"hsor": [], "quran": []}
            st.session_state.searched_word = ""
            st.session_state.success_message = ""
            st.rerun()

    res_hsor = st.session_state.search_results.get("hsor", [])
    res_quran = st.session_state.search_results.get("quran", [])
    current_word = st.session_state.searched_word

    if current_word:
        # أولاً: عرض نتائج الحصر المعتمد
        if res_hsor:
            st.success(
                f"✅ تم العثور على {len(res_hsor)} نتيجة مطابقة في **حصرك المعتمد**"
                f" لـ: '{current_word}' (مرتبة حسب المجموعة والسورة والآية)"
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
                <p style='font-size: 18px; font-weight: bold; color: #F1C40F;'>{idx}. الكلمة / الموضوع: {word}</p>
                <p class='quran-ayah'>{text}</p>
                <p style='font-size: 14px; color: #ECF0F1; margin: 5px 0;'>📖 سورة: <b>{surah} (رقم {surah_num})</b> | آية رقم: <b>{ayah}</b> | 🏷️ المجموعة: <b>{g_id}</b></p>
                <p style='font-size: 15px; color: #BDC3C7;'>💡 المقصد: <b>{notes}</b></p>
            </div>
            """,
                    unsafe_allow_html=True,
                )
        else:
            st.info(
                f"ℹ️ لا توجد سجلات مطابقة لـ '{current_word}' في حصرك المعتمد"
                " حالياً."
            )

        st.markdown("---")
        st.markdown(
            f"### 🌍 استكشاف المصحف الشامل لـ: '{current_word}' (مرتبة حسب ترتيب"
            " المصحف)"
        )

        # ثانياً: عرض نتائج المصحف الشامل مع نموذج الحفظ والإضافة
        if res_quran:
            st.info(
                f"تم العثور على {len(res_quran)} آية في **المصحف الشامل** تطابق"
                f" بحثك '{current_word}'."
            )

            with st.form(key="batch_save_form_final"):
                st.markdown(
                    "📋 **جدول تدبر وحفظ الآيات** (الآيات التي تحفظها بمقصد ستختفي، وتظل"
                    " البقية لمراجعتها)"
                )

                batch_inputs = []
                for idx, row in enumerate(res_quran, 1):
                    surah_name = row["surah_name"]
                    surah_num = row["surah_number"]
                    ayah_num = row["ayah_number"]
                    ayah_text = row["ayah_text"]

                    default_group = surah_group_map.get(surah_name, 1)

                    st.markdown(
                        f"""
              <div style='background-color: #34495E; padding: 10px; border-radius: 6px; margin-top: 10px;'>
                  <p class='quran-ayah'>{idx}. {ayah_text}</p>
                  <p style='font-size: 13px; color: #ECF0F1;'>📖 سورة: <b>{surah_name} (رقم {surah_num})</b> | آية رقم: <b>{ayah_num}</b></p>
              </div>
              """,
                        unsafe_allow_html=True,
                    )

                    col_g, col_n = st.columns([1, 3])
                    with col_g:
                        g_index = max(0, min(default_group - 1, 7))
                        g_val = st.selectbox(
                            "المجموعة:",
                            range(1, 9),
                            index=g_index,
                            key=f"batch_g_f_{idx}",
                        )
                    with col_n:
                        n_val = st.text_input(
                            "المقصد أو التدبر لهذه الآية (اتركه فارغاً لتبقيها للمراجعة):",
                            placeholder="اكتب المقصد...",
                            key=f"batch_n_f_{idx}",
                        )

                    batch_inputs.append(
                        {
                            "surah_name": surah_name,
                            "surah_serial": surah_num,
                            "ayah_num": ayah_num,
                            "ayah_text": ayah_text,
                            "group_id": g_val,
                            "note": n_val,
                        }
                    )

                submit_batch = st.form_submit_button(
                    "💾 حفظ الآيات المدخل مقاصدها وإبقاء البقية"
                )

                if submit_batch:
                    success_count = 0
                    remaining_quran_data = []

                    for item in batch_inputs:
                        if item["note"].strip():
                            insert_data = {
                                "word_code": 0,
                                "topic_or_keyword": current_word,
                                "group_id": item["group_id"],
                                "surah_serial": item["surah_serial"],
                                "surah_name": item["surah_name"],
                                "ayah_number": item["ayah_num"],
                                "ayah_text": item["ayah_text"],
                                "notes": item["note"].strip(),
                                "half_code": 0,
                                "quarter_code": 0,
                                "frequency_count": 1,
                            }
                            try:
                                supabase.table("ayah_group_relations").insert(
                                    insert_data
                                ).execute()
                                success_count += 1
                            except Exception as e:
                                st.error(
                                    f"خطأ في حفظ آية {item['ayah_num']} سورة"
                                    f" {item['surah_name']}: {e}"
                                )
                        else:
                            remaining_quran_data.append(
                                {
                                    "surah_name": item["surah_name"],
                                    "surah_number": item["surah_serial"],
                                    "ayah_number": item["ayah_num"],
                                    "ayah_text": item["ayah_text"],
                                    "plain_ayah_text": "",
                                }
                            )

                    if success_count > 0:
                        st.session_state.success_message = (
                            f"🎉 تم بنجاح حفظ {success_count} آية مرتبطة بـ"
                            f" '{current_word}'!"
                        )
                        st.session_state.search_results["quran"] = remaining_quran_data
                        st.rerun()
                    else:
                        st.warning(
                            "⚠️ يرجى كتابة المقصد لآية واحدة على الأقل قبل الضغط"
                            " على زر الحفظ."
                        )
        else:
            st.warning(
                f"❌ لم يتم العثور على أي نتائج في المصحف الشامل لـ: '{current_word}'."
            )

# باقي التبويبات (2، 3، 4)
with tab2:
    st.info("التبويب الثاني يعمل بنفس الإعدادات السابقة.")
with tab3:
    st.info("التبويب الثالث يعمل بنفس الإعدادات السابقة.")
with tab4:
    st.info("التبويب الرابع يعمل بنفس الإعدادات السابقة.")
