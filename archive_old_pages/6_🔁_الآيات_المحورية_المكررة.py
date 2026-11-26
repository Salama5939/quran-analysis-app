import pandas as pd
import streamlit as st
import theme  # استدعاء ملف التنسيق المركزي لضمان اتجاه RTL
from database import convert_df_to_excel, supabase  # الاستيراد المركزي المعتمد

# 1. إعدادات الصفحة المستقلة الجديدة
st.set_page_config(
    page_title="تحليل الآيات المحورية الأكثر ارتباطاً وتكراراً",
    page_icon="🔁",
    layout="wide",
)

# تطبيق التنسيق المركزي الموحد وزر الرئيسية
theme.apply_custom_theme()
theme.add_home_button()


# دالة مساعدة لعكس ترتيب الأعمدة بصرياً (RTL) للعرض دون المساس بالجدول الأصلي
def prepare_rtl_display_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    return df.iloc[:, ::-1].copy()


st.markdown(
    "<h1 style='text-align: center; color: #F1C40F;'>🔁 تحليل الآيات المحورية الأكثر ارتباطاً وتكراراً</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #BDC3C7;'>استعرض الآيات التي تتقاطع فيها عدة موضوعات وكلمات محصورة لتعرف الآيات المحورية الكبرى في التدبر القرآني (معتمدة على العرض السحابي الموحد).</p>",
    unsafe_allow_html=True,
)
st.markdown("---")


# 2. جلب البيانات حصرياً من الـ View السحابي المركزي (v_ayah_relations_with_pages)
@st.cache_data(ttl=60)
def fetch_ayah_relations_from_view():
    try:
        response = supabase.table("v_ayah_relations_with_pages").select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء جلب البيانات من العرض السحابي: {e}")
        return pd.DataFrame()


with st.spinner("جاري جلب وتحليل ارتباطات الآيات من العرض السحابي المعتمد..."):
    df_relations = fetch_ayah_relations_from_view()

if not df_relations.empty:
    # تحديد اسم عمود رقم السورة بدقة ديناميكية
    surah_col = (
        "surah_number"
        if "surah_number" in df_relations.columns
        else (
            "surah_serial"
            if "surah_serial" in df_relations.columns
            else df_relations.columns[0]
        )
    )

    # 3. تجميع البيانات حسب الآية لحساب عدد الموضوعات المرتبطة
    try:
        df_pivoted = (
            df_relations.groupby([surah_col, "surah_name", "ayah_number", "ayah_text"])
            .agg(
                عدد_الموضوعات_المرتبطة=("topic_or_keyword", "count"),
                الموضوعات_والكلمات=(
                    "topic_or_keyword",
                    lambda x: " ، ".join(
                        sorted(list(set(str(v) for v in x if pd.notna(v))))
                    ),
                ),
                المجموعات_المشاركة=(
                    "group_id",
                    lambda x: " ، ".join(
                        map(
                            str,
                            sorted(list(set(map(int, [v for v in x if pd.notna(v)])))),
                        )
                    ),
                ),
            )
            .reset_index()
        )
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء تجميع البيانات: {e}")
        st.stop()

    # خيار اختيار طريقة الترتيب
    col_opt1, _ = st.columns([2, 2])
    with col_opt1:
        sort_method = st.radio(
            "اختر طريقة ترتيب الجدول:",
            [
                "ترتيب حسب المصحف الشريف (رقم السورة ثم الآية)",
                "ترتيب تنازلي حسب الأكثر ارتباطاً وتكراراً",
            ],
            horizontal=True,
        )

    if sort_method == "ترتيب حسب المصحف الشريف (رقم السورة ثم الآية)":
        df_pivoted = df_pivoted.sort_values(
            by=[surah_col, "ayah_number"], ascending=[True, True]
        ).reset_index(drop=True)
    else:
        df_pivoted = df_pivoted.sort_values(
            by="عدد_الموضوعات_المرتبطة", ascending=False
        ).reset_index(drop=True)

    # المؤشرات العليا (KPIs)
    total_unique_ayahs_touched = len(df_pivoted)
    max_repeated_count = (
        int(df_pivoted["عدد_الموضوعات_المرتبطة"].max()) if not df_pivoted.empty else 0
    )

    c1, c2 = st.columns(2)
    with c1:
        st.metric(
            label="إجمالي الآيات الفريدة المرتبطة بالموضوعات",
            value=total_unique_ayahs_touched,
        )
    with c2:
        st.metric(
            label="أقصى عدد موضوعات في آية واحدة (محورية كبرى)",
            value=max_repeated_count,
        )

    st.markdown("---")
    st.markdown("### 📋 جدول الآيات المحورية والمكررة")

    min_freq_filter = st.slider(
        "تصفية الحد الأدنى لعدد الموضوعات المرتبطة بالآية:",
        min_value=1,
        max_value=max_repeated_count if max_repeated_count > 0 else 1,
        value=1,
    )

    df_filtered_view = df_pivoted[
        df_pivoted["عدد_الموضوعات_المرتبطة"] >= min_freq_filter
    ]

    table_display_df = df_filtered_view[
        [
            surah_col,
            "surah_name",
            "ayah_number",
            "ayah_text",
            "عدد_الموضوعات_المرتبطة",
            "الموضوعات_والكلمات",
            "المجموعات_المشاركة",
        ]
    ].copy()

    table_display_df.columns = [
        "رقم السورة",
        "اسم السورة",
        "رقم الآية",
        "منطوق الآية",
        "عدد الموضوعات المرتبطة",
        "الموضوعات والكلمات المشتركة",
        "المجموعات",
    ]

    st.success(f"✅ تم العثور على ({len(table_display_df)}) آية مطابقة لشروط الفلتر.")

    # نسخة العرض البصري المستقلة RTL مع الإبقاء على table_display_df للتصدير إلى Excel
    rtl_table_df = prepare_rtl_display_df(table_display_df)

    st.dataframe(
        rtl_table_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "رقم السورة": st.column_config.NumberColumn(
                "رقم السورة", width="small", format="%d"
            ),
            "اسم السورة": st.column_config.TextColumn("اسم السورة", width="medium"),
            "رقم الآية": st.column_config.NumberColumn(
                "رقم الآية", width="small", format="%d"
            ),
            "منطوق الآية": st.column_config.TextColumn(
                "منطوق الآية",
                width="large",
                help="انقر مرتين لتوسعة وعرض الآية بالكامل",
            ),
            "عدد الموضوعات المرتبطة": st.column_config.NumberColumn(
                "عدد الموضوعات المرتبطة", width="small", format="%d"
            ),
            "الموضوعات والكلمات المشتركة": st.column_config.TextColumn(
                "الموضوعات والكلمات المشتركة",
                width="large",
                help="انقر مرتين لعرض كافة الموضوعات",
            ),
            "المجموعات": st.column_config.TextColumn("المجموعات", width="small"),
        },
    )

    # استخدام دالة التصدير المركزية من database.py مع table_display_df الأصلي
    excel_data_ayahs = convert_df_to_excel(
        table_display_df, sheet_name="الآيات_المحورية"
    )
    st.download_button(
        label="📥 تصدير تقرير الآيات المحورية والمكررة إلى ملف Excel احترافي",
        data=excel_data_ayahs,
        file_name="تقرير_الآيات_المحورية_المكررة.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

else:
    st.warning("⚠️ لا توجد بيانات ارتباطات كافية في العرض السحابي لعرض التقرير حالياً.")
