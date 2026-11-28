import re
from collections import defaultdict
import pandas as pd
import streamlit as st
import theme
from database import (
    supabase,
    fetch_all_supabase_rows,
    convert_df_to_excel,
    highlight_uthmani_keyword,
    clean_arabic_display,
    normalize_arabic,
)


# 1. إعدادات الصفحة المستقلة
st.set_page_config(
    page_title="الآيات المحورية وتقاطع الموضوعات والمتشابهات",
    page_icon="🔗",
    layout="wide",
)

# تطبيق التنسيق المركزي الموحد وزر الرئيسية
theme.apply_custom_theme()
theme.add_home_button()
theme.render_page_guide("gate5")

# ==============================================================================
# حقن التنسيق البصري الموحد (مطابق لهوية البوابة 4 والصفحتين 11 و 12)
# ==============================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700&display=swap');

    .g5-hero-box {
        background: linear-gradient(135deg, rgba(27, 77, 62, 0.10) 0%, rgba(212, 175, 55, 0.12) 100%);
        border: 1px solid rgba(212, 175, 55, 0.45);
        border-right: 6px solid #1B4D3E;
        border-radius: 14px;
        padding: 20px 26px;
        margin-bottom: 18px;
        text-align: center;
        font-family: 'Cairo', sans-serif;
    }
    .g5-hero-title {
        color: #1B4D3E;
        font-size: 1.85rem;
        font-weight: 700;
        margin: 0 0 6px 0;
    }
    .g5-hero-sub {
        color: #555555;
        font-size: 1.02rem;
        margin: 0;
    }
    .g5-kpi-card {
        background: #FFFFFF;
        border: 1px solid #E6E2D6;
        border-top: 4px solid #D4AF37;
        border-radius: 12px;
        padding: 14px 16px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        font-family: 'Cairo', sans-serif;
    }
    .g5-kpi-label {
        color: #666666;
        font-size: 0.90rem;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .g5-kpi-val {
        color: #1B4D3E;
        font-size: 1.65rem;
        font-weight: 700;
    }
    .g5-ayah-card {
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
    .g5-anchor-banner {
        background: linear-gradient(135deg, #1B4D3E 0%, #143D30 100%);
        color: #FFFFFF;
        border-right: 6px solid #D4AF37;
        border-radius: 12px;
        padding: 14px 20px;
        margin: 18px 0 10px 0;
        box-shadow: 0 3px 10px rgba(27, 77, 62, 0.16);
        direction: rtl;
        text-align: right;
    }
    .g5-anchor-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        font-family: 'Cairo', sans-serif;
        font-size: 0.94rem;
        font-weight: 700;
        color: #FDE68A;
        margin-bottom: 6px;
    }
    .g5-anchor-text {
        font-family: 'Amiri', serif;
        font-size: 1.42rem;
        line-height: 2.05;
        color: #FFFFFF;
    }
    .g5-mutashabih-subcard {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-right: 5px solid #0284C7;
        border-radius: 11px;
        padding: 13px 18px;
        margin: 0 18px 10px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        direction: rtl;
        text-align: right;
    }
    .g5-mutashabih-card {
        background: #FFFFFF;
        border: 1px solid #DDD6C5;
        border-right: 5px solid #0284C7;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 2px 7px rgba(0,0,0,0.04);
        direction: rtl;
        text-align: right;
    }
    .g5-ayah-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 8px;
        font-family: 'Cairo', sans-serif;
    }
    .g5-badge-surah {
        background: #1B4D3E;
        color: #FFFFFF;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 600;
    }
    .g5-badge-sim {
        background: rgba(2, 132, 199, 0.14);
        color: #0369A1;
        border: 1px solid rgba(2, 132, 199, 0.45);
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.86rem;
        font-weight: 700;
    }
    .g5-badge-meta {
        background: rgba(212, 175, 55, 0.22);
        color: #7A5C00;
        border: 1px solid rgba(212, 175, 55, 0.6);
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
    }
    .g5-topics-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 7px;
        align-items: center;
        margin: 8px 0 10px 0;
        font-family: 'Cairo', sans-serif;
    }
    .g5-topic-pill {
        background: rgba(2, 132, 199, 0.10);
        border: 1px solid rgba(2, 132, 199, 0.35);
        color: #0369A1;
        padding: 3px 11px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 700;
    }
    .g5-ayah-text {
        font-family: 'Amiri', serif;
        font-size: 1.44rem;
        line-height: 2.15;
        color: #1E293B;
        margin: 6px 0 8px 0;
    }
    .g5-ayah-note {
        background: rgba(27, 77, 62, 0.06);
        border-radius: 8px;
        padding: 8px 14px;
        font-family: 'Cairo', sans-serif;
        font-size: 0.92rem;
        color: #2C3E50;
    }
    .g5-legend-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 8px 14px;
        margin-bottom: 12px;
        font-family: 'Cairo', sans-serif;
        font-size: 0.90rem;
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


def strip_opening_basmala(norm_text: str, surah_num: int, ayah_num: int) -> str:
    """استبعاد البسملة المدمجة في مطلع الآية الأولى للسور (2 إلى 114) لضمان دقة المتشابهات"""
    if surah_num > 1 and ayah_num == 1:
        basmala_norm = normalize_arabic("بسم الله الرحمن الرحيم")
        if norm_text.startswith(basmala_norm):
            return norm_text[len(basmala_norm) :].strip()
    return norm_text


def highlight_multiple_keywords_html(ayah_text: str, keywords_list: list[str]) -> str:
    """تظليل جميع المفاهيم المشتركة داخل نص الآية العثماني بأسلوب الصفحة 12"""
    raw_text = str(ayah_text or "")
    if not raw_text or not keywords_list:
        return raw_text

    highlighted_tokens = set()
    for kw in keywords_list:
        md_res = highlight_uthmani_keyword(raw_text, str(kw))
        for m in re.findall(r":blue\[\*\*«(.*?)»\*\*\]", md_res):
            highlighted_tokens.add(m)

    if not highlighted_tokens:
        return raw_text

    out_words = []
    for tok in raw_text.split():
        if tok in highlighted_tokens:
            out_words.append(
                f"<span style='color:#0284C7; font-weight:700;'>«{tok}»</span>"
            )
        else:
            out_words.append(tok)
    return " ".join(out_words)


