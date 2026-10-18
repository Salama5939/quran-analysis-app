import os
import re
import pandas as pd
import streamlit as st
from supabase import Client, create_client

# ==========================================
# 1. إعدادات الصفحة والتصميم الجمالي التكيفي
# ==========================================
st.set_page_config(
    page_title="النظام التحليلي للتدبر القرآني",
    page_icon="📖",
    layout="wide",
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Cairo', sans-serif;
            direction: rtl;
            text-align: right;
        }
        
        .stTextInput input, .stSelectbox div[data-baseweb="select"], .stTextArea textarea {
            text-align: right;
        }
        
        h1, h2, h3, h4 {
            font-family: 'Amiri', serif;
            font-weight: 700;
        }
        
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
# 3. الدوال المساعدة للتطبيع الذكي والبحث الدقيق
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
    # إزالة التشكيل وكل العلامات القرآنية والتطويل
    text = re.sub(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]", "", text)
    # توحيد الألفات
    text = re.sub(r"[إأآٱ]", "ا", text)
    # توحيد الياء والألف المقصورة (لحل مشكلة الحى والحي)
    text = re.sub(r"[ىي]", "ي", text)
    return text.strip()


def is_exact_word_match(query, plain_txt, uthmani_txt):
    """
    التحقق من أن الكلمة المستقلة مطابقة تماماً.
    يتم فحص النص المجرد والنص العثماني لضمان التقاط الكلمات
    التي تختلف إملائياً عن الرسم العثماني (مثل سنة وسنت).
    """
    norm_query = normalize_arabic(query)

    # فحص النص المجرد
    norm_plain = normalize_arabic(plain_txt)
    words_plain = re.findall(r"[\u0600-\u06FF]+", norm_plain)

    # فحص النص العثماني (بعد تجريده من التشكيل)
    norm_uthmani = normalize_arabic(uthmani_txt)
    words_uthmani = re.findall(r"[\u0600-\u06FF]+", norm_uthmani)

    # المطابقة تنجح إذا وُجدت الكلمة ككلمة مستقلة في أي من النصين
    return (norm_query in words_plain) or (norm_query in words_uthmani)


# ==========================================
# 4. واجهة النظام التحليلي (التبويبات الأربعة)
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

