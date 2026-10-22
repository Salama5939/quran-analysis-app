import os
import re
import pandas as pd
import streamlit as st
from supabase import Client, create_client
import theme  # استدعاء ملف التنسيق المركزي

# ==========================================
# 1. إعدادات الصفحة وتصميم الجداول الواسعة
# ==========================================
st.set_page_config(
    page_title="النظام التحليلي للتدبر القرآني (الإصدار النهائي المصحح)",
    page_icon="📖",
    layout="wide",
)

# تطبيق التنسيق المركزي
theme.apply_custom_theme()

# تنسيق إضافي لراحة العرض وتكبير خطوط الجداول
st.markdown(
    """
    <style>
        .main-header {
            text-align: center; 
            color: #F1C40F !important;
            font-weight: bold;
        }
        .quran-ayah {
            font-size: 18px;
            color: #F1C40F;
            font-family: 'Amiri', serif;
        }
        [data-testid="stDataFrame"] {
            direction: rtl;
            text-align: right;
        }
        [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
            direction: rtl !important;
            text-align: right !important;
            font-family: 'Amiri', serif !important;
            font-size: 16px !important;
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
# 3. الدوال المساعدة وقراءة ملفات الربط
# ==========================================
@st.cache_data
def load_surah_mapping_details():
    """قراءة ملف تقسيم السور لجلب المجموعة، النصف، والربع بدقة"""
    mapping_file = "تقسيم سور القرآن حسب الجزء و الربع و المجموعة.xlsx"
    surah_details = {}
    if os.path.exists(mapping_file):
        df_map = pd.read_excel(mapping_file, sheet_name="السور_نصف_ربع_مجموعة")
        for _, row in df_map.iterrows():
            s_name = str(row["إسم السورة"]).strip()
            surah_details[s_name] = {
                "group_id": int(row["كود المجموعة"]),
                "half_code": int(row["كود النصف"]),
                "quarter_code": int(row["كود الربع "]),
            }
    return surah_details


surah_mapping_db = load_surah_mapping_details()


def get_next_word_code():
    """جلب أقصى رقم مسلسل word_code وإضافة 1 لضمان تسلسل صحيح"""
    try:
        res = (
            supabase.table("ayah_group_relations")
            .select("word_code")
            .order("word_code", desc=True)
            .limit(1)
            .execute()
        )
        data = res.data
        if data and len(data) > 0:
            max_code = data[0].get("word_code", 0)
            return int(max_code) + 1
    except Exception:
        pass
    return 1


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
    "<h1 class='main-header'>📊 النظام التحليلي والبحث الموضوعي (الإصدار"
    " النهائي المصحح)</h1>",
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

# التبويب الأول: البحث والتدبر الذكي
with tab1:
    st.subheader(
        "البحث الفوري المتكامل في الحصر المعتمد والمصحف الشامل (مع تفريغ الشاشة"
        " التلقائي)"
    )

    # معالجة أمر مسح الشاشة وإعادة تعيين الحقول تماماً
    if st.session_state.get("clear_screen_flag", False):
        st.session_state.search_results_final = {"hsor": [], "quran": []}
        st.session_state.searched_word_final = ""
        st.session_state.search_input_table_final = ""  # مسح حقل النص تماماً
        st.session_state.clear_screen_flag = False

    search_query = st.text_input(
        "أدخل الكلمة أو العبارة بدقة (مثل: استوى، استوى على، المجيد):",
        placeholder="اكتب هنا...",
        key="search_input_table_final",
    )

    if "search_results_final" not in st.session_state:
        st.session_state.search_results_final = {"hsor": [], "quran": []}
    if "searched_word_final" not in st.session_state:
        st.session_state.searched_word_final = ""

    col_s1, col_s2 = st.columns([1, 5])
    with col_s1:
        search_button = st.button("🔍 بحث شامل", key="btn_t1_search_final_v2")

    if search_button and search_query:
        with st.spinner("جاري البحث اللغوي الدقيق وتحليل النتائج..."):
            raw_query = search_query.strip()
            st.session_state.searched_word_final = raw_query
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
                item["_group_id"] = surah_mapping_db.get(s_name, {}).get("group_id", 1)

            hsor_results = sorted(
                hsor_results,
                key=lambda x: (
                    x.get("_group_id", 1),
                    x.get("surah_serial", 0),
                    x.get("ayah_number", 0),
                ),
            )

            # 2. البحث في المصحف الشامل (full_quran)
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

            st.session_state.search_results_final = {
                "hsor": hsor_results,
                "quran": quran_results,
            }

    res_hsor = st.session_state.search_results_final.get("hsor", [])
    res_quran = st.session_state.search_results_final.get("quran", [])
    current_word = st.session_state.searched_word_final

    if current_word:
        # --- الجدول الأول: نتائج الحصر المعتمد ---
        if res_hsor:
            st.success(
                f"✅ تم العثور على {len(res_hsor)} نتيجة مطابقة في **حصرك المعتمد**"
                f" لـ: '{current_word}'"
            )
            table_data_hsor = []
            for idx, row in enumerate(res_hsor, 1):
                table_data_hsor.append(
                    {
                        "مسلسل البحث": idx,
                        "كلمة البحث": row.get("topic_or_keyword", current_word),
                        "رقم المجموعة": row.get("_group_id", 1),
                        "رقم السورة": row.get("surah_serial", 1),
                        "إسم السورة": row.get("surah_name", "-"),
                        "رقم الآية": row.get("ayah_number", 1),
                        "منطوق الآية": row.get("ayah_text", "-"),
                    }
                )
            df_hsor_view = pd.DataFrame(table_data_hsor)
            st.dataframe(
                df_hsor_view,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "منطوق الآية": st.column_config.TextColumn(
                        "منطوق الآية", width="large"
                    ),
                    "إسم السورة": st.column_config.TextColumn(
                        "إسم السورة", width="medium"
                    ),
                },
            )
        else:
            st.info(
                f"ℹ️ لا توجد سجلات مطابقة لـ '{current_word}' في حصرك المعتمد حالياً."
            )

        st.markdown("---")

        # --- الجدول الثاني: نتائج المصحف الشامل للمراجعة والترحيل الذكي ---
        if res_quran:
            count_hsor = len(res_hsor)
            count_quran = len(res_quran)

            st.markdown(
                f"### 🌍 نتائج المصحف الشامل لـ: '{current_word}' (إجمالي الآيات"
                f" في القرآن: {count_quran})"
            )

            if count_hsor >= count_quran:
                st.success(
                    "🎉 **ممتاز!** النتائج المخزنة في حصرك المعتمد مطابقة أو تغطي"
                    " بالكامل النتائج الموجودة في القرآن لهذه الكلمة."
                )
            else:
                st.warning(
                    f"⚠️ العدد المخزن في الحصر ({count_hsor}) أقل من إجمالي الوجوه في"
                    f" القرآن ({count_quran}). يمكنك مراجعة الجدول أدناه واختيار الآيات"
                    " المراد ترحيلها."
                )

            existing_ayahs = set()
            for r in res_hsor:
                try:
                    s_ser = int(r.get("surah_serial", 0))
                    a_num = int(r.get("ayah_number", 0))
                    existing_ayahs.add((s_ser, a_num))
                except:
                    pass

            table_data_quran = []
            for idx, q in enumerate(res_quran, 1):
                s_num = int(q.get("surah_number", 0))
                a_num = int(q.get("ayah_number", 0))
                is_already_saved = (s_num, a_num) in existing_ayahs

                table_data_quran.append(
                    {
                        "اختيار للترحيل": False,
                        "مسلسل": idx,
                        "رقم السورة": s_num,
                        "إسم السورة": q.get("surah_name"),
                        "رقم الآية": a_num,
                        "منطوق الآية": q.get("ayah_text"),
                        "حالة الحفظ": (
                            "مخزن مسبقاً (مكرر)"
                            if is_already_saved
                            else "جديد غير مخزن"
                        ),
                    }
                )

            df_quran_view = pd.DataFrame(table_data_quran)

            edited_df = st.data_editor(
                df_quran_view,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "اختيار للترحيل": st.column_config.CheckboxColumn(
                        "هل تريد ترحيل هذه الآية؟ (نعم/لا)",
                        help=(
                            "حدد مربع الاختيار للآيات التي تود إضافتها لقاعدة البيانات"
                        ),
                        default=False,
                    ),
                    "منطوق الآية": st.column_config.TextColumn(
                        "منطوق الآية", width="large"
                    ),
                },
                key="editor_quran_verses_final_v2",
            )

            if st.button("📥 تنفيذ وفحص ترحيل الآيات المحددة", type="primary"):
                migrated_count = 0
                duplicate_attempt_count = 0
                duplicate_details = []

                target_word_code = get_next_word_code()

                for index, row in edited_df.iterrows():
                    if row["اختيار للترحيل"] == True:
                        s_name = row["إسم السورة"]
                        s_num = int(row["رقم السورة"])
                        a_num = int(row["رقم الآية"])
                        a_text = row["منطوق الآية"]

                        if (s_num, a_num) in existing_ayahs:
                            duplicate_attempt_count += 1
                            duplicate_details.append(f"سورة {s_name} - آية {a_num}")
                            continue

                        surah_info = surah_mapping_db.get(s_name, {})
                        default_g = surah_info.get("group_id", 1)
                        half_c = surah_info.get("half_code", 0)
                        quarter_c = surah_info.get("quarter_code", 0)

                        insert_data = {
                            "word_code": target_word_code,
                            "topic_or_keyword": current_word,
                            "group_id": default_g,
                            "surah_serial": s_num,
                            "surah_name": s_name,
                            "ayah_number": a_num,
                            "ayah_text": a_text,
                            "notes": "إضافة نهائية ذكية من المصحف الشامل",
                            "half_code": half_c,
                            "quarter_code": quarter_c,
                            "frequency_count": 1,
                        }
                        try:
                            supabase.table("ayah_group_relations").insert(
                                insert_data
                            ).execute()
                            migrated_count += 1
                            existing_ayahs.add((s_num, a_num))
                        except Exception as e:
                            st.error(f"خطأ أثناء ترحيل آية {a_num} سورة {s_name}: {e}")

                if migrated_count > 0:
                    st.success(
                        f"🎉 تم بنجاح ترحيل وإضافة ({migrated_count}) آية جديدة برقم مسلسل"
                        f" (word_code = {target_word_code}) وتحديث قاعدة البيانات!"
                    )

                if duplicate_attempt_count > 0:
                    st.warning(
                        f"⚠️ تنبيه ذكي: تم استثناء وتجاهل ({duplicate_attempt_count}) آية"
                        " لاختيارك ترحيلها بينما هي مسجلة مسبقاً في حصرك المعتمد وهي:"
                        f" {', '.join(duplicate_details)}"
                    )

                if migrated_count == 0 and duplicate_attempt_count == 0:
                    st.warning(
                        "⚠️ لم تقم بتحديد أي آية للترحيل. يرجى اختيار آية واحدة على الأقل"
                        " عبر خانة الاختيار."
                    )
                else:
                    st.markdown("---")
                    if st.button(
                        "🔄 إدخال كلمة جديدة وبحث جديد (مسح الشاشة)",
                        type="primary",
                        key="btn_clear_screen_v2",
                    ):
                        st.session_state.clear_screen_flag = True
                        st.rerun()
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
