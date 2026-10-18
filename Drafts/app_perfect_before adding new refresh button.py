import os
import pandas as pd
import streamlit as st
from supabase import Client, create_client

# إعدادات صفحة Streamlit
st.set_page_config(
    page_title="النظام التحليلي للتدبر القرآني", page_icon="📖", layout="wide"
)

# دعم الاتجاه من اليمين لليسار والتنسيق الاحترافي
st.markdown(
    """
    <style>
    body, html, [class*="css"] {
        direction: RTL;
        text-align: right;
        font-family: 'Amiri', 'Traditional Arabic', sans-serif;
    }
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stTextArea textarea {
        text-align: right;
    }
    h1, h2, h3 {
        color: #FFFFFF !important;
    }
    .main-header {
        text-align: center; 
        color: #F1C40F !important;
        font-weight: bold;
    }
    .sub-header {
        text-align: center; 
        color: #ECF0F1 !important;
    }
    .quran-ayah {
        font-size: 20px;
        color: #F1C40F;
        font-family: 'Amiri', serif;
        line-height: 1.6;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# الاتصال بـ Supabase
url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")

if not url or not key:
    st.error("❌ خطأ: لم يتم العثور على مفاتيح الاتصال بـ Supabase.")
    st.stop()

supabase: Client = create_client(url, key)


# تحميل ملف ربط السور بالمجموعات لتحديد المجموعة تلقائياً
@st.cache_data
def load_surah_group_mapping():
    mapping_file = "ملف ربط المجموعات الثمانبة بالسور.xlsx"
    if os.path.exists(mapping_file):
        df_map = pd.read_excel(mapping_file, sheet_name=0)
        # بناء قاموس يربط اسم السورة برقم المجموعة
        mapping = {}
        for _, row in df_map.iterrows():
            s_name = str(row["إسم السورة"]).strip()
            g_num = int(row["رقم المجموعة"])
            mapping[s_name] = g_num
        return mapping
    return {}


surah_group_map = load_surah_group_mapping()

# العنوان الرئيسي
st.markdown(
    "<h1 class='main-header'>📖 النظام التحليلي للتدبر القرآني والإضافة" " الذكية</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p class='sub-header'>بحث مزدوج دقيق، استنتاج تلقائي للمجموعات، وحفظ"
    " جماعي للتدبر.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# تقسيم الواجهة إلى تبويبات
tab1, tab2, tab3 = st.tabs(
    [
        "🔍 البحث والتدبر الذكي (مُحدّث)",
        "📊 البحث التحليلي والموضوعي",
        "📖 استعراض السور والمجموعات",
    ]
)

# ==========================================
# التبويب الأول: البحث والتدبر الذكي والحفظ الجماعي
# ==========================================
with tab1:
    st.subheader("البحث الفوري أولاً في الحصر المعتمد، ثم استكشاف المصحف الشامل")
    search_query = st.text_input(
        "أدخل الكلمة أو العبارة بدقة (مثل: العليم، الغفار، سنن):",
        placeholder="اكتب الكلمة هنا...",
        key="search_input",
    )

    # الاحتفاظ بالنتائج في الذاكرة المؤقتة للجلسة لمنع مسحها عند التفاعل
    if "search_results" not in st.session_state:
        st.session_state.search_results = {}
    if "searched_word" not in st.session_state:
        st.session_state.searched_word = ""

    col_s1, col_s2 = st.columns([1, 5])
    with col_s1:
        search_button = st.button("🔍 بحث شامل")

    if search_button and search_query:
        with st.spinner("جاري البحث الذكي..."):
            raw_query = search_query.strip()
            st.session_state.searched_word = raw_query

            # 1. البحث أولاً في جدول الحصر المعتمد (ayah_group_relations)
            response = (
                supabase.table("ayah_group_relations")
                .select("*")
                .ilike("topic_or_keyword", f"%{raw_query}%")
                .execute()
            )
            hsor_results = response.data

            if hsor_results:
                seen_notes = set()
                unique_hsor = []
                for r in hsor_results:
                    note = r.get("notes", "")
                    if note not in seen_notes:
                        seen_notes.add(note)
                        unique_hsor.append(r)

                st.session_state.search_results = {"type": "hsor", "data": unique_hsor}
            else:
                # 2. إذا لم توجد في الحصر القديم، نبحث في المصحف الشامل (full_quran)
                quran_res = (
                    supabase.table("full_quran")
                    .select("*")
                    .ilike("ayah_text", f"%{raw_query}%")
                    .execute()
                )
                st.session_state.search_results = {
                    "type": "quran",
                    "data": quran_res.data if quran_res.data else [],
                }

    # عرض النتائج من ذاكرة الجلسة
    if st.session_state.search_results:
        res_type = st.session_state.search_results["type"]
        res_data = st.session_state.search_results["data"]
        current_word = st.session_state.searched_word

        if res_type == "hsor":
            st.success(
                f"✅ تم العثور على {len(res_data)} نتيجة مطابقة في **حصرك"
                f" المعتمد** للبحث عن: '{current_word}'"
            )
            for idx, row in enumerate(res_data, 1):
                word = row.get("topic_or_keyword", "-")
                g_id = row.get("group_id", "-")
                notes = row.get("notes", "-")
                st.markdown(
                    f"""
                <div style='background-color: #2C3E50; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-right: 5px solid #27AE60;'>
                    <p style='font-size: 18px; font-weight: bold; color: #F1C40F;'>{idx}. الكلمة / الموضوع: {word}</p>
                    <p style='font-size: 16px; color: #FFFFFF; margin: 8px 0;'>📜 <b>{notes}</b></p>
                    <p style='font-size: 14px; color: #BDC3C7;'>🏷️ التصنيف: المجموعة رقم {g_id}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

        elif res_type == "quran":
            if res_data:
                st.success(
                    f"ℹ️ الكلمة غير موجودة في حصرك القديم. تم العثور على"
                    f" {len(res_data)} آية في **المصحف الشامل** تحتوي على:"
                    f" '{current_word}'"
                )

                # نموذج التدبر والحفظ الجماعي (Batch Save Form)
                with st.form(key="batch_save_form"):
                    st.markdown(
                        "### 📋 جدول تدبر وحفظ الآيات (تم تحديد رقم المجموعة تلقائياً بناءً"
                        " على السورة)"
                    )

                    batch_inputs = []
                    for idx, row in enumerate(res_data, 1):
                        surah_name = row["surah_name"]
                        ayah_num = row["ayah_number"]
                        ayah_text = row["ayah_text"]

                        # الاستنتاج التلقائي لرقم المجموعة من ملف الربط (افتراضي 1 إذا لم يوجد)
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
                            # ضبط المؤشر (index) ليطابق المجموعة المستنتجة تلقائياً (من 1 إلى 8 -> index من 0 إلى 7)
                            g_index = max(0, min(default_group - 1, 7))
                            g_val = st.selectbox(
                                "المجموعة:",
                                range(1, 9),
                                index=g_index,
                                key=f"batch_g_{idx}",
                            )
                        with col_n:
                            n_val = st.text_input(
                                "المقصد أو التدبر لهذه الآية:",
                                placeholder="اكتب مقصد الآية...",
                                key=f"batch_n_{idx}",
                            )

                        batch_inputs.append(
                            {
                                "surah_name": surah_name,
                                "ayah_num": ayah_num,
                                "group_id": g_val,
                                "note": n_val,
                            }
                        )

                    submit_batch = st.form_submit_button(
                        "💾 حفظ جميع الآيات المحددة دفعة واحدة (Batch Save)"
                    )

                    if submit_batch:
                        success_count = 0
                        for item in batch_inputs:
                            if item["note"].strip():
                                insert_data = {
                                    "topic_or_keyword": current_word,
                                    "frequency_count": 1,
                                    "group_id": item["group_id"],
                                    "notes": (
                                        f"مقصد: {item['note'].strip()} | سورة:"
                                        f" {item['surah_name']} | آية: {item['ayah_num']}"
                                    ),
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

                        if success_count > 0:
                            st.success(
                                f"🎉 تم بنجاح حفظ {success_count} آية مرتبطة بكلمة"
                                f" '{current_word}' إلى حصرك المعتمد دفعة واحدة!"
                            )
                        else:
                            st.warning(
                                "⚠️ يرجى كتابة المقصد لآية واحدة على الأقل قبل الحفظ."
                            )
            else:
                st.warning(
                    f"❌ لم يتم العثور على أي نتائج مطابقة للبحث عن: '{current_word}'."
                )

# ==========================================
# التبويب الثاني: البحث التحليلي والموضوعي
# ==========================================
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
            seen = set()
            unique_analysis = [
                r
                for r in analysis_results
                if r.get("notes") not in seen and not seen.add(r.get("notes"))
            ]
            st.success(f"✅ تم العثور على {len(unique_analysis)} سجل تحليلي مطابق.")
            for record in unique_analysis:
                word = record.get("topic_or_keyword", "-")
                g_id = record.get("group_id", "-")
                notes = record.get("notes", "-")
                st.markdown(
                    f"""
                <div style='background-color: #34495E; padding: 12px; border-radius: 6px; margin-bottom: 8px;'>
                    <p style='margin: 0; font-weight: bold; color: #F39C12;'>الكلمة / الموضوع: {word}</p>
                    <p style='margin: 5px 0 0 0; font-size: 14px; color: #ECF0F1;'>🏷️ المجموعة: <b>المجموعة {g_id}</b> | التفاصيل: {notes}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )
        else:
            st.warning("❌ لم يتم العثور على نتائج تحليلية مطابقة لشروط البحث.")

# ==========================================
# التبويب الثالث: استعراض السور والمجموعات
# ==========================================
with tab3:
    st.subheader("📖 هيكل السور والمجموعات الثمانية الأساسية")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("### قائمة المجموعات الثمانية (1-8)")
        groups_res = (
            supabase.table("groups_8").select("*").order("group_number").execute()
        )
        if groups_res.data:
            for g in groups_res.data:
                st.info(
                    f"🔹 **{g.get('group_name')}** (رقم المجموعة:"
                    f" {g.get('group_number')}) - المقصد العام:"
                    f" {g.get('group_objective')}"
                )
    with col_s2:
        st.markdown("### السور القرآنية (114 سورة)")
        surahs_res = (
            supabase.table("surahs")
            .select("surah_number, name_arabic, total_ayahs")
            .order("surah_number")
            .execute()
        )
        if surahs_res.data:
            for s in surahs_res.data:
                st.write(
                    f"▫️ سورة {s.get('name_arabic')} (رقم {s.get('surah_number')}) —"
                    f" عدد الآيات: {s.get('total_ayahs')}"
                )
