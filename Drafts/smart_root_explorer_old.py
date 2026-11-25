import streamlit as st
import pandas as pd
from theme import apply_custom_theme, add_home_button
from database import supabase, convert_df_to_excel, normalize_arabic, clean_dataframe_for_display

# 1. إعدادات الصفحة المستقلة
st.set_page_config(
    page_title="منصة الاستكشاف الذكي للجذور والمشتقات", page_icon="🔎", layout="wide"
)

# تطبيق التنسيق المركزي الموحد واتجاه RTL وزر الرئيسية
apply_custom_theme()
add_home_button()

st.title("🔎 منصة الاستكشاف الذكي للجذور والمشتقات القرآنية")
st.markdown(
    "<p style='text-align: center; color: #666666;'>منصة متقدمة للبحث الذكي في الجذور، الحصر الشامل للتقاطعات المعجمية، والحفظ في جداول مستقلة.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")


# جلب كافة بيانات المصحف الشريف من Supabase على دفعات لتجاوز حد الـ Limit
@st.cache_data(ttl=60)
def fetch_all_full_quran_for_roots():
    try:
        all_data = []
        batch_size = 1000
        start = 0
        while True:
            response = (
                supabase.table("full_quran")
                .select(
                    "surah_number, surah_name, ayah_number, ayah_text, plain_ayah_text, page_number"
                )
                .range(start, start + batch_size - 1)
                .execute()
            )
            batch = response.data if response.data else []
            if not batch:
                break
            all_data.extend(batch)
            if len(batch) < batch_size:
                break
            start += batch_size
        return pd.DataFrame(all_data) if all_data else pd.DataFrame()
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء جلب بيانات المصحف: {e}")
        return pd.DataFrame()


with st.spinner("جاري تحميل وتحليل بيانات المصحف الشريف..."):
    df_quran = fetch_all_full_quran_for_roots()

if df_quran.empty:
    st.warning("⚠️ لا توجد بيانات متاحة في جدول full_quran حالياً.")