# التبويب الأول: البحث والتدبر الذكي
with tab1:
    st.subheader(
        "البحث الفوري المتكامل في الحصر المعتمد والمصحف الشامل (بدعم التطبيع"
        " والكلمة التامة)"
    )
    search_query = st.text_input(
        "أدخل الكلمة أو العبارة بدقة (مثل: الحميد، سنت، الحى، آدم):",
        placeholder="اكتب الكلمة هنا...",
        key="search_input",
    )

    if "search_results" not in st.session_state:
        st.session_state.search_results = {"hsor": [], "quran": []}
    if "searched_word" not in st.session_state:
        st.session_state.searched_word = ""
    if "success_message" not in st.session_state:
        st.session_state.success_message = ""

    col_s1, col_s2 = st.columns([1, 5])
    with col_s1:
        search_button = st.button("🔍 بحث شامل", key="btn_t1_search")

    if search_button and search_query:
        with st.spinner("جاري البحث اللغوي والشامل..."):
            raw_query = search_query.strip()
            st.session_state.searched_word = raw_query
            st.session_state.success_message = ""
            norm_target = normalize_arabic(raw_query)

            # 1. البحث في الحصر المعتمد (دعم مطابقة الكلمة داخل العبارة)
            resp_hsor = supabase.table("ayah_group_relations").select("*").execute()
            all_hsor = resp_hsor.data if resp_hsor.data else []

            hsor_results = []
            for r in all_hsor:
                w = str(r.get("topic_or_keyword", "")).strip()
                norm_w = normalize_arabic(w)
                words_in_w = re.findall(r"[\u0600-\u06FF]+", norm_w)
                # مطابقة الكلمة سواء كانت الكلمة بأكملها أو جزء مستقل من عبارة
                if norm_target in words_in_w or norm_target == norm_w:
                    hsor_results.append(r)

            # ترتيب نتائج الحصر المعتمد
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

            # 2. البحث في المصحف الشامل (استعلام ذكي لضمان جلب كل الاحتمالات)
            variants = {raw_query, norm_target}
            # تبديل التاء المربوطة والمفتوحة لجلب السجلات من الداتابيز (التصفية الدقيقة لاحقاً)
            if norm_target.endswith("ت"):
                variants.add(norm_target[:-1] + "ة")
            elif norm_target.endswith("ة"):
                variants.add(norm_target[:-1] + "ت")

            or_conditions = []
            for v in variants:
                if v:
                    or_conditions.append(f"plain_ayah_text.ilike.%{v}%")
            or_query_string = ",".join(or_conditions)

            quran_res = (
                supabase.table("full_quran").select("*").or_(or_query_string).execute()
            )
            raw_quran_data = quran_res.data if quran_res.data else []

            quran_results = []
            for q in raw_quran_data:
                plain_txt = q.get("plain_ayah_text", "")
                uthmani_txt = q.get("ayah_text", "")
                # تصفية دقيقة جداً تفصل بين التاء المربوطة والمفتوحة بناءً على النص العثماني
                if is_exact_word_match(raw_query, plain_txt, uthmani_txt):
                    quran_results.append(q)

            # ترتيب نتائج المصحف
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
        if res_hsor:
            st.success(
                f"✅ تم العثور على {len(res_hsor)} نتيجة مطابقة في **حصرك المعتمد**"
                f" للكلمة: '{current_word}' (مرتبة حسب المجموعة والسورة والآية)"
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
                f"ℹ️ لا توجد سجلات مطابقة للكلمة '{current_word}' في حصرك المعتمد"
                " حالياً."
            )

        st.markdown("---")
        st.markdown(
            f"### 🌍 استكشاف المصحف الشامل لكلمة: '{current_word}' (مرتبة حسب"
            " ترتيب المصحف)"
        )

        if res_quran:
            st.info(
                f"تم العثور على {len(res_quran)} آية في **المصحف الشامل** تحتوي على"
                f" الكلمة المستقلة '{current_word}'."
            )

            with st.form(key="batch_save_form"):
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
                            key=f"batch_g_{idx}",
                        )
                    with col_n:
                        n_val = st.text_input(
                            "المقصد أو التدبر لهذه الآية (اتركه فارغاً لتبقيها للمراجعة):",
                            placeholder="اكتب المقصد...",
                            key=f"batch_n_{idx}",
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
                            f"🎉 تم بنجاح حفظ {success_count} آية مرتبطة بكلمة"
                            f" '{current_word}'!"
                        )
                        st.session_state.search_results["quran"] = remaining_quran_data
                        st.rerun()
                    else:
                        st.warning(
                            "⚠️ يرجى كتابة المقصد لآية واحدة على الأقل قبل الضغط على زر الحفظ."
                        )
        else:
            st.warning(
                f"❌ لم يتم العثور على أي نتائج في المصحف الشامل لـ: '{current_word}'."
            )

