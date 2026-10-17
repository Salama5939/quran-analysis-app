import os
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
# 3. الدوال المساعدة (ربط المجموعات وترتيب السور)
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

# التبويب الأول: البحث والتدبر الذكي والحفظ الجماعي
with tab1:
    st.subheader("البحث الفوري أولاً في الحصر المعتمد، ثم استكشاف المصحف الشامل")
    search_query = st.text_input(
        "أدخل الكلمة أو العبارة بدقة (مثل: العليم، الغفار، سنن):",
        placeholder="اكتب الكلمة هنا...",
        key="search_input",
    )

    if "search_results" not in st.session_state:
        st.session_state.search_results = {"type": "", "data": []}
    if "searched_word" not in st.session_state:
        st.session_state.searched_word = ""
    if "success_message" not in st.session_state:
        st.session_state.success_message = ""

    col_s1, col_s2 = st.columns([1, 5])
    with col_s1:
        search_button = st.button("🔍 بحث شامل", key="btn_t1_search")

    if search_button and search_query:
        with st.spinner("جاري البحث الذكي..."):
            raw_query = search_query.strip()
            st.session_state.searched_word = raw_query
            st.session_state.success_message = ""

            response = (
                supabase.table("ayah_group_relations")
                .select("*")
                .ilike("topic_or_keyword", f"%{raw_query}%")
                .execute()
            )
            hsor_results = response.data

            if hsor_results:
                st.session_state.search_results = {"type": "hsor", "data": hsor_results}
            else:
                # البحث في المصحف الشامل باستخدام النص المجرد (بدون تشكيل)
                quran_res = (
                    supabase.table("full_quran")
                    .select("*")
                    .ilike("plain_ayah_text", f"%{raw_query}%")
                    .execute()
                )
                st.session_state.search_results = {
                    "type": "quran",
                    "data": quran_res.data if quran_res.data else [],
                }

    if st.session_state.success_message:
        st.success(st.session_state.success_message)
        if st.button("🔄 البحث عن كلمة جديدة أخرى", type="primary"):
            st.session_state.search_results = {"type": "", "data": []}
            st.session_state.searched_word = ""
            st.session_state.success_message = ""
            st.rerun()

    if st.session_state.search_results:
        res_type = st.session_state.search_results["type"]
        res_data = st.session_state.search_results["data"]
        current_word = st.session_state.searched_word

        if res_type == "hsor":
            st.success(
                f"✅ تم العثور على {len(res_data)} نتيجة مطابقة في **حصرك المعتمد**"
                f" للبحث عن: '{current_word}'"
            )
            for idx, row in enumerate(res_data, 1):
                word = row.get("topic_or_keyword", "-")
                g_id = row.get("group_id", "-")
                notes = row.get("notes", "-")
                surah = row.get("surah_name", "-")
                ayah = row.get("ayah_number", "-")
                text = row.get("ayah_text", "")
                st.markdown(
                    f"""
            <div style='background-color: #2C3E50; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-right: 5px solid #27AE60;'>
                <p style='font-size: 18px; font-weight: bold; color: #F1C40F;'>{idx}. الكلمة / الموضوع: {word}</p>
                <p class='quran-ayah'>{text}</p>
                <p style='font-size: 14px; color: #ECF0F1; margin: 5px 0;'>📖 سورة: <b>{surah}</b> | آية رقم: <b>{ayah}</b> | 🏷️ المجموعة: <b>{g_id}</b></p>
                <p style='font-size: 15px; color: #BDC3C7;'>💡 المقصد: <b>{notes}</b></p>
            </div>
            """,
                    unsafe_allow_html=True,
                )

        elif res_type == "quran":
            if res_data:
                st.info(
                    f"ℹ️ الكلمة غير موجودة في حصرك الجديد. تم العثور على {len(res_data)}"
                    f" آية في **المصحف الشامل** تحتوي على: '{current_word}'"
                )

                with st.form(key="batch_save_form"):
                    st.markdown(
                        "### 📋 جدول تدبر وحفظ الآيات (الآيات التي تحفظها ستختفي، وتظل"
                        " البقية لمراجعتها)"
                    )

                    batch_inputs = []
                    for idx, row in enumerate(res_data, 1):
                        surah_name = row["surah_name"]
                        ayah_num = row["ayah_number"]
                        ayah_text = row["ayah_text"]

                        default_group = surah_group_map.get(surah_name, 1)

                        st.markdown(
                            f"""
                <div style='background-color: #34495E; padding: 10px; border-radius: 6px; margin-top: 10px;'>
                    <p class='quran-ayah'>{idx}. {ayah_text}</p>
                    <p style='font-size: 13px; color: #ECF0F1;'>📖 سورة: <b>{surah_name}</b> | آية رقم: <b>{ayah_num}</b></p>
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
                        remaining_res_data = []

                        for item in batch_inputs:
                            if item["note"].strip():
                                insert_data = {
                                    "word_code": 0,
                                    "topic_or_keyword": current_word,
                                    "group_id": item["group_id"],
                                    "surah_serial": 0,
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
                                remaining_res_data.append(
                                    {
                                        "surah_name": item["surah_name"],
                                        "ayah_number": item["ayah_num"],
                                        "ayah_text": item["ayah_text"],
                                    }
                                )

                        if success_count > 0:
                            st.session_state.success_message = (
                                f"🎉 تم بنجاح حفظ {success_count} آية مرتبطة بكلمة"
                                f" '{current_word}'!"
                            )
                            if remaining_res_data:
                                st.session_state.search_results = {
                                    "type": "quran",
                                    "data": remaining_res_data,
                                }
                            else:
                                st.session_state.search_results = []
                            st.rerun()
                        else:
                            st.warning(
                                "⚠️ يرجى كتابة المقصد لآية واحدة على الأقل قبل الضغط على زر الحفظ."
                            )
            else:
                st.warning(
                    f"❌ لم يتم العثور على أي نتائج مطابقة للبحث عن: '{current_word}'."
                )

# التبويب الثاني: البحث التحليلي والموضوعي
with tab2:
    st.subheader("البحث المتقدم في الكلمات المحصورة والمقاصد والمجموعات الثمانية")
    analysis_query = st.text_input(
        "أدخل الكلمة أو الموضوع للبحث في التحليلات:",
        placeholder="مثال: سنن، سنة الأولين...",
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
        if analysis_query:
            query_builder = query_builder.ilike(
                "topic_or_keyword", f"%{analysis_query}%"
            )
        if group_filter != "الكل":
            g_num = int(group_filter.replace("المجموعة ", ""))
            query_builder = query_builder.eq("group_id", g_num)

        response = query_builder.execute()
        analysis_results = response.data

        if analysis_results:
            st.success(f"✅ تم العثور على {len(analysis_results)} سجل تحليلي مطابق.")
            for record in analysis_results:
                word = record.get("topic_or_keyword", "-")
                g_id = record.get("group_id", "-")
                notes = record.get("notes", "-")
                surah = record.get("surah_name", "-")
                ayah = record.get("ayah_number", "-")
                text = record.get("ayah_text", "")
                st.markdown(
                    f"""
            <div style='background-color: #34495E; padding: 12px; border-radius: 6px; margin-bottom: 8px;'>
                <p style='margin: 0; font-weight: bold; color: #F39C12;'>الكلمة / الموضوع: {word} | المجموعة {g_id}</p>
                <p class='quran-ayah' style='font-size: 16px; margin: 4px 0;'>{text} ({surah}: {ayah})</p>
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
