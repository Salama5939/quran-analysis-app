import pandas as pd
import streamlit as st
import theme  # استدعاء ملف التنسيق المركزي
from database import supabase, convert_df_to_excel

# 1. إعدادات الصفحة المطورة
st.set_page_config(
    page_title="منصة التناظر وموضوعات السور القرآنية",
    page_icon="🔗",
    layout="wide",
)

# تطبيق التنسيق المركزي وزر الرئيسية
theme.apply_custom_theme()
theme.add_home_button()


# دالة مساعدة لعكس ترتيب الأعمدة بصرياً (RTL) للعرض دون المساس بالجدول الأصلي
def prepare_rtl_display_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    return df.iloc[:, ::-1].copy()


# دالة تحديد المجموعة المتناظرة بناءً على رقم المجموعة group_id
def map_paired_group(group_val) -> str:
    if pd.isna(group_val):
        return "غير محدد"
    try:
        digits = "".join(ch for ch in str(group_val) if ch.isdigit())
        if not digits:
            return "غير محدد"
        g_num = int(digits)
    except Exception:
        return "غير محدد"

    pairing_map = {
        1: "مجموعة 1 متناظرة مع مجموعة 5",
        5: "مجموعة 1 متناظرة مع مجموعة 5",
        2: "المجموعة 2 متناظرة مع المجموعة 6",
        6: "المجموعة 2 متناظرة مع المجموعة 6",
        3: "المجموعة 3 متناظرة مع المجموعة 7",
        7: "المجموعة 3 متناظرة مع المجموعة 7",
        4: "المجموعة 4 متناظرة مع المجموعة 8",
        8: "المجموعة 4 متناظرة مع المجموعة 8",
    }
    return pairing_map.get(g_num, f"المجموعة {g_num}")


st.markdown(
    "<h1 style='text-align: center; color: #F1C40F;'>🔗 منصة التناظر وموضوعات السور القرآنية المتقدمة</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #666666;'>استكشاف وتحليل خريطة التناظر بين السور والمجموعات الثمانية، مع الاستعراض العميق لمقاصد وموضوعات السور التفصيلية.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")


# 2. جلب البيانات حصرياً من قاعدة بيانات Supabase مع التخزين المؤقت
@st.cache_data(ttl=60)
def fetch_surah_group_relations():
    try:
        response = (
            supabase.table("surah_group_relations")
            .select("*")
            .order("surah_number")
            .execute()
        )
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء جلب بيانات التناظر من قاعدة البيانات: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=60)
def fetch_objectives_data():
    try:
        response = (
            supabase.table("surah_objectives")
            .select("*")
            .order("surah_number")
            .execute()
        )
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء جلب بيانات مقاصد السور من قاعدة البيانات: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=60)
def fetch_surah_topics_detail():
    try:
        all_rows = []
        batch_size = 1000
        start = 0
        while True:
            response = (
                supabase.table("surah_topics_detail")
                .select(
                    "surah_number, surah_name, total_ayahs, start_page, group_id, topic_order, topic_detail"
                )
                .order("surah_number")
                .order("topic_order")
                .range(start, start + batch_size - 1)
                .execute()
            )
            batch = response.data if response.data else []
            if not batch:
                break
            all_rows.extend(batch)
            if len(batch) < batch_size:
                break
            start += batch_size
        return pd.DataFrame(all_rows) if all_rows else pd.DataFrame()
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء جلب موضوعات السور التفصيلية من قاعدة البيانات: {e}")
        return pd.DataFrame()


df_rel = fetch_surah_group_relations()
df_top = fetch_objectives_data()
df_topics_detail = fetch_surah_topics_detail()

# تقسيم العرض إلى 3 تبويبات رئيسية متكاملة
tab1, tab2, tab3 = st.tabs(
    [
        "⚖️ أولاً: خريطة التناظر والتشابه بين السور والمجموعات",
        "📖 ثانياً: مقاصد وموضوعات السور (حسب كتاب التدبر)",
        "🗂️ ثالثاً: موضوعات كل سورة التفصيلية",
    ]
)

