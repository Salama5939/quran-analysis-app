import io
import os
import pandas as pd
import plotly.express as px
import streamlit as st
from supabase import Client, create_client
import theme  # استدعاء ملف التنسيق المركزي

# إعدادات الصفحة المستقلة
st.set_page_config(
    page_title="الخريطة الإحصائية ولوحة المؤشرات التحليلية",
    page_icon="📈",
    layout="wide",
)

# تطبيق التنسيق المركزي الموحد وزر الرئيسية
theme.apply_custom_theme()
theme.add_home_button()

st.markdown(
    "<h1 style='text-align: center; color: #F1C40F;'>📈 الخريطة الإحصائية ولوحة المؤشرات التحليلية</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #BDC3C7;'>استعرض التحليلات المرئية المتقدمة لتوزيع الكلمات، المجموعات الثمانية، ومؤشرات التدبر القرآني بأعلى دقة واحترافية.</p>",
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


# دالة مساعدة لتصدير البيانات إلى ملف Excel منسق
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="التقرير_التحليلي")
    processed_data = output.getvalue()
    return processed_data


# جلب البيانات التحليلية الشاملة
@st.cache_data(ttl=60)
def fetch_all_dash_data():
    all_dash_data = []
    batch_size = 1000
    start = 0

    while True:
        resp = (
            supabase.table("ayah_group_relations")
            .select(
                "topic_or_keyword, group_id, frequency_count, surah_name,"
                " surah_serial, ayah_number, ayah_text, notes"
            )
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
    return all_dash_data


with st.spinner("جاري جلب وحساب البيانات الإحصائية الشاملة من الخادم..."):
    raw_data = fetch_all_dash_data()

if raw_data:
    df_dash = pd.DataFrame(raw_data)
    df_dash["group_id"] = pd.to_numeric(df_dash["group_id"], errors="coerce").fillna(1)
    df_dash["surah_serial"] = pd.to_numeric(
        df_dash["surah_serial"], errors="coerce"
    ).fillna(1)

    # 1. المؤشرات العليا الحيوية (KPIs)
    total_relations = len(df_dash)
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

    # 2. تقسيم الصفحة على رأسها إلى تبويبين رئيسيين مستقلين
    tab_stats, tab_drill = st.tabs(
        [
            "📊 التبويب الأول: الخريطة الإحصائية والرسوم البيانية",
            "🔍 التبويب الثاني: الاستعراض التفاعلي والبحث الموضوعي العميق",
        ]
    )

    # -------------------------------------------------------------------------
    # التبويب الأول: الخريطة الإحصائية والرسوم البيانية وملخص المجموعات
    # -------------------------------------------------------------------------
    with tab_stats:
        st.subheader("📊 التحليلات المرئية ومؤشرات التوزيع للمجموعات والكلمات")

        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown("##### 📌 توزيع الآيات حسب المجموعات الثمانية")
            group_counts = (
                df_dash.groupby("group_id")
                .size()
                .reset_index(name="عدد_الآيات")
                .sort_values(by="group_id")
            )
            group_counts["المجموعة"] = "المجموعة " + group_counts["group_id"].astype(
                str
            )

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
                xaxis_tickangle=-30,
                font=dict(family="Amiri", size=14),
            )
            st.plotly_chart(fig_groups, width= "stretch")

        with col_chart2:
            st.markdown("##### 🏆 أكثر 10 كلمات تكراراً وارتباطاً")
            top_words = (
                df_dash.groupby("topic_or_keyword")
                .size()
                .reset_index(name="التكرار")
                .sort_values(by="التكرار", ascending=False)
                .head(10)
            )

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
                xaxis_tickangle=-45,
                font=dict(family="Amiri", size=14),
            )
            st.plotly_chart(fig_words, width= "stretch")

        st.markdown("---")

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
            width= "stretch",
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

        excel_data_summary = convert_df_to_excel(summary_group_df)
        st.download_button(
            label="📥 تصدير جدول ملخص المجموعات إلى ملف Excel احترافي",
            data=excel_data_summary,
            file_name="التقرير_الإحصائي_للمجموعات.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    # -------------------------------------------------------------------------
    # التبويب الثاني: الاستعراض التفاعلي والبحث الموضوعي العميق
    # -------------------------------------------------------------------------
    with tab_drill:
        st.subheader("🔍 منصة الاستعراض التفاعلي المتقدم للكلمات والموضوعات والآيات")
        st.markdown(
            "استكشف تفاصيل الكلمات والموضوعات المرتبطة إما بالتصفية حسب المجموعات أو عبر القائمة المنسدلة المرتبة ترتيباً مصحفياً دقيقاً."
        )

        sub_tab1, sub_tab2 = st.tabs(
            [
                "📂 الاستعراض والبحث حسب المجموعة",
                "📖 الاستعراض الاستكشافي حسب السورة (ترتيب المصحف)",
            ]
        )

        with sub_tab1:
            selected_group_drill = st.selectbox(
                "🎯 اختر رقم المجموعة لعرض الكلمات والموضوعات والآيات التابعة لها:",
                sorted(df_dash["group_id"].unique()),
                key="drill_down_group",
            )
            if selected_group_drill:
                filtered_group_df = (
                    df_dash[df_dash["group_id"] == selected_group_drill][
                        [
                            "topic_or_keyword",
                            "surah_name",
                            "ayah_number",
                            "ayah_text",
                            "notes",
                        ]
                    ]
                    .drop_duplicates()
                    .reset_index(drop=True)
                )
                filtered_group_df.columns = [
                    "الكلمة المحصورة",
                    "السورة",
                    "رقم الآية",
                    "منطوق الآية",
                    "المقصد / ملاحظات",
                ]
                st.success(
                    f"📌 الكلمات والموضوعات والآيات التابعة للمجموعة ({selected_group_drill}) وعددها ({len(filtered_group_df)} سجل):"
                )
                st.dataframe(
                    filtered_group_df,
                    width= "stretch",
                    hide_index=True,
                    column_config={
                        "الكلمة المحصورة": st.column_config.TextColumn(
                            "الكلمة المحصورة", width="medium"
                        ),
                        "السورة": st.column_config.TextColumn("السورة", width="small"),
                        "رقم الآية": st.column_config.NumberColumn(
                            "رقم الآية", width="small", format="%d"
                        ),
                        "منطوق الآية": st.column_config.TextColumn(
                            "منطوق الآية", width="large"
                        ),
                        "المقصد / ملاحظات": st.column_config.TextColumn(
                            "المقصد / ملاحظات", width="large"
                        ),
                    },
                )

                excel_data_group = convert_df_to_excel(filtered_group_df)
                st.download_button(
                    label=f"📥 تصدير تفاصيل وموضوعات المجموعة ({selected_group_drill}) إلى Excel",
                    data=excel_data_group,
                    file_name=f"مجموعة_{selected_group_drill}_الآيات_والموضوعات.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

        with sub_tab2:
            st.markdown(
                "#### 📖 الاستعراض المصحفي المباشر للسور لاستعراض موضوعاتها وآياتها"
            )

            # استخراج قائمة السور الفريدة مرتبطة برقمها المصحفي وتثبيتها بالترتيب القرآني الصارم
            surahs_ordered = (
                df_dash[["surah_serial", "surah_name"]]
                .drop_duplicates()
                .sort_values("surah_serial")["surah_name"]
                .tolist()
            )

            if surahs_ordered:
                selected_surah_drill = st.selectbox(
                    "🎯 اختر السورة من القائمة المرتبطة بترتيب المصحف الشريف:",
                    options=surahs_ordered,
                    key="surah_ordered_selectbox_v7",
                )

                if selected_surah_drill:
                    final_surah_df = (
                        df_dash[df_dash["surah_name"] == selected_surah_drill][
                            [
                                "topic_or_keyword",
                                "group_id",
                                "ayah_number",
                                "ayah_text",
                                "notes",
                            ]
                        ]
                        .drop_duplicates()
                        .reset_index(drop=True)
                    )

                    final_surah_df.columns = [
                        "الكلمة الموضوعية المحصورة",
                        "رقم المجموعة",
                        "رقم الآية",
                        "منطوق الآية",
                        "المقصد / ملاحظات",
                    ]

                    st.success(
                        f"📖 الكلمات والموضوعات المحصورة والآيات المرتبطة بـ **(سورة {selected_surah_drill})** وعددها ({len(final_surah_df)} سجل):"
                    )
                    st.dataframe(
                        final_surah_df,
                        width= "stretch",
                        hide_index=True,
                        column_config={
                            "الكلمة الموضوعية المحصورة": st.column_config.TextColumn(
                                "الكلمة الموضوعية المحصورة", width="medium"
                            ),
                            "رقم المجموعة": st.column_config.NumberColumn(
                                "رقم المجموعة", width="small", format="%d"
                            ),
                            "رقم الآية": st.column_config.NumberColumn(
                                "رقم الآية", width="small", format="%d"
                            ),
                            "منطوق الآية": st.column_config.TextColumn(
                                "منطوق الآية", width="large"
                            ),
                            "المقصد / ملاحظات": st.column_config.TextColumn(
                                "المقصد / ملاحظات", width="large"
                            ),
                        },
                    )

                    excel_data_surah = convert_df_to_excel(final_surah_df)
                    st.download_button(
                        label=f"📥 تصدير موضوعات وآيات (سورة {selected_surah_drill}) إلى ملف Excel احترافي",
                        data=excel_data_surah,
                        file_name=f"موضوعات_وآيات_سورة_{selected_surah_drill}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )

                    # ==========================================================
                    # 🛠️ شريط أدوات التصفية المتقدم أسفل الجدول
                    # ==========================================================
                    st.markdown("---")
                    st.markdown(
                        "### 🎛️ خيارات التصفية المتقدمة للآيات في سورة "
                        + selected_surah_drill
                    )

                    col_f1, col_f2 = st.columns(2)

                    with col_f1:
                        unique_words_in_surah = ["الكل"] + sorted(
                            final_surah_df["الكلمة الموضوعية المحصورة"]
                            .dropna()
                            .unique()
                            .tolist()
                        )
                        selected_word_filter = st.selectbox(
                            "📌 تصفية حسب الكلمة الموضوعية:",
                            options=unique_words_in_surah,
                            key="filter_word_subtab2",
                        )

                    with col_f2:
                        unique_groups_in_surah = ["الكل"] + sorted(
                            final_surah_df["رقم المجموعة"].dropna().unique().tolist()
                        )
                        selected_group_filter = st.selectbox(
                            "📌 تصفية حسب رقم المجموعة:",
                            options=unique_groups_in_surah,
                            key="filter_group_subtab2",
                        )

                    filtered_drill_df = final_surah_df.copy()
                    if selected_word_filter != "الكل":
                        filtered_drill_df = filtered_drill_df[
                            filtered_drill_df["الكلمة الموضوعية المحصورة"]
                            == selected_word_filter
                        ]
                    if selected_group_filter != "الكل":
                        filtered_drill_df = filtered_drill_df[
                            filtered_drill_df["رقم المجموعة"] == selected_group_filter
                        ]

                    st.markdown(
                        f"** النتائج المفلترة المخصصة (عدد السجلات: {len(filtered_drill_df)}):**"
                    )
                    st.dataframe(
                        filtered_drill_df,
                        width= "stretch",
                        hide_index=True,
                        column_config={
                            "الكلمة الموضوعية المحصورة": st.column_config.TextColumn(
                                "الكلمة الموضوعية المحصورة", width="medium"
                            ),
                            "رقم المجموعة": st.column_config.NumberColumn(
                                "رقم المجموعة", width="small", format="%d"
                            ),
                            "رقم الآية": st.column_config.NumberColumn(
                                "رقم الآية", width="small", format="%d"
                            ),
                            "منطوق الآية": st.column_config.TextColumn(
                                "منطوق الآية", width="large"
                            ),
                            "المقصد / ملاحظات": st.column_config.TextColumn(
                                "المقصد / ملاحظات", width="large"
                            ),
                        },
                    )

                    excel_data_filtered = convert_df_to_excel(filtered_drill_df)
                    st.download_button(
                        label=f"📥 تصدير النتيجة المفلترة المخصصة إلى Excel",
                        data=excel_data_filtered,
                        file_name=f"Filtered_Ayahs_Surah_{selected_surah_drill}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
            else:
                st.warning("⚠️ لا توجد سور مسجلة لعرضها.")

else:
    st.warning("⚠️ لا توجد بيانات إحصائية كافية لعرض لوحة المؤشرات حالياً.")
