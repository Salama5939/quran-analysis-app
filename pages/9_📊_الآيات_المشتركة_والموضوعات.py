import streamlit as st
import pandas as pd
import io
from theme import apply_custom_theme, add_home_button
from database import supabase, convert_df_to_excel  # الاستيراد المركزي المعتمد

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="محلل ومستكشف الآيات المشتركة", page_icon="📊", layout="wide"
)

# تطبيق الهوية البصرية الموحدة واتجاه RTL وزر الرئيسية
apply_custom_theme()
add_home_button()


# دالة مساعدة لعكس ترتيب الأعمدة بصرياً (RTL) للعرض دون المساس بالجدول الأصلي
def prepare_rtl_display_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    return df.iloc[:, ::-1].copy()


st.title("📊 محلل ومستكشف الآيات المشتركة والموضوعات المتعددة")
st.markdown(
    "<p style='text-align: center; color: #666666;'>استكشاف وتحليل الآيات التي تحوي أكثر من موضوع أو كلمة حصر، مع لوحة مؤشرات تفاعلية وترتيب مصحفي دقيق وربط بالمقاصد.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")


# جلب البيانات حصرياً عبر كائن Supabase المركزي من database.py
@st.cache_data(ttl=60)
def fetch_ayah_relations():
    try:
        response = supabase.table("v_ayah_relations_with_pages").select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        st.error(f"❌ خطأ أثناء جلب البيانات: {e}")
        return pd.DataFrame()


df_all = fetch_ayah_relations()

if df_all.empty:
    st.error(
        "❌ لا توجد بيانات متاحة في العرض (v_ayah_relations_with_pages). تأكد من إنشاء الـ SQL View في Supabase."
    )
