import pandas as pd
import plotly.express as px
import streamlit as st
import re
import theme
from database import (
    supabase,
    search_ayah_group_relations_stable,
    search_full_quran_stable,
    get_or_create_word_code,
    normalize_arabic,
    convert_df_to_excel,
    highlight_uthmani_keyword,
)


def render_highlighted_html(ayah_text: str, target_word: str) -> str:
    """استخدام دالة الصفحة 12 الأصلية وتحويل تنسيق :blue[**...**] إلى HTML لبني متوافق مع البطاقات"""
    md_highlighted = highlight_uthmani_keyword(
        str(ayah_text or ""), str(target_word or "")
    )
    return re.sub(
        r":blue\[\*\*(.*?)\*\*\]",
        r"<span style='color:#0284C7; font-weight:700;'>\1</span>",
        md_highlighted,
    )


# 1. إعدادات الصفحة المستقلة
st.set_page_config(
    page_title="الإحصاءات والرسوم البيانية وإدارة الحصر",
    page_icon="📊",
    layout="wide",
)

# تطبيق التنسيق المركزي الموحد وزر الرئيسية
theme.apply_custom_theme()
theme.add_home_button()

# ==============================================================================
# حقن التنسيق البصري الموحد (مطابق لهوية الصفحتين 11 و 12)
# ==============================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700&display=swap');

    .g4-hero-box {
        background: linear-gradient(135deg, rgba(27, 77, 62, 0.10) 0%, rgba(212, 175, 55, 0.12) 100%);
        border: 1px solid rgba(212, 175, 55, 0.45);
        border-right: 6px solid #1B4D3E;
        border-radius: 14px;
        padding: 20px 26px;
        margin-bottom: 18px;
        text-align: center;
        font-family: 'Cairo', sans-serif;
    }
    .g4-hero-title {
        color: #1B4D3E;
        font-size: 1.85rem;
        font-weight: 700;
        margin: 0 0 6px 0;
    }
    .g4-hero-sub {
        color: #555555;
        font-size: 1.02rem;
        margin: 0;
    }
    .g4-kpi-card {
        background: #FFFFFF;
        border: 1px solid #E6E2D6;
        border-top: 4px solid #D4AF37;
        border-radius: 12px;
        padding: 14px 16px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        font-family: 'Cairo', sans-serif;
    }
    .g4-kpi-label {
        color: #666666;
        font-size: 0.90rem;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .g4-kpi-val {
        color: #1B4D3E;
        font-size: 1.65rem;
        font-weight: 700;
    }
    .g4-dist-strip {
        background: #FFFFFF;
        border: 1px solid #E2DDD0;
        border-right: 5px solid #D4AF37;
        border-radius: 12px;
        padding: 14px 18px;
        margin: 12px 0 18px 0;
        direction: rtl;
        text-align: right;
        font-family: 'Cairo', sans-serif;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    .g4-dist-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #1B4D3E;
        margin-bottom: 10px;
    }
    .g4-dist-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        align-items: center;
    }
    .g4-dist-badge-active {
        background: rgba(27, 77, 62, 0.10);
        border: 1px solid rgba(27, 77, 62, 0.35);
        color: #1B4D3E;
        padding: 6px 14px;
        border-radius: 10px;
        font-size: 0.94rem;
        font-weight: 700;
    }
    .g4-dist-badge-zero {
        background: #F5F5F4;
        border: 1px solid #E5E5E5;
        color: #888888;
        padding: 6px 14px;
        border-radius: 10px;
        font-size: 0.92rem;
        font-weight: 600;
    }
    .g4-ayah-card {
        background: #FCFBF7;
        border: 1px solid #E5DFD0;
        border-right: 5px solid #1B4D3E;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        direction: rtl;
        text-align: right;
    }
    .g4-ayah-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 10px;
        font-family: 'Cairo', sans-serif;
    }
    .g4-badge-surah {
        background: #1B4D3E;
        color: #FFFFFF;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 600;
    }
    .g4-badge-group {
        background: rgba(212, 175, 55, 0.22);
        color: #7A5C00;
        border: 1px solid rgba(212, 175, 55, 0.6);
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
    }
    .g4-ayah-text {
        font-family: 'Amiri', serif;
        font-size: 1.42rem;
        line-height: 2.1;
        color: #1E293B;
        margin: 8px 0 10px 0;
    }
    .g4-ayah-note {
        background: rgba(27, 77, 62, 0.06);
        border-radius: 8px;
        padding: 8px 14px;
        font-family: 'Cairo', sans-serif;
        font-size: 0.92rem;
        color: #2C3E50;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def prepare_rtl_display_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    return df.iloc[:, ::-1].copy()


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
        1: "المجموعة 1 متناظرة مع المجموعة 5",
        5: "المجموعة 1 متناظرة مع المجموعة 5",
        2: "المجموعة 2 متناظرة مع المجموعة 6",
        6: "المجموعة 2 متناظرة مع المجموعة 6",
        3: "المجموعة 3 متناظرة مع المجموعة 7",
        7: "المجموعة 3 متناظرة مع المجموعة 7",
        4: "المجموعة 4 متناظرة مع المجموعة 8",
        8: "المجموعة 4 متناظرة مع المجموعة 8",
    }
    return pairing_map.get(g_num, f"المجموعة {g_num}")