# ---------------------------------------------------------
# TAB 1: خريطة التناظر والتشابه بين السور والمجموعات (حصرياً من Supabase)
# ---------------------------------------------------------
with tab1:
    st.subheader("⚖️ خريطة التناظر والتشابه بين سور القرآن والمجموعات الثمانية")
    st.markdown("استعراض منظم لجميع سور القرآن مستخرج مباشرة من قاعدة بيانات Supabase.")

    if not df_rel.empty:
        working_df = df_rel.copy()
        if "group_id" in working_df.columns:
            working_df["start_ayah"] = working_df["group_id"].apply(map_paired_group)
        else:
            working_df["start_ayah"] = "غير محدد"

        col_f1, col_f2 = st.columns([2, 3])

        with col_f1:
            group_col_name = (
                "group_id"
                if "group_id" in working_df.columns
                else working_df.columns[1]
            )
            available_groups = ["الكل"] + sorted(
                working_df[group_col_name].dropna().unique().tolist()
            )

            selected_group = st.selectbox(
                "🎯 تصفية حسب رقم المجموعة:",
                available_groups,
                key="filter_grp_t1_db",
            )

        with col_f2:
            search_t_input = st.text_input(
                "🔍 بحث سريع برقم أو اسم السورة أو المجموعة المتناظرة:",
                placeholder="اكتب اسم السورة أو رقمها...",
                key="search_tanazor_input_db",
            )

        filtered_df = working_df.copy()

        if selected_group != "الكل":
            filtered_df = filtered_df[
                filtered_df[group_col_name].astype(str) == str(selected_group)
            ]

        if search_t_input.strip():
            term = search_t_input.strip()
            mask = pd.Series(False, index=filtered_df.index)
            for col in ["surah_number", "surah_name", "group_id", "start_ayah"]:
                if col in filtered_df.columns:
                    mask = mask | filtered_df[col].astype(str).str.contains(
                        term, na=False
                    )
            filtered_df = filtered_df[mask]

        rename_map_t1 = {
            "surah_number": "رقم السورة",
            "surah_name": "اسم السورة",
            "total_ayahs": "عدد الآيات",
            "group_id": "رقم المجموعة",
            "start_ayah": "المجموعة المتناظرة",
        }
        valid_cols_t1 = [c for c in rename_map_t1.keys() if c in filtered_df.columns]
        display_df_t1 = filtered_df[valid_cols_t1].rename(
            columns={c: rename_map_t1[c] for c in valid_cols_t1}
        )

        st.success(f"✅ عدد السور المعروضة مطابقة للشروط: {len(display_df_t1)} سورة")

        rtl_display_t1 = prepare_rtl_display_df(display_df_t1)

        st.dataframe(
            rtl_display_t1,
            use_container_width=True,
            hide_index=True,
        )

        excel_bytes_t = convert_df_to_excel(display_df_t1, sheet_name="خريطة_التناظر")
        col_dl1, _ = st.columns([2, 5])
        with col_dl1:
            st.download_button(
                label="📥 تصدير جدول التناظر إلى Excel",
                data=excel_bytes_t,
                file_name="Surahs_Tanazor_Map.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="dl_t1_excel",
            )
    else:
        st.warning(
            "⚠️ لا توجد بيانات متاحة في جدول `surah_group_relations` في قاعدة بيانات Supabase."
        )