else:
    # الكشف التلقائي والآمن عن أسماء الأعمدة لمنع أي KeyError
    surah_col = (
        "surah_number"
        if "surah_number" in df_all.columns
        else ("surah_serial" if "surah_serial" in df_all.columns else df_all.columns[0])
    )
    page_col = (
        "page_number"
        if "page_number" in df_all.columns
        else ("page" if "page" in df_all.columns else None)
    )
    notes_col = (
        "notes"
        if "notes" in df_all.columns
        else ("objective_text" if "objective_text" in df_all.columns else None)
    )

    # بناء أعمدة التجميع ديناميكياً بناءً على المتاح في الـ View
    group_cols = [surah_col, "surah_name", "ayah_number", "ayah_text"]
    if page_col and page_col in df_all.columns:
        group_cols.append(page_col)

    agg_kwargs = {
        "topics_count": ("topic_or_keyword", "count"),
        "topics_list": (
            "topic_or_keyword",
            lambda x: "، ".join(str(v) for v in x.unique() if pd.notna(v)),
        ),
        "groups_list": (
            "group_id",
            lambda x: "، ".join(str(v) for v in x.unique() if pd.notna(v)),
        ),
    }
    if notes_col:
        agg_kwargs["notes_list"] = (
            notes_col,
            lambda x: " | ".join(str(v) for v in x.dropna().unique()),
        )

    agg_df = df_all.groupby(group_cols).agg(**agg_kwargs).reset_index()

    # توحيد اسم عمود السورة داخلياً
    if surah_col != "surah_number":
        agg_df = agg_df.rename(columns={surah_col: "surah_number"})
        surah_col = "surah_number"

    # تأمين وجود عمود page_number في العرض إن لم يكن موجوداً أصلاً في الـ View
    if "page_number" not in agg_df.columns:
        agg_df["page_number"] = 1

    multi_topic_df = agg_df[agg_df["topics_count"] > 1].sort_values(
        by=["surah_number", "ayah_number"]
    )
    single_topic_df = agg_df[agg_df["topics_count"] == 1].sort_values(
        by=["surah_number", "ayah_number"]
    )
    agg_df = agg_df.sort_values(by=["surah_number", "ayah_number"])

    surah_ordered_df = (
        agg_df[["surah_number", "surah_name"]]
        .drop_duplicates()
        .sort_values("surah_number")
    )
    surah_names_ordered = surah_ordered_df["surah_name"].tolist()

    # -------------------------------------------------------------
    # لوحة المؤشرات الإحصائية (Dashboard)
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

    # التقسيم إلى تبويبات رئيسية
    title_tab1, title_tab2 = st.tabs(
        ["📂 الفهرس الشامل للآيات المشتركة", "🔍 منصة التدقيق والتحليل المعميق للآية"]
    )

    # -------------------------------------------------------------
    # TAB 1: الفهرس الشامل الكلي
    # -------------------------------------------------------------
    with title_tab1:
        st.subheader(
            f"📊 الفهرس الاستكشافي للآيات ذات الموضوعات المشتركة (إجمالي الآيات: {len(multi_topic_df)})"
        )
        st.markdown(
            "يستعرض هذا الجدول الآيات التي وردت في أكثر من موضوع أو كلمة حصر (مرتبة حسب ترتيب السور بالمصحف)."
        )

        if multi_topic_df.empty:
            st.info("ℹ️ لا توجد آيات مشتركة مطابقة.")
        else:
            display_master = multi_topic_df[
                [
                    "surah_number",
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

            rtl_master = prepare_rtl_display_df(display_master)
            st.dataframe(rtl_master, use_container_width=True, hide_index=True)

            st.markdown("---")
            excel_data_master = convert_df_to_excel(
                display_master, sheet_name="Multi_Topic_Ayahs_Index"
            )

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
    # TAB 2: منصة التدقيق والتحليل المعميق
    # -------------------------------------------------------------
    with title_tab2:
        st.subheader("🔍 منصة التدقيق والتحليل المعميق للآية الفردية")
        st.markdown(
            "اختر السورة، ثم اختر آية معينة أو اختر **[الكل]** لاستعراض كافة آيات السورة المشتركة."
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

            if selected_deep_surah == "الكل (جميع السور)":
                filtered_deep_df = multi_topic_df
            else:
                filtered_deep_df = multi_topic_df[
                    multi_topic_df["surah_name"] == selected_deep_surah
                ]

            ayah_options_map = {}
            ayah_labels_list = ["[الكل] جميع آيات السورة المشتركة المختارة"]

            for _, r in filtered_deep_df.iterrows():
                lbl = f"آية رقم {r['ayah_number']} (صفحة {r['page_number']}) [موضوعات: {r['topics_count']}]"
                ayah_labels_list.append(lbl)
                ayah_options_map[lbl] = (r["surah_name"], int(r["ayah_number"]))

            with col_box2:
                selected_ayah_label = st.selectbox(
                    "2️⃣ اختر رقم الآية:",
                    options=ayah_labels_list,
                    key="deep_ayah_select",
                )

            st.markdown("---")

            if selected_ayah_label == "[الكل] جميع آيات السورة المشتركة المختارة":
                st.markdown(
                    f"<div dir='rtl' style='text-align: right; font-size: 1.05rem; font-weight: bold; margin-bottom: 8px;'>📂 عرض كافة الآيات المشتركة للسورة: <span style='color: #1b4d3e;'>{selected_deep_surah}</span> (إجمالي الآيات: {len(filtered_deep_df)})</div>",
                    unsafe_allow_html=True,
                )

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

                rtl_all_ayahs = prepare_rtl_display_df(all_ayahs_display)
                st.dataframe(
                    rtl_all_ayahs, use_container_width=True, hide_index=True
                )

                excel_data_all_surah = convert_df_to_excel(
                    all_ayahs_display, sheet_name="All_Surah_Ayahs_Report"
                )

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

                    details_cols = ["topic_or_keyword", "group_id"]
                    if notes_col and notes_col in ayah_details.columns:
                        details_cols.append(notes_col)
                    if "half_code" in ayah_details.columns:
                        details_cols.append("half_code")
                    if "quarter_code" in ayah_details.columns:
                        details_cols.append("quarter_code")

                    details_display = ayah_details[details_cols].copy()

                    rename_dict = {
                        "topic_or_keyword": "الكلمة / الموضوع",
                        "group_id": "رقم المجموعة",
                        "notes": "المقاصد والملاحظات",
                        "objective_text": "المقاصد والملاحظات",
                        "half_code": "نصف الحزب",
                        "quarter_code": "ربع الحزب",
                    }
                    details_display = details_display.rename(columns=rename_dict)
                    rtl_details = prepare_rtl_display_df(details_display)

                    st.dataframe(
                        rtl_details, use_container_width=True, hide_index=True
                    )

                    st.markdown("---")
                    excel_data_detail = convert_df_to_excel(
                        details_display, sheet_name="Ayah_Deep_Analysis"
                    )

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
