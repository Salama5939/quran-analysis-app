import re
from collections import defaultdict
import pandas as pd
import streamlit as st
import theme
from database import (
    supabase,
    fetch_all_supabase_rows,
    convert_df_to_excel,
    normalize_arabic,
    clean_arabic_display,
)

# 1. إعدادات الصفحة المستقلة
st.set_page_config(
    page_title="منصة الاستكشاف الذكي للجذور والمشتقات",
    page_icon="🔎",
    layout="wide",
)

# تطبيق التنسيق المركزي الموحد وزر الرئيسية
theme.apply_custom_theme()
theme.add_home_button()
theme.render_page_guide("gate7")

# ==============================================================================
# حقن التنسيق البصري الموحد (مطابق لهوية البوابات 4، 5، 6)
# ==============================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700&display=swap');

    .g7-hero-box {
        background: linear-gradient(135deg, rgba(27, 77, 62, 0.10) 0%, rgba(212, 175, 55, 0.12) 100%);
        border: 1px solid rgba(212, 175, 55, 0.45);
        border-right: 6px solid #1B4D3E;
        border-radius: 14px;
        padding: 20px 26px;
        margin-bottom: 18px;
        text-align: center;
        font-family: 'Cairo', sans-serif;
    }
    .g7-hero-title {
        color: #1B4D3E;
        font-size: 1.85rem;
        font-weight: 700;
        margin: 0 0 6px 0;
    }
    .g7-hero-sub {
        color: #555555;
        font-size: 1.02rem;
        margin: 0;
    }
    .g7-kpi-card {
        background: #FFFFFF;
        border: 1px solid #E6E2D6;
        border-top: 4px solid #D4AF37;
        border-radius: 12px;
        padding: 14px 16px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        font-family: 'Cairo', sans-serif;
    }
    .g7-kpi-label {
        color: #666666;
        font-size: 0.90rem;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .g7-kpi-val {
        color: #1B4D3E;
        font-size: 1.65rem;
        font-weight: 700;
    }
    .g7-ayah-card {
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
    .g7-ayah-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 10px;
        font-family: 'Cairo', sans-serif;
    }
    .g7-badge-surah {
        background: #1B4D3E;
        color: #FFFFFF;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 600;
    }
    .g7-badge-meta {
        background: rgba(212, 175, 55, 0.22);
        color: #7A5C00;
        border: 1px solid rgba(212, 175, 55, 0.6);
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
    }
    .g7-deriv-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        align-items: center;
        margin: 6px 0 8px 0;
        font-family: 'Cairo', sans-serif;
    }
    .g7-deriv-pill {
        background: rgba(2, 132, 199, 0.10);
        border: 1px solid rgba(2, 132, 199, 0.35);
        color: #0369A1;
        padding: 2px 10px;
        border-radius: 8px;
        font-size: 0.84rem;
        font-weight: 700;
    }
    .g7-ayah-text {
        font-family: 'Amiri', serif;
        font-size: 1.44rem;
        line-height: 2.15;
        color: #1E293B;
        margin: 8px 0 8px 0;
    }
    .g7-ayah-note {
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


def strip_opening_basmala(norm_text: str, surah_num: int, ayah_num: int) -> str:
    """استبعاد البسملة المدمجة في مطلع السور (2 إلى 114) لضمان دقة المرصد المعجمي"""
    if surah_num > 1 and ayah_num == 1:
        basmala_norm = normalize_arabic("بسم الله الرحمن الرحيم")
        if norm_text.startswith(basmala_norm):
            return norm_text[len(basmala_norm) :].strip()
    return norm_text


def highlight_root_derivatives_html(
    ayah_text: str, norm_root: str
) -> tuple[str, list[str]]:
    """تظليل جميع الكلمات المشتقة المحتوية على الجذر داخل الآية العثمانية وإرجاع قائمة المشتقات"""
    raw_tokens = str(ayah_text or "").split()
    if not raw_tokens or not norm_root:
        return str(ayah_text or ""), []

    out_parts = []
    found_derivatives = []
    seen_norm_derivs = set()

    for tok in raw_tokens:
        nw = normalize_arabic(tok)
        if nw and norm_root in nw:
            out_parts.append(
                f"<span style='color:#0284C7; font-weight:700;'>«{tok}»</span>"
            )
            if nw not in seen_norm_derivs:
                seen_norm_derivs.add(nw)
                found_derivatives.append(tok)
        else:
            out_parts.append(tok)

    return " ".join(out_parts), found_derivatives


# الترويسة البصرية الموحدة
st.markdown(
    """
    <div class="g7-hero-box">
        <div class="g7-hero-title">🔎 منصة الاستكشاف الذكي للجذور والمشتقات القرآنية</div>
        <p class="g7-hero-sub">استخراج المشتقات القرآنية للجذور، الأرشفة المباشرة في smart_root_topics، والمرصد المعجمي التفاعلي الشامل عبر Supabase</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# جلب البيانات من Supabase (بدون حد الـ 1000 صف)
# ==============================================================================
@st.cache_data(ttl=300)
def fetch_all_full_quran_for_roots():
    rows_q = fetch_all_supabase_rows(
        table_name="full_quran",
        select_cols="id, surah_number, surah_name, ayah_number, ayah_text, plain_ayah_text, page_number",
        order_col="id",
    )
    df_q = pd.DataFrame(rows_q) if rows_q else pd.DataFrame()
    if df_q.empty:
        return df_q

    df_q["surah_number"] = (
        pd.to_numeric(df_q["surah_number"], errors="coerce").fillna(1).astype(int)
    )
    df_q["ayah_number"] = (
        pd.to_numeric(df_q["ayah_number"], errors="coerce").fillna(1).astype(int)
    )
    df_q["page_number"] = (
        pd.to_numeric(
            (
                df_q["page_number"]
                if "page_number" in df_q.columns
                else pd.Series(1, index=df_q.index)
            ),
            errors="coerce",
        )
        .fillna(1)
        .astype(int)
    )
    df_q = df_q.sort_values(["surah_number", "ayah_number"]).reset_index(drop=True)

    # تجهيز عمود نصي مُطبّع ونظيف من البسملة المدمجة بأوائل السور
    norm_clean_list = []
    for _, r in df_q.iterrows():
        raw_plain = str(r.get("plain_ayah_text") or r.get("ayah_text") or "")
        n_txt = normalize_arabic(raw_plain)
        n_clean = strip_opening_basmala(
            n_txt, int(r["surah_number"]), int(r["ayah_number"])
        )
        norm_clean_list.append(n_clean)
    df_q["norm_clean_text"] = norm_clean_list
    return df_q


@st.cache_data(ttl=60)
def fetch_saved_smart_roots():
    try:
        rows_r = fetch_all_supabase_rows(
            table_name="smart_root_topics",
            select_cols="*",
            order_col="id",
        )
        return pd.DataFrame(rows_r) if rows_r else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300)
def fetch_surah_objectives_map():
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
    return obj_map


@st.cache_data(ttl=300)
def build_lexical_observatory(df_q: pd.DataFrame):
    """بناء فهرس المرصد المعجمي الشامل للمفردات المشتركة في المصحف"""
    word_to_rows = defaultdict(list)
    for idx, row in df_q.iterrows():
        clean_txt = str(row.get("norm_clean_text") or "")
        words = {w for w in clean_txt.split() if len(w) > 2}
        for w in words:
            word_to_rows[w].append(idx)

    shared_map = {w: idxs for w, idxs in word_to_rows.items() if len(idxs) > 1}
    summary_records = []
    all_shared_ayah_indices = set()
    all_shared_surahs = set()

    for w in sorted(shared_map.keys()):
        idxs = shared_map[w]
        all_shared_ayah_indices.update(idxs)
        sub_df = df_q.iloc[idxs]
        surahs_cnt = int(sub_df["surah_number"].nunique())
        all_shared_surahs.update(sub_df["surah_number"].unique().tolist())
        summary_records.append(
            {
                "الكلمة المفردة المشتركة": w,
                "عدد مرات التكرار (آية)": len(idxs),
                "عدد السور المنتشرة بها": surahs_cnt,
            }
        )

    df_summary = pd.DataFrame(summary_records)
    return df_summary, shared_map, len(all_shared_ayah_indices), len(all_shared_surahs)


with st.spinner("جاري تحميل بيانات المصحف الشريف والمرصد المعجمي من Supabase..."):
    df_quran = fetch_all_full_quran_for_roots()
    df_saved_roots = fetch_saved_smart_roots()
    surah_objectives_map = fetch_surah_objectives_map()

if df_quran.empty:
    st.warning("⚠️ لا توجد بيانات متاحة في جدول `full_quran` حالياً.")
    st.stop()

df_lex_summary, lex_word_to_indices, total_lex_ayahs, total_lex_surahs = (
    build_lexical_observatory(df_quran)
)

# بطاقات المؤشرات العليا (KPI Cards)
saved_records_cnt = len(df_saved_roots)
saved_unique_roots_cnt = (
    int(df_saved_roots["root_name"].dropna().nunique())
    if not df_saved_roots.empty and "root_name" in df_saved_roots.columns
    else 0
)

k1, k2, k3, k4 = st.columns(4)
kpis = [
    (k1, "الجذور المعتمدة في الأرشيف", f"{saved_unique_roots_cnt:,} جذر"),
    (k2, "إجمالي سجلات smart_root_topics", f"{saved_records_cnt:,} سجل"),
    (k3, "المفردات المشتركة بالمرصد", f"{len(df_lex_summary):,} كلمة"),
    (k4, "آيات التقاطع المعجمي بالمصحف", f"{total_lex_ayahs:,} آية"),
]
for c_box, lbl, val in kpis:
    with c_box:
        st.markdown(
            f"""
            <div class="g7-kpi-card">
                <div class="g7-kpi-label">{lbl}</div>
                <div class="g7-kpi-val">{val}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

# التبويبات الثلاثة للبوابة السابعة
tab_explore, tab_archive, tab_observatory = st.tabs(
    [
        "🔎 الاستكشاف الفردي للجذر والمشتقات والحفظ",
        "📚 أرشيف الجذور المعتمدة (smart_root_topics)",
        "🔀 المرصد المعجمي التفاعلي والحصر الشامل للتقاطعات",
    ]
)

# ==============================================================================
# التبويب 1: الاستكشاف الفردي للجذر والمشتقات والحفظ
# ==============================================================================
with tab_explore:
    st.subheader("🔎 البحث الاستكشافي الموجه للجذر الواحد ومشتقاته")
    st.markdown(
        "أدخل الجذر اللغوي أو الحروف الأساسية لاستخراج كافة الآيات ومشتقاتها المظللة بالرسم العثماني، واعتمادها في جدول `smart_root_topics`."
    )

    col_in1, col_in2 = st.columns([4, 1])
    with col_in1:
        root_input = st.text_input(
            "🔤 أدخل الجذر اللغوي أو الحروف (مثال: شكر، علم، رحم، صبر):",
            placeholder="اكتب الجذر هنا...",
            key="g7_root_search_input",
        )
    with col_in2:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        search_btn = st.button(
            "🚀 استخراج الآيات",
            type="primary",
            width="stretch",
            key="g7_btn_search_t1",
        )

    if search_btn or root_input.strip():
        query_root = root_input.strip()
        norm_query = normalize_arabic(query_root)

        if len(norm_query) < 2:
            st.warning("⚠️ الرجاء إدخال حرفين على الأقل للبحث.")
        else:
            df_results = df_quran[
                df_quran["norm_clean_text"].str.contains(
                    re.escape(norm_query), na=False
                )
            ].copy()

            st.markdown("---")
            if df_results.empty:
                st.info(f"ℹ️ لم يتم العثور على آيات تطابق الجذر «{query_root}».")
            else:
                # استخراج جميع المشتقات الفريدة التي ظهرت عبر الآيات
                all_derivs_set = set()
                hl_html_list = []
                row_derivs_list = []

                for _, r in df_results.iterrows():
                    hl_txt, r_derivs = highlight_root_derivatives_html(
                        r["ayah_text"], norm_query
                    )
                    hl_html_list.append(hl_txt)
                    row_derivs_list.append(" ، ".join(r_derivs))
                    for d in r_derivs:
                        all_derivs_set.add(d)

                df_results["hl_html"] = hl_html_list
                df_results["derivatives_str"] = row_derivs_list

                surahs_found_cnt = int(df_results["surah_number"].nunique())
                st.success(
                    f"✅ نتائج الجذر «{query_root}»: تم العثور على **{len(df_results)}** آية في **{surahs_found_cnt}** سورة، بواقع **{len(all_derivs_set)}** صيغة ومشتق قرآني."
                )

                # شريط المشتقات المستخرجة
                if all_derivs_set:
                    sample_derivs = sorted(list(all_derivs_set))[:30]
                    pills_html = "".join(
                        f"<span class='g7-deriv-pill'>{d}</span>" for d in sample_derivs
                    )
                    more_txt = (
                        f" <span style='color:#64748B; font-size:0.85rem;'>... (+{len(all_derivs_set) - 30} مشتق آخر)</span>"
                        if len(all_derivs_set) > 30
                        else ""
                    )
                    st.markdown(
                        f"<div class='g7-deriv-bar'><b>🌿 أبرز المشتقات الواردة:</b> {pills_html}{more_txt}</div>",
                        unsafe_allow_html=True,
                    )

                col_f1, col_f2 = st.columns([2.2, 2.8])
                with col_f1:
                    surah_opts_t1 = ["جميع السور"] + (
                        df_results[["surah_number", "surah_name"]]
                        .drop_duplicates()
                        .sort_values("surah_number")["surah_name"]
                        .tolist()
                    )
                    sel_surah_t1 = st.selectbox(
                        "🎯 تصفية النتائج بالسورة:",
                        options=surah_opts_t1,
                        key="g7_t1_surah_filter",
                    )
                with col_f2:
                    view_mode_t1 = st.radio(
                        "👁️ طريقة عرض الآيات:",
                        options=[
                            "بطاقات الآيات التدبرية المظللة",
                            "الجدول الإحصائي الشامل",
                        ],
                        horizontal=True,
                        key="g7_t1_view_mode",
                    )

                df_filtered_t1 = df_results.copy()
                if sel_surah_t1 != "جميع السور":
                    df_filtered_t1 = df_filtered_t1[
                        df_filtered_t1["surah_name"] == sel_surah_t1
                    ]

                export_df_t1 = df_filtered_t1[
                    [
                        "surah_number",
                        "surah_name",
                        "ayah_number",
                        "page_number",
                        "derivatives_str",
                        "ayah_text",
                    ]
                ].copy()
                export_df_t1.columns = [
                    "رقم السورة",
                    "اسم السورة",
                    "رقم الآية",
                    "رقم الصفحة",
                    "المشتقات الواردة",
                    "منطوق الآية الكريمة",
                ]

                if view_mode_t1 == "بطاقات الآيات التدبرية المظللة":
                    limit_c1 = 60
                    if len(df_filtered_t1) > limit_c1:
                        st.info(
                            f"ℹ️ يتم عرض أول {limit_c1} بطاقة لسرعة التصفح؛ يمكنك التصفية بالسورة أعلاه أو تصدير الكشف الكامل إلى Excel."
                        )

                    for _, r in df_filtered_t1.head(limit_c1).iterrows():
                        s_num = int(r["surah_number"])
                        s_name = r["surah_name"]
                        a_num = int(r["ayah_number"])
                        p_num = int(r["page_number"])
                        s_obj = surah_objectives_map.get(s_num, "—")

                        st.markdown(
                            f"""
                            <div class="g7-ayah-card">
                                <div class="g7-ayah-header">
                                    <span class="g7-badge-surah">📖 سورة {s_name} — الآية ({a_num})</span>
                                    <span class="g7-badge-meta">🌿 المشتقات: {r['derivatives_str']} | صفحة {p_num}</span>
                                </div>
                                <div class="g7-ayah-text">﴿ {r['hl_html']} ﴾</div>
                                <div class="g7-ayah-note">🎯 <b>مقصد سورة {s_name}:</b> {s_obj}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.dataframe(
                        prepare_rtl_display_df(export_df_t1),
                        width="stretch",
                        hide_index=True,
                    )

                st.markdown("---")
                st.subheader("💾 اعتماد وحفظ نتائج الجذر في جدول (smart_root_topics)")

                with st.form("g7_save_smart_root_form"):
                    save_note = st.text_input(
                        "بيان / ملاحظات الحفظ في الأرشيف:",
                        value=f"بحث آلي للجذر: {query_root} ({len(df_results)} آية)",
                    )
                    col_sv1, col_sv2 = st.columns([2.2, 4.8])
                    with col_sv1:
                        submitted_save = st.form_submit_button(
                            f"📥 حفظ كافة النتائج ({len(df_results)} آية) في Supabase",
                            type="primary",
                            width="stretch",
                        )

                    if submitted_save:
                        try:
                            records_to_insert = []
                            for _, r in df_results.iterrows():
                                records_to_insert.append(
                                    {
                                        "root_name": query_root,
                                        "derived_words": r["derivatives_str"]
                                        or save_note,
                                        "surah_number": int(r["surah_number"]),
                                        "surah_name": str(r["surah_name"]),
                                        "ayah_number": int(r["ayah_number"]),
                                        "page_number": int(r["page_number"]),
                                        "ayah_text": str(r["ayah_text"]),
                                    }
                                )
                            # الإدراج على دفعات لضمان الاستقرار
                            batch_sz = 500
                            for i in range(0, len(records_to_insert), batch_sz):
                                supabase.table("smart_root_topics").insert(
                                    records_to_insert[i : i + batch_sz]
                                ).execute()

                            fetch_saved_smart_roots.clear()
                            st.success(
                                f"✅ تم اعتماد وحفظ ({len(records_to_insert)}) سجلاً للجذر «{query_root}» بنجاح في Supabase!"
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ حدث خطأ أثناء الحفظ: {e}")

                col_dl1, _ = st.columns([2.2, 4.8])
                with col_dl1:
                    st.download_button(
                        label=f"📥 تصدير نتائج الجذر «{query_root}» إلى Excel",
                        data=convert_df_to_excel(
                            export_df_t1, sheet_name=f"Root_{query_root[:20]}"
                        ),
                        file_name=f"Smart_Root_{query_root}_Report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        width="stretch",
                        key="g7_dl_excel_t1",
                    )
    else:
        st.info("👈 أدخل الجذر في الحقل أعلاه واضغط على زر **'استخراج الآيات'** للبدء.")

# ==============================================================================
# التبويب 2: أرشيف الجذور المعتمدة (smart_root_topics)
# ==============================================================================
with tab_archive:
    st.subheader("📚 استعراض وإدارة أرشيف الجذور المعتمدة في قاعدة البيانات")

    if df_saved_roots.empty:
        st.info(
            "ℹ️ لا توجد جذور محفوظة بعد في جدول `smart_root_topics`. يمكنك استخراج أي جذر من التبويب الأول وحفظه هنا."
        )
    else:
        saved_roots_list = sorted(
            [r for r in df_saved_roots["root_name"].dropna().unique() if str(r).strip()]
        )
        c_ar1, c_ar2 = st.columns([2.2, 2.8])
        with c_ar1:
            sel_archive_root = st.selectbox(
                "🎯 اختر الجذر المعتمد لعرض آياته:",
                options=["الكل (جميع الجذور المعتمدة)"] + saved_roots_list,
                key="g7_archive_root_sel",
            )
        with c_ar2:
            ar_view_mode = st.radio(
                "👁️ أسلوب العرض:",
                options=["بطاقات الآيات التدبرية", "الجدول الإحصائي الشامل"],
                horizontal=True,
                key="g7_archive_view_mode",
            )

        df_arch_view = df_saved_roots.copy()
        if sel_archive_root != "الكل (جميع الجذور المعتمدة)":
            df_arch_view = df_arch_view[df_arch_view["root_name"] == sel_archive_root]

        if (
            "surah_number" in df_arch_view.columns
            and "ayah_number" in df_arch_view.columns
        ):
            df_arch_view = df_arch_view.sort_values(["surah_number", "ayah_number"])

        st.success(f"✅ عدد السجلات المعروضة من الأرشيف: **{len(df_arch_view)}** سجل")

        rename_arch = {
            "id": "رقم السجل",
            "root_name": "الجذر المعتمد",
            "derived_words": "المشتقات / البيان",
            "surah_number": "رقم السورة",
            "surah_name": "اسم السورة",
            "ayah_number": "رقم الآية",
            "page_number": "رقم الصفحة",
            "ayah_text": "منطوق الآية الكريمة",
        }
        valid_arch_cols = [c for c in rename_arch if c in df_arch_view.columns]
        df_arch_export = df_arch_view[valid_arch_cols].rename(
            columns={c: rename_arch[c] for c in valid_arch_cols}
        )

        if ar_view_mode == "بطاقات الآيات التدبرية":
            for _, r in df_arch_view.head(60).iterrows():
                r_root = str(r.get("root_name") or "")
                hl_arch, _ = highlight_root_derivatives_html(
                    str(r.get("ayah_text") or ""), normalize_arabic(r_root)
                )
                st.markdown(
                    f"""
                    <div class="g7-ayah-card">
                        <div class="g7-ayah-header">
                            <span class="g7-badge-surah">📖 سورة {r.get('surah_name', '')} — الآية ({r.get('ayah_number', '')})</span>
                            <span class="g7-badge-meta">🔑 الجذر: {r_root} | صفحة {r.get('page_number', '—')}</span>
                        </div>
                        <div class="g7-ayah-text">﴿ {hl_arch} ﴾</div>
                        <div class="g7-ayah-note">📝 <b>البيان / المشتقات:</b> {r.get('derived_words', '—')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.dataframe(
                prepare_rtl_display_df(df_arch_export),
                width="stretch",
                hide_index=True,
            )

        col_ad1, col_ad2, _ = st.columns([2.2, 2.4, 2.4])
        with col_ad1:
            st.download_button(
                label="📥 تصدير الأرشيف إلى Excel",
                data=convert_df_to_excel(df_arch_export, sheet_name="أرشيف_الجذور"),
                file_name="Saved_Smart_Roots_Archive.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch",
                key="g7_dl_archive_excel",
            )
        with col_ad2:
            if sel_archive_root != "الكل (جميع الجذور المعتمدة)":
                if st.button(
                    f"🗑️ حذف جذر «{sel_archive_root}» بالكامل من الأرشيف",
                    type="primary",
                    width="stretch",
                    key="g7_del_root_archive",
                ):
                    try:
                        supabase.table("smart_root_topics").delete().eq(
                            "root_name", sel_archive_root
                        ).execute()
                        fetch_saved_smart_roots.clear()
                        st.success(f"🗑️ تم حذف الجذر «{sel_archive_root}» بنجاح!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ حدث خطأ أثناء الحذف: {e}")

# ==============================================================================
# التبويب 3: المرصد المعجمي التفاعلي والحصر الشامل للتقاطعات
# ==============================================================================
with tab_observatory:
    st.subheader("🔀 المرصد المعجمي التفاعلي والحصر الشامل للمفردات المشتركة")
    st.markdown(
        "يستعرض هذا المرصد جميع المفردات القرآنية المشتركة (المتكررة في أكثر من آية) مرتبة أبجدياً مع استبعاد البسملة من أوائل السور. **انقر على أي كلمة في الجدول** لعرض آياتها فوراً."
    )

    if df_lex_summary.empty:
        st.info("ℹ️ لا توجد بيانات متاحة في المرصد المعجمي.")
    else:
        col_lx1, col_lx2 = st.columns([2.0, 2.5])
        with col_lx1:
            lex_search_kw = st.text_input(
                "🔍 تصفية جدول الملخص المعجمي بكلمة أو جذر:",
                placeholder="اكتب حرفاً أو كلمة...",
                key="g7_lex_kw_filter",
            )
        with col_lx2:
            min_freq_lex = st.slider(
                "📊 الحد الأدنى لعدد الآيات التي وردت بها الكلمة:",
                min_value=2,
                max_value=50,
                value=3,
                key="g7_lex_min_freq",
            )

        df_lex_filtered = df_lex_summary[
            df_lex_summary["عدد مرات التكرار (آية)"] >= min_freq_lex
        ].copy()

        if lex_search_kw.strip():
            nq_lx = normalize_arabic(lex_search_kw.strip())
            df_lex_filtered = df_lex_filtered[
                df_lex_filtered["الكلمة المفردة المشتركة"].str.contains(
                    re.escape(nq_lx), na=False
                )
            ]

        df_lex_filtered = df_lex_filtered.reset_index(drop=True)
        st.success(
            f"✅ عدد المفردات المطابقة في المرصد المعجمي: **{len(df_lex_filtered):,}** كلمة"
        )

        if not df_lex_filtered.empty:
            rtl_lex_summary = prepare_rtl_display_df(df_lex_filtered)
            lex_event = st.dataframe(
                rtl_lex_summary,
                width="stretch",
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                key="g7_lex_interactive_table",
            )

            clicked_lex_word = None
            try:
                selection = lex_event.get("selection", {})
                sel_r = selection.get("rows", [])
                if sel_r:
                    clicked_lex_word = df_lex_filtered.iloc[sel_r[0]][
                        "الكلمة المفردة المشتركة"
                    ]
            except Exception:
                clicked_lex_word = None

            st.markdown("---")
            lex_words_opts = df_lex_filtered["الكلمة المفردة المشتركة"].tolist()
            def_lex_idx = (
                lex_words_opts.index(clicked_lex_word)
                if clicked_lex_word and clicked_lex_word in lex_words_opts
                else 0
            )

            col_w_sel, col_w_mode = st.columns([2.6, 2.4])
            with col_w_sel:
                chosen_lex_word = st.selectbox(
                    "🎯 الكلمة المختارة لاستعراض مواضع ورودها في المصحف:",
                    options=lex_words_opts,
                    index=def_lex_idx,
                    format_func=lambda w: f"«{w}» — ({len(lex_word_to_indices.get(w, []))} آية)",
                    key="g7_lex_word_picker",
                )
            with col_w_mode:
                lex_detail_mode = st.radio(
                    "👁️ عرض آيات الكلمة المختارة:",
                    options=["بطاقات الآيات المظللة", "الجدول التفصيلي"],
                    horizontal=True,
                    key="g7_lex_detail_mode",
                )

            if chosen_lex_word and chosen_lex_word in lex_word_to_indices:
                matched_idxs = lex_word_to_indices[chosen_lex_word]
                df_lex_ayahs = df_quran.iloc[matched_idxs].copy()

                st.markdown(
                    f"### 📜 مواضع ورود كلمة «{chosen_lex_word}» في المصحف الشريف ({len(df_lex_ayahs)} آية)"
                )

                exp_lex_detail = df_lex_ayahs[
                    [
                        "surah_number",
                        "surah_name",
                        "ayah_number",
                        "page_number",
                        "ayah_text",
                    ]
                ].copy()
                exp_lex_detail.insert(0, "الكلمة المشتركة", chosen_lex_word)
                exp_lex_detail.columns = [
                    "الكلمة المشتركة",
                    "رقم السورة",
                    "اسم السورة",
                    "رقم الآية",
                    "رقم الصفحة",
                    "منطوق الآية الكريمة",
                ]

                if lex_detail_mode == "بطاقات الآيات المظللة":
                    for _, r in df_lex_ayahs.head(60).iterrows():
                        s_num = int(r["surah_number"])
                        hl_w_ayah, _ = highlight_root_derivatives_html(
                            r["ayah_text"], chosen_lex_word
                        )
                        s_obj = surah_objectives_map.get(s_num, "—")
                        st.markdown(
                            f"""
                            <div class="g7-ayah-card">
                                <div class="g7-ayah-header">
                                    <span class="g7-badge-surah">📖 سورة {r['surah_name']} — الآية ({r['ayah_number']})</span>
                                    <span class="g7-badge-meta">📄 صفحة {r['page_number']}</span>
                                </div>
                                <div class="g7-ayah-text">﴿ {hl_w_ayah} ﴾</div>
                                <div class="g7-ayah-note">🎯 <b>مقصد سورة {r['surah_name']}:</b> {s_obj}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.dataframe(
                        prepare_rtl_display_df(exp_lex_detail),
                        width="stretch",
                        hide_index=True,
                    )

                col_ex_lx1, col_ex_lx2, _ = st.columns([2.2, 2.2, 2.6])
                with col_ex_lx1:
                    st.download_button(
                        label=f"📥 تصدير آيات «{chosen_lex_word}» إلى Excel",
                        data=convert_df_to_excel(
                            exp_lex_detail, sheet_name="آيات_الكلمة_المشتركة"
                        ),
                        file_name=f"Lexical_Word_{chosen_lex_word}_Ayahs.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        width="stretch",
                        key="g7_dl_lex_ayahs",
                    )
                with col_ex_lx2:
                    st.download_button(
                        label="📥 تصدير الملخص المعجمي الأبجدي إلى Excel",
                        data=convert_df_to_excel(
                            df_lex_filtered, sheet_name="الملخص_المعجمي"
                        ),
                        file_name="Lexical_Summary_Alphabetical.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        width="stretch",
                        key="g7_dl_lex_summary",
                    )