def highlight_phrase_in_uthmani_html(ayah_text: str, norm_phrase: str) -> str:
    """تظليل كلمات العبارة المختارة داخل منطوق الآية العثماني باللون اللبني"""
    raw_tokens = str(ayah_text or "").split()
    phrase_tokens = [w for w in str(norm_phrase or "").split() if w]
    if not raw_tokens or not phrase_tokens:
        return str(ayah_text or "")

    norm_raw = [normalize_arabic(t) for t in raw_tokens]
    n = len(phrase_tokens)
    matched_indices = set()

    for i in range(len(norm_raw) - n + 1):
        if norm_raw[i : i + n] == phrase_tokens:
            for k in range(i, i + n):
                matched_indices.add(k)

    # احتياطي في حال وجود فرق طفيف في التطبيع
    if not matched_indices:
        phrase_set = set(phrase_tokens)
        for idx, nw in enumerate(norm_raw):
            if nw in phrase_set:
                matched_indices.add(idx)

    out_parts = []
    for idx, tok in enumerate(raw_tokens):
        if idx in matched_indices:
            out_parts.append(
                f"<span style='color:#0284C7; font-weight:700;'>«{tok}»</span>"
            )
        else:
            out_parts.append(tok)
    return " ".join(out_parts)


def diff_highlight_ayahs_html(ayah_a: str, ayah_b: str) -> tuple[str, str]:
    """تلوين الكلمات المتفقة باللبني والكلمات الفارقة بالذهبي الداكن لإبراز موضع المتشابه"""
    words_a = str(ayah_a or "").split()
    words_b = str(ayah_b or "").split()

    norm_set_a = {normalize_arabic(w) for w in words_a if normalize_arabic(w)}
    norm_set_b = {normalize_arabic(w) for w in words_b if normalize_arabic(w)}

    def fmt_tokens(tokens: list[str], other_norm_set: set[str]) -> str:
        rendered = []
        for tok in tokens:
            nw = normalize_arabic(tok)
            if nw and nw in other_norm_set:
                rendered.append(
                    f"<span style='color:#0284C7; font-weight:700;'>{tok}</span>"
                )
            elif nw:
                rendered.append(
                    f"<span style='color:#B45309; background:rgba(245,158,11,0.14); padding:0 4px; border-radius:4px; font-weight:700;'>{tok}</span>"
                )
            else:
                rendered.append(tok)
        return " ".join(rendered)

    return fmt_tokens(words_a, norm_set_b), fmt_tokens(words_b, norm_set_a)


# الترويسة البصرية الموحدة
st.markdown(
    """
    <div class="g5-hero-box">
        <div class="g5-hero-title">🔗 الآيات المحورية وتقاطع الموضوعات والمتشابهات</div>
        <p class="g5-hero-sub">تحليل الآيات الجامعة للمفاهيم، تقاطع الموضوعات، ومحرك المتشابه اللفظي الشامل على جدول full_quran (معتمدة 100% على Supabase)</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# جلب البيانات من العروض والجداول السحابية في Supabase
# ==============================================================================
@st.cache_data(ttl=90)
def load_pivotal_data():
    rows_view = fetch_all_supabase_rows(
        table_name="v_ayah_relations_with_pages",
        select_cols="*",
        order_col="relation_id",
    )
    df_v = pd.DataFrame(rows_view) if rows_view else pd.DataFrame()

    obj_map = {}
    try:
        res_obj = (
            supabase.table("surah_objectives")
            .select("surah_number, surah_objective")
            .execute()
        )
        for r in res_obj.data or []:
            obj_map[int(r["surah_number"])] = clean_arabic_display(
                r.get("surah_objective", "")
            )
    except Exception:
        pass

    return df_v, obj_map


@st.cache_data(ttl=300)
def load_full_quran_index():
    """جلب وفهرسة جدول full_quran بالكامل (6,236 آية) مع استبعاد البسملة المدمجة في أوائل السور"""
    rows_q = fetch_all_supabase_rows(
        table_name="full_quran",
        select_cols="id, surah_number, surah_name, ayah_number, ayah_text, page_number",
        order_col="id",
    )
    df_q = pd.DataFrame(rows_q) if rows_q else pd.DataFrame()
    if df_q.empty:
        return df_q, [], {}

    df_q["surah_number"] = (
        pd.to_numeric(df_q["surah_number"], errors="coerce").fillna(1).astype(int)
    )
    df_q["ayah_number"] = (
        pd.to_numeric(df_q["ayah_number"], errors="coerce").fillna(1).astype(int)
    )
    page_numbers = (
        df_q["page_number"]
        if "page_number" in df_q.columns
        else pd.Series(1, index=df_q.index)
    )
    df_q["page_number"] = (
        pd.to_numeric(page_numbers, errors="coerce").fillna(1).astype(int)
    )
    df_q = df_q.sort_values(["surah_number", "ayah_number"]).reset_index(drop=True)

    records = []
    inverted_index = defaultdict(list)

    for idx, row in df_q.iterrows():
        s_num = int(row["surah_number"])
        a_num = int(row["ayah_number"])
        raw_txt = str(row["ayah_text"] or "").strip()
        norm_txt_full = normalize_arabic(raw_txt)
        norm_txt_clean = strip_opening_basmala(norm_txt_full, s_num, a_num)

        tokens_clean = [w for w in norm_txt_clean.split() if len(w) >= 2]
        token_set = set(tokens_clean)

        rec = {
            "idx": idx,
            "surah_number": s_num,
            "surah_name": str(row["surah_name"] or "").strip(),
            "ayah_number": a_num,
            "page_number": int(row["page_number"]),
            "ayah_text": raw_txt,
            "norm_text": norm_txt_clean,
            "tokens": tokens_clean,
            "token_set": token_set,
        }
        records.append(rec)
        for tok in token_set:
            inverted_index[tok].append(idx)

    return df_q, records, dict(inverted_index)


with st.spinner("جاري تحميل بيانات الحصر والمصحف الشامل من Supabase..."):
    df_all, surah_objectives_map = load_pivotal_data()

# تجهيز بيانات الحصر للتبويبات الثلاثة الأولى
saved_ayah_pairs = set()
if not df_all.empty:
    surah_col = (
        "surah_number"
        if "surah_number" in df_all.columns
        else ("surah_serial" if "surah_serial" in df_all.columns else df_all.columns[0])
    )
    df_all["surah_number"] = (
        pd.to_numeric(df_all[surah_col], errors="coerce").fillna(1).astype(int)
    )
    df_all["ayah_number"] = (
        pd.to_numeric(df_all["ayah_number"], errors="coerce").fillna(1).astype(int)
    )
    df_all["group_id"] = (
        pd.to_numeric(df_all["group_id"], errors="coerce").fillna(1).astype(int)
    )
    if "page_number" not in df_all.columns:
        df_all["page_number"] = 1
    else:
        df_all["page_number"] = (
            pd.to_numeric(df_all["page_number"], errors="coerce").fillna(1).astype(int)
        )

    df_all["topic_or_keyword"] = df_all["topic_or_keyword"].astype(str).str.strip()
    saved_ayah_pairs = set(zip(df_all["surah_number"], df_all["ayah_number"]))

    agg_df = (
        df_all.groupby(
            ["surah_number", "surah_name", "ayah_number", "ayah_text", "page_number"],
            as_index=False,
        )
        .agg(
            topics_count=("topic_or_keyword", lambda s: len(set(x for x in s if x))),
            topics_tuple=(
                "topic_or_keyword",
                lambda s: tuple(sorted(set(x for x in s if x))),
            ),
            groups_list=(
                "group_id",
                lambda s: "، ".join(str(x) for x in sorted(set(s))),
            ),
        )
        .sort_values(["surah_number", "ayah_number"])
        .reset_index(drop=True)
    )
    agg_df["topics_str"] = agg_df["topics_tuple"].apply(lambda t: " ، ".join(t))
    multi_df = agg_df[agg_df["topics_count"] > 1].copy().reset_index(drop=True)
    single_df = agg_df[agg_df["topics_count"] == 1].copy().reset_index(drop=True)

    surah_names_ordered = (
        agg_df[["surah_number", "surah_name"]]
        .drop_duplicates()
        .sort_values("surah_number")["surah_name"]
        .tolist()
    )

    col_f_top, _ = st.columns([2.2, 4.8])
    with col_f_top:
        sel_top_surah = st.selectbox(
            "🎯 تصفية لوحة المؤشرات حسب السورة:",
            options=["الكل (جميع السور)"] + surah_names_ordered,
            key="g5_top_surah_filter",
        )

    if sel_top_surah == "الكل (جميع السور)":
        cur_all = agg_df
        cur_multi = multi_df
        cur_single = single_df
        cur_records_cnt = len(df_all)
    else:
        cur_all = agg_df[agg_df["surah_name"] == sel_top_surah]
        cur_multi = multi_df[multi_df["surah_name"] == sel_top_surah]
        cur_single = single_df[single_df["surah_name"] == sel_top_surah]
        cur_records_cnt = len(df_all[df_all["surah_name"] == sel_top_surah])

    max_topics_in_ayah = int(cur_all["topics_count"].max()) if not cur_all.empty else 0

    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        (k1, "إجمالي سجلات الحصر", f"{cur_records_cnt:,}"),
        (k2, "الآيات المحورية المشتركة (+2)", f"{len(cur_multi):,} آية"),
        (k3, "الآيات الفريدة (مفهوم واحد)", f"{len(cur_single):,} آية"),
        (k4, "أقصى تقاطع في آية واحدة", f"{max_topics_in_ayah} مفاهيم"),
    ]
    for c_box, lbl, val in kpis:
        with c_box:
            st.markdown(
                f"""
                <div class="g5-kpi-card">
                    <div class="g5-kpi-label">{lbl}</div>
                    <div class="g5-kpi-val">{val}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)