# دوال رد النداء الفورية لمسح الشاشة في التبويب الثاني والتبويب الرابع
BRIDGE_PLACEHOLDER = "— اختر كلمة أو مفهوماً للتحليل —"


def reset_bridge_screen_callback():
    st.session_state.g4_bridge_kw_sel = BRIDGE_PLACEHOLDER
    st.session_state.g4_active_bridge_kw = ""
    st.session_state.pop("g4_bridge_drill_g", None)


def reset_migrate_screen_callback():
    st.session_state.g4_migrate_results = {"hsor": [], "quran": []}
    st.session_state.g4_migrate_word = ""
    st.session_state.g4_migrate_input = ""
    st.session_state.g4_custom_mig_note = ""
    st.session_state.g4_sel_map = {}
    st.session_state.g4_sel_word = ""
    st.session_state.pop("g4_editor_verses", None)


# الترويسة البصرية الموحدة
st.markdown(
    """
    <div class="g4-hero-box">
        <div class="g4-hero-title">📊 الإحصاءات والرسوم البيانية وإدارة الحصر</div>
        <p class="g4-hero-sub">بوابة التحليل الإحصائي الشامل، توزيع الكلمات عبر المجموعات الثمانية، خريطة التناظر، والترحيل الانتقائي للآيات (معتمدة 100% على Supabase)</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# دوال جلب البيانات حصرياً من قاعدة بيانات Supabase
# ==============================================================================
@st.cache_data(ttl=60)
def fetch_all_relations_data():
    all_rows = []
    batch_size = 1000
    start = 0
    while True:
        resp = (
            supabase.table("ayah_group_relations")
            .select(
                "word_code, topic_or_keyword, group_id, surah_serial, surah_name, "
                "ayah_number, ayah_text, notes, half_code, quarter_code, frequency_count"
            )
            .range(start, start + batch_size - 1)
            .execute()
        )
        batch = resp.data if resp.data else []
        if not batch:
            break
        all_rows.extend(batch)
        if len(batch) < batch_size:
            break
        start += batch_size
    return all_rows


@st.cache_data(ttl=120)
def fetch_surah_metadata_from_db():
    objectives_map = {}
    codes_map = {}

    try:
        res_obj = (
            supabase.table("surah_objectives")
            .select("surah_number, surah_name, group_id, surah_objective")
            .order("surah_number")
            .execute()
        )
        for row in res_obj.data or []:
            s_num = int(row["surah_number"])
            objectives_map[s_num] = str(row.get("surah_objective") or "").strip()
            codes_map[s_num] = {
                "surah_name": str(row.get("surah_name") or "").strip(),
                "group_id": int(row.get("group_id") or 1),
                "half_code": 0,
                "quarter_code": 0,
            }
    except Exception:
        pass

    try:
        res_rel = (
            supabase.table("ayah_group_relations")
            .select("surah_serial, group_id, half_code, quarter_code")
            .range(0, 9999)
            .execute()
        )
        for row in res_rel.data or []:
            s_ser = row.get("surah_serial")
            if s_ser is not None:
                s_num = int(s_ser)
                entry = codes_map.setdefault(
                    s_num,
                    {
                        "surah_name": "",
                        "group_id": 1,
                        "half_code": 0,
                        "quarter_code": 0,
                    },
                )
                if row.get("group_id") is not None:
                    entry["group_id"] = int(row["group_id"])
                if row.get("half_code") is not None and entry["half_code"] == 0:
                    entry["half_code"] = int(row["half_code"])
                if row.get("quarter_code") is not None and entry["quarter_code"] == 0:
                    entry["quarter_code"] = int(row["quarter_code"])
    except Exception:
        pass

    return objectives_map, codes_map


@st.cache_data(ttl=120)
def fetch_surah_group_relations_db():
    try:
        res = (
            supabase.table("surah_group_relations")
            .select("*")
            .order("surah_number")
            .execute()
        )
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        st.error(f"❌ تعذّر جلب خريطة التناظر من قاعدة البيانات: {e}")
        return pd.DataFrame()


with st.spinner("جاري تحميل المؤشرات والبيانات التحليلية من قاعدة البيانات..."):
    raw_relations = fetch_all_relations_data()
    surah_objectives_map, surah_codes_map = fetch_surah_metadata_from_db()

df_dash = pd.DataFrame(raw_relations) if raw_relations else pd.DataFrame()
if not df_dash.empty:
    df_dash["group_id"] = (
        pd.to_numeric(df_dash["group_id"], errors="coerce").fillna(1).astype(int)
    )
    df_dash["surah_serial"] = (
        pd.to_numeric(df_dash["surah_serial"], errors="coerce").fillna(1).astype(int)
    )
    df_dash["frequency_count"] = (
        pd.to_numeric(df_dash["frequency_count"], errors="coerce").fillna(1).astype(int)
    )

# شريط بطاقات المؤشرات العليا الحيوية (KPI Cards)
if not df_dash.empty:
    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        (k1, "إجمالي سجلات الحصر المعتمد", f"{len(df_dash):,}"),
        (
            k2,
            "الكلمات والمفاهيم المحصورة",
            f"{df_dash['topic_or_keyword'].nunique():,}",
        ),
        (k3, "المجموعات الثمانية المفعّلة", f"{df_dash['group_id'].nunique()} مجموعات"),
        (k4, "السور المرتبطة بالحصر", f"{df_dash['surah_serial'].nunique()} سورة"),
    ]
    for col_box, lbl, val in kpis:
        with col_box:
            st.markdown(
                f"""
                <div class="g4-kpi-card">
                    <div class="g4-kpi-label">{lbl}</div>
                    <div class="g4-kpi-val">{val}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

# التبويبات الأربعة الموحدة للبوابة الرابعة
tab_charts, tab_bridge, tab_symmetry, tab_migrate = st.tabs(
    [
        "📈 الرسوم البيانية ومؤشرات الحصر",
        "🌐 توزيع الكلمات عبر المجموعات الثمانية",
        "⚖️ خريطة التناظر الثنائي للمجموعات",
        "✅ الترحيل الانتقائي للآيات إلى الحصر",
    ]
)

# ==============================================================================
# التبويب الأول: الرسوم البيانية ومؤشرات الحصر + الكشف الإجمالي الأبجدي
# ==============================================================================
with tab_charts:
    st.subheader("📈 التحليلات المرئية لتوزيع الآيات والكلمات على المجموعات الثمانية")

    if df_dash.empty:
        st.warning("⚠️ لا توجد بيانات كافية في جدول الحصر لعرض الرسوم البيانية.")
    else:
        col_c1, col_c2 = st.columns(2)

        with col_c1:
            st.markdown("##### 📌 توزيع الآيات المسجلة حسب المجموعات الثمانية")
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
                color_continuous_scale=["#8BB8A8", "#1B4D3E"],
            )
            fig_groups.update_layout(
                xaxis_title="المجموعات الثمانية",
                yaxis_title="عدد الآيات",
                xaxis_tickangle=-25,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
                font=dict(family="Cairo", size=13),
            )
            st.plotly_chart(fig_groups, width="stretch")

        with col_c2:
            st.markdown("##### 🏆 أكثر 10 كلمات ومفاهيم ارتباطاً بالآيات")
            top_words = (
                df_dash.groupby("topic_or_keyword")
                .size()
                .reset_index(name="عدد_الآيات")
                .sort_values(by="عدد_الآيات", ascending=False)
                .head(10)
            )

            fig_words = px.bar(
                top_words,
                x="topic_or_keyword",
                y="عدد_الآيات",
                text="عدد_الآيات",
                color="عدد_الآيات",
                color_continuous_scale=["#E6C767", "#9C7A16"],
            )
            fig_words.update_layout(
                xaxis_title="الكلمة / المفهوم",
                yaxis_title="عدد الآيات المرتبطة",
                xaxis_tickangle=-35,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
                font=dict(family="Cairo", size=13),
            )
            st.plotly_chart(fig_words, width="stretch")

        st.markdown("---")
        st.markdown("### 📋 الملخص الإحصائي الشامل لكل مجموعة")

        summary_group_df = (
            df_dash.groupby("group_id")
            .agg(
                عدد_الكلمات_المختلفة=("topic_or_keyword", "nunique"),
                إجمالي_الآيات_المرتبطة=("topic_or_keyword", "count"),
                إجمالي_التكرارات_اللفظية=("frequency_count", "sum"),
            )
            .reset_index()
        )
        summary_group_df.columns = [
            "رقم المجموعة",
            "عدد الكلمات المختلفة",
            "إجمالي الآيات المرتبطة",
            "إجمالي التكرارات اللفظية",
        ]

        st.dataframe(
            prepare_rtl_display_df(summary_group_df),
            width="stretch",
            hide_index=True,
        )

        excel_groups = convert_df_to_excel(
            summary_group_df, sheet_name="ملخص_المجموعات"
        )
        col_dl_g, _ = st.columns([2, 5])
        with col_dl_g:
            st.download_button(
                label="📥 تصدير ملخص المجموعات إلى Excel",
                data=excel_groups,
                file_name="Groups_Statistical_Summary.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch",
                key="dl_g4_groups_summary",
            )

        st.markdown("---")
        st.subheader("📚 الكشف الإجمالي الأبجدي لجميع الكلمات والمفاهيم المحصورة")

        col_rep_f1, col_rep_f2 = st.columns([2, 3])
        with col_rep_f1:
            rep_grp = st.selectbox(
                "تصفية الكشف حسب المجموعة:",
                ["جميع المجموعات"] + [f"المجموعة {i}" for i in range(1, 9)],
                key="g4_rep_grp",
            )
        with col_rep_f2:
            rep_kw_search = st.text_input(
                "🔍 بحث سريع داخل الكلمات المحصورة:",
                placeholder="اكتب جزءاً من الكلمة...",
                key="g4_rep_kw_search",
            )

        df_rep_src = df_dash.copy()
        if rep_grp != "جميع المجموعات":
            g_num = int(rep_grp.replace("المجموعة ", ""))
            df_rep_src = df_rep_src[df_rep_src["group_id"] == g_num]

        if not df_rep_src.empty:
            df_grouped_words = (
                df_rep_src.groupby("topic_or_keyword")
                .agg(
                    عدد_الآيات_المسجلة=("topic_or_keyword", "count"),
                    إجمالي_التكرارات=("frequency_count", "sum"),
                    المجموعات_المرتبطة=(
                        "group_id",
                        lambda s: "، ".join(str(x) for x in sorted(set(s))),
                    ),
                )
                .reset_index()
                .sort_values(by="topic_or_keyword", ascending=True)
            )

            if rep_kw_search.strip():
                norm_q = normalize_arabic(rep_kw_search.strip())
                df_grouped_words = df_grouped_words[
                    df_grouped_words["topic_or_keyword"].apply(
                        lambda x: norm_q in normalize_arabic(str(x))
                    )
                ]

            df_grouped_words.columns = [
                "الكلمة / المفهوم",
                "عدد الآيات المسجلة",
                "إجمالي التكرارات",
                "المجموعات المرتبطة",
            ]
            st.success(
                f"✅ إجمالي الكلمات الفريدة المطابقة: **{len(df_grouped_words)}** كلمة"
            )
            st.dataframe(
                prepare_rtl_display_df(df_grouped_words),
                width="stretch",
                hide_index=True,
            )

            excel_all_words = convert_df_to_excel(
                df_grouped_words, sheet_name="الكلمات_المحصورة"
            )
            col_dl_w, _ = st.columns([2, 5])
            with col_dl_w:
                st.download_button(
                    label="📥 تصدير الكشف الإجمالي للكلمات إلى Excel",
                    data=excel_all_words,
                    file_name="All_Indexed_Keywords_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    width="stretch",
                    key="dl_g4_all_words",
                )

