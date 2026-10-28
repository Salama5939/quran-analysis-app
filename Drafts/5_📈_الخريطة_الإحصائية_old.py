import os
import pandas as pd
import plotly.express as px  # استيراد مكتبة Plotly للرسوم التفاعلية المتقدمة
import streamlit as st
from supabase import Client, create_client
import theme  # استدعاء ملف التنسيق المركزي

# إعدادات الصفحة المستقلة
st.set_page_config(
    page_title="الخريطة الإحصائية ولوحة المؤشرات التحليلية",
    page_icon="📈",
    layout="wide",
)

# تطبيق التنسيق المركزي الموحد
theme.apply_custom_theme()

st.markdown(
    "<h1 style='text-align: center; color: #F1C40F;'>📈 الخريطة الإحصائية"
    " ولوحة المؤشرات التحليلية</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #BDC3C7;'>استعرض التحليلات المرئية"
    " المتقدمة لتوزيع الكلمات، المجموعات الثمانية، ومؤشرات التدبر القرآني بأعلى"
    " دقة.</p>",
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

# جلب البيانات التحليلية وتجاوز حد الـ 1000 سجل عبر جلب كافة البيانات
with st.spinner("جاري جلب وحساب البيانات الإحصائية الشاملة من الخادم..."):
    all_dash_data = []
    batch_size = 1000
    start = 0

    # حلقة التكرار لجلب كافة السجلات بدون انقطاع عند حد الـ 1000
    while True:
        resp = (
            supabase.table("ayah_group_relations")
            .select("topic_or_keyword, group_id, frequency_count, surah_name")
            .range(start, start + batch_size - 1)
            .execute()
        )
        batch_data = resp.data if resp.data else []
        if not batch_data:
            break
        all_dash_data.extend(batch_data)
        if len(batch_data) < batch_size:
            break
        start += batch_size

if all_dash_data:
    df_dash = pd.DataFrame(all_dash_data)
    df_dash["group_id"] = pd.to_numeric(df_dash["group_id"], errors="coerce").fillna(1)

    # 1. المؤشرات العليا الحيوية (KPI Metrics Cards)
    total_relations = len(df_dash)  # يعكس الآن العدد الحقيقي الكامل (أكثر من 2500 سجل)
    total_unique_words = df_dash["topic_or_keyword"].nunique()
    total_groups = df_dash["group_id"].nunique()
    total_surahs_touched = df_dash["surah_name"].nunique()

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric(label="إجمالي سجلات الربط والآيات", value=total_relations)
    with col_m2:
        st.metric(label="إجمالي الكلمات الفريدة المحصورة", value=total_unique_words)
    with col_m3:
        st.metric(label="المجموعات المفعلة", value=total_groups)
    with col_m4:
        st.metric(label="السور المرتبطة بالحصر", value=total_surahs_touched)

    st.markdown("---")

    # 2. الرسوم البيانية باستخدام Plotly (واضحة، مائلة، واحترافية)
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("### 📊 توزيع الآيات حسب المجموعات الثمانية")
        group_counts = (
            df_dash.groupby("group_id")
            .size()
            .reset_index(name="عدد_الآيات")
            .sort_values(by="group_id")
        )
        group_counts["المجموعة"] = "المجموعة " + group_counts["group_id"].astype(str)

        # رسم بياني تفاعلي بـ Plotly
        fig_groups = px.bar(
            group_counts,
            x="المجموعة",
            y="عدد_الآيات",
            text="عدد_الآيات",
            color="عدد_الآيات",
            color_continuous_scale="Viridis",
        )
        fig_groups.update_layout(
            xaxis_title="المجموعات الثمانية",
            yaxis_title="عدد الآيات",
            xaxis_tickangle=-30,  # إمالة العناوين لتصبح واضحة تماماً
            font=dict(family="Amiri", size=14),
        )
        st.plotly_chart(fig_groups, use_container_width=True)

    with col_chart2:
        st.markdown("### 🏆 أكثر 10 كلمات تكراراً وارتباطاً")
        top_words = (
            df_dash.groupby("topic_or_keyword")
            .size()
            .reset_index(name="التكرار")
            .sort_values(by="التكرار", ascending=False)
            .head(10)
        )

        # رسم بياني تفاعلي بـ Plotly للكلمات الأكثر تكراراً
        fig_words = px.bar(
            top_words,
            x="topic_or_keyword",
            y="التكرار",
            text="التكرار",
            color="التكرار",
            color_continuous_scale="Blues",
        )
        fig_words.update_layout(
            xaxis_title="الكلمة / الموضوع",
            yaxis_title="عدد التكرارات",
            xaxis_tickangle=-45,  # إمالة عناوين الكلمات 45 درجة لتظهر بوضوح تام
            font=dict(family="Amiri", size=14),
        )
        st.plotly_chart(fig_words, use_container_width=True)

    st.markdown("---")

    # 3. جدول تحليلي إضافي تفصيلي للمجموعات مع ميزة تفاعلية
    st.markdown("### 📋 جدول الملخص الإحصائي لكل مجموعة")
    summary_group_df = (
        df_dash.groupby("group_id")
        .agg(
            عدد_الكلمات_المختلفة=("topic_or_keyword", "nunique"),
            إجمالي_الآيات_المرتبطة=("topic_or_keyword", "count"),
        )
        .reset_index()
    )
    summary_group_df.columns = [
        "رقم المجموعة",
        "عدد الكلمات المختلفة",
        "إجمالي الآيات المرتبطة",
    ]

    st.dataframe(
        summary_group_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "رقم المجموعة": st.column_config.NumberColumn(
                "رقم المجموعة", width="small", format="%d"
            ),
            "عدد الكلمات المختلفة": st.column_config.NumberColumn(
                "عدد الكلمات المختلفة", width="medium", format="%d"
            ),
            "إجمالي الآيات المرتبطة": st.column_config.NumberColumn(
                "إجمالي الآيات المرتبطة", width="medium", format="%d"
            ),
        },
    )

    # إضافة قسم تفاعلي عند اختيار المجموعة لاستعراض الكلمات المختلفة الخاصة بها
    st.markdown("---")
    st.markdown("### 🔍 استعراض تفاعلي: كلمات مجموعة معينة")
    selected_group_drill = st.selectbox(
        "اختر رقم المجموعة لعرض تفاصيل الكلمات المختلفة التابعة لها:",
        sorted(df_dash["group_id"].unique()),
        key="drill_down_group",
    )

    if selected_group_drill:
        filtered_group_df = (
            df_dash[df_dash["group_id"] == selected_group_drill][
                ["topic_or_keyword", "surah_name"]
            ]
            .drop_duplicates()
            .reset_index(drop=True)
        )
        filtered_group_df.columns = ["الكلمة المحصورة", "السورة"]
        st.info(
            f"📌 الكلمات والموضوعات المختلفة التابعة للمجموعة ({selected_group_drill})"
            f" وعددها ({len(filtered_group_df)} كلمة):"
        )
        st.dataframe(
            filtered_group_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "الكلمة المحصورة": st.column_config.TextColumn(
                    "الكلمة المحصورة", width="medium"
                ),
                "السورة": st.column_config.TextColumn("السورة", width="medium"),
            },
        )

else:
    st.warning("⚠️ لا توجد بيانات إحصائية كافية لعرض لوحة المؤشرات حالياً.")