# ---------------------------------------------------------
# TAB 2: مقاصد وموضوعات السور (حصرياً من Supabase)
# ---------------------------------------------------------
with tab2:
    st.subheader("📖 تفاصيل مقاصد وموضوعات كل سورة من سور القرآن الكريم")
    st.markdown("مستندة إلى المصادر المعتمدة لكتاب 'تسهيل فهم وتدبر القرآن'.")

    if not df_top.empty:
        col_surah_name = (
            "surah_name" if "surah_name" in df_top.columns else df_top.columns[1]
        )
        surah_names_list = ["الكل (عرض كافة السور)"] + (
            df_top.sort_values("surah_number")[col_surah_name]
            .dropna()
            .unique()
            .tolist()
            if "surah_number" in df_top.columns
            else sorted(df_top[col_surah_name].dropna().unique().tolist())
        )

        col_s1, col_s2 = st.columns([2, 2])
        with col_s1:
            selected_surah_dd = st.selectbox(
                "🎯 اختر السورة للاستعراض السريع:",
                surah_names_list,
                key="surah_dropdown_topics_db",
            )

        with col_s2:
            st.markdown("<br>", unsafe_allow_html=True)
            show_extra_cols = st.checkbox(
                "إظهار الأعمدة التقنية الإضافية",
                value=False,
                key="chk_extra_cols_db",
            )

        filtered_df_top = df_top.copy()
        if selected_surah_dd != "الكل (عرض كافة السور)":
            filtered_df_top = filtered_df_top[
                filtered_df_top[col_surah_name].astype(str).str.strip()
                == selected_surah_dd.strip()
            ]

        always_hidden_cols = ["created_at", "id", "serial_no"]
        optional_tech_cols = ["code", "half_code", "quarter_code", "group_code"]

        cols_to_drop = [c for c in always_hidden_cols if c in filtered_df_top.columns]
        if not show_extra_cols:
            cols_to_drop.extend(
                [c for c in optional_tech_cols if c in filtered_df_top.columns]
            )

        cleaned_df_top = filtered_df_top.drop(columns=cols_to_drop, errors="ignore")

        rename_map_t2 = {
            "surah_number": "رقم السورة",
            "surah_name": "اسم السورة",
            "group_id": "رقم المجموعة",
            "surah_objective": "مقصد السورة",
            "objective_text": "مقصد السورة",
            "main_topic": "الموضوع الرئيسي",
            "sub_topics": "الموضوعات الفرعية",
            "code": "الرمز",
            "half_code": "نصف الحزب",
            "quarter_code": "ربع الحزب",
            "group_code": "رمز المجموعة",
        }
        valid_rename_t2 = {
            k: v for k, v in rename_map_t2.items() if k in cleaned_df_top.columns
        }
        display_df_top = cleaned_df_top.rename(columns=valid_rename_t2)

        st.success(f"✅ إجمالي السجلات المطابقة: {len(display_df_top)} سجل موضوعي")

        rtl_display_top = prepare_rtl_display_df(display_df_top)

        st.dataframe(
            rtl_display_top,
            use_container_width=True,
            hide_index=True,
        )

        excel_bytes_top = convert_df_to_excel(display_df_top, sheet_name="مقاصد_السور")
        col_dl2, _ = st.columns([2, 5])
        with col_dl2:
            st.download_button(
                label="📥 تصدير تقرير مقاصد السور إلى Excel",
                data=excel_bytes_top,
                file_name="Surahs_Objectives_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="dl_t2_excel",
            )
    else:
        st.warning(
            "⚠️ لا توجد بيانات متاحة في جدول موضوعات السور (`surah_objectives`) في قاعدة بيانات Supabase."
        )

