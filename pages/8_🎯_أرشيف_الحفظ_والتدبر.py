from datetime import datetime
import pandas as pd
import streamlit as st
import theme
from database import (
    supabase,
    convert_df_to_excel,
    get_everyayah_audio_url,
    clean_arabic_display,
)

# إعدادات الصفحة
st.set_page_config(
    page_title="أرشيف الحفظ والتدبر الشخصي | منصة تدبر القرآن",
    page_icon="🎯",
    layout="wide",
)

# تطبيق التنسيق المركزي الموحد وأزرار التنقل والدليل
theme.apply_custom_theme()
theme.add_home_button()
theme.render_page_guide("gate8")

# ==============================================================================
# التنسيق البصري الخاص بالبوابة الثامنة
# ==============================================================================
st.markdown(
    """
    <style>
    .g8-arch-hero {
        background: linear-gradient(135deg, rgba(27, 77, 62, 0.12) 0%, rgba(212, 175, 55, 0.14) 100%);
        border: 1px solid rgba(212, 175, 55, 0.50);
        border-right: 6px solid #1B4D3E;
        border-radius: 14px;
        padding: 18px 24px;
        margin-bottom: 16px;
        direction: rtl;
        text-align: right;
        font-family: 'Cairo', sans-serif;
    }
    .g8-arch-hero h2 {
        color: #1B4D3E !important;
        margin: 0 0 6px 0 !important;
        font-size: 1.55rem !important;
    }
    .g8-arch-hero p {
        color: #4A5568;
        margin: 0;
        font-size: 0.96rem;
    }
    .arch-kpi-box {
        background: #FFFFFF;
        border: 1px solid #E5DFD0;
        border-top: 4px solid #D4AF37;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        font-family: 'Cairo', sans-serif;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    .arch-kpi-lbl {
        color: #64748B;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .arch-kpi-val {
        color: #1B4D3E;
        font-size: 1.45rem;
        font-weight: 700;
        margin-top: 2px;
    }
    .arch-ayah-card {
        background: #FFFFFF;
        border: 1px solid #E5DFD0;
        border-right: 5px solid #1B4D3E;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        direction: rtl;
        text-align: right;
    }
    .arch-ayah-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        border-bottom: 1px dashed #E2E8F0;
        padding-bottom: 8px;
        margin-bottom: 10px;
        font-family: 'Cairo', sans-serif;
    }
    .arch-badge-surah {
        background: rgba(27, 77, 62, 0.10);
        color: #1B4D3E;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.90rem;
    }
    .arch-badge-status {
        background: rgba(212, 175, 55, 0.16);
        color: #7A5C00;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .arch-uthmani-text {
        font-family: 'Amiri', serif;
        font-size: 24px;
        line-height: 2.15;
        color: #1E293B;
        text-align: right;
        margin: 8px 0;
    }
    .arch-obj-note {
        background: #FCFBF7;
        border-right: 3px solid #D4AF37;
        padding: 6px 12px;
        border-radius: 6px;
        font-family: 'Cairo', sans-serif;
        font-size: 0.88rem;
        color: #475569;
        margin-top: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=60)
def fetch_archive_records() -> list[dict]:
    """جلب كافة سجلات أرشيف الحفظ والتدبر مرتبة مصحفياً"""
    try:
        res = (
            supabase.table("user_memorization_archive")
            .select("*")
            .order("surah_serial")
            .order("ayah_number")
            .execute()
        )
        return res.data if res.data else []
    except Exception as e:
        st.error(f"❌ تعذّر تحميل بيانات الأرشيف: {e}")
        return []


@st.cache_data(ttl=3600)
def fetch_surah_objectives_map() -> dict[int, str]:
    """جلب مقاصد السور لربطها ببطاقات الآيات المحفوظة"""
    try:
        res = (
            supabase.table("surah_objectives")
            .select("surah_serial, general_objective")
            .execute()
        )
        return {
            int(r["surah_serial"]): str(r.get("general_objective") or "")
            for r in (res.data or [])
            if r.get("surah_serial") is not None
        }
    except Exception:
        return {}


# الترويسة البصرية للبوابة
st.markdown(
    """
    <div class="g8-arch-hero">
        <h2>🎯 أرشيف الحفظ والتدبر الشخصي والمراجعة الدورية</h2>
        <p>متابعة رحلتك القرآنية في حفظ وتدبر الآيات الكريمة، تسجيل المراجعات اليومية، وتوثيق الفوائد والخواطر التدبرية.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

records = fetch_archive_records()
objectives_map = fetch_surah_objectives_map()

if not records:
    st.info(
        "📭 الأرشيف الشخصي فارغ حالياً. يمكنك إضافة آيات للحفظ أو التدبر من «البوابة الأولى: المصحف المصور» أو «البوابة الثالثة: المجموعات الثمانية»."
    )
    st.stop()

df_all = pd.DataFrame(records)

# حساب المؤشرات الإجمالية
total_ayahs = len(df_all)
total_surahs = df_all["surah_serial"].nunique()
total_reviews = (
    int(df_all["review_count"].fillna(0).sum())
    if "review_count" in df_all.columns
    else 0
)
status_counts = (
    df_all["memorization_status"].fillna("غير محدد").value_counts().to_dict()
)
top_status = next(iter(status_counts.keys()), "—")

c1, c2, c3, c4 = st.columns(4)
kpis = [
    (c1, "إجمالي الآيات المؤرشفة", f"{total_ayahs:,} آية"),
    (c2, "عدد السور المشمولة", f"{total_surahs} سورة"),
    (c3, "إجمالي جلسات المراجعة", f"{total_reviews:,} مرة"),
    (c4, "الحالة الأكثر تسجيلاً", top_status),
]
for box, lbl, val in kpis:
    with box:
        st.markdown(
            f"""
            <div class="arch-kpi-box">
                <div class="arch-kpi-lbl">{lbl}</div>
                <div class="arch-kpi-val" style="font-size: {'1.15rem' if box == c4 else '1.45rem'};">{val}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

tab_cards, tab_manage = st.tabs(
    [
        "📖 سجل المحفوظات وبطاقات المراجعة",
        "⚙️ إدارة الأرشيف وتحديث الحالات والتصدير",
    ]
)

# ==============================================================================
# التبويب الأول: بطاقات الآيات العثمانية والمراجعة الصوتية
# ==============================================================================
with tab_cards:
    f1, f2, f3 = st.columns([2, 2, 2])
    with f1:
        surah_options = ["جميع السور"] + [
            f"{int(s_id)} - {s_name}"
            for s_id, s_name in df_all[["surah_serial", "surah_name"]]
            .drop_duplicates()
            .sort_values("surah_serial")
            .itertuples(index=False)
        ]
        sel_surah = st.selectbox("تصفية حسب السورة:", surah_options, key="arch_f_surah")

    with f2:
        status_options = ["جميع الحالات"] + sorted(
            df_all["memorization_status"].dropna().unique().tolist()
        )
        sel_status = st.selectbox(
            "تصفية حسب الحالة:", status_options, key="arch_f_status"
        )

    with f3:
        reciters = {
            "الشيخ ماهر المعيقلي": "MaherAlMuaiqly128kbps",
            "الشيخ محمود خليل الحصري": "Husary_128kbps",
            "الشيخ سعود الشريم": "Saood_ash-Shuraym_128kbps",
        }
        sel_reciter_name = st.selectbox(
            "قارئ المراجعة الصوتية:", list(reciters.keys()), key="arch_reciter"
        )
        reciter_code = reciters[sel_reciter_name]

    df_filtered = df_all.copy()
    if sel_surah != "جميع السور":
        s_num_filter = int(sel_surah.split(" - ")[0])
        df_filtered = df_filtered[df_filtered["surah_serial"] == s_num_filter]
    if sel_status != "جميع الحالات":
        df_filtered = df_filtered[df_filtered["memorization_status"] == sel_status]

    st.caption(f"عرض ({len(df_filtered)}) آية مطابقة للتصفية الحالية:")

    for row in df_filtered.to_dict("records"):
        rec_id = row["id"]
        s_num = int(row.get("surah_serial", 1))
        s_name = row.get("surah_name", "")
        a_num = int(row.get("ayah_number", 1))
        a_text = clean_arabic_display(row.get("ayah_text", ""))
        m_status = row.get("memorization_status", "محفوظ")
        rev_cnt = int(row.get("review_count") or 0)
        last_rev = str(row.get("last_reviewed_at") or "لم تُراجع بعد")[:10]
        obj_txt = objectives_map.get(s_num, "")

        st.markdown(
            f"""
            <div class="arch-ayah-card">
                <div class="arch-ayah-header">
                    <span class="arch-badge-surah">سورة {s_name} — الآية ({a_num})</span>
                    <span class="arch-badge-status">🏷️ {m_status} | 🔄 المراجعات: {rev_cnt} | 📅 {last_rev}</span>
                </div>
                <div class="arch-uthmani-text">{a_text} ﴿{a_num}﴾</div>
                {f'<div class="arch-obj-note"><b>🎯 مقصد السورة:</b> {obj_txt}</div>' if obj_txt else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )

        b_audio, b_rev, b_del = st.columns([3, 1.5, 1])
        with b_audio:
            st.audio(
                get_everyayah_audio_url(s_num, a_num, reciter_code), format="audio/mp3"
            )
        with b_rev:
            if st.button(
                f"✅ تسجيل مراجعة (+1)",
                key=f"rev_btn_{rec_id}",
                width="stretch",
            ):
                try:
                    supabase.table("user_memorization_archive").update(
                        {
                            "review_count": rev_cnt + 1,
                            "last_reviewed_at": datetime.utcnow().isoformat(),
                        }
                    ).eq("id", rec_id).execute()
                    fetch_archive_records.clear()
                    st.toast(f"تم تسجيل مراجعة جديدة للآية ({s_name}: {a_num})!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ تعذّر تحديث المراجعة: {e}")
        with b_del:
            if st.button("🗑️ حذف", key=f"del_card_{rec_id}", width="stretch"):
                try:
                    supabase.table("user_memorization_archive").delete().eq(
                        "id", rec_id
                    ).execute()
                    fetch_archive_records.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ خطأ في الحذف: {e}")

# ==============================================================================
# التبويب الثاني: الجدول الشامل، تحديث الحالة، والتصدير إلى Excel
# ==============================================================================
with tab_manage:
    col_exp, _ = st.columns([2, 4])
    with col_exp:
        export_cols = [
            c
            for c in [
                "surah_serial",
                "surah_name",
                "ayah_number",
                "ayah_text",
                "memorization_status",
                "review_count",
                "last_reviewed_at",
            ]
            if c in df_all.columns
        ]
        excel_bytes = convert_df_to_excel(df_all[export_cols], sheet_name="أرشيف_الحفظ")
        st.download_button(
            label="📥 تصدير الأرشيف الكامل إلى Excel",
            data=excel_bytes,
            file_name="أرشيف_الحفظ_والتدبر.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch",
        )

    st.dataframe(
        df_all[export_cols].rename(
            columns={
                "surah_serial": "رقم السورة",
                "surah_name": "اسم السورة",
                "ayah_number": "رقم الآية",
                "ayah_text": "نص الآية",
                "memorization_status": "حالة الحفظ / التدبر",
                "review_count": "عدد المراجعات",
                "last_reviewed_at": "تاريخ آخر مراجعة",
            }
        ),
        width="stretch",
        hide_index=True,
    )

    st.markdown("---")
    st.subheader("✏️ تعديل حالة الحفظ أو حذف سجل")
    record_labels = {
        f"[{r['id']}] سورة {r['surah_name']} — آية ({r['ayah_number']}) ({r.get('memorization_status', '')})": r
        for r in records
    }
    selected_lbl = st.selectbox(
        "اختر السجل المطلوب تعديله:", list(record_labels.keys()), key="manage_sel_rec"
    )
    target_rec = record_labels[selected_lbl]

    u1, u2, u3 = st.columns([3, 1.5, 1.5])
    with u1:
        new_status = st.text_input(
            "تحديث حالة الحفظ / الملاحظة التدبرية:",
            value=str(target_rec.get("memorization_status") or ""),
            key="manage_new_status",
        )
    with u2:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button("💾 حفظ التعديل", width="stretch", key="manage_save_btn"):
            try:
                supabase.table("user_memorization_archive").update(
                    {"memorization_status": new_status.strip()}
                ).eq("id", target_rec["id"]).execute()
                fetch_archive_records.clear()
                st.success("✅ تم تحديث حالة السجل بنجاح.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ تعذّر التحديث: {e}")
    with u3:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🗑️ حذف السجل نهائياً", width="stretch", key="manage_del_btn"):
            try:
                supabase.table("user_memorization_archive").delete().eq(
                    "id", target_rec["id"]
                ).execute()
                fetch_archive_records.clear()
                st.success("🗑️ تم حذف السجل من الأرشيف.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ تعذّر الحذف: {e}")