# التبويب الثاني: البحث التحليلي والموضوعي
with tab2:
    st.subheader(
        "البحث المتقدم في الكلمات المحصورة والمقاصد والمجموعات الثمانية (مرتبة حسب"
        " المجموعة والسورة والآية)"
    )
    analysis_query = st.text_input(
        "أدخل الكلمة أو الموضوع للبحث في التحليلات:",
        placeholder="مثال: الحميد، سنت، الحى...",
        key="analysis_search",
    )

    group_filter = st.selectbox(
        "تصفية حسب المجموعة الثمانية (اختياري):",
        [
            "الكل",
            "المجموعة 1",
            "المجموعة 2",
            "المجموعة 3",
            "المجموعة 4",
            "المجموعة 5",
            "المجموعة 6",
            "المجموعة 7",
            "المجموعة 8",
        ],
        key="t2_group_sel",
    )

    if analysis_query or group_filter != "الكل":
        query_builder = supabase.table("ayah_group_relations").select("*")
        if group_filter != "الكل":
            g_num = int(group_filter.replace("المجموعة ", ""))
            query_builder = query_builder.eq("group_id", g_num)

        response = query_builder.execute()
        all_records = response.data if response.data else []

        analysis_results = []
        norm_query_t2 = normalize_arabic(analysis_query) if analysis_query else ""

        for record in all_records:
            word = str(record.get("topic_or_keyword", "")).strip()
            norm_word = normalize_arabic(word)
            words_in_word = re.findall(r"[\u0600-\u06FF]+", norm_word)

            if analysis_query:
                if norm_query_t2 in words_in_word or norm_query_t2 == norm_word:
                    analysis_results.append(record)
            else:
                analysis_results.append(record)

        if analysis_results:
            # ترتيب نتائج التحليلي هرمياً
            for record in analysis_results:
                s_name = str(record.get("surah_name", "")).strip()
                if not record.get("group_id") or int(record.get("group_id", 0)) == 0:
                    record["group_id"] = surah_group_map.get(s_name, 1)

            analysis_results = sorted(
                analysis_results,
                key=lambda x: (
                    int(x.get("group_id", 1)),
                    int(x.get("surah_serial", 0)),
                    int(x.get("ayah_number", 0)),
                ),
            )

            st.success(
                f"✅ تم العثور على {len(analysis_results)} سجل تحليلي مطابق (مرتبة"
                " حسب المجموعة والسورة والآية)."
            )
            for record in analysis_results:
                word = record.get("topic_or_keyword", "-")
                g_id = record.get("group_id", "-")
                notes = record.get("notes", "-")
                surah = record.get("surah_name", "-")
                surah_num = record.get("surah_serial", "-")
                ayah = record.get("ayah_number", "-")
                text = record.get("ayah_text", "")
                st.markdown(
                    f"""
            <div style='background-color: #34495E; padding: 12px; border-radius: 6px; margin-bottom: 8px;'>
                <p style='margin: 0; font-weight: bold; color: #F39C12;'>الكلمة / الموضوع: {word} | المجموعة {g_id}</p>
                <p class='quran-ayah' style='font-size: 16px; margin: 4px 0;'>{text} ({surah} [رقم {surah_num}]: {ayah})</p>
                <p style='margin: 0; font-size: 14px; color: #ECF0F1;'>💡 المقصد: {notes}</p>
            </div>
            """,
                    unsafe_allow_html=True,
                )
        else:
            st.warning("❌ لم يتم العثور على نتائج تحليلية مطابقة لشروط البحث.")

# التبويب الثالث: استعراض السور والمقاصد
with tab3:
    st.subheader("📖 الجدول الشامل لمقاصد السور وربطها بالمجموعات الثمانية")
    st.markdown(
        "<p style='color: #BDC3C7;'>استعرض خريطة السور القرآنية الـ 114 مرتبطةً"
        " بمقاصدها وتصنيفها ضمن المجموعات الثمانية، مع إمكانية الفلترة السريعة.</p>",
        unsafe_allow_html=True,
    )

    col_t3_1, col_t3_2 = st.columns([2, 2])
    with col_t3_1:
        selected_t3_group = st.selectbox(
            "تصفية السور حسب المجموعة الثمانية:",
            [
                "جميع المجموعات (114 سورة)",
                "المجموعة 1",
                "المجموعة 2",
                "المجموعة 3",
                "المجموعة 4",
                "المجموعة 5",
                "المجموعة 6",
                "المجموعة 7",
                "المجموعة 8",
            ],
            key="t3_group_filter",
        )

    with col_t3_2:
        search_surah_name = st.text_input(
            "بحث سريع عن سورة:",
            placeholder="اكتب اسم السورة (مثل: البقرة، يوسف)...",
            key="t3_surah_search",
        )

    query_t3 = supabase.table("surah_objectives").select("*")

    if selected_t3_group != "جميع المجموعات (114 سورة)":
        g_id_val = int(selected_t3_group.replace("المجموعة ", ""))
        query_t3 = query_t3.eq("group_id", g_id_val)

    if search_surah_name.strip():
        query_t3 = query_t3.ilike("surah_name", f"%{search_surah_name.strip()}%")

    response_t3 = query_t3.order("surah_number").execute()
    surah_objs_data = response_t3.data

    if surah_objs_data:
        st.success(f"✅ تم العثور على {len(surah_objs_data)} سورة مطابقة.")

        df_surahs_view = pd.DataFrame(surah_objs_data)
        df_surahs_view = df_surahs_view[
            ["surah_number", "surah_name", "group_id", "surah_objective"]
        ]
        df_surahs_view.columns = [
            "مسلسل",
            "اسم السورة",
            "المجموعة",
            "تفاصيل مقصد السورة",
        ]

        st.dataframe(
            df_surahs_view,
            use_container_width=True,
            hide_index=True,
            column_config={
                "مسلسل": st.column_config.NumberColumn(
                    "مسلسل", width="small", format="%d"
                ),
                "اسم السورة": st.column_config.TextColumn("اسم السورة", width="medium"),
                "المجموعة": st.column_config.NumberColumn(
                    "المجموعة", width="small", format="%d"
                ),
                "تفاصيل مقصد السورة": st.column_config.TextColumn(
                    "تفاصيل مقصد السورة", width="large"
                ),
            },
        )
    else:
        st.warning("❌ لم يتم العثور على سور مطابقة لشروط البحث أو الفلترة.")

