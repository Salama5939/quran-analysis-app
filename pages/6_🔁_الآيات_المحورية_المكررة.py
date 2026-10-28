import io
import os
import pandas as pd
import streamlit as st
from supabase import Client, create_client
import theme  # استدعاء ملف التنسيق المركزي لضمان اتجاه RTL

# إعدادات الصفحة المستقلة الجديدة
st.set_page_config(
    page_title="تحليل الآيات المحورية الأكثر ارتباطاً وتكراراً",
    page_icon="🔁",
    layout="wide",
)

# تطبيق التنسيق المركزي الموحد
theme.apply_custom_theme()

# إضافة زر العودة السريع للرئيسية
theme.add_home_button()

st.markdown(
    "<h1 style='text-align: center; color: #F1C40F;'>🔁 تحليل الآيات المحورية"
    " الأكثر ارتباطاً وتكراراً</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #BDC3C7;'>استعرض الآيات التي تتقاطع"
    " فيها عدة موضوعات وكلمات محصورة لتعرف الآيات المحورية الكبرى في التدبر"
    " القرآني.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# الاتصال الآمن بقاعدة بيانات Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url:
    try:
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "")
    except Exception:
        pass

if not url or not key:
    st.error("❌ خطأ: لم يتم العثور على مفاتيح الاتصال بـ Supabase.")
    st.stop()

supabase: Client = create_client(url, key)


# دالة تصدير البيانات إلى Excel
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="الآيات_المحورية")
    processed_data = output.getvalue()
    return processed_data


# جلب كافة بيانات الارتباطات من الخادم
with st.spinner("جاري جلب وتحليل ارتباطات الآيات بالكلمات من الخادم..."):
    all_relations_data = []
    batch_size = 1000
    start = 0

    while True:
        resp = (
            supabase.table("ayah_group_relations")
            .select(
                "topic_or_keyword, group_id, surah_serial, surah_name, ayah_number,"
                " ayah_text"
            )
            .range(start, start + batch_size - 1)
            .execute()
        )
        batch_data = resp.data if resp.data else []
        if not batch_data:
            break
        all_relations_data.extend(batch_data)
        if len(batch_data) < batch_size:
            break
        start += batch_size

if all_relations_data:
    df_relations = pd.DataFrame(all_relations_data)

    # تجميع البيانات حسب الآية (السورة ورقم الآية ومنطوقها) لحساب عدد الموضوعات المرتبطة
    df_pivoted = (
        df_relations.groupby(["surah_serial", "surah_name", "ayah_number", "ayah_text"])
        .agg(
            عدد_الموضوعات_المرتبطة=("topic_or_keyword", "count"),
            الموضوعات_والكلمات=(
                "topic_or_keyword",
                lambda x: " ، ".join(sorted(list(set(x)))),
            ),
            المجموعات_المشاركة=(
                "group_id",
                lambda x: " ، ".join(map(str, sorted(list(set(map(int, x)))))),
            ),
        )
        .reset_index()
    )

    # خيار اختيار طريقة الترتيب لتسهيل التدبر والقراءة
    col_opt1, col_opt2 = st.columns([2, 2])
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
            by=["surah_serial", "ayah_number"], ascending=[True, True]
        ).reset_index(drop=True)
    else:
        df_pivoted = df_pivoted.sort_values(
            by="عدد_الموضوعات_المرتبطة", ascending=False
        ).reset_index(drop=True)

    # المؤشرات العليا
    total_unique_ayahs_touched = len(df_pivoted)
    max_repeated_count = (
        df_pivoted["عدد_الموضوعات_المرتبطة"].max() if not df_pivoted.empty else 0
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

    # فلتر اختياري لتصفية الآيات حسب الحد الأدنى للتكرار
    min_freq_filter = st.slider(
        "تصفية الحد الأدنى لعدد الموضوعات المرتبطة بالآية:",
        min_value=1,
        max_value=int(max_repeated_count),
        value=1,
    )

    df_filtered_view = df_pivoted[
        df_pivoted["عدد_الموضوعات_المرتبطة"] >= min_freq_filter
    ]

    # إعادة تسمية الأعمدة لتظهر باحترافية تامة
    table_display_df = df_filtered_view[
        [
            "surah_serial",
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

    # عرض الجدول المتقدم مع إمكانية التوسعة بالنقر المزدوج
    st.dataframe(
        table_display_df,
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

    # زر تصدير التقرير إلى Excel
    excel_data_ayahs = convert_df_to_excel(table_display_df)
    st.download_button(
        label="📥 تصدير تقرير الآيات المحورية والمكررة إلى ملف Excel احترافي",
        data=excel_data_ayahs,
        file_name="تقرير_الآيات_المحورية_المكررة.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

else:
    st.warning("⚠️ لا توجد بيانات ارتباطات كافية لعرض التقرير حالياً.")