else:
    agg_df = pd.DataFrame()
    multi_df = pd.DataFrame()

# التبويبات الأربعة للبوابة الخامسة
tab_cards, tab_intersect, tab_index, tab_mutashabih = st.tabs(
    [
        "💎 بطاقات الآيات المحورية الكبرى",
        "🔀 تقاطع مفهومين داخل الآية الواحدة",
        "📋 الفهرس الإحصائي الشامل والتصدير",
        "🪞 المتشابه اللفظي في المصحف الشامل (full_quran)",
    ]
)

# ==============================================================================
# التبويب 1: بطاقات الآيات المحورية الكبرى
# ==============================================================================
with tab_cards:
    st.subheader("💎 استعراض الآيات الجامعة لعدة مفاهيم قرآنية")

    if multi_df.empty:
        st.info("ℹ️ لا توجد آيات مشتركة لأكثر من مفهوم في قاعدة البيانات حالياً.")
    else:
        max_global_topics = int(multi_df["topics_count"].max())
        c_f1, c_f2, c_f3 = st.columns([1.8, 1.8, 2.4])
        with c_f1:
            surah_multi_opts = ["جميع السور"] + (
                multi_df[["surah_number", "surah_name"]]
                .drop_duplicates()
                .sort_values("surah_number")["surah_name"]
                .tolist()
            )
            sel_card_surah = st.selectbox(
                "1️⃣ تصفية بالسورة:",
                options=surah_multi_opts,
                key="g5_card_surah",
            )
        with c_f2:
            min_topics_val = st.slider(
                "2️⃣ الحد الأدنى للمفاهيم بالآية:",
                min_value=2,
                max_value=max(2, max_global_topics),
                value=2,
                key="g5_min_topics_slider",
            )
        with c_f3:
            sort_cards_mode = st.selectbox(
                "3️⃣ ترتيب العرض:",
                options=[
                    "الأكثر محورية وتقاطعاً (تنازلي)",
                    "ترتيب المصحف الشريف (السورة ثم الآية)",
                ],
                key="g5_sort_cards",
            )

        filtered_cards = multi_df[multi_df["topics_count"] >= min_topics_val].copy()
        if sel_card_surah != "جميع السور":
            filtered_cards = filtered_cards[
                filtered_cards["surah_name"] == sel_card_surah
            ]

        if sort_cards_mode == "الأكثر محورية وتقاطعاً (تنازلي)":
            filtered_cards = filtered_cards.sort_values(
                by=["topics_count", "surah_number", "ayah_number"],
                ascending=[False, True, True],
            )
        else:
            filtered_cards = filtered_cards.sort_values(
                by=["surah_number", "ayah_number"],
                ascending=[True, True],
            )

        st.success(f"✅ عدد الآيات المحورية المطابقة: **{len(filtered_cards)}** آية")

        display_limit = 50
        if len(filtered_cards) > display_limit:
            st.info(
                f"ℹ️ يتم عرض أول {display_limit} آية محورية لسرعة التصفح؛ يمكنك التصفية بالسورة أو رفع الحد الأدنى للمفاهيم لتضييق النطاق."
            )

        for _, row in filtered_cards.head(display_limit).iterrows():
            s_num = int(row["surah_number"])
            s_name = row["surah_name"]
            a_num = int(row["ayah_number"])
            p_num = int(row["page_number"])
            t_tuple = row["topics_tuple"]
            t_cnt = int(row["topics_count"])
            g_str = row["groups_list"]

            hl_ayah = highlight_multiple_keywords_html(row["ayah_text"], list(t_tuple))
            s_obj = surah_objectives_map.get(s_num, "—")
            pills_html = "".join(
                f"<span class='g5-topic-pill'>🔑 {kw}</span>" for kw in t_tuple
            )

            st.markdown(
                f"""
                <div class="g5-ayah-card">
                    <div class="g5-ayah-header">
                        <span class="g5-badge-surah">📖 سورة {s_name} — الآية ({a_num})</span>
                        <span class="g5-badge-meta">🔗 {t_cnt} مفاهيم مجتمعة | المجموعة: {g_str} | صفحة {p_num}</span>
                    </div>
                    <div class="g5-topics-bar">{pills_html}</div>
                    <div class="g5-ayah-text">{hl_ayah}</div>
                    <div class="g5-ayah-note">🎯 <b>مقصد سورة {s_name}:</b> {s_obj}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ==============================================================================
# التبويب 2: تقاطع مفهومين داخل الآية الواحدة
# ==============================================================================
with tab_intersect:
    st.subheader("🔀 اكتشاف الآيات التي تجمع بين مفهومين محددين")
    st.markdown(
        "اختر **مفهوماً أول** و**مفهوماً ثانياً** لاستخراج الآيات القرآنية التي جمعت بينهما معاً في سجل الحصر المعتمد."
    )

    if df_all.empty:
        st.info("ℹ️ لا توجد بيانات متاحة حالياً.")
    else:
        all_unique_keywords = sorted(
            [k for k in df_all["topic_or_keyword"].dropna().unique() if str(k).strip()]
        )

        col_i1, col_i2 = st.columns(2)
        with col_i1:
            kw_first = st.selectbox(
                "1️⃣ اختر المفهوم / الكلمة الأولى:",
                options=all_unique_keywords,
                index=0,
                key="g5_intersect_kw1",
            )
        with col_i2:
            co_occurring_kws = set()
            for t_tup in multi_df["topics_tuple"]:
                if kw_first in t_tup:
                    for item in t_tup:
                        if item != kw_first:
                            co_occurring_kws.add(item)

            second_opts = (
                sorted(list(co_occurring_kws))
                if co_occurring_kws
                else [k for k in all_unique_keywords if k != kw_first]
            )
            kw_second = st.selectbox(
                f"2️⃣ اختر المفهوم المتقاطع معه ({len(co_occurring_kws)} مفهوم متقاطع):",
                options=second_opts,
                key="g5_intersect_kw2",
            )

        if kw_first and kw_second:
            intersect_matches = multi_df[
                multi_df["topics_tuple"].apply(
                    lambda t: (kw_first in t) and (kw_second in t)
                )
            ].sort_values(["surah_number", "ayah_number"])

            if intersect_matches.empty:
                st.warning(
                    f"⚠️ لا توجد آية مسجلة في الحصر تجمع بين «{kw_first}» و«{kw_second}» معاً."
                )
            else:
                st.success(
                    f"✅ تم العثور على **{len(intersect_matches)}** آية تجمع بين «{kw_first}» و«{kw_second}»:"
                )
                for _, r in intersect_matches.iterrows():
                    s_num = int(r["surah_number"])
                    s_name = r["surah_name"]
                    a_num = int(r["ayah_number"])
                    p_num = int(r["page_number"])
                    t_tuple = r["topics_tuple"]
                    hl_ayah = highlight_multiple_keywords_html(
                        r["ayah_text"], [kw_first, kw_second]
                    )
                    s_obj = surah_objectives_map.get(s_num, "—")
                    pills_html = "".join(
                        f"<span class='g5-topic-pill'>🔑 {kw}</span>" for kw in t_tuple
                    )
                    st.markdown(
                        f"""
                        <div class="g5-ayah-card">
                            <div class="g5-ayah-header">
                                <span class="g5-badge-surah">📖 سورة {s_name} — الآية ({a_num})</span>
                                <span class="g5-badge-meta">المجموعة: {r['groups_list']} | صفحة {p_num}</span>
                            </div>
                            <div class="g5-topics-bar">{pills_html}</div>
                            <div class="g5-ayah-text">{hl_ayah}</div>
                            <div class="g5-ayah-note">🎯 <b>مقصد سورة {s_name}:</b> {s_obj}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

# ==============================================================================
# التبويب 3: الفهرس الإحصائي الشامل والتصدير إلى Excel
# ==============================================================================
with tab_index:
    st.subheader("📋 الفهرس الإحصائي الشامل للآيات المحورية والمشتركة")

    if multi_df.empty:
        st.info("ℹ️ لا توجد بيانات لعرضها في الفهرس.")
    else:
        export_df = multi_df[
            [
                "surah_number",
                "surah_name",
                "ayah_number",
                "page_number",
                "topics_count",
                "topics_str",
                "groups_list",
                "ayah_text",
            ]
        ].copy()

        export_df.columns = [
            "رقم السورة",
            "اسم السورة",
            "رقم الآية",
            "رقم الصفحة",
            "عدد المفاهيم",
            "المفاهيم والكلمات المشتركة",
            "المجموعات",
            "منطوق الآية الكريمة",
        ]

        st.dataframe(
            prepare_rtl_display_df(export_df),
            width="stretch",
            hide_index=True,
        )

        excel_bytes = convert_df_to_excel(
            export_df, sheet_name="الآيات_المحورية_المشتركة"
        )
        col_dl, _ = st.columns([2, 5])
        with col_dl:
            st.download_button(
                label="📥 تصدير الفهرس الشامل للآيات المحورية إلى Excel",
                data=excel_bytes,
                file_name="Pivotal_MultiTopic_Ayahs.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch",
                key="dl_g5_pivotal_excel",
            )

# ==============================================================================
# التبويب 4: المتشابه اللفظي في المصحف الشامل (full_quran فقط)
# ==============================================================================
with tab_mutashabih:
    st.subheader("🪞 محرك استكشاف المتشابه اللفظي في المصحف الشامل (full_quran)")
    st.markdown(
        "يبحث هذا المحرك مباشرة داخل **آيات القرآن الكريم الـ 6,236** في جدول `full_quran` فقط (مع استبعاد البسملة المدمجة في أوائل السور)، ويُبرز مواضع **الاتفاق اللفظي** ومواضع **الفروق الدقيقة**."
    )

    df_fq, fq_records, fq_inv_idx = load_full_quran_index()

    if not fq_records:
        st.error("❌ تعذّر تحميل بيانات جدول `full_quran` من قاعدة البيانات.")
    else:
        st.markdown(
            """
            <div class="g5-legend-box">
                🎨 <b>دليل الألوان البصرية للمتشابهات:</b>
                &nbsp;&nbsp;|&nbsp;&nbsp;
                <span style="color:#0284C7; font-weight:700;">■ اللون اللبني:</span> الكلمات المتفقة
                &nbsp;&nbsp;|&nbsp;&nbsp;
                <span style="color:#B45309; background:rgba(245,158,11,0.14); padding:0 5px; border-radius:4px; font-weight:700;">■ اللون الذهبي:</span> مواضع الاختلاف اللفظي (الزيادة أو التغيير)
            </div>
            """,
            unsafe_allow_html=True,
        )

        search_mode = st.radio(
            "🧭 اختر نمط استكشاف المتشابهات في المصحف الشامل:",
            options=[
                "🎯 متشابهات آية محددة (أو كل آيات السورة)",
                "📜 مسح المتشابهات المجمّع على مستوى سورة كاملة",
                "🔤 العبارات المتطابقة المتكررة (N-Grams)",
            ],
            horizontal=True,
            key="g5_mutashabih_mode",
        )

        st.markdown("---")

        surah_catalog = (
            df_fq[["surah_number", "surah_name"]]
            .drop_duplicates()
            .sort_values("surah_number")
            .to_dict("records")
        )
        surah_display_opts = [
            f"{r['surah_number']:03d} - سورة {r['surah_name']}" for r in surah_catalog
        ]
        surah_label_to_num = {
            f"{r['surah_number']:03d} - سورة {r['surah_name']}": int(r["surah_number"])
            for r in surah_catalog
        }

        # ----------------------------------------------------------------------
        # النمط 1: متشابهات آية محددة (أو كل آيات السورة + بحث لفظي للمتدبر)
        # ----------------------------------------------------------------------
        if search_mode == "🎯 متشابهات آية محددة (أو كل آيات السورة)":
            c_m1, c_m2, c_m3 = st.columns([1.8, 2.5, 1.7])
            with c_m1:
                sel_s_lbl = st.selectbox(
                    "1️⃣ اختر السورة:",
                    options=surah_display_opts,
                    index=1,  # البقرة افتراضياً
                    key="g5_mut_s1",
                )
                sel_s_num = surah_label_to_num[sel_s_lbl]

            surah_ayahs_recs = [r for r in fq_records if r["surah_number"] == sel_s_num]

            with c_m2:
                ayah_filter_kw = st.text_input(
                    "🔍 تصفية آيات السورة بكلمة (للمتدبر - اختياري):",
                    placeholder="اكتب كلمة من الآية لتضييق القائمة...",
                    key="g5_mut_ayah_kw_filter",
                )

            filtered_surah_recs = surah_ayahs_recs
            if ayah_filter_kw.strip():
                nq_f = normalize_arabic(ayah_filter_kw.strip())
                filtered_surah_recs = [
                    r for r in surah_ayahs_recs if nq_f in r["norm_text"]
                ]

            ALL_AYAHS_LABEL = "الكل (جميع آيات السورة)"
            ayah_label_map = {}
            ayah_select_opts = [ALL_AYAHS_LABEL]
            for r in filtered_surah_recs:
                snippet = r["ayah_text"][:46] + (
                    "..." if len(r["ayah_text"]) > 46 else ""
                )
                lbl = f"آية ({r['ayah_number']}) — {snippet}"
                ayah_select_opts.append(lbl)
                ayah_label_map[lbl] = r

            c_sel_a, c_sl_a = st.columns([2.8, 2.2])
            with c_sel_a:
                sel_ayah_lbl = st.selectbox(
                    f"2️⃣ اختر الآية ({len(filtered_surah_recs)} آية متاحة):",
                    options=ayah_select_opts,
                    index=1 if len(ayah_select_opts) > 1 else 0,
                    key="g5_mut_a1_rich",
                )
            with c_sl_a:
                sim_threshold = st.slider(
                    "3️⃣ الحد الأدنى لنسبة التشابه اللفظي (%):",
                    min_value=50,
                    max_value=100,
                    value=70,
                    step=5,
                    key="g5_mut_slider_1",
                )

            target_base_list = (
                filtered_surah_recs
                if sel_ayah_lbl == ALL_AYAHS_LABEL
                else (
                    [ayah_label_map[sel_ayah_lbl]]
                    if sel_ayah_lbl in ayah_label_map
                    else []
                )
            )

            if not target_base_list:
                st.warning("⚠️ لا توجد آيات مطابقة لكلمة التصفية داخل هذه السورة.")
            else:
                grouped_hits = []
                total_similar_hits = 0

                for b_rec in target_base_list:
                    base_set = b_rec["token_set"]
                    if len(base_set) < 2:
                        continue
                    candidate_indices = set()
                    for tok in base_set:
                        candidate_indices.update(fq_inv_idx.get(tok, []))

                    hits_for_b = []
                    for c_idx in candidate_indices:
                        if c_idx == b_rec["idx"]:
                            continue
                        cand = fq_records[c_idx]
                        cand_set = cand["token_set"]
                        if len(cand_set) < 2:
                            continue
                        inter_len = len(base_set & cand_set)
                        union_len = len(base_set | cand_set)
                        jaccard_pct = round((inter_len / union_len) * 100, 1)
                        containment_pct = round((inter_len / len(base_set)) * 100, 1)
                        score_pct = max(
                            jaccard_pct,
                            round((jaccard_pct + containment_pct) / 2, 1),
                        )
                        if score_pct >= sim_threshold:
                            hits_for_b.append((score_pct, cand))

                    if hits_for_b:
                        hits_for_b.sort(
                            key=lambda x: (
                                -x[0],
                                x[1]["surah_number"],
                                x[1]["ayah_number"],
                            )
                        )
                        grouped_hits.append((b_rec, hits_for_b))
                        total_similar_hits += len(hits_for_b)

                if not grouped_hits:
                    st.warning(
                        f"⚠️ لم يتم العثور على آيات متشابهة بنسبة {sim_threshold}% فأكثر. جرّب تقليل شريط التمرير."
                    )
                else:
                    st.success(
                        f"✅ تم العثور على **{len(grouped_hits)}** آية مرجعية لها نظائر متشابهة، بإجمالي **{total_similar_hits}** موضع تشابه في المصحف:"
                    )

                    export_rows_m1 = []
                    rendered_cards_cnt = 0
                    MAX_RENDER_CARDS = 65

                    for b_rec, hits_for_b in grouped_hits:
                        if rendered_cards_cnt < MAX_RENDER_CARDS:
                            st.markdown(
                                f"""
                                <div class="g5-anchor-banner">
                                    <div class="g5-anchor-top">
                                        <span>📌 الآية المرجعية: سورة {b_rec['surah_name']} — الآية ({b_rec['ayah_number']}) | صفحة {b_rec['page_number']}</span>
                                        <span>🔗 عدد النظائر المتشابهة: {len(hits_for_b)} آية</span>
                                    </div>
                                    <div class="g5-anchor-text">﴿ {b_rec['ayah_text']} ﴾</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                        for score_pct, cand in hits_for_b:
                            export_rows_m1.append(
                                {
                                    "السورة المرجعية": b_rec["surah_name"],
                                    "الآية المرجعية": b_rec["ayah_number"],
                                    "منطوق الآية المرجعية": b_rec["ayah_text"],
                                    "السورة المتشابهة": cand["surah_name"],
                                    "الآية المتشابهة": cand["ayah_number"],
                                    "صفحة المتشابهة": cand["page_number"],
                                    "نسبة التشابه %": score_pct,
                                    "منطوق الآية المتشابهة": cand["ayah_text"],
                                }
                            )
                            if rendered_cards_cnt < MAX_RENDER_CARDS:
                                _, hl_cand = diff_highlight_ayahs_html(
                                    b_rec["ayah_text"], cand["ayah_text"]
                                )
                                st.markdown(
                                    f"""
                                    <div class="g5-mutashabih-subcard">
                                        <div class="g5-ayah-header">
                                            <span class="g5-badge-surah">📖 سورة {cand['surah_name']} — الآية ({cand['ayah_number']})</span>
                                            <span class="g5-badge-sim">🎯 نسبة التشابه: {score_pct}% | صفحة {cand['page_number']}</span>
                                        </div>
                                        <div class="g5-ayah-text">﴿ {hl_cand} ﴾</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                                rendered_cards_cnt += 1

                    if total_similar_hits > MAX_RENDER_CARDS:
                        st.info(
                            f"ℹ️ تم عرض أول {MAX_RENDER_CARDS} بطاقة لسرعة التصفح؛ يمكنك تحميل الكشف الكامل ({total_similar_hits} موضع) في ملف Excel أدناه."
                        )

                    df_exp_m1 = pd.DataFrame(export_rows_m1)
                    st.download_button(
                        label="📥 تصدير متشابهات الآيات إلى Excel",
                        data=convert_df_to_excel(
                            df_exp_m1, sheet_name="متشابهات_الآيات"
                        ),
                        file_name=f"Mutashabihat_Surah_{sel_s_num}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="dl_g5_mut_m1",
                    )

        # ----------------------------------------------------------------------
        # النمط 2: مسح المتشابهات المجمّع على مستوى سورة كاملة (هرمي بدون تكرار)
        # ----------------------------------------------------------------------
        elif search_mode == "📜 مسح المتشابهات المجمّع على مستوى سورة كاملة":
            c_s1, c_s2, c_s3 = st.columns([2.0, 2.2, 1.8])
            with c_s1:
                scan_s_lbl = st.selectbox(
                    "1️⃣ اختر السورة المراد مسح متشابهاتها:",
                    options=surah_display_opts,
                    index=1,
                    key="g5_mut_scan_s",
                )
                scan_s_num = surah_label_to_num[scan_s_lbl]
            with c_s2:
                scan_scope = st.selectbox(
                    "2️⃣ نطاق المقارنة:",
                    options=[
                        "بين هذه السورة وجميع سور المصحف",
                        "داخل هذه السورة فقط (متشابهات داخلية)",
                    ],
                    key="g5_mut_scan_scope",
                )
            with c_s3:
                scan_threshold = st.slider(
                    "3️⃣ الحد الأدنى لنسبة التشابه (%):",
                    min_value=60,
                    max_value=100,
                    value=75,
                    step=5,
                    key="g5_mut_slider_2",
                )

            view_style_m2 = st.radio(
                "👁️ أسلوب عرض المجموعات:",
                options=[
                    "عرض هرمي مفتوح (رأس الآية ⬅ بطاقات النظائر)",
                    "عرض مطوي برؤوس الآيات (للسور الطويلة)",
                ],
                horizontal=True,
                key="g5_mut_m2_style",
            )

            target_recs = [r for r in fq_records if r["surah_number"] == scan_s_num]
            grouped_surah_matches = []
            total_matches_cnt = 0

            for b_rec in target_recs:
                b_set = b_rec["token_set"]
                if len(b_set) < 3:
                    continue
                cand_ids = set()
                for tok in b_set:
                    cand_ids.update(fq_inv_idx.get(tok, []))

                matches_for_ayah = []
                for cid in cand_ids:
                    if cid == b_rec["idx"]:
                        continue
                    c_rec = fq_records[cid]
                    if (
                        scan_scope == "داخل هذه السورة فقط (متشابهات داخلية)"
                        and c_rec["surah_number"] != scan_s_num
                    ):
                        continue

                    c_set = c_rec["token_set"]
                    if len(c_set) < 3:
                        continue
                    inter_n = len(b_set & c_set)
                    union_n = len(b_set | c_set)
                    sim_pct = round((inter_n / union_n) * 100, 1)

                    if sim_pct >= scan_threshold:
                        matches_for_ayah.append((sim_pct, c_rec))

                if matches_for_ayah:
                    matches_for_ayah.sort(
                        key=lambda x: (
                            -x[0],
                            x[1]["surah_number"],
                            x[1]["ayah_number"],
                        )
                    )
                    grouped_surah_matches.append((b_rec, matches_for_ayah))
                    total_matches_cnt += len(matches_for_ayah)

            if not grouped_surah_matches:
                st.warning(
                    f"⚠️ لا توجد آيات متشابهة بنسبة {scan_threshold}% فأكثر في هذا النطاق. جرّب تقليل شريط التمرير."
                )
            else:
                surah_title_clean = target_recs[0]["surah_name"]
                st.success(
                    f"✅ في سورة ({surah_title_clean}): توجد **{len(grouped_surah_matches)}** آية لها نظائر متشابهة، بإجمالي **{total_matches_cnt}** موضع تشابه (بنسبة ≥ {scan_threshold}%):"
                )

                export_rows_m2 = []
                is_collapsed = view_style_m2.startswith("عرض مطوي")

                for b_rec, matches_for_ayah in grouped_surah_matches:
                    for sim_pct, c_rec in matches_for_ayah:
                        export_rows_m2.append(
                            {
                                "السورة الأصلية": b_rec["surah_name"],
                                "الآية الأصلية": b_rec["ayah_number"],
                                "منطوق الآية الأصلية": b_rec["ayah_text"],
                                "السورة المتشابهة": c_rec["surah_name"],
                                "الآية المتشابهة": c_rec["ayah_number"],
                                "صفحة المتشابهة": c_rec["page_number"],
                                "نسبة التشابه %": sim_pct,
                                "منطوق الآية المتشابهة": c_rec["ayah_text"],
                            }
                        )

                    if is_collapsed:
                        with st.expander(
                            f"📌 آية سورة {b_rec['surah_name']} رقم ({b_rec['ayah_number']}) — [عدد النظائر: {len(matches_for_ayah)}] — {b_rec['ayah_text'][:75]}...",
                            expanded=False,
                        ):
                            st.markdown(
                                f"<div class='g5-ayah-text' style='font-weight:700; color:#1B4D3E;'>﴿ {b_rec['ayah_text']} ﴾</div>",
                                unsafe_allow_html=True,
                            )
                            for sim_pct, c_rec in matches_for_ayah:
                                _, hl_c = diff_highlight_ayahs_html(
                                    b_rec["ayah_text"], c_rec["ayah_text"]
                                )
                                st.markdown(
                                    f"""
                                    <div class="g5-mutashabih-subcard">
                                        <div class="g5-ayah-header">
                                            <span class="g5-badge-surah">📖 سورة {c_rec['surah_name']} — الآية ({c_rec['ayah_number']})</span>
                                            <span class="g5-badge-sim">🎯 نسبة التطابق: {sim_pct}% | صفحة {c_rec['page_number']}</span>
                                        </div>
                                        <div class="g5-ayah-text">﴿ {hl_c} ﴾</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                    else:
                        # رأس الآية الأصلية مرة واحدة فقط
                        st.markdown(
                            f"""
                            <div class="g5-anchor-banner">
                                <div class="g5-anchor-top">
                                    <span>📌 آية سورة {b_rec['surah_name']} رقم ({b_rec['ayah_number']}) — صفحة {b_rec['page_number']}</span>
                                    <span>🔗 لها ({len(matches_for_ayah)}) نظائر متشابهة</span>
                                </div>
                                <div class="g5-anchor-text">﴿ {b_rec['ayah_text']} ﴾</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        # بطاقات النظائر المرتبطة بها فقط دون تكرار الآية الأصلية
                        for sim_pct, c_rec in matches_for_ayah:
                            _, hl_c = diff_highlight_ayahs_html(
                                b_rec["ayah_text"], c_rec["ayah_text"]
                            )
                            st.markdown(
                                f"""
                                <div class="g5-mutashabih-subcard">
                                    <div class="g5-ayah-header">
                                        <span class="g5-badge-surah">📖 سورة {c_rec['surah_name']} — الآية ({c_rec['ayah_number']})</span>
                                        <span class="g5-badge-sim">🎯 نسبة التطابق: {sim_pct}% | صفحة {c_rec['page_number']}</span>
                                    </div>
                                    <div class="g5-ayah-text">﴿ {hl_c} ﴾</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                df_exp_m2 = pd.DataFrame(export_rows_m2)
                st.download_button(
                    label="📥 تصدير متشابهات السورة المجمّعة إلى Excel",
                    data=convert_df_to_excel(
                        df_exp_m2, sheet_name="متشابهات_السورة_المجمعة"
                    ),
                    file_name=f"Surah_{scan_s_num}_Grouped_Mutashabihat.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_g5_mut_m2",
                )

        # ----------------------------------------------------------------------
        # النمط 3: العبارات المتطابقة المتكررة (N-Grams) + اختيار تفاعلي للبطاقات
        # ----------------------------------------------------------------------
        else:
            c_ng1, c_ng2 = st.columns([2.5, 2.5])
            with c_ng1:
                ngram_len = st.slider(
                    "1️⃣ طول العبارة القرآنية المتتالية (عدد الكلمات):",
                    min_value=3,
                    max_value=7,
                    value=4,
                    key="g5_mut_ngram_slider",
                )
            with c_ng2:
                min_occ_slider = st.slider(
                    "2️⃣ الحد الأدنى لعدد مرات التكرار في المصحف:",
                    min_value=2,
                    max_value=20,
                    value=3,
                    key="g5_mut_ngram_occ",
                )

            ngram_map = defaultdict(list)
            for rec in fq_records:
                toks = rec["tokens"]
                if len(toks) >= ngram_len:
                    seen_in_ayah = set()
                    for i in range(len(toks) - ngram_len + 1):
                        phrase = " ".join(toks[i : i + ngram_len])
                        if phrase not in seen_in_ayah:
                            seen_in_ayah.add(phrase)
                            ngram_map[phrase].append(rec)

            freq_phrases = [
                (phrase, recs)
                for phrase, recs in ngram_map.items()
                if len(recs) >= min_occ_slider
            ]
            freq_phrases.sort(key=lambda x: (-len(x[1]), x[0]))

            st.success(
                f"✅ تم استخراج **{len(freq_phrases)}** عبارة قرآنية متطابقة بطول ({ngram_len}) كلمات وتكررت ({min_occ_slider}) مرات فأكثر (مع استبعاد البسملة):"
            )

            if freq_phrases:
                phrase_to_recs = {p: r_list for p, r_list in freq_phrases}
                ng_table = []
                for phrase, recs in freq_phrases[:250]:
                    locs = " ، ".join(
                        f"{r['surah_name']} ({r['ayah_number']})" for r in recs[:10]
                    )
                    if len(recs) > 10:
                        locs += f" ... (+{len(recs) - 10})"
                    ng_table.append(
                        {
                            "العبارة المتطابقة (مجرّدة)": phrase,
                            "عدد الآيات": len(recs),
                            "مواضع الورود في المصحف": locs,
                        }
                    )

                df_ng_view = pd.DataFrame(ng_table)
                rtl_ng_df = prepare_rtl_display_df(df_ng_view)

                st.info(
                    "💡 **انقر على أي صف في الجدول أدناه** أو اختر العبارة من القائمة لعرض جميع بطاقات آياتها الكريمة بالرسم العثماني:"
                )

                table_event = st.dataframe(
                    rtl_ng_df,
                    width="stretch",
                    hide_index=True,
                    on_select="rerun",
                    selection_mode="single-row",
                    key="g5_ngram_interactive_table",
                )

                # استخراج العبارة المختارة بالنقر على الجدول إن وجدت
                clicked_phrase = None
                try:
                    selection = table_event.get("selection")
                    sel_rows = selection.get("rows", []) if selection else []
                    if sel_rows:
                        clicked_phrase = df_ng_view.iloc[sel_rows[0]][
                            "العبارة المتطابقة (مجرّدة)"
                        ]
                except Exception:
                    clicked_phrase = None

                st.markdown("---")
                c_pick1, c_pick2 = st.columns([1.8, 3.2])
                with c_pick1:
                    phrase_kw_filter = st.text_input(
                        "🔍 بحث بكلمة داخل العبارات المتكررة:",
                        placeholder="مثال: الأنهار، الصالحات، قدير...",
                        key="g5_ngram_kw_search",
                    )

                available_phrases = [p for p, _ in freq_phrases]
                if phrase_kw_filter.strip():
                    nq_p = normalize_arabic(phrase_kw_filter.strip())
                    filtered_p_list = [p for p in available_phrases if nq_p in p]
                else:
                    filtered_p_list = available_phrases

                with c_pick2:
                    if not filtered_p_list:
                        st.warning("⚠️ لا توجد عبارة متكررة تطابق كلمة البحث.")
                        chosen_phrase = None
                    else:
                        default_idx = 0
                        if clicked_phrase and clicked_phrase in filtered_p_list:
                            default_idx = filtered_p_list.index(clicked_phrase)

                        chosen_phrase = st.selectbox(
                            "🎯 أو اختر العبارة المتطابقة من القائمة لعرض آياتها:",
                            options=filtered_p_list,
                            index=default_idx,
                            format_func=lambda p: f"«{p}» — ({len(phrase_to_recs[p])} آية في المصحف)",
                            key="g5_ngram_phrase_picker",
                        )

                # عرض بطاقات جميع الآيات الخاصة بالعبارة المختارة
                if chosen_phrase and chosen_phrase in phrase_to_recs:
                    matched_ayah_recs = phrase_to_recs[chosen_phrase]
                    st.markdown(
                        f"### 📜 مواضع ورود عبارة «{chosen_phrase}» في المصحف الشريف ({len(matched_ayah_recs)} آية)"
                    )

                    phrase_export_rows = []
                    for rec in matched_ayah_recs:
                        s_num = rec["surah_number"]
                        s_name = rec["surah_name"]
                        a_num = rec["ayah_number"]
                        p_num = rec["page_number"]
                        is_in_hsor = (s_num, a_num) in saved_ayah_pairs
                        status_badge = (
                            "✅ مسجلة بالحصر"
                            if is_in_hsor
                            else "🆕 بالمصحف (غير مسجلة بالحصر)"
                        )
                        hl_phrase_ayah = highlight_phrase_in_uthmani_html(
                            rec["ayah_text"], chosen_phrase
                        )
                        s_obj = surah_objectives_map.get(s_num, "—")

                        st.markdown(
                            f"""
                            <div class="g5-ayah-card">
                                <div class="g5-ayah-header">
                                    <span class="g5-badge-surah">📖 سورة {s_name} — الآية ({a_num})</span>
                                    <span class="g5-badge-meta">📄 صفحة {p_num} | {status_badge}</span>
                                </div>
                                <div class="g5-ayah-text">﴿ {hl_phrase_ayah} ﴾</div>
                                <div class="g5-ayah-note">🎯 <b>مقصد سورة {s_name}:</b> {s_obj}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        phrase_export_rows.append(
                            {
                                "العبارة المتطابقة": chosen_phrase,
                                "رقم السورة": s_num,
                                "اسم السورة": s_name,
                                "رقم الآية": a_num,
                                "رقم الصفحة": p_num,
                                "حالة الحصر": status_badge,
                                "منطوق الآية الكريمة": rec["ayah_text"],
                            }
                        )

                    col_ex1, col_ex2, _ = st.columns([2.2, 2.2, 2.6])
                    with col_ex1:
                        st.download_button(
                            label=f"📥 تصدير آيات «{chosen_phrase}» إلى Excel",
                            data=convert_df_to_excel(
                                pd.DataFrame(phrase_export_rows),
                                sheet_name="آيات_العبارة",
                            ),
                            file_name=f"Phrase_Ayahs_{ngram_len}Grams.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            width="stretch",
                            key="dl_g5_mut_phrase_ayahs",
                        )
                    with col_ex2:
                        st.download_button(
                            label="📥 تصدير جدول العبارات الكلي إلى Excel",
                            data=convert_df_to_excel(
                                df_ng_view, sheet_name="العبارات_المتطابقة"
                            ),
                            file_name=f"Quran_Repeated_{ngram_len}Grams.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            width="stretch",
                            key="dl_g5_mut_m3",
                        )