# التبويب الرابع: تقرير الكلمات المحصورة
with tab4:
    st.subheader("📈 التقرير التحليلي للكلمات المحصورة (حسب المجموعة والترتيب الأبجدي)")
    st.markdown(
        "<p style='color: #BDC3C7;'>قم بتصفية الكلمات حسب المجموعة المطلوبة أولاً،"
        " لترى الكلمات مرتبة أبجدياً مع إجمالي الآيات والتكرارات.</p>",
        unsafe_allow_html=True,
    )

    col_rep1, col_rep2 = st.columns([2, 2])
    with col_rep1:
        selected_group_filter = st.selectbox(
            "اختر المجموعة للعرض:",
            [
                "جميع المجموعات",
                "المجموعة 1",
                "المجموعة 2",
                "المجموعة 3",
                "المجموعة 4",
                "المجموعة 5",
                "المجموعة 6",
                "المجموعة 7",
                "المجموعة 8",
            ],
            key="rep_group_sel",
        )

    with col_rep2:
        st.write("")
        st.write("")
        run_report = st.button(
            "📊 عرض وتحديث التقرير المنظم", key="btn_report_filtered"
        )

    if run_report:
        with st.spinner("جاري استخراج وتحليل البيانات..."):
            query = supabase.table("ayah_group_relations").select(
                "topic_or_keyword, group_id, frequency_count"
            )

            if selected_group_filter != "جميع المجموعات":
                g_num = int(selected_group_filter.replace("المجموعة ", ""))
                query = query.eq("group_id", g_num)

            rep_res = query.limit(5000).execute()
            rep_data = rep_res.data

            if rep_data:
                df_rep = pd.DataFrame(rep_data)

                df_rep["group_id"] = pd.to_numeric(
                    df_rep["group_id"], errors="coerce"
                ).fillna(1)

                def get_unique_groups(series):
                    unique_g = sorted(
                        list(set([int(x) for x in series if pd.notna(x)]))
                    )
                    return ", ".join([str(g) for g in unique_g])

                df_grouped = (
                    df_rep.groupby("topic_or_keyword")
                    .agg(
                        عدد_الآيات_المسجلة=("topic_or_keyword", "count"),
                        إجمالي_التكرارات=("frequency_count", "sum"),
                        المجموعات_المرتبطة=("group_id", get_unique_groups),
                    )
                    .reset_index()
                )

                df_grouped = df_grouped.sort_values(
                    by="topic_or_keyword", ascending=True
                )

                total_unique_words = len(df_grouped)

                st.success(
                    f"✅ إجمالي عدد الكلمات الفريدة الناتجة في ({selected_group_filter}):"
                    f" **{total_unique_words} كلمة**"
                )

                st.dataframe(
                    df_grouped.rename(
                        columns={
                            "topic_or_keyword": "الكلمة / الموضوع",
                            "المجموعات_المرتبطة": "رقم المجموعة (المجموعات)",
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.warning(
                    f"⚠️ لا توجد بيانات مسجلة مطابقة لـ ({selected_group_filter})."
                )
    else:
        st.info(
            "💡 اختر المجموعة من القائمة واضغط على زر **عرض وتحديث التقرير المنظم**"
            " لبدء الاستعراض."
        )