# ---------------------------------------------------------
# TAB 3: موضوعات كل سورة التفصيلية (حصرياً من Supabase: surah_topics_detail)
# ---------------------------------------------------------
with tab3:
    st.subheader("🗂️ موضوعات كل سورة التفصيلية (حسب كتاب تسهيل فهم وتدبر القرآن)")
    st.markdown(
        "<div dir='rtl' style='text-align: right; color: #666666; margin-bottom: 10px;'>استعراض تفصيلي لمحاور وموضوعات السور القرآنية الـ 114 مع الربط بالمجموعات الثمانية والمجموعات المتناظرة.</div>",
        unsafe_allow_html=True,
    )

    if not df_topics_detail.empty:
        df_t3 = df_topics_detail.copy()
        df_t3["paired_group_label"] = df_t3["group_id"].apply(map_paired_group)

        col_t3_f1, col_t3_f2, col_t3_f3 = st.columns([2, 2, 3])

        with col_t3_f1:
            groups_t3 = ["الكل"] + sorted(df_t3["group_id"].dropna().unique().tolist())
            sel_group_t3 = st.selectbox(
                "🎯 تصفية حسب المجموعة:",
                options=groups_t3,
                key="t3_group_filter",
            )

        df_t3_filtered_step1 = df_t3.copy()
        if sel_group_t3 != "الكل":
            df_t3_filtered_step1 = df_t3_filtered_step1[
                df_t3_filtered_step1["group_id"] == sel_group_t3
            ]

        with col_t3_f2:
            surahs_t3_ordered = (
                df_t3_filtered_step1[["surah_number", "surah_name"]]
                .drop_duplicates()
                .sort_values("surah_number")
            )
            surah_t3_options = ["الكل (جميع السور)"] + [
                f"{int(r['surah_number'])} - {r['surah_name']}"
                for _, r in surahs_t3_ordered.iterrows()
            ]
            sel_surah_t3 = st.selectbox(
                "📖 اختر السورة:",
                options=surah_t3_options,
                key="t3_surah_filter",
            )

        with col_t3_f3:
            search_t3_query = st.text_input(
                "🔍 بحث نصي داخل تفاصيل الموضوعات أو السور:",
                placeholder="مثال: الابتلاء، بني إسرائيل، الاستعاذة...",
                key="t3_search_query",
            )

        df_t3_res = df_t3_filtered_step1.copy()
        if sel_surah_t3 != "الكل (جميع السور)":
            chosen_s_num = int(sel_surah_t3.split(" - ")[0])
            df_t3_res = df_t3_res[df_t3_res["surah_number"] == chosen_s_num]

        if search_t3_query.strip():
            q_term = search_t3_query.strip()
            mask_t3 = (
                df_t3_res["surah_name"]
                .astype(str)
                .str.contains(q_term, case=False, na=False)
                | df_t3_res["topic_detail"]
                .astype(str)
                .str.contains(q_term, case=False, na=False)
                | df_t3_res["paired_group_label"]
                .astype(str)
                .str.contains(q_term, case=False, na=False)
            )
            df_t3_res = df_t3_res[mask_t3]

        # مؤشرات سريعة للتبويب الثالث
        m_c1, m_c2, m_c3 = st.columns(3)
        m_c1.metric("إجمالي الموضوعات المعروضة", f"{len(df_t3_res)} موضوع")
        m_c2.metric("عدد السور المشمولة", f"{df_t3_res['surah_number'].nunique()} سورة")
        avg_topics = (
            len(df_t3_res) / df_t3_res["surah_number"].nunique()
            if df_t3_res["surah_number"].nunique() > 0
            else 0
        )
        m_c3.metric("متوسط الموضوعات لكل سورة", f"{avg_topics:.1f}")

        st.markdown("---")
        st.markdown(
            f"<div dir='rtl' style='text-align: right; font-size: 1.05rem; font-weight: bold; margin-bottom: 8px;'>📋 جدول موضوعات السور التفصيلية (إجمالي السجلات: <span style='color: #1b4d3e;'>{len(df_t3_res)}</span>)</div>",
            unsafe_allow_html=True,
        )

        # تعريب رؤوس الحقول واستبعاد created_at و id و serial_no تماماً
        rename_map_t3 = {
            "surah_number": "رقم السورة",
            "surah_name": "اسم السورة",
            "total_ayahs": "عدد الآيات",
            "start_page": "صفحة بداية السورة",
            "group_id": "رقم المجموعة",
            "paired_group_label": "المجموعة المتناظرة",
            "topic_order": "ترتيب الموضوع",
            "topic_detail": "تفاصيل الموضوع",
        }
        valid_cols_t3 = [c for c in rename_map_t3.keys() if c in df_t3_res.columns]
        display_df_t3 = df_t3_res[valid_cols_t3].rename(
            columns={c: rename_map_t3[c] for c in valid_cols_t3}
        )

        # نسخة العرض البصري RTL مع الإبقاء على display_df_t3 للتصدير إلى Excel
        rtl_display_t3 = prepare_rtl_display_df(display_df_t3)

        st.dataframe(
            rtl_display_t3,
            use_container_width=True,
            hide_index=True,
        )

        excel_bytes_t3 = convert_df_to_excel(
            display_df_t3, sheet_name="موضوعات_السور_التفصيلية"
        )
        col_dl3, _ = st.columns([2, 5])
        with col_dl3:
            st.download_button(
                label="📥 تصدير موضوعات السور التفصيلية إلى Excel",
                data=excel_bytes_t3,
                file_name="Surahs_Detailed_Topics_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="dl_t3_excel",
            )
    else:
        st.warning(
            "⚠️ لا توجد بيانات متاحة في جدول `surah_topics_detail` في قاعدة بيانات Supabase."
        )