else:
    # تقسيم المنصة إلى تبويبين رئيسيين
    tab1, tab2 = st.tabs(
        [
            "🔎 التبويب الأول: الاستكشاف الفردي للجذر والحفظ",
            "🔀 التبويب الثاني: الحصر الشامل للآيات ذات الجذور والكلمات المشتركة",
        ]
    )

    # -------------------------------------------------------------
    # TAB 1: الاستكشاف الفردي للجذر والحفظ المستقل
    # -------------------------------------------------------------
    with tab1:
        st.subheader("🔎 البحث الاستكشافي الموجه للجذر الواحد")
        st.markdown(
            "أدخل الجذر اللغوي لاستخراج كافة الآيات المرتبطة به واعتمادها في جدول `smart_root_topics`."
        )

        col_input1, col_input2 = st.columns([4, 1])
        with col_input1:
            root_input = st.text_input(
                "🔤 أدخل الجذر اللغوي أو الحروف (مثال: شكر، علم، رحم):",
                placeholder="اكتب الجذر هنا...",
                key="root_search_input_t1",
            )
        with col_input2:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            search_btn = st.button(
                "🚀 استخراج الآيات",
                type="primary",
                use_container_width=True,
                key="btn_search_t1",
            )

        if search_btn or root_input.strip():
            query_root = root_input.strip()
            norm_query = normalize_arabic(query_root)

            if len(norm_query) < 2:
                st.warning("⚠️ الرجاء إدخال حرفين على الأقل للبحث.")
            else:
                matched_rows = []
                for _, row in df_quran.iterrows():
                    plain_txt = str(row.get("plain_ayah_text", ""))
                    norm_plain = normalize_arabic(plain_txt)
                    if norm_query in norm_plain:
                        matched_rows.append(row)

                df_results = pd.DataFrame(matched_rows)

                st.markdown("---")
                st.subheader(
                    f"📊 نتائج البحث للجذر: ( {query_root} ) - عدد الآيات: {len(df_results)}"
                )

                if df_results.empty:
                    st.info("ℹ️ لم يتم العثور على آيات تطابق هذا الجذر.")
                else:
                    display_df = df_results[
                        [
                            "surah_number",
                            "surah_name",
                            "ayah_number",
                            "ayah_text",
                            "page_number",
                        ]
                    ].copy()
                    display_df.columns = [
                        "رقم السورة",
                        "اسم السورة",
                        "رقم الآية",
                        "منطوق الآية الكريمة",
                        "رقم الصفحة",
                    ]

                    st.dataframe(display_df, use_container_width=True, hide_index=True)

                    st.markdown("---")
                    st.subheader("💾 حفظ النتائج في جدول (smart_root_topics)")

                    with st.form("save_smart_root_form_t1"):
                        save_note = st.text_input(
                            "ملاحظات إضافية على الحفظ:", f"بحث آلي للجذر: {query_root}"
                        )
                        submitted_save = st.form_submit_button(
                            "📥 حفظ كافة النتائج في قاعدة البيانات"
                        )

                        if submitted_save:
                            try:
                                records_to_insert = []
                                for _, r in df_results.iterrows():
                                    records_to_insert.append(
                                        {
                                            "root_name": query_root,
                                            "derived_words": save_note,
                                            "surah_number": int(r["surah_number"]),
                                            "surah_name": str(r["surah_name"]),
                                            "ayah_number": int(r["ayah_number"]),
                                            "page_number": (
                                                int(r["page_number"])
                                                if pd.notna(r["page_number"])
                                                else 1
                                            ),
                                            "ayah_text": str(r["ayah_text"]),
                                        }
                                    )
                                supabase.table("smart_root_topics").insert(
                                    records_to_insert
                                ).execute()
                                st.success(
                                    f"✅ تم حفظ عدد ({len(records_to_insert)}) سجلاً بنجاح!"
                                )
                            except Exception as e:
                                st.error(f"❌ حدث خطأ أثناء الحفظ: {e}")

                    excel_data = convert_df_to_excel(
                        display_df, sheet_name=f"Root_{query_root}"
                    )
                    col_dl, _ = st.columns([2, 5])
                    with col_dl:
                        st.download_button(
                            label="📥 تصدير النتائج إلى Excel",
                            data=excel_data,
                            file_name=f"Smart_Root_{query_root}_Report.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                            key="dl_excel_t1",
                        )
        else:
            st.info(
                "👈 أدخل الجذر في الحقل أعلاه واضغط على زر **'استخراج الآيات'** للبدء."
            )

    # -------------------------------------------------------------
    # TAB 2: الحصر الشامل للآيات ذات الجذور والكلمات المشتركة
    # -------------------------------------------------------------
    with tab2:
        st.subheader("🔀 الحصر الشامل والتحليلي للتقاطعات المعجمية في المصحف")
        st.markdown(
            "يستعرض هذا الجدول تلقائياً الآيات التي تتقاطع في الألفاظ والمشتقات المتكررة عبر سور المصحف الشريف، مع إمكانية التصفية اللاحقة."
        )

        @st.cache_data
        def extract_shared_words_matrix(df):
            word_records = []
            for _, row in df.iterrows():
                plain = str(row.get("plain_ayah_text", ""))
                # تنظيف وتفكيك كلمات الآية
                words = [
                    w for w in plain.split() if len(w) > 2
                ]  # استبعاد الكلمات القصيرة جداً
                for w in set(
                    words
                ):  # استخدام set لمنع تكرار نفس الكلمة داخل الآية الواحدة
                    word_records.append(
                        {
                            "common_word": w,
                            "surah_number": row["surah_number"],
                            "surah_name": row["surah_name"],
                            "ayah_number": row["ayah_number"],
                            "ayah_text": row["ayah_text"],
                            "page_number": row["page_number"],
                        }
                    )
            if not word_records:
                return pd.DataFrame()

            w_df = pd.DataFrame(word_records)
            # تصفية الكلمات التي تكررت في أكثر من آية (مشتركة)
            counts = w_df.groupby("common_word")["ayah_text"].nunique().reset_index()
            shared_words = counts[counts["ayah_text"] > 1]["common_word"]

            filtered = w_df[w_df["common_word"].isin(shared_words)]
            return filtered.sort_values(
                by=["common_word", "surah_number", "ayah_number"]
            )

        with st.spinner("جاري استخراج وتحليل التقاطعات المعجمية في المصحف..."):
            df_shared = extract_shared_words_matrix(df_quran)

        if df_shared.empty:
            st.info("ℹ️ لا توجد تقاطعات كافية مطابقة بالشروط الحالية.")
        else:
            # فلترة تفاعلية لاحقة كما طلبت (بعد الاطلاع على الجدول الكلي)
            st.markdown("##### 🔍 أدوات التصفية والاطلاع الموجه:")
            unique_words_list = ["الكل (عرض كافة التقاطعات)"] + sorted(
                df_shared["common_word"].unique().tolist()
            )

            sel_word_filter = st.selectbox(
                "اختر كلمة أو مصطلحاً مشتركاً لتصفية النتائج لحظياً:",
                options=unique_words_list,
                key="word_filter_t2",
            )

            df_view_t2 = df_shared.copy()
            if sel_word_filter != "الكل (عرض كافة التقاطعات)":
                df_view_t2 = df_view_t2[df_view_t2["common_word"] == sel_word_filter]

            st.markdown(f"📊 **إجمالي السجلات المعروضة:** {len(df_view_t2)}")

            # تجهيز جدول العرض المعرب
            display_t2 = df_view_t2[
                [
                    "common_word",
                    "surah_number",
                    "surah_name",
                    "ayah_number",
                    "ayah_text",
                    "page_number",
                ]
            ].copy()
            display_t2.columns = [
                "الكلمة / المقطع المشترك",
                "رقم السورة",
                "اسم السورة",
                "رقم الآية",
                "منطوق الآية الكريمة",
                "رقم الصفحة",
            ]

            st.dataframe(display_t2, use_container_width=True, hide_index=True)

            # زر تصدير التبويب الثاني
            excel_data_t2 = convert_df_to_excel(
                display_t2, sheet_name="Shared_Roots_Matrix"
            )
            col_dl2, _ = st.columns([2, 5])
            with col_dl2:
                st.download_button(
                    label="📥 تصدير تقرير التقاطعات المعجمية إلى Excel",
                    data=excel_data_t2,
                    file_name="Shared_Lexical_Matrix_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="dl_excel_t2",
                )
