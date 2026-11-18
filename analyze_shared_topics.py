import io
import pandas as pd
import streamlit as st
from supabase import create_client

# 1. إعدادات الصفحة والهوية البصرية
st.set_page_config(
    page_title="مستكشف الآيات المشتركة والموضوعات الكبرى",
    page_icon="📖",
    layout="wide",
)

st.markdown(
    "<h1 style='text-align: center; color: #D4AC0D;'>📖 مستكشف الآيات المشتركة والموضوعات المتعددة</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #666666;'>استكشاف وتحليل الآيات التي تحوي أكثر من موضوع أو كلمة حصر، مع لوحة مؤشرات تفاعلية وترتيب مصحفي دقيق وربط مباشر بالمقاصد وأرقام الصفحات.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")


# 2. الاتصال بقاعدة بيانات Supabase
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


supabase = init_supabase()


# جلب البيانات من الـ View الجديد المعتمد (v_ayah_relations_with_pages)
@st.cache_data(ttl=60)
def fetch_ayah_relations():
    try:
        response = supabase.table("v_ayah_relations_with_pages").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء جلب البيانات: {e}")
        return pd.DataFrame()


df_all = fetch_ayah_relations()

if df_all.empty:
    st.error(
        "❌ لا توجد بيانات متاحة في العرض (v_ayah_relations_with_pages). تأكد من إنشاء الـ SQL View في Supabase."
    )
else:
    # 3. التجميع والتحليل الإحصائي للآيات حسب الترتيب المصحفي (surah_serial)
    agg_df = (
        df_all.groupby(
            ["surah_serial", "surah_name", "ayah_number", "ayah_text", "page_number"]
        )
        .agg(
            topics_count=("topic_or_keyword", "count"),
            topics_list=(
                "topic_or_keyword",
                lambda x: " ، ".join(
                    sorted(list(set(str(v) for v in x if pd.notna(v))))
                ),
            ),
            groups_list=(
                "group_id",
                lambda x: " ، ".join(map(str, sorted(list(set(map(int, x)))))),
            ),
        )
        .reset_index()
    )

    # ترتيب تصاعدي حسب الترتيب المصحفي الدقيق
    agg_df = agg_df.sort_values(by=["surah_serial", "ayah_number"]).reset_index(
        drop=True
    )

    # فصل الآيات المشتركة (التي تحتوي على أكثر من موضوع) عن بقية الآيات
    multi_topic_df = agg_df[agg_df["topics_count"] > 1].reset_index(drop=True)

    # 4. لوحة المؤشرات السريعة (KPIs)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("إجمالي الارتباطات الكلية بالأساس", len(df_all))
    with col2:
        st.metric("إجمالي الآيات الفريدة المحللة", len(agg_df))
    with col3:
        st.metric("الآيات المشتركة (تحوي أكثر من موضوع)", len(multi_topic_df))

    st.markdown("---")

    # 5. تبويبات العرض (الجدول الشامل مقابل البحث العميق والتدبر)
    tab1, tab2 = st.tabs(
        ["📊 الجدول الشامل للآيات المشتركة", "🔍 العرض التحليلي والتدبر العميق للآيات"]
    )

    with tab1:
        st.subheader("📋 جدول الآيات التي تقاطعت فيها موضوعات الحصر")

        # فلتر اختياري لتصفية الحد الأدنى للتكرار
        max_t_count = int(agg_df["topics_count"].max()) if not agg_df.empty else 1
        min_freq_filter = st.slider(
            "تصفية الحد الأدنى لعدد الموضوعات المشتركة بالآية:",
            min_value=1,
            max_value=max_t_count,
            value=2,  # الافتراضي يبدأ بالآيات المشتركة (2 فأكثر)
            key="slider_min_freq",
        )

        filtered_master = agg_df[agg_df["topics_count"] >= min_freq_filter]

        display_master = filtered_master[
            [
                "surah_serial",
                "surah_name",
                "ayah_number",
                "page_number",
                "topics_count",
                "topics_list",
                "groups_list",
            ]
        ].copy()

        display_master.columns = [
            "رقم السورة",
            "اسم السورة",
            "رقم الآية",
            "رقم الصفحة",
            "عدد الموضوعات",
            "الكلمات والموضوعات المشتركة",
            "المجموعات المرتبطة",
        ]

        st.dataframe(display_master, width= "stretch", hide_index=True)

        # زر تصدير التقرير إلى Excel
        st.markdown("---")
        output_master = io.BytesIO()
        with pd.ExcelWriter(output_master, engine="xlsxwriter") as writer:
            display_master.to_excel(writer, index=False, sheet_name="الآيات_المشتركة")

        st.download_button(
            label="📥 تصدير تقرير الآيات المشتركة إلى ملف Excel احترافي",
            data=output_master.getvalue(),
            file_name="shared_ayahs_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    with tab2:
        st.subheader("🔍 استعراض تفصيلي ومقاصدي لكل آية مشتركة")

        surahs_with_multi = sorted(multi_topic_df["surah_name"].unique().tolist())
        if not surahs_with_multi:
            st.warning("⚠️ لا توجد آيات مشتركة حالياً بالحدود المطلوبة.")
        else:
            col_b1, col_b2 = st.columns([1, 2])
            with col_b1:
                selected_deep_surah = st.selectbox(
                    "اختر السورة:", surahs_with_multi, key="deep_surah_sel"
                )

            filtered_deep_df = multi_topic_df[
                multi_topic_df["surah_name"] == selected_deep_surah
            ]

            ayah_options_map = {}
            for _, r in filtered_deep_df.iterrows():
                lbl = f"آية {r['ayah_number']} (صفحة {r['page_number']}) [عدد الموضوعات: {r['topics_count']}]"
                ayah_options_map[lbl] = int(r["ayah_number"])

            with col_b2:
                selected_ayah_lbl = st.selectbox(
                    "اختر الآية للاستعراض المقاصدي:",
                    list(ayah_options_map.keys()),
                    key="deep_ayah_sel",
                )

            if selected_ayah_lbl:
                target_ayah_num = ayah_options_map[selected_ayah_lbl]

                # جلب تفاصيل هذه الآية تحديداً من الجدول الشامل df_all
                ayah_details = df_all[
                    (df_all["surah_name"] == selected_deep_surah)
                    & (df_all["ayah_number"] == target_ayah_num)
                ]

                if not ayah_details.empty:
                    first_row = ayah_details.iloc[0]

                    st.markdown(
                        f"""
                        <div style='background-color: #1E1E1E; padding: 20px; border-radius: 8px; border-right: 5px solid #D4AC0D; margin-top: 15px; margin-bottom: 15px;'>
                            <p style='color: #F1C40F; font-size: 1.1rem; margin-bottom: 5px;'>سورة {selected_deep_surah} - الآية ({target_ayah_num}) | رقم الصفحة: ({first_row['page_number']})</p>
                            <p style='font-size: 1.3rem; font-weight: bold; color: #FFFFFF; line-height: 1.9; text-align: right;'>{first_row['ayah_text']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        "##### 📌 تفاصيل الموضوعات، المجموعات، والمقاصد المرتبطة بهذه الآية:"
                    )

                    details_display = ayah_details[
                        ["topic_or_keyword", "group_id", "notes"]
                    ].copy()

                    details_display.columns = [
                        "الكلمة / الموضوع",
                        "رقم المجموعة",
                        "المقاصد والملاحظات (Notes)",
                    ]

                    st.dataframe(
                        details_display, width= "stretch", hide_index=True
                    )
