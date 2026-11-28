import pandas as pd
import streamlit as st
import theme
from database import (
    supabase,
    fetch_all_supabase_rows,
    convert_df_to_excel,
    normalize_arabic,
)


# 1. إعدادات الصفحة المستقلة
st.set_page_config(
    page_title="الفهرس الهرمي الموضوعي وإدارة موضوعات القرآن",
    page_icon="🏛️",
    layout="wide",
)

# تطبيق التنسيق المركزي الموحد وزر الرئيسية
theme.apply_custom_theme()
theme.add_home_button()
theme.render_page_guide("gate6")

# ==============================================================================
# حقن التنسيق البصري الموحد (مطابق لهوية البوابتين 4 و 5 والصفحتين 11 و 12)
# ==============================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700&display=swap');

    .g6-hero-box {
        background: linear-gradient(135deg, rgba(27, 77, 62, 0.10) 0%, rgba(212, 175, 55, 0.12) 100%);
        border: 1px solid rgba(212, 175, 55, 0.45);
        border-right: 6px solid #1B4D3E;
        border-radius: 14px;
        padding: 20px 26px;
        margin-bottom: 18px;
        text-align: center;
        font-family: 'Cairo', sans-serif;
    }
    .g6-hero-title {
        color: #1B4D3E;
        font-size: 1.85rem;
        font-weight: 700;
        margin: 0 0 6px 0;
    }
    .g6-hero-sub {
        color: #555555;
        font-size: 1.02rem;
        margin: 0;
    }
    .g6-kpi-card {
        background: #FFFFFF;
        border: 1px solid #E6E2D6;
        border-top: 4px solid #D4AF37;
        border-radius: 12px;
        padding: 14px 16px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        font-family: 'Cairo', sans-serif;
    }
    .g6-kpi-label {
        color: #666666;
        font-size: 0.90rem;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .g6-kpi-val {
        color: #1B4D3E;
        font-size: 1.65rem;
        font-weight: 700;
    }
    .g6-ayah-card {
        background: #FCFBF7;
        border: 1px solid #E5DFD0;
        border-right: 5px solid #1B4D3E;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        direction: rtl;
        text-align: right;
    }
    .g6-ayah-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 10px;
        font-family: 'Cairo', sans-serif;
    }
    .g6-badge-surah {
        background: #1B4D3E;
        color: #FFFFFF;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 600;
    }
    .g6-badge-meta {
        background: rgba(212, 175, 55, 0.22);
        color: #7A5C00;
        border: 1px solid rgba(212, 175, 55, 0.6);
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
    }
    .g6-breadcrumb {
        background: rgba(2, 132, 199, 0.07);
        border: 1px solid rgba(2, 132, 199, 0.25);
        border-radius: 8px;
        padding: 7px 14px;
        margin-bottom: 10px;
        font-family: 'Cairo', sans-serif;
        font-size: 0.90rem;
        color: #0369A1;
        font-weight: 600;
    }
    .g6-ayah-text {
        font-family: 'Amiri', serif;
        font-size: 1.44rem;
        line-height: 2.15;
        color: #1E293B;
        margin: 8px 0 6px 0;
    }
    .g6-preview-box {
        background: #F0F7F4;
        border: 1px solid #CBE3D8;
        border-right: 5px solid #1B4D3E;
        border-radius: 10px;
        padding: 12px 16px;
        margin: 10px 0 14px 0;
        direction: rtl;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def prepare_rtl_display_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    return df.iloc[:, ::-1].copy()


SURAH_NAMES_AR = {
    1: "الفاتحة",
    2: "البقرة",
    3: "آل عمران",
    4: "النساء",
    5: "المائدة",
    6: "الأنعام",
    7: "الأعراف",
    8: "الأنفال",
    9: "التوبة",
    10: "يونس",
    11: "هود",
    12: "يوسف",
    13: "الرعد",
    14: "إبراهيم",
    15: "الحجر",
    16: "النحل",
    17: "الإسراء",
    18: "الكهف",
    19: "مريم",
    20: "طه",
    21: "الأنبياء",
    22: "الحج",
    23: "المؤمنون",
    24: "النور",
    25: "الفرقان",
    26: "الشعراء",
    27: "النمل",
    28: "القصص",
    29: "العنكبوت",
    30: "الروم",
    31: "لقمان",
    32: "السجدة",
    33: "الأحزاب",
    34: "سبأ",
    35: "فاطر",
    36: "يس",
    37: "الصافات",
    38: "ص",
    39: "الزمر",
    40: "غافر",
    41: "فصلت",
    42: "الشورى",
    43: "الزخرف",
    44: "الدخان",
    45: "الجاثية",
    46: "الأحقاف",
    47: "محمد",
    48: "الفتح",
    49: "الحجرات",
    50: "ق",
    51: "الذاريات",
    52: "الطور",
    53: "النجم",
    54: "القمر",
    55: "الرحمن",
    56: "الواقعة",
    57: "الحديد",
    58: "المجادلة",
    59: "الحشر",
    60: "الممتحنة",
    61: "الصف",
    62: "الجمعة",
    63: "المنافقون",
    64: "التغابن",
    65: "الطلاق",
    66: "التحريم",
    67: "الملك",
    68: "القلم",
    69: "الحاقة",
    70: "المعارج",
    71: "نوح",
    72: "الجن",
    73: "المزمل",
    74: "المدثر",
    75: "القيامة",
    76: "الإنسان",
    77: "المرسلات",
    78: "النبأ",
    79: "النازعات",
    80: "عبس",
    81: "التكوير",
    82: "الانفطار",
    83: "المطففين",
    84: "الانشقاق",
    85: "البروج",
    86: "الطارق",
    87: "الأعلى",
    88: "الغاشية",
    89: "الفجر",
    90: "البلد",
    91: "الشمس",
    92: "الليل",
    93: "الضحى",
    94: "الشرح",
    95: "التين",
    96: "العلق",
    97: "القدر",
    98: "البينة",
    99: "الزلزلة",
    100: "العاديات",
    101: "القارعة",
    102: "التكاثر",
    103: "العصر",
    104: "الهمزة",
    105: "الفيل",
    106: "قريش",
    107: "الماعون",
    108: "الكوثر",
    109: "الكافرون",
    110: "النصر",
    111: "المسد",
    112: "الإخلاص",
    113: "الفلق",
    114: "الناس",
}

# الترويسة البصرية الموحدة
st.markdown(
    """
    <div class="g6-hero-box">
        <div class="g6-hero-title">🏛️ الفهرس الهرمي الموضوعي وإدارة موضوعات القرآن</div>
        <p class="g6-hero-sub">التصنيف الموضوعي المتدرج (الباب ⬅ الفصل ⬅ العنوان الرئيسي ⬅ التصنيف ⬅ العنوان الفرعي) وإدارة السجلات مباشرة عبر Supabase</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# دوال جلب البيانات من Supabase (بدون حد 1000 صف)
# ==============================================================================
@st.cache_data(ttl=300)
def fetch_full_quran_lookup():
    """خريطة سريعة (رقم السورة، رقم الآية) -> (منطوق الآية العثماني، رقم الصفحة)"""
    rows_q = fetch_all_supabase_rows(
        table_name="full_quran",
        select_cols="surah_number, ayah_number, ayah_text, page_number",
        order_col="id",
    )
    lookup = {}
    for r in rows_q or []:
        try:
            s_n = int(r["surah_number"])
            a_n = int(r["ayah_number"])
            lookup[(s_n, a_n)] = (
                str(r.get("ayah_text") or "").strip(),
                r.get("page_number", "—"),
            )
        except Exception:
            continue
    return lookup


@st.cache_data(ttl=60)
def fetch_hierarchical_view_data():
    try:
        rows = fetch_all_supabase_rows(
            table_name="v_quran_topics_with_ayahs",
            select_cols="*",
            order_col="topic_relation_id",
        )
        df_v = pd.DataFrame(rows) if rows else pd.DataFrame()
        if not df_v.empty:
            q_lookup = fetch_full_quran_lookup()

            def resolve_ayah_and_page(row):
                s_n = int(row.get("surah_number") or 0)
                a_n = int(row.get("start_ayah") or 0)
                q_txt, q_page = q_lookup.get((s_n, a_n), ("", "—"))
                existing_txt = str(row.get("ayah_text") or "").strip()
                existing_page = row.get("page_number")
                final_txt = existing_txt if existing_txt else q_txt
                final_page = (
                    existing_page
                    if pd.notna(existing_page) and str(existing_page).strip()
                    else q_page
                )
                return pd.Series([final_txt, final_page])

            df_v[["ayah_text", "page_number"]] = df_v.apply(
                resolve_ayah_and_page, axis=1
            )
        return df_v
    except Exception as e:
        st.error(f"❌ تعذّر جلب العرض الهرمي: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=60)
def fetch_raw_topics_table():
    try:
        rows = fetch_all_supabase_rows(
            table_name="quran_topics",
            select_cols="*",
            order_col="id",
        )
        return pd.DataFrame(rows) if rows else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


with st.spinner("جاري تحميل الفهرس الهرمي الموضوعي من قاعدة البيانات..."):
    df_view = fetch_hierarchical_view_data()
    df_topics_raw = fetch_raw_topics_table()

# بطاقات المؤشرات العليا (KPI Cards)
total_records = len(df_topics_raw) if not df_topics_raw.empty else len(df_view)
chapters_cnt = (
    df_topics_raw["main_chapter"].dropna().nunique()
    if not df_topics_raw.empty and "main_chapter" in df_topics_raw.columns
    else (
        df_view["main_chapter_name"].dropna().nunique()
        if not df_view.empty and "main_chapter_name" in df_view.columns
        else 0
    )
)
sections_cnt = (
    df_topics_raw["section_name"].dropna().nunique()
    if not df_topics_raw.empty and "section_name" in df_topics_raw.columns
    else (
        df_view["section_name"].dropna().nunique()
        if not df_view.empty and "section_name" in df_view.columns
        else 0
    )
)
surahs_cnt = (
    df_topics_raw["surah_number"].dropna().nunique()
    if not df_topics_raw.empty and "surah_number" in df_topics_raw.columns
    else (
        df_view["surah_number"].dropna().nunique()
        if not df_view.empty and "surah_number" in df_view.columns
        else 0
    )
)

k1, k2, k3, k4 = st.columns(4)
kpis = [
    (k1, "إجمالي السجلات الموضوعية", f"{total_records:,}"),
    (k2, "الأبواب الرئيسية", f"{chapters_cnt} باب"),
    (k3, "الفصول الموضوعية", f"{sections_cnt} فصل"),
    (k4, "السور المرتبطة بالفهرس", f"{surahs_cnt} سورة"),
]
for c_box, lbl, val in kpis:
    with c_box:
        st.markdown(
            f"""
            <div class="g6-kpi-card">
                <div class="g6-kpi-label">{lbl}</div>
                <div class="g6-kpi-val">{val}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

# التبويبات الثلاثة للبوابة السادسة
tab_browse, tab_add, tab_manage = st.tabs(
    [
        "🏛️ المستعرض الهرمي التفاعلي وبطاقات الآيات",
        "➕ إضافة سجل موضوعي هرمي جديد",
        "🛠️ تعديل أو حذف السجلات الحالية",
    ]
)

# ==============================================================================
# التبويب 1: المستعرض الهرمي التفاعلي وبطاقات الآيات
# ==============================================================================
with tab_browse:
    st.subheader("🏛️ تصفح الفهرس الهرمي الموضوعي للقرآن الكريم")

    if df_view.empty:
        st.warning(
            "⚠️ لا توجد بيانات متاحة في العرض `v_quran_topics_with_ayahs` حالياً."
        )
    else:
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            m_opts = ["الكل"] + sorted(
                df_view["main_chapter_name"].dropna().unique().tolist()
            )
            sel_m = st.selectbox("1️⃣ الباب الرئيسي:", options=m_opts, key="g6_sel_m")

        df_t1 = df_view.copy()
        if sel_m != "الكل":
            df_t1 = df_t1[df_t1["main_chapter_name"] == sel_m]

        with c2:
            s_opts = ["الكل"] + sorted(df_t1["section_name"].dropna().unique().tolist())
            sel_s = st.selectbox("2️⃣ الفصل:", options=s_opts, key="g6_sel_s")

        df_t2 = df_t1.copy()
        if sel_s != "الكل":
            df_t2 = df_t2[df_t2["section_name"] == sel_s]

        with c3:
            h_opts = ["الكل"] + sorted(
                df_t2["topic_heading_name"].dropna().unique().tolist()
            )
            sel_h = st.selectbox("3️⃣ العنوان الرئيسي:", options=h_opts, key="g6_sel_h")

        df_t3 = df_t2.copy()
        if sel_h != "الكل":
            df_t3 = df_t3[df_t3["topic_heading_name"] == sel_h]

        with c4:
            cat_opts = ["الكل"] + sorted(
                df_t3["topic_category_name"].dropna().unique().tolist()
            )
            sel_cat = st.selectbox("4️⃣ التصنيف:", options=cat_opts, key="g6_sel_cat")

        df_t4 = df_t3.copy()
        if sel_cat != "الكل":
            df_t4 = df_t4[df_t4["topic_category_name"] == sel_cat]

        with c5:
            sub_opts = ["الكل"] + sorted(
                df_t4["topic_sub_category_name"].dropna().unique().tolist()
            )
            sel_sub = st.selectbox(
                "5️⃣ العنوان الفرعي:", options=sub_opts, key="g6_sel_sub"
            )

        df_res = df_t4.copy()
        if sel_sub != "الكل":
            df_res = df_res[df_res["topic_sub_category_name"] == sel_sub]

        col_q_s1, col_q_s2 = st.columns([2.8, 2.2])
        with col_q_s1:
            kw_filter = st.text_input(
                "🔍 بحث سريع في العناوين الهرمية أو اسم السورة أو منطوق الآية:",
                placeholder="اكتب كلمة للبحث داخل النتائج...",
                key="g6_browse_kw_search",
            )
        with col_q_s2:
            browse_view_mode = st.radio(
                "👁️ طريقة عرض النتائج:",
                options=["بطاقات الآيات التدبرية", "الجدول الإحصائي الشامل"],
                horizontal=True,
                key="g6_browse_mode",
            )

        if kw_filter.strip():
            nq = normalize_arabic(kw_filter.strip())
            mask = df_res.apply(
                lambda r: nq
                in normalize_arabic(
                    f"{r.get('main_chapter_name', '')} {r.get('section_name', '')} "
                    f"{r.get('topic_heading_name', '')} {r.get('topic_category_name', '')} "
                    f"{r.get('topic_sub_category_name', '')} {r.get('surah_name', '')} "
                    f"{r.get('ayah_text', '')}"
                ),
                axis=1,
            )
            df_res = df_res[mask]

        if "surah_number" in df_res.columns and "start_ayah" in df_res.columns:
            df_res = df_res.sort_values(["surah_number", "start_ayah"])

        st.success(f"✅ إجمالي السجلات الموضوعية المطابقة: **{len(df_res)}** سجل")

        if not df_res.empty:
            rename_map = {
                "main_chapter_name": "الباب الرئيسي",
                "section_name": "الفصل",
                "topic_heading_name": "العنوان الرئيسي",
                "topic_category_name": "التصنيف",
                "topic_sub_category_name": "العنوان الفرعي",
                "surah_number": "رقم السورة",
                "surah_name": "اسم السورة",
                "start_ayah": "رقم الآية",
                "page_number": "رقم الصفحة",
                "ayah_text": "منطوق الآية الكريمة",
            }
            valid_cols = {k: v for k, v in rename_map.items() if k in df_res.columns}
            df_export = df_res[list(valid_cols.keys())].rename(columns=valid_cols)

            if browse_view_mode == "بطاقات الآيات التدبرية":
                limit_cards = 60
                if len(df_res) > limit_cards:
                    st.info(
                        f"ℹ️ يتم عرض أول {limit_cards} بطاقة لسرعة التصفح؛ استخدم الفلاتر الهرمية أعلاه لتضييق النطاق أو حمّل التقرير الكامل في Excel."
                    )

                for _, r in df_res.head(limit_cards).iterrows():
                    s_name = r.get("surah_name", "")
                    a_num = r.get("start_ayah", "")
                    p_num = r.get("page_number", "—")
                    a_text = r.get("ayah_text", "")
                    path_str = " ⬅ ".join(
                        [
                            str(r.get(col, "")).strip()
                            for col in [
                                "main_chapter_name",
                                "section_name",
                                "topic_heading_name",
                                "topic_category_name",
                                "topic_sub_category_name",
                            ]
                            if str(r.get(col, "")).strip()
                        ]
                    )
                    st.markdown(
                        f"""
                        <div class="g6-ayah-card">
                            <div class="g6-ayah-header">
                                <span class="g6-badge-surah">📖 سورة {s_name} — الآية ({a_num})</span>
                                <span class="g6-badge-meta">📄 صفحة {p_num}</span>
                            </div>
                            <div class="g6-breadcrumb">🏛️ {path_str}</div>
                            <div class="g6-ayah-text">﴿ {a_text} ﴾</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.dataframe(
                    prepare_rtl_display_df(df_export),
                    width="stretch",
                    hide_index=True,
                )

            excel_bytes = convert_df_to_excel(
                df_export, sheet_name="الفهرس_الهرمي_الموضوعي"
            )
            col_dl, _ = st.columns([2.2, 4.8])
            with col_dl:
                st.download_button(
                    label="📥 تصدير نتائج الفهرس الهرمي إلى Excel",
                    data=excel_bytes,
                    file_name="Hierarchical_Topic_Index_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    width="stretch",
                    key="dl_g6_hier_excel",
                )

# ==============================================================================
# التبويب 2: إضافة سجل موضوعي هرمي جديد
# ==============================================================================
with tab_add:
    st.subheader("➕ إضافة سجل موضوعي هرمي جديد إلى قاعدة البيانات")

    existing_main_chapters = (
        sorted(df_topics_raw["main_chapter"].dropna().unique().tolist())
        if not df_topics_raw.empty and "main_chapter" in df_topics_raw.columns
        else []
    )
    existing_sections = (
        sorted(df_topics_raw["section_name"].dropna().unique().tolist())
        if not df_topics_raw.empty and "section_name" in df_topics_raw.columns
        else []
    )
    existing_headings = (
        sorted(df_topics_raw["topic_heading"].dropna().unique().tolist())
        if not df_topics_raw.empty and "topic_heading" in df_topics_raw.columns
        else []
    )
    existing_categories = (
        sorted(df_topics_raw["topic_category"].dropna().unique().tolist())
        if not df_topics_raw.empty and "topic_category" in df_topics_raw.columns
        else []
    )
    existing_sub_categories = (
        sorted(df_topics_raw["topic_sub_category"].dropna().unique().tolist())
        if not df_topics_raw.empty and "topic_sub_category" in df_topics_raw.columns
        else []
    )

    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        surah_num = st.selectbox(
            "1️⃣ اختر السورة:",
            options=list(SURAH_NAMES_AR.keys()),
            format_func=lambda x: f"{x:03d} - سورة {SURAH_NAMES_AR[x]}",
            key="g6_add_surah",
        )
    with col_s2:
        ayah_num = st.number_input(
            "2️⃣ رقم الآية:", min_value=1, max_value=286, value=1, key="g6_add_ayah"
        )

    auto_page_val = ""
    preview_ayah_txt = ""
    try:
        fq_response = (
            supabase.table("full_quran")
            .select("page_number, ayah_text")
            .eq("surah_number", surah_num)
            .eq("ayah_number", int(ayah_num))
            .execute()
        )
        if fq_response.data:
            raw_page_num = fq_response.data[0].get("page_number")
            if raw_page_num is not None:
                auto_page_val = str(raw_page_num)
            preview_ayah_txt = str(fq_response.data[0].get("ayah_text") or "")
    except Exception:
        pass

    if preview_ayah_txt:
        st.markdown(
            f"""
            <div class="g6-preview-box">
                <div style="font-family:'Cairo',sans-serif; font-size:0.90rem; color:#1B4D3E; font-weight:700; margin-bottom:4px;">
                    📖 معاينة الآية المختارة (سورة {SURAH_NAMES_AR[surah_num]}: {int(ayah_num)} — صفحة {auto_page_val or '—'}):
                </div>
                <div style="font-family:'Amiri',serif; font-size:1.35rem; color:#1E293B; line-height:2.0;">
                    ﴿ {preview_ayah_txt} ﴾
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.form("g6_smart_insert_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### 🏛️ المستويات الهرمية العليا")
            mc_choice = st.selectbox(
                "الباب الرئيسي:",
                options=existing_main_chapters + ["➕ إضافة بيان جديد..."],
                key="g6_mc_c",
            )
            main_chapter = (
                st.text_input(
                    "أدخل اسم الباب الرئيسي الجديد:",
                    "الباب الأول: أركان الإسلام",
                    key="g6_mc_t",
                )
                if mc_choice == "➕ إضافة بيان جديد..."
                else mc_choice
            )

            sec_choice = st.selectbox(
                "الفصل:",
                options=existing_sections + ["➕ إضافة بيان جديد..."],
                key="g6_sec_c",
            )
            section_name = (
                st.text_input(
                    "أدخل اسم الفصل الجديد:",
                    "الفصل الأول: التوحيد",
                    key="g6_sec_t",
                )
                if sec_choice == "➕ إضافة بيان جديد..."
                else sec_choice
            )

            th_choice = st.selectbox(
                "العنوان الرئيسي:",
                options=existing_headings + ["➕ إضافة بيان جديد..."],
                key="g6_th_c",
            )
            topic_heading = (
                st.text_input(
                    "أدخل العنوان الرئيسي الجديد:",
                    "أولاً: توحيد الله",
                    key="g6_th_t",
                )
                if th_choice == "➕ إضافة بيان جديد..."
                else th_choice
            )

        with col2:
            st.markdown("##### 📂 التصنيفات ورقم الصفحة")
            tc_choice = st.selectbox(
                "التصنيف:",
                options=existing_categories + ["➕ إضافة بيان جديد..."],
                key="g6_tc_c",
            )
            topic_category = (
                st.text_input(
                    "أدخل التصنيف الجديد:",
                    "التوحيد والعقيدة",
                    key="g6_tc_t",
                )
                if tc_choice == "➕ إضافة بيان جديد..."
                else tc_choice
            )

            tsc_choice = st.selectbox(
                "العنوان الفرعي:",
                options=existing_sub_categories + ["➕ إضافة بيان جديد..."],
                key="g6_tsc_c",
            )
            topic_sub_category = (
                st.text_input(
                    "أدخل العنوان الفرعي الجديد:",
                    "1- وحدانيته تعالى",
                    key="g6_tsc_t",
                )
                if tsc_choice == "➕ إضافة بيان جديد..."
                else tsc_choice
            )

            page_desc = st.text_input(
                "رقم الصفحة (يُجلب تلقائياً من المصحف):",
                value=auto_page_val,
                key="g6_page_desc_input",
            )

        submitted = st.form_submit_button(
            "💾 حفظ وإضافة السجل الجديد لقاعدة بيانات Supabase",
            type="primary",
        )
        if submitted:
            try:
                payload = {
                    "main_chapter": main_chapter,
                    "section_name": section_name,
                    "topic_heading": topic_heading,
                    "topic_category": topic_category,
                    "topic_sub_category": topic_sub_category,
                    "surah_number": int(surah_num),
                    "surah_name_ar": SURAH_NAMES_AR.get(int(surah_num), "غير محدد"),
                    "start_ayah": int(ayah_num),
                    "end_ayah": int(ayah_num),
                    "topic_description": page_desc.strip(),
                }
                supabase.table("quran_topics").insert([payload]).execute()
                fetch_hierarchical_view_data.clear()
                fetch_raw_topics_table.clear()
                st.success("✅ تم حفظ السجل الموضوعي الجديد بنجاح مباشر في Supabase!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء الحفظ: {e}")

# ==============================================================================
# التبويب 3: تعديل أو حذف السجلات الحالية
# ==============================================================================
with tab_manage:
    st.subheader("🛠️ إدارة وتعديل وحذف السجلات الموضوعية المسجلة")

    if df_topics_raw.empty:
        st.info("ℹ️ لا توجد سجلات مسجلة حالياً في جدول `quran_topics`.")
    else:
        rename_raw = {
            "id": "رقم السجل",
            "main_chapter": "الباب الرئيسي",
            "section_name": "الفصل",
            "topic_heading": "العنوان الرئيسي",
            "topic_category": "التصنيف",
            "topic_sub_category": "العنوان الفرعي",
            "surah_number": "رقم السورة",
            "surah_name_ar": "اسم السورة",
            "start_ayah": "رقم الآية",
            "topic_description": "رقم الصفحة",
        }
        valid_raw_cols = [c for c in rename_raw if c in df_topics_raw.columns]
        df_disp_manage = df_topics_raw[valid_raw_cols].rename(
            columns={c: rename_raw[c] for c in valid_raw_cols}
        )

        search_manage = st.text_input(
            "🔍 ابحث برقم السجل أو العنوان أو اسم السورة:",
            placeholder="اكتب كلمة للبحث في السجلات...",
            key="g6_manage_search",
        )
        if search_manage.strip():
            mask_m = df_disp_manage.apply(
                lambda row: row.astype(str)
                .str.contains(search_manage.strip(), case=False, na=False)
                .any(),
                axis=1,
            )
            df_disp_manage = df_disp_manage[mask_m]

        st.dataframe(
            prepare_rtl_display_df(df_disp_manage),
            width="stretch",
            hide_index=True,
        )

        st.markdown("---")
        selected_id = st.selectbox(
            "🎯 اختر رقم السجل (ID) للتعديل أو الحذف:",
            options=df_topics_raw["id"].tolist(),
            key="g6_sel_id_edit",
        )

        if selected_id:
            record_row = df_topics_raw[df_topics_raw["id"] == selected_id].iloc[0]
            with st.form("g6_edit_delete_form"):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    e_main_chapter = st.text_input(
                        "الباب الرئيسي:", str(record_row.get("main_chapter") or "")
                    )
                    e_section_name = st.text_input(
                        "الفصل:", str(record_row.get("section_name") or "")
                    )
                    e_topic_heading = st.text_input(
                        "العنوان الرئيسي:", str(record_row.get("topic_heading") or "")
                    )
                    e_topic_category = st.text_input(
                        "التصنيف:", str(record_row.get("topic_category") or "")
                    )
                with col_e2:
                    e_topic_sub_category = st.text_input(
                        "العنوان الفرعي:",
                        str(record_row.get("topic_sub_category") or ""),
                    )
                    current_surah_num = (
                        int(record_row["surah_number"])
                        if pd.notna(record_row.get("surah_number"))
                        else 1
                    )
                    e_surah_num = st.selectbox(
                        "السورة:",
                        options=list(SURAH_NAMES_AR.keys()),
                        index=(
                            list(SURAH_NAMES_AR.keys()).index(current_surah_num)
                            if current_surah_num in SURAH_NAMES_AR
                            else 0
                        ),
                        format_func=lambda x: f"{x:03d} - سورة {SURAH_NAMES_AR[x]}",
                        key="g6_edit_surah_num",
                    )
                    e_ayah_num = st.number_input(
                        "رقم الآية:",
                        min_value=1,
                        max_value=286,
                        value=(
                            int(record_row["start_ayah"])
                            if pd.notna(record_row.get("start_ayah"))
                            else 1
                        ),
                        key="g6_edit_ayah_num",
                    )
                    e_page_desc = st.text_input(
                        "رقم الصفحة:",
                        str(record_row.get("topic_description") or ""),
                    )

                col_btn1, col_btn2, _ = st.columns([2, 2, 3])
                update_submitted = col_btn1.form_submit_button(
                    "💾 تحديث السجل المحدد", width="stretch"
                )
                delete_submitted = col_btn2.form_submit_button(
                    "🗑️ حذف السجل نهائياً", type="primary", width="stretch"
                )

                if update_submitted:
                    try:
                        updated_payload = {
                            "main_chapter": e_main_chapter,
                            "section_name": e_section_name,
                            "topic_heading": e_topic_heading,
                            "topic_category": e_topic_category,
                            "topic_sub_category": e_topic_sub_category,
                            "surah_number": int(e_surah_num),
                            "surah_name_ar": SURAH_NAMES_AR.get(
                                int(e_surah_num), "غير محدد"
                            ),
                            "start_ayah": int(e_ayah_num),
                            "end_ayah": int(e_ayah_num),
                            "topic_description": e_page_desc.strip(),
                        }
                        supabase.table("quran_topics").update(updated_payload).eq(
                            "id", selected_id
                        ).execute()
                        fetch_hierarchical_view_data.clear()
                        fetch_raw_topics_table.clear()
                        st.success(f"✅ تم تحديث السجل رقم ({selected_id}) بنجاح!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ حدث خطأ أثناء التحديث: {e}")

                if delete_submitted:
                    try:
                        supabase.table("quran_topics").delete().eq(
                            "id", selected_id
                        ).execute()
                        fetch_hierarchical_view_data.clear()
                        fetch_raw_topics_table.clear()
                        st.success(f"🗑️ تم حذف السجل رقم ({selected_id}) بنجاح!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ حدث خطأ أثناء الحذف: {e}")
