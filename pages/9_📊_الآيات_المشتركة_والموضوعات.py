import streamlit as st
import pandas as pd

# from supabase import create_client
from supabase import Client, create_client
from theme import apply_custom_theme, add_home_button
import io
import os

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="محلل ومستكشف الآيات المشتركة", page_icon="📊", layout="wide"
)

# تطبيق الهوية البصرية الموحدة واتجاه RTL وزر الرئيسية
apply_custom_theme()
add_home_button()

st.title("📊 محلل ومستكشف الآيات المشتركة والموضوعات المتعددة")
st.markdown(
    "<p style='text-align: center; color: #666666;'>استكشاف وتحليل الآيات التي تحوي أكثر من موضوع أو كلمة حصر، مع لوحة مؤشرات تفاعلية وترتيب مصحفي دقيق وربط بالمقاصد وأرقام الصفحات.</p>",
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


# جلب البيانات من الـ View الجديد (v_ayah_relations_with_pages)
@st.cache_data(ttl=60)
def fetch_ayah_relations():
    try:
        response = supabase.table("v_ayah_relations_with_pages").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        return pd.DataFrame()


df_all = fetch_ayah_relations()

if df_all.empty:
    st.error(
        "❌ لا توجد بيانات متاحة في العرض (v_ayah_relations_with_pages). تأكد من إنشاء الـ SQL View في Supabase."
    )
else:
    # -------------------------------------------------------------
    # تجهيز وتجميع البيانات الأساسية مع الحفاظ على الترتيب المصحفي (surah_serial)
    # -------------------------------------------------------------
    agg_df = (
        df_all.groupby(
            ["surah_serial", "surah_name", "ayah_number", "ayah_text", "page_number"]
        )
        .agg(
            topics_count=("topic_or_keyword", "count"),
            topics_list=(
                "topic_or_keyword",
                lambda x: "، ".join(str(v) for v in x.unique()),
            ),
            groups_list=("group_id", lambda x: "، ".join(str(v) for v in x.unique())),
            notes_list=(
                "notes",
                lambda x: " | ".join(str(v) for v in x.dropna().unique()),
            ),
        )
        .reset_index()
    )

    multi_topic_df = agg_df[agg_df["topics_count"] > 1].sort_values(
        by=["surah_serial", "ayah_number"]
    )
    single_topic_df = agg_df[agg_df["topics_count"] == 1].sort_values(
        by=["surah_serial", "ayah_number"]
    )
    agg_df = agg_df.sort_values(by=["surah_serial", "ayah_number"])

    # استخراج قائمة السور الفريدة مرتبة حصرياً برقم السورة (الترتيب المصحفي)
    surah_ordered_df = (
        agg_df[["surah_serial", "surah_name"]]
        .drop_duplicates()
        .sort_values("surah_serial")
    )
    surah_names_ordered = surah_ordered_df["surah_name"].tolist()

    # -------------------------------------------------------------
    # لوحة المؤشرات الإحصائية (Dashboard) المعتمدة
    # -------------------------------------------------------------
    st.markdown("### 📈 لوحة المؤشرات الإحصائية والملخص العام")

    col_d1, _ = st.columns([2, 5])
    with col_d1:
        surah_filter_opts = ["الكل (جميع السور)"] + surah_names_ordered
        selected_dashboard_surah = st.selectbox(
            "🎯 اختر السورة لتحديث المؤشرات الإحصائية لحظياً:",
            options=surah_filter_opts,
            key="dash_surah_sel",
        )

    if selected_dashboard_surah == "الكل (جميع السور)":
        current_df_all = agg_df
        current_multi = multi_topic_df
        current_single = single_topic_df
        total_keywords_count = len(df_all)
    else:
        current_df_all = agg_df[agg_df["surah_name"] == selected_dashboard_surah]
        current_multi = multi_topic_df[
            multi_topic_df["surah_name"] == selected_dashboard_surah
        ]
        current_single = single_topic_df[
            single_topic_df["surah_name"] == selected_dashboard_surah
        ]
        total_keywords_count = len(
            df_all[df_all["surah_name"] == selected_dashboard_surah]
        )

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("إجمالي كلمات الحصر", f"{total_keywords_count} كلمة")
    col_m2.metric("إجمالي الآيات المشتركة", f"{len(current_multi)} آية")
    col_m3.metric("إجمالي الآيات الفريدة (موضوع واحد)", f"{len(current_single)} آية")

    ratio = (
        (len(current_multi) / len(current_df_all) * 100)
        if len(current_df_all) > 0
        else 0
    )
    col_m4.metric("نسبة التقاطع والشمول", f"{ratio:.1f}%")

    st.markdown("---")

    # -------------------------------------------------------------
    # التقسيم إلى تبويبات رئيسية
    # -------------------------------------------------------------
    title_tab1, title_tab2 = st.tabs(
        ["📂 الفهرس الشامل للآيات المشتركة", "🔍 منصة التدقيق والتحليل المعميق للآية"]
    )

    # -------------------------------------------------------------
    # TAB 1: الفهرس الشامل الكلي للآيات المشتركة (مرتب مصحفياً)
    # -------------------------------------------------------------
    with title_tab1:
        st.subheader(
            f"📊 الفهرس الاستكشافي للآيات ذات الموضوعات المشتركة (إجمالي الآيات: {len(multi_topic_df)})"
        )
        st.markdown(
            "يستعرض هذا الجدول الآيات التي وردت في أكثر من موضوع أو كلمة حصر (مرتبة حسب ترتيب السور بالمصحف)، مع بيان رقم الصفحة لتسهيل المراجعة."
        )

        if multi_topic_df.empty:
            st.info("ℹ️ لا توجد آيات مشتركة مطابقة.")
        else:
            display_master = multi_topic_df[
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

            st.dataframe(display_master, use_container_width=True, hide_index=True)

            st.markdown("---")
            output_master = io.BytesIO()
            with pd.ExcelWriter(output_master, engine="xlsxwriter") as writer:
                display_master.to_excel(
                    writer, index=False, sheet_name="Multi_Topic_Ayahs_Index"
                )
            excel_data_master = output_master.getvalue()

            col_btn1, _ = st.columns([2, 5])
            with col_btn1:
                st.download_button(
                    label="📥 تصدير الكشف الشامل إلى Excel",
                    data=excel_data_master,
                    file_name="Multi_Topic_Ayahs_Index.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="dl_master_excel",
                )

    # -------------------------------------------------------------
    # TAB 2: منصة التدقيق والتحليل المعميق للآية الفردية (مع خيار الكل للآيات)
    # -------------------------------------------------------------
    with title_tab2:
        st.subheader("🔍 منصة التدقيق والتحليل المعميق للآية الفردية")
        st.markdown(
            "اختر السورة، ثم اختر آية معينة أو اختر **[الكل]** لاستعراض كافة آيات السورة المشتركة مع منطوقها مباشرة في جدول موحد."
        )

        if multi_topic_df.empty:
            st.info("ℹ️ لا توجد بيانات متاحة للعرض.")
        else:
            col_box1, col_box2 = st.columns([2, 3])

            with col_box1:
                deep_surah_options = ["الكل (جميع السور)"] + surah_names_ordered
                selected_deep_surah = st.selectbox(
                    "1️⃣ اختر السورة:",
                    options=deep_surah_options,
                    key="deep_surah_select",
                )

            # تصفية الآيات المشتركة حسب السورة
            if selected_deep_surah == "الكل (جميع السور)":
                filtered_deep_df = multi_topic_df
            else:
                filtered_deep_df = multi_topic_df[
                    multi_topic_df["surah_name"] == selected_deep_surah
                ]

            # إضافة خيار [الكل] لقائمة الآيات
            ayah_options_map = {}
            ayah_labels_list = ["[الكل] جميع آيات السورة المشتركة المختارة"]

            for _, r in filtered_deep_df.iterrows():
                lbl = f"آية رقم {r['ayah_number']} (صفحة {r['page_number']}) [موضوعات: {r['topics_count']}]"
                ayah_labels_list.append(lbl)
                ayah_options_map[lbl] = (r["surah_name"], r["ayah_number"])

            with col_box2:
                selected_ayah_label = st.selectbox(
                    "2️⃣ اختر رقم الآية:",
                    options=ayah_labels_list,
                    key="deep_ayah_select",
                )

            st.markdown("---")

            # -------------------------------------------------------------
            # الحالة الأولى: إذا اختر الباحث "[الكل] جميع آيات السورة"
            # -------------------------------------------------------------
            if selected_ayah_label == "[الكل] جميع آيات السورة المشتركة المختارة":
                st.markdown(
                    f"##### 📂 عرض كافة الآيات المشتركة للسورة: **{selected_deep_surah}** (إجمالي الآيات: {len(filtered_deep_df)})"
                )

                # تجهيز جدول شامل بدون نصف وربع حزب، ومع إدراج عمود منطوق الآية
                all_ayahs_display = filtered_deep_df[
                    [
                        "surah_name",
                        "ayah_number",
                        "page_number",
                        "ayah_text",
                        "topics_list",
                        "groups_list",
                    ]
                ].copy()

                all_ayahs_display.columns = [
                    "اسم السورة",
                    "رقم الآية",
                    "رقم الصفحة",
                    "منطوق الآية الكريمة",
                    "الكلمات والموضوعات المشتركة",
                    "المجموعات المرتبطة",
                ]

                st.dataframe(
                    all_ayahs_display, use_container_width=True, hide_index=True
                )

                # زر تصدير كل آيات السورة
                output_all_surah = io.BytesIO()
                with pd.ExcelWriter(output_all_surah, engine="xlsxwriter") as writer:
                    all_ayahs_display.to_excel(
                        writer, index=False, sheet_name="All_Surah_Ayahs_Report"
                    )
                excel_data_all_surah = output_all_surah.getvalue()

                col_as_btn1, _ = st.columns([2, 5])
                with col_as_btn1:
                    st.download_button(
                        label="📥 تصدير تقرير آيات السورة إلى Excel",
                        data=excel_data_all_surah,
                        file_name=f"Ayahs_Report_{selected_deep_surah}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key="dl_all_surah_excel",
                    )

            # -------------------------------------------------------------
            # الحالة الثانية: إذا اختر الباحث آية معينة
            # -------------------------------------------------------------
            elif selected_ayah_label and selected_ayah_label in ayah_options_map:
                chosen_surah_name, chosen_ayah_num = ayah_options_map[
                    selected_ayah_label
                ]

                ayah_details = df_all[
                    (df_all["surah_name"] == chosen_surah_name)
                    & (df_all["ayah_number"] == chosen_ayah_num)
                ]

                if not ayah_details.empty:
                    first_row = ayah_details.iloc[0]

                    # حقل المعاينة الفورية المستقل والبارز لمنطوق الآية
                    st.markdown(
                        f"""
                    <div style="background-color: #f0f7f4; padding: 15px 20px; border-radius: 8px; border-right: 5px solid #1b4d3e; text-align: right; margin-bottom: 15px;">
                        <span style="font-size: 0.9rem; color: #1b4d3e; font-weight: bold;">📖 معاينة منطوق الآية المختارة:</span>
                        <p style="font-size: 1.15rem; font-weight: bold; color: #2c3e50; margin-top: 5px; line-height: 1.7;">{first_row['ayah_text']}</p>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        "##### 📌 تفاصيل الموضوعات والكلمات المرتبطة بهذه الآية:"
                    )

                    details_display = ayah_details[
                        [
                            "topic_or_keyword",
                            "group_id",
                            "notes",
                            "half_code",
                            "quarter_code",
                        ]
                    ].copy()

                    details_display.columns = [
                        "الكلمة / الموضوع",
                        "رقم المجموعة",
                        "المقاصد والملاحظات (Notes)",
                        "نصف الحزب",
                        "ربع الحزب",
                    ]

                    st.dataframe(
                        details_display, use_container_width=True, hide_index=True
                    )

                    st.markdown("---")
                    output_detail = io.BytesIO()
                    with pd.ExcelWriter(output_detail, engine="xlsxwriter") as writer:
                        details_display.to_excel(
                            writer, index=False, sheet_name="Ayah_Deep_Analysis"
                        )
                    excel_data_detail = output_detail.getvalue()

                    col_d_btn1, _ = st.columns([2, 5])
                    with col_d_btn1:
                        st.download_button(
                            label="📥 تصدير تقرير الآية المحددة إلى Excel",
                            data=excel_data_detail,
                            file_name=f"Ayah_{chosen_surah_name}_{chosen_ayah_num}_Report.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                            key="dl_detail_excel",
                        )