# ==============================================================================
# التبويب الثاني: توزيع الكلمات عبر المجموعات الثمانية (النسخة المركزة والنظيفة)
# ==============================================================================
with tab_bridge:
    st.subheader("🌐 شبكة الترابط الموضوعي وتوزيع الكلمة عبر المجموعات الثمانية")

    if df_dash.empty:
        st.warning("⚠️ لا توجد كلمات مسجلة في قاعدة البيانات حالياً.")
    else:
        keywords_list = [BRIDGE_PLACEHOLDER] + sorted(
            [
                str(w).strip()
                for w in df_dash["topic_or_keyword"].dropna().unique()
                if str(w).strip()
            ]
        )

        col_b1, col_b2, col_b3 = st.columns([3.4, 1.1, 1.1])
        with col_b1:
            selected_keyword = st.selectbox(
                "🎯 اختر الكلمة أو المفهوم لعرض خريطة انتشاره ومقاصده عبر المجموعات الثمانية:",
                options=keywords_list,
                key="g4_bridge_kw_sel",
            )
        with col_b2:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            btn_show_bridge = st.button(
                "🔗 تحليل التوزيع",
                type="primary",
                width="stretch",
                key="btn_g4_bridge_run",
            )
        with col_b3:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            st.button(
                "🔄 مسح الشاشة",
                width="stretch",
                key="btn_g4_bridge_clear",
                on_click=reset_bridge_screen_callback,
            )

        if btn_show_bridge:
            if selected_keyword and selected_keyword != BRIDGE_PLACEHOLDER:
                st.session_state.g4_active_bridge_kw = selected_keyword
            else:
                st.session_state.g4_active_bridge_kw = ""
        elif selected_keyword and selected_keyword != BRIDGE_PLACEHOLDER:
            st.session_state.g4_active_bridge_kw = selected_keyword

        active_kw = st.session_state.get("g4_active_bridge_kw", "")

        if not active_kw or active_kw == BRIDGE_PLACEHOLDER:
            st.info(
                "ℹ️ اختر كلمة أو مفهوماً من القائمة أعلاه لعرض توزيعه على المجموعات الثمانية وبطاقات آياته."
            )
        else:
            response = supabase.rpc(
                "get_semantic_bridge_card", {"target_keyword": active_kw}
            ).execute()
            bridge_data = response.data if response.data else []

            if bridge_data:
                group_counts_map = {i: 0 for i in range(1, 9)}
                available_groups = []
                for row in bridge_data:
                    g_id = int(row.get("group_id", 1))
                    cnt = int(row.get("total_ayahs", 0))
                    if 1 <= g_id <= 8:
                        group_counts_map[g_id] = cnt
                    available_groups.append(g_id)

                available_groups = sorted(list(set(available_groups)))
                total_occ = sum(group_counts_map.values())

                # 1. بطاقتا المؤشرات العليا
                c_bm1, c_bm2 = st.columns(2)
                with c_bm1:
                    st.markdown(
                        f"""
                        <div class="g4-kpi-card">
                            <div class="g4-kpi-label">إجمالي الآيات المرتبطة بـ «{active_kw}»</div>
                            <div class="g4-kpi-val">{total_occ} آية</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with c_bm2:
                    st.markdown(
                        f"""
                        <div class="g4-kpi-card">
                            <div class="g4-kpi-label">عدد المجموعات التي تظهر فيها</div>
                            <div class="g4-kpi-val">{len(available_groups)} من 8</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # 2. الشريط التحليلي الأفقي لتوزيع الآيات على المجموعات الثمانية
                badges_html_parts = []
                for g_idx in range(1, 9):
                    c_val = group_counts_map[g_idx]
                    if c_val > 0:
                        badges_html_parts.append(
                            f"<span class='g4-dist-badge-active'>المجموعة {g_idx}: {c_val} آية</span>"
                        )
                    else:
                        badges_html_parts.append(
                            f"<span class='g4-dist-badge-zero'>المجموعة {g_idx}: 0</span>"
                        )

                st.markdown(
                    f"""
                    <div class="g4-dist-strip">
                        <div class="g4-dist-title">📊 التوزيع التفصيلي لإجمالي الآيات عبر المجموعات الثمانية:</div>
                        <div class="g4-dist-badges">
                            {' '.join(badges_html_parts)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # 3. استعراض بطاقات الآيات لمجموعة محددة مع التظليل الموحد (قوسين + لون لبني مطابق لص 12)
                selected_drill_g = st.selectbox(
                    "🔍 استعراض بطاقات الآيات لمجموعة محددة لهذه الكلمة:",
                    options=available_groups,
                    format_func=lambda x: f"المجموعة رقم ({x}) — ({group_counts_map.get(x, 0)} آية)",
                    key="g4_bridge_drill_g",
                )

                if selected_drill_g:
                    res_ayahs = (
                        supabase.table("ayah_group_relations")
                        .select(
                            "surah_serial, surah_name, ayah_number, ayah_text, notes"
                        )
                        .eq("topic_or_keyword", active_kw)
                        .eq("group_id", int(selected_drill_g))
                        .order("surah_serial")
                        .order("ayah_number")
                        .execute()
                    )
                    ayahs_data = res_ayahs.data if res_ayahs.data else []
                    for r in ayahs_data:
                        hl_text = render_highlighted_html(
                            str(r.get("ayah_text", "")), active_kw
                        )
                        st.markdown(
                            f"""
                            <div class="g4-ayah-card">
                                <div class="g4-ayah-header">
                                    <span class="g4-badge-surah">📖 سورة {r.get('surah_name')} — الآية ({r.get('ayah_number')})</span>
                                    <span class="g4-badge-group">المجموعة {selected_drill_g}</span>
                                </div>
                                <div class="g4-ayah-text">{hl_text}</div>
                                <div class="g4-ayah-note">🎯 <b>المقصد / الملاحظة:</b> {r.get('notes') or '—'}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

# ==============================================================================
# التبويب الثالث: خريطة التناظر الثنائي للمجموعات
# ==============================================================================
with tab_symmetry:
    st.subheader("⚖️ خريطة التناظر والتشابه بين سور القرآن والمجموعات الثمانية")
    st.markdown(
        "تُبرز هذه الخريطة التناظر البنائي بين المجموعات الثمانية: **(1 ⇄ 5)**، **(2 ⇄ 6)**، **(3 ⇄ 7)**، **(4 ⇄ 8)**."
    )

    df_rel = fetch_surah_group_relations_db()
    if df_rel.empty:
        st.warning("⚠️ لا توجد بيانات متاحة في جدول `surah_group_relations`.")
    else:
        working_df = df_rel.copy()
        working_df["paired_label"] = working_df["group_id"].apply(map_paired_group)

        col_s1, col_s2 = st.columns([2, 3])
        with col_s1:
            grp_opts = ["الكل"] + sorted(
                working_df["group_id"].dropna().unique().tolist()
            )
            sel_sym_grp = st.selectbox(
                "🎯 تصفية حسب رقم المجموعة:",
                options=grp_opts,
                key="g4_sym_grp",
            )
        with col_s2:
            sym_search = st.text_input(
                "🔍 بحث برقم أو اسم السورة أو المجموعة المتناظرة:",
                placeholder="اكتب اسم السورة أو رقمها...",
                key="g4_sym_search",
            )

        filtered_sym = working_df.copy()
        if sel_sym_grp != "الكل":
            filtered_sym = filtered_sym[filtered_sym["group_id"] == sel_sym_grp]

        if sym_search.strip():
            term = sym_search.strip()
            mask = pd.Series(False, index=filtered_sym.index)
            for col in ["surah_number", "surah_name", "group_id", "paired_label"]:
                if col in filtered_sym.columns:
                    mask = mask | filtered_sym[col].astype(str).str.contains(
                        term, na=False
                    )
            filtered_sym = filtered_sym[mask]

        rename_sym = {
            "surah_number": "رقم السورة",
            "surah_name": "اسم السورة",
            "total_ayahs": "عدد الآيات",
            "group_id": "رقم المجموعة",
            "paired_label": "المجموعة المتناظرة",
        }
        valid_sym_cols = [c for c in rename_sym if c in filtered_sym.columns]
        display_sym = filtered_sym[valid_sym_cols].rename(
            columns={c: rename_sym[c] for c in valid_sym_cols}
        )

        st.success(f"✅ عدد السور المعروضة: {len(display_sym)} سورة")
        st.dataframe(
            prepare_rtl_display_df(display_sym),
            width="stretch",
            hide_index=True,
        )

        excel_sym = convert_df_to_excel(display_sym, sheet_name="خريطة_التناظر")
        col_dl_sym, _ = st.columns([2, 5])
        with col_dl_sym:
            st.download_button(
                label="📥 تصدير خريطة التناظر إلى Excel",
                data=excel_sym,
                file_name="Surahs_Symmetry_Map.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch",
                key="dl_g4_sym",
            )

# ==============================================================================
# التبويب الرابع: الترحيل الانتقائي للآيات إلى الحصر
# ==============================================================================
with tab_migrate:
    st.subheader("✅ الترحيل الانتقائي الدقيق للآيات إلى ملف الحصر المعتمد")
    st.markdown(
        "استخدم هذه الأداة عندما ترغب في **انتقاء آيات محددة فقط** (وليس كل نتائج البحث) لإضافتها إلى جدول `ayah_group_relations`."
    )

    col_mq1, col_mq2, col_mq3 = st.columns([3.4, 1.1, 1.1])
    with col_mq1:
        mig_query = st.text_input(
            "أدخل الكلمة أو العبارة للبحث والترحيل الانتقائي:",
            placeholder="مثال: استوى، المتعال، المجيد...",
            key="g4_migrate_input",
        )
    with col_mq2:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        btn_mig_search = st.button(
            "🔍 بحث للمقارنة",
            type="primary",
            width="stretch",
            key="btn_g4_mig_search",
        )
    with col_mq3:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        st.button(
            "🔄 مسح الشاشة",
            width="stretch",
            key="btn_g4_clear_top",
            on_click=reset_migrate_screen_callback,
        )

    if "g4_migrate_results" not in st.session_state:
        st.session_state.g4_migrate_results = {"hsor": [], "quran": []}
    if "g4_migrate_word" not in st.session_state:
        st.session_state.g4_migrate_word = ""

    if btn_mig_search and mig_query.strip():
        with st.spinner("جاري مطابقة النتائج بين الحصر المعتمد والمصحف الشامل..."):
            raw_q = mig_query.strip()
            st.session_state.g4_migrate_word = raw_q

            hsor_res = search_ayah_group_relations_stable(raw_q)
            for item in hsor_res:
                s_num = int(item.get("surah_serial") or 1)
                item["_group_id"] = surah_codes_map.get(s_num, {}).get(
                    "group_id", item.get("group_id", 1)
                )

            hsor_res = sorted(
                hsor_res,
                key=lambda x: (
                    x.get("_group_id", 1),
                    x.get("surah_serial", 0),
                    x.get("ayah_number", 0),
                ),
            )
            quran_res = search_full_quran_stable(raw_q)
            st.session_state.g4_migrate_results = {"hsor": hsor_res, "quran": quran_res}

    res_hsor = st.session_state.g4_migrate_results.get("hsor", [])
    res_quran = st.session_state.g4_migrate_results.get("quran", [])
    curr_word = st.session_state.g4_migrate_word

    if curr_word:
        if res_hsor:
            st.success(
                f"✅ المسجل حالياً في حصرك المعتمد لـ «{curr_word}»: ({len(res_hsor)}) آية"
            )
            with st.expander(
                f"📂 عرض بطاقات الآيات المسجلة مسبقاً ({len(res_hsor)} آية)",
                expanded=False,
            ):
                for r in res_hsor:
                    hl_hsor = render_highlighted_html(
                        str(r.get("ayah_text", "")), curr_word
                    )
                    st.markdown(
                        f"""
                        <div class="g4-ayah-card">
                            <div class="g4-ayah-header">
                                <span class="g4-badge-surah">📖 سورة {r.get('surah_name')} — الآية ({r.get('ayah_number')})</span>
                                <span class="g4-badge-group">المجموعة {r.get('_group_id', 1)} | ✅ مسجلة بالحصر</span>
                            </div>
                            <div class="g4-ayah-text">{hl_hsor}</div>
                            <div class="g4-ayah-note">🎯 <b>المقصد:</b> {r.get('notes') or '—'}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            st.info(f"ℹ️ لا توجد سجلات مسجلة مسبقاً لـ «{curr_word}» في الحصر المعتمد.")

        st.markdown("---")

        if res_quran:
            st.markdown(
                f"### 🌍 آيات المصحف الشامل لـ «{curr_word}» (الإجمالي: {len(res_quran)} آية)"
            )

            existing_pairs = {
                (int(r.get("surah_serial", 0)), int(r.get("ayah_number", 0)))
                for r in res_hsor
            }

            if "g4_sel_map" not in st.session_state:
                st.session_state.g4_sel_map = {}
            if st.session_state.get("g4_sel_word") != curr_word:
                st.session_state.g4_sel_map = {}
                st.session_state.g4_sel_word = curr_word
                st.session_state.pop("g4_editor_verses", None)

            prev_ed = st.session_state.get("g4_editor_verses")
            if isinstance(prev_ed, dict) and "edited_rows" in prev_ed:
                sync_keys = [
                    f"{int(q.get('surah_number', 0))}:{int(q.get('ayah_number', 0))}:{i}"
                    for i, q in enumerate(res_quran)
                ]
                for r_idx_str, changes in prev_ed["edited_rows"].items():
                    try:
                        r_idx = int(r_idx_str)
                        if "اختيار للترحيل" in changes and 0 <= r_idx < len(sync_keys):
                            st.session_state.g4_sel_map[sync_keys[r_idx]] = bool(
                                changes["اختيار للترحيل"]
                            )
                    except Exception:
                        pass

            row_keys = []
            new_row_keys = []
            for idx, q in enumerate(res_quran):
                s_num = int(q.get("surah_number", 0))
                a_num = int(q.get("ayah_number", 0))
                r_key = f"{s_num}:{a_num}:{idx}"
                row_keys.append(r_key)
                if (s_num, a_num) not in existing_pairs:
                    new_row_keys.append(r_key)
                if r_key not in st.session_state.g4_sel_map:
                    st.session_state.g4_sel_map[r_key] = False

            c_a1, c_a2, c_a3, c_a4 = st.columns([1.4, 1.6, 1.4, 2.6])
            with c_a1:
                if st.button("☑️ تحديد الكل", key="g4_sel_all", width="stretch"):
                    for k in row_keys:
                        st.session_state.g4_sel_map[k] = True
                    st.session_state.pop("g4_editor_verses", None)
                    st.rerun()
            with c_a2:
                if st.button("✨ تحديد الجديد فقط", key="g4_sel_new", width="stretch"):
                    new_set = set(new_row_keys)
                    for k in row_keys:
                        st.session_state.g4_sel_map[k] = k in new_set
                    st.session_state.pop("g4_editor_verses", None)
                    st.rerun()
            with c_a3:
                if st.button("☐ إلغاء التحديد", key="g4_desel_all", width="stretch"):
                    for k in row_keys:
                        st.session_state.g4_sel_map[k] = False
                    st.session_state.pop("g4_editor_verses", None)
                    st.rerun()

            sel_count = sum(
                1 for k in row_keys if st.session_state.g4_sel_map.get(k, False)
            )
            with c_a4:
                st.info(
                    f"📌 **المحدد للترحيل:** {sel_count} من {len(row_keys)} آية (الجديد غير المسجل: {len(new_row_keys)})"
                )

            table_quran = []
            for idx, q in enumerate(res_quran, 1):
                s_num = int(q.get("surah_number", 0))
                a_num = int(q.get("ayah_number", 0))
                r_key = f"{s_num}:{a_num}:{idx - 1}"
                is_saved = (s_num, a_num) in existing_pairs
                table_quran.append(
                    {
                        "اختيار للترحيل": bool(
                            st.session_state.g4_sel_map.get(r_key, False)
                        ),
                        "مسلسل": idx,
                        "رقم السورة": s_num,
                        "اسم السورة": q.get("surah_name"),
                        "رقم الآية": a_num,
                        "منطوق الآية": q.get("ayah_text"),
                        "حالة الحفظ": (
                            "✅ مخزن مسبقاً" if is_saved else "🆕 جديد غير مخزن"
                        ),
                    }
                )

            df_q_view = pd.DataFrame(table_quran)
            edited_df = st.data_editor(
                prepare_rtl_display_df(df_q_view),
                width="stretch",
                hide_index=True,
                column_config={
                    "اختيار للترحيل": st.column_config.CheckboxColumn(
                        "ترحيل الآية؟", default=False
                    ),
                    "منطوق الآية": st.column_config.TextColumn(
                        "منطوق الآية", width="large"
                    ),
                },
                key="g4_editor_verses",
            )

            custom_mig_note = st.text_input(
                "📝 ملاحظة تدبرية مخصصة للآيات المرحّلة (اتركها فارغة لاعتماد مقصد السورة تلقائياً):",
                placeholder="اختياري...",
                key="g4_custom_mig_note",
            )

            col_exec1, col_exec2, _ = st.columns([2, 1.5, 3])
            with col_exec1:
                exec_clicked = st.button(
                    "📥 تنفيذ ترحيل الآيات المحددة إلى قاعدة البيانات",
                    type="primary",
                    width="stretch",
                    key="btn_g4_exec_migrate",
                )
            with col_exec2:
                st.button(
                    "🔄 مسح الشاشة والبدء بكلمة جديدة",
                    width="stretch",
                    key="btn_g4_clear_bottom",
                    on_click=reset_migrate_screen_callback,
                )

            if exec_clicked:
                migrated_count = 0
                dup_count = 0
                target_word_code = get_or_create_word_code(curr_word)
                norm_kw = normalize_arabic(curr_word)
                rows_to_insert = []

                for _, row in edited_df.iterrows():
                    if row["اختيار للترحيل"] is True:
                        s_num = int(row["رقم السورة"])
                        s_name = str(row["اسم السورة"]).strip()
                        a_num = int(row["رقم الآية"])
                        a_text = str(row["منطوق الآية"]).strip()

                        if (s_num, a_num) in existing_pairs:
                            dup_count += 1
                            continue

                        s_meta = surah_codes_map.get(s_num, {})
                        g_id = int(s_meta.get("group_id") or 1)
                        half_c = int(s_meta.get("half_code") or 0)
                        quarter_c = int(s_meta.get("quarter_code") or 0)

                        default_obj = surah_objectives_map.get(s_num, "مقصد السورة")
                        note_val = (
                            custom_mig_note.strip()
                            if custom_mig_note.strip()
                            else default_obj
                        )

                        plain_txt = normalize_arabic(a_text)
                        freq_cnt = (
                            max(1, plain_txt.split().count(norm_kw)) if norm_kw else 1
                        )

                        rows_to_insert.append(
                            {
                                "word_code": int(target_word_code),
                                "topic_or_keyword": curr_word,
                                "group_id": g_id,
                                "surah_serial": s_num,
                                "surah_name": s_name,
                                "ayah_number": a_num,
                                "ayah_text": a_text,
                                "notes": note_val,
                                "half_code": half_c,
                                "quarter_code": quarter_c,
                                "frequency_count": freq_cnt,
                            }
                        )
                        existing_pairs.add((s_num, a_num))

                if rows_to_insert:
                    try:
                        supabase.table("ayah_group_relations").insert(
                            rows_to_insert
                        ).execute()
                        migrated_count = len(rows_to_insert)
                        fetch_all_relations_data.clear()
                        st.success(
                            f"🎉 تم بنجاح ترحيل ({migrated_count}) آية مختارة إلى الحصر المعتمد (كود المفهوم: {target_word_code})!"
                        )
                    except Exception as e:
                        st.error(f"❌ حدث خطأ أثناء الترحيل: {e}")

                if dup_count > 0:
                    st.warning(
                        f"⚠️ تم تجاهل ({dup_count}) آية لأنها مسجلة مسبقاً في الحصر."
                    )

                if migrated_count == 0 and dup_count == 0:
                    st.warning("⚠️ لم تقم بتحديد أي آية جديدة للترحيل.")
        else:
            st.warning(f"❌ لم يتم العثور على نتائج في المصحف لـ «{curr_word}».")
