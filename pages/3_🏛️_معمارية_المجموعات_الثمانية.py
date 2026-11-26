import os
import io
import json
import random
import importlib.util
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

HAS_DOCX = importlib.util.find_spec("docx") is not None

from theme import apply_custom_theme, add_home_button
from database import (
    supabase,
    normalize_arabic,
    convert_df_to_excel,
    clean_dataframe_for_display,
    fetch_all_supabase_rows,
    search_full_quran_stable,
    highlight_uthmani_keyword,
    save_ayah_to_memorization_archive,
    save_keyword_bulk_to_relations,
    clean_arabic_display,
    get_everyayah_audio_url,
    init_rtl_docx,
)

# ==============================================================================
# إعدادات الصفحة التجريبية المستقلة (في المجلد الجذري بجانب Home.py)
# ==============================================================================
st.set_page_config(
    page_title="اختبار التبويب الرابع المطور — المجموعات الثمانية",
    page_icon="🧪",
    layout="wide",
)

apply_custom_theme()
add_home_button()

# ==============================================================================
# تنسيقات CSS مخصصة للصفحة
# ==============================================================================
st.markdown(
    """
    <style>
        .g8-hero {
            background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 60%, #0D9488 100%);
            color: #FFFFFF !important;
            padding: 1.5rem 2rem;
            border-radius: 16px;
            border-bottom: 4px solid #D97706;
            margin-bottom: 1.2rem;
            box-shadow: 0 6px 20px rgba(15, 23, 42, 0.12);
        }
        .g8-hero h2 {
            font-family: 'Amiri', serif !important;
            color: #FFFFFF !important;
            text-align: center !important;
            font-size: 1.95rem !important;
            margin-bottom: 0.35rem !important;
        }
        .g8-hero p {
            color: #E2E8F0 !important;
            text-align: center !important;
            font-size: 0.98rem !important;
            margin: 0 !important;
        }
        .surah-obj-banner {
            background-color: #FFFFFF;
            border: 1px solid #E2D9C8;
            border-right: 6px solid #D97706;
            border-radius: 12px;
            padding: 1.15rem 1.4rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(44, 34, 30, 0.05);
        }
        .ayah-card {
            background-color: #FFFFFF;
            border: 1px solid #E2D9C8;
            border-right: 5px solid #0D9488;
            border-radius: 12px;
            padding: 1.05rem 1.35rem;
            margin-bottom: 0.8rem;
            box-shadow: 0 2px 8px rgba(44, 34, 30, 0.05);
        }
        .ayah-uthmani {
            font-family: 'Amiri', serif !important;
            font-size: 1.45rem !important;
            line-height: 2.1 !important;
            color: #1E293B !important;
            text-align: right !important;
            direction: rtl !important;
            margin-bottom: 0.45rem;
        }
        .ayah-meta-badge {
            display: inline-block;
            background-color: #F3EFE4;
            color: #2C221E;
            border: 1px solid #D6CBB8;
            padding: 0.2rem 0.7rem;
            border-radius: 6px;
            font-size: 0.83rem;
            font-weight: 700;
            margin-left: 0.45rem;
        }
        .badge-saved {
            display: inline-block;
            background-color: #DCFCE7;
            color: #166534;
            border: 1px solid #86EFAC;
            padding: 0.18rem 0.65rem;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 800;
            margin-bottom: 0.4rem;
        }
        .badge-new-quran {
            display: inline-block;
            background-color: #DBEAFE;
            color: #1E40AF;
            border: 1px solid #93C5FD;
            padding: 0.18rem 0.65rem;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 800;
            margin-bottom: 0.4rem;
        }
        .discovery-panel {
            background-color: #FFFFFF;
            border: 1px solid #CBD5E1;
            border-right: 5px solid #1E3A8A;
            border-radius: 12px;
            padding: 0.85rem 1.2rem;
            margin-bottom: 0.9rem;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# دوال توليد بطاقات التدبر (Word .docx)
# ==============================================================================
def generate_surah_tadabbur_docx(
    s_info: pd.Series, topics_df: pd.DataFrame, ayahs_df: pd.DataFrame
) -> bytes:
    doc, set_p_rtl, set_tbl_rtl, add_run_rtl, WD_ALIGN = init_rtl_docx()

    p_title = doc.add_paragraph()
    set_p_rtl(p_title, WD_ALIGN.CENTER)
    add_run_rtl(
        p_title,
        f"بطاقة تدبر مقاصدية: سورة {s_info['surah_name']} (رقم {int(s_info['surah_number'])})",
        font_name="Amiri",
        size_pt=20,
        bold=True,
        color_rgb=(30, 58, 138),
    )

    p_sub = doc.add_paragraph()
    set_p_rtl(p_sub, WD_ALIGN.CENTER)
    add_run_rtl(
        p_sub,
        f"{s_info['group_name']} — المقصد العام للمجموعة: {s_info['group_objective']}",
        size_pt=12,
        bold=True,
        color_rgb=(13, 148, 136),
    )

    p_obj_h = doc.add_paragraph()
    set_p_rtl(p_obj_h)
    add_run_rtl(
        p_obj_h,
        "🎯 المقصد الخاص للسورة:",
        size_pt=14,
        bold=True,
        color_rgb=(180, 83, 9),
    )

    p_obj = doc.add_paragraph()
    set_p_rtl(p_obj)
    add_run_rtl(
        p_obj, str(s_info["surah_objective"]), size_pt=12, color_rgb=(15, 23, 42)
    )

    if not topics_df.empty:
        p_top_h = doc.add_paragraph()
        set_p_rtl(p_top_h)
        add_run_rtl(
            p_top_h,
            f"📑 البناء المقطعي والموضوعي للسورة ({len(topics_df)} مقطعاً):",
            size_pt=14,
            bold=True,
            color_rgb=(30, 58, 138),
        )
        tbl = doc.add_table(rows=1, cols=2)
        tbl.style = "Table Grid"
        set_tbl_rtl(tbl)
        hdr = tbl.rows[0].cells
        set_p_rtl(hdr[0].paragraphs[0], WD_ALIGN.CENTER)
        add_run_rtl(
            hdr[0].paragraphs[0],
            "رقم المقطع",
            size_pt=11,
            bold=True,
            color_rgb=(30, 58, 138),
        )
        set_p_rtl(hdr[1].paragraphs[0], WD_ALIGN.RIGHT)
        add_run_rtl(
            hdr[1].paragraphs[0],
            "موضوع المقطع وتفصيله",
            size_pt=11,
            bold=True,
            color_rgb=(30, 58, 138),
        )

        for _, trow in topics_df.iterrows():
            rc = tbl.add_row().cells
            set_p_rtl(rc[0].paragraphs[0], WD_ALIGN.CENTER)
            add_run_rtl(
                rc[0].paragraphs[0],
                f"المقطع {int(trow['topic_order'])}",
                size_pt=11,
                bold=True,
            )
            set_p_rtl(rc[1].paragraphs[0], WD_ALIGN.RIGHT)
            add_run_rtl(rc[1].paragraphs[0], str(trow["topic_detail"]), size_pt=11)

    if not ayahs_df.empty:
        p_ay_h = doc.add_paragraph()
        set_p_rtl(p_ay_h)
        add_run_rtl(
            p_ay_h,
            f"\n📜 الآيات المختارة من سورة {s_info['surah_name']}:",
            size_pt=14,
            bold=True,
            color_rgb=(13, 148, 136),
        )
        for _, arow in ayahs_df.iterrows():
            p_ay = doc.add_paragraph()
            set_p_rtl(p_ay)
            add_run_rtl(
                p_ay,
                f"﴿ {arow['ayah_text']} ﴾ ({int(arow['ayah_number'])})",
                font_name="Amiri",
                size_pt=14,
                color_rgb=(15, 23, 42),
            )

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def generate_search_tadabbur_docx(
    query_str: str,
    matched_surahs: pd.DataFrame,
    matched_topics: pd.DataFrame,
    combined_ayahs_list: list[dict],
) -> bytes:
    doc, set_p_rtl, _, add_run_rtl, WD_ALIGN = init_rtl_docx()

    p_title = doc.add_paragraph()
    set_p_rtl(p_title, WD_ALIGN.CENTER)
    add_run_rtl(
        p_title,
        f"بطاقة البحث والتدبر الموضوعي: « {query_str} »",
        font_name="Amiri",
        size_pt=20,
        bold=True,
        color_rgb=(30, 58, 138),
    )

    p_meta = doc.add_paragraph()
    set_p_rtl(p_meta, WD_ALIGN.CENTER)
    add_run_rtl(
        p_meta,
        f"السور المرتبطة: {len(matched_surahs)} | المقاطع التفصيلية: {len(matched_topics)} | إجمالي الشواهد: {len(combined_ayahs_list)}",
        size_pt=11,
        bold=True,
        color_rgb=(13, 148, 136),
    )

    if not matched_surahs.empty:
        p_h1 = doc.add_paragraph()
        set_p_rtl(p_h1)
        add_run_rtl(
            p_h1,
            "1️⃣ السور والمقاصد المرتبطة:",
            size_pt=14,
            bold=True,
            color_rgb=(180, 83, 9),
        )
        for _, sr in matched_surahs.iterrows():
            p_s = doc.add_paragraph()
            set_p_rtl(p_s)
            add_run_rtl(
                p_s,
                f"• سورة {sr['surah_name']} ({int(sr['surah_number'])}) — {sr['group_name']} ({sr['group_objective']}):\n",
                size_pt=12,
                bold=True,
                color_rgb=(30, 58, 138),
            )
            add_run_rtl(p_s, f"   مقصد السورة: {sr['surah_objective']}", size_pt=11)

    if not matched_topics.empty:
        p_h2 = doc.add_paragraph()
        set_p_rtl(p_h2)
        add_run_rtl(
            p_h2,
            "\n2️⃣ المقاطع الموضوعية ذات الصلة:",
            size_pt=14,
            bold=True,
            color_rgb=(13, 148, 136),
        )
        for _, tr in matched_topics.head(40).iterrows():
            p_t = doc.add_paragraph()
            set_p_rtl(p_t)
            add_run_rtl(
                p_t,
                f"• سورة {tr['surah_name']} (المقطع {int(tr['topic_order'])}): ",
                size_pt=11,
                bold=True,
            )
            add_run_rtl(p_t, str(tr["topic_detail"]), size_pt=11)

    if combined_ayahs_list:
        p_h3 = doc.add_paragraph()
        set_p_rtl(p_h3)
        add_run_rtl(
            p_h3,
            "\n3️⃣ الشواهد القرآنية (الحصر المعتمد والمصحف الشامل):",
            size_pt=14,
            bold=True,
            color_rgb=(30, 58, 138),
        )
        for item in combined_ayahs_list[:50]:
            p_k = doc.add_paragraph()
            set_p_rtl(p_k)
            src_label = (
                "مسجلة بالحصر" if item["source"] == "saved" else "من المصحف الشامل"
            )
            add_run_rtl(
                p_k,
                f"«{item['label']}» — سورة {item['surah_name']} ({item['surah_number']}:{item['ayah_number']}) [{src_label}]\n",
                size_pt=12,
                bold=True,
                color_rgb=(180, 83, 9),
            )
            add_run_rtl(
                p_k,
                f"﴿ {item['ayah_text']} ﴾\n",
                font_name="Amiri",
                size_pt=14,
                color_rgb=(15, 23, 42),
            )
            if item.get("notes"):
                add_run_rtl(
                    p_k,
                    f"الملاحظة: {item['notes']}",
                    size_pt=10,
                    color_rgb=(71, 85, 105),
                )

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


# ==============================================================================
# دوال جلب البيانات
# ==============================================================================
def load_groups8_hierarchy() -> pd.DataFrame:
    rows = fetch_all_supabase_rows(
        table_name="view_groups8_surah_hierarchy",
        select_cols="*",
        order_col="surah_number",
    )
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["group_number", "surah_number"]).reset_index(drop=True)
        df["group_objective"] = df["group_objective"].apply(clean_arabic_display)
        df["surah_objective"] = df["surah_objective"].apply(clean_arabic_display)
    return df


def load_groups8_topics() -> pd.DataFrame:
    rows = fetch_all_supabase_rows(
        table_name="view_groups8_surah_topics",
        select_cols="*",
        order_col="topic_id",
    )
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(
            ["group_number", "surah_number", "topic_order"]
        ).reset_index(drop=True)
        df["topic_detail"] = df["topic_detail"].apply(clean_arabic_display)
    return df


@st.cache_data(ttl=3600)
def load_surah_ayahs(surah_num: int) -> pd.DataFrame:
    res = (
        supabase.table("full_quran")
        .select(
            "id, surah_number, surah_name, ayah_number, ayah_text, juz, page_number"
        )
        .eq("surah_number", int(surah_num))
        .order("ayah_number")
        .range(0, 500)
        .execute()
    )
    return pd.DataFrame(res.data if res.data else [])


def load_group_keywords_with_ayahs() -> pd.DataFrame:
    rows = fetch_all_supabase_rows(
        table_name="v_ayah_relations_with_pages",
        select_cols="relation_id, surah_number, surah_name, ayah_number, ayah_text, group_id, topic_or_keyword, frequency_count",
        order_col="relation_id",
    )
    df = pd.DataFrame(rows)

    notes_rows = fetch_all_supabase_rows(
        table_name="ayah_group_relations",
        select_cols="id, notes",
        order_col="id",
    )
    notes_map = {
        int(r["id"]): clean_arabic_display(r.get("notes", ""))
        for r in notes_rows
        if r.get("id") is not None
    }

    if not df.empty:
        df["notes"] = df["relation_id"].apply(
            lambda rid: notes_map.get(int(rid), "") if pd.notna(rid) else ""
        )
        df = df.sort_values(["surah_number", "ayah_number"]).reset_index(drop=True)
    return df


def load_ayah_pages_lookup() -> dict:
    rows = fetch_all_supabase_rows(
        table_name="full_quran",
        select_cols="id, surah_number, ayah_number, page_number, juz",
        order_col="id",
    )
    return {
        (int(r["surah_number"]), int(r["ayah_number"])): (
            int(r["page_number"]),
            int(r["juz"]),
        )
        for r in rows
    }


# ==============================================================================
# الخريطة البصرية (التبويب 1)
# ==============================================================================
def build_groups8_visual_map_html(
    df_hier: pd.DataFrame, df_topics: pd.DataFrame
) -> str:
    group_colors = {
        1: "#1E3A8A",
        2: "#0D9488",
        3: "#B45309",
        4: "#6D28D9",
        5: "#0369A1",
        6: "#047857",
        7: "#C2410C",
        8: "#1D4ED8",
    }
    topics_by_surah = {}
    if not df_topics.empty:
        for _, trow in df_topics.iterrows():
            snum = int(trow["surah_number"])
            topics_by_surah.setdefault(snum, []).append(
                {"order": int(trow["topic_order"]), "detail": str(trow["topic_detail"])}
            )

    surahs_js_dict = {}
    for _, row in df_hier.iterrows():
        snum = int(row["surah_number"])
        gnum = int(row["group_number"])
        s_topics = topics_by_surah.get(snum) or [
            {"order": 1, "detail": str(row.get("surah_objective", ""))}
        ]
        surahs_js_dict[str(snum)] = {
            "surah_num": snum,
            "surah_name": str(row["surah_name"]),
            "group_num": gnum,
            "group_name": str(row["group_name"]),
            "group_objective": str(row["group_objective"]),
            "surah_objective": str(row["surah_objective"]),
            "total_ayahs": int(row.get("total_ayahs", 0)),
            "start_page": int(row.get("start_page", 1)),
            "topics": s_topics,
        }

    group_pills_html = "".join(
        [
            f'<button id="g-pill-{g}" class="tab-btn group-pill" onclick="filterByGroup({g})">م{g}</button>'
            for g in range(1, 9)
        ]
    )

    groups_html_parts = []
    for gnum in range(1, 9):
        g_df = df_hier[df_hier["group_number"] == gnum]
        if g_df.empty:
            continue
        g_name = str(g_df["group_name"].iloc[0])
        g_obj = str(g_df["group_objective"].iloc[0])
        color_hex = group_colors.get(gnum, "#1E3A8A")
        chips_parts = []
        for _, srow in g_df.iterrows():
            snum = int(srow["surah_number"])
            sname = str(srow["surah_name"])
            sayahs = int(srow.get("total_ayahs", 0))
            spage = int(srow.get("start_page", 1))
            sobj = str(srow.get("surah_objective", ""))
            short_obj = sobj[:68] + ("..." if len(sobj) > 68 else "")
            chips_parts.append(f"""
                <div class="surah-chip" data-group="{gnum}" data-search="{sname} {snum} {sobj}" onclick="openSurah('{snum}')">
                    <div class="chip-top">
                        <span class="surah-num-badge">سورة {snum}</span>
                        <span class="surah-meta-mini">{sayahs} آية | ص {spage}</span>
                    </div>
                    <span class="surah-name">{sname}</span>
                    <span class="surah-obj-mini">{short_obj}</span>
                </div>
                """)
        groups_html_parts.append(f"""
            <div class="group-card" id="group-card-{gnum}" style="border-right-color: {color_hex};">
                <div class="group-header-row">
                    <div><span class="group-title">{g_name}: {g_obj}</span></div>
                    <div class="group-stats-badges">
                        <span class="g-badge">{len(g_df)} سورة</span>
                        <span class="g-badge">{int(g_df["total_ayahs"].sum())} آية</span>
                    </div>
                </div>
                <div class="surahs-grid">{"".join(chips_parts)}</div>
            </div>
            """)

    surahs_json_str = json.dumps(surahs_js_dict, ensure_ascii=False)
    sorted_surah_keys = json.dumps(
        [str(int(x)) for x in df_hier["surah_number"].tolist()], ensure_ascii=False
    )

    return f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{ font-family: 'Cairo', sans-serif; background-color: #FBF9F1; color: #1E293B; direction: rtl; text-align: right; line-height: 1.7; padding: 0.4rem; }}
            .nav-bar {{ background: #FFFFFF; border: 1px solid #E2D9C8; border-radius: 12px; padding: 0.75rem 1rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05); }}
            .nav-controls {{ display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.6rem; }}
            .nav-group {{ display: flex; align-items: center; gap: 0.35rem; flex-wrap: wrap; }}
            .tab-btn {{ background: #F1F5F9; border: 1px solid #CBD5E1; color: #1E293B; padding: 0.38rem 0.75rem; border-radius: 8px; font-family: 'Cairo', sans-serif; font-size: 0.83rem; font-weight: 700; cursor: pointer; transition: all 0.2s ease; }}
            .tab-btn:hover {{ background: #E2E8F0; }}
            .tab-btn.active {{ background: #1E3A8A; color: #FFFFFF; border-color: #1E3A8A; }}
            .tab-btn.group-pill.active {{ background: #0D9488; border-color: #0D9488; }}
            .search-box {{ padding: 0.4rem 0.85rem; border: 1px solid #CBD5E1; border-radius: 8px; font-family: 'Cairo', sans-serif; font-size: 0.85rem; min-width: 240px; background: #F8FAFC; }}
            .view-section {{ display: none; animation: fadeIn 0.25s ease; }}
            .view-section.active {{ display: block; }}
            @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(5px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            .groups-stack {{ display: flex; flex-direction: column; gap: 1.15rem; }}
            .group-card {{ background: #FFFFFF; border-radius: 14px; box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05); border: 1px solid #E2D9C8; border-right: 7px solid #1E3A8A; padding: 1.1rem 1.3rem; }}
            .group-header-row {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.85rem; padding-bottom: 0.55rem; border-bottom: 1px dashed #CBD5E1; flex-wrap: wrap; gap: 0.5rem; }}
            .group-title {{ font-size: 1.12rem; font-weight: 800; color: #0F172A; }}
            .group-stats-badges {{ display: flex; gap: 0.45rem; }}
            .g-badge {{ font-size: 0.78rem; color: #1E3A8A; font-weight: 700; background: #EFF6FF; border: 1px solid #BFDBFE; padding: 0.18rem 0.65rem; border-radius: 6px; }}
            .surahs-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(215px, 1fr)); gap: 0.75rem; }}
            .surah-chip {{ background: #F8FAFC; border: 1.5px solid #CBD5E1; border-radius: 10px; padding: 0.72rem 0.88rem; cursor: pointer; transition: all 0.2s ease; display: flex; flex-direction: column; justify-content: space-between; }}
            .surah-chip:hover {{ background: #EFF6FF; border-color: #2563EB; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.14); }}
            .surah-chip.dimmed {{ opacity: 0.2; }}
            .surah-chip.matched {{ background: #FEF3C7; border-color: #D97706; box-shadow: 0 4px 12px rgba(217, 119, 6, 0.22); }}
            .chip-top {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem; }}
            .surah-num-badge {{ font-size: 0.75rem; font-weight: 800; color: #0D9488; }}
            .surah-meta-mini {{ font-size: 0.72rem; color: #64748B; font-weight: 600; }}
            .surah-name {{ font-family: 'Amiri', serif; font-weight: 700; font-size: 1.25rem; color: #0F172A; display: block; margin-bottom: 0.2rem; }}
            .surah-obj-mini {{ font-size: 0.78rem; color: #475569; line-height: 1.45; }}
            .surah-workspace {{ background: #FFFFFF; border-radius: 14px; padding: 1.5rem; border: 1px solid #E2D9C8; margin-bottom: 1.2rem; }}
            .section-header {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.8rem; border-bottom: 2px solid #E2E8F0; padding-bottom: 0.8rem; margin-bottom: 1rem; }}
            .section-header h2 {{ font-family: 'Amiri', serif; font-size: 1.85rem; color: #1E3A8A; }}
            .meta-pill-header {{ background: #FEF3C7; color: #92400E; border: 1px solid #F59E0B; padding: 0.3rem 0.85rem; border-radius: 8px; font-size: 0.84rem; font-weight: 700; }}
            .surah-objective-box {{ background: #F0FDFA; border-right: 5px solid #0D9488; padding: 0.95rem 1.2rem; border-radius: 8px; margin-bottom: 1.2rem; font-size: 1rem; font-weight: 600; color: #0F172A; }}
            .topics-flow {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 0.85rem; margin-bottom: 1.2rem; }}
            .topic-node-card {{ background: #F8FAFC; border: 2px solid #CBD5E1; border-radius: 10px; padding: 0.95rem; cursor: pointer; transition: all 0.2s ease; }}
            .topic-node-card:hover, .topic-node-card.selected {{ border-color: #0D9488; background: #EFF6FF; transform: translateY(-2px); }}
            .topic-index {{ display: inline-block; background: #1E3A8A; color: #FFF; padding: 0.1rem 0.55rem; border-radius: 6px; font-size: 0.78rem; font-weight: 800; margin-bottom: 0.4rem; }}
            .topic-text {{ font-size: 0.9rem; color: #1E293B; font-weight: 600; }}
            .inspector-box {{ background: #F1F5F9; border-right: 5px solid #1E3A8A; border-radius: 10px; padding: 1.15rem 1.35rem; }}
            .inspector-box h4 {{ color: #1E3A8A; font-size: 1.08rem; margin-bottom: 0.4rem; }}
            .equation-banner {{ background: #0F172A; color: #FFFFFF; border-radius: 12px; padding: 1.2rem 1.5rem; border-right: 6px solid #D97706; margin-bottom: 1rem; }}
            .equation-banner h3 {{ color: #FBBF24; font-size: 1.02rem; margin-bottom: 0.65rem; }}
            .equation-formula {{ display: flex; align-items: center; justify-content: center; gap: 0.6rem; flex-wrap: wrap; background: rgba(255, 255, 255, 0.08); padding: 0.85rem; border-radius: 8px; font-weight: 700; font-size: 0.9rem; }}
            .eq-box {{ background: #1E3A8A; border: 1px solid #60A5FA; padding: 0.35rem 0.85rem; border-radius: 8px; }}
            .eq-result {{ background: #0D9488; border: 1px solid #5EEAD4; padding: 0.35rem 0.95rem; border-radius: 8px; }}
            .surah-footer-nav {{ display: flex; justify-content: space-between; gap: 0.8rem; flex-wrap: wrap; }}
        </style>
    </head>
    <body>
        <div class="nav-bar">
            <div class="nav-controls">
                <div class="nav-group">
                    <button id="btn-master" class="tab-btn active" onclick="showAllGroups()">🏛️ المجموعات الثمانية (114 سورة)</button>
                    <input type="search" id="surahSearchFilter" class="search-box" placeholder="🔍 ابحث باسم سورة أو كلمة في مقصدها..." oninput="filterSurahsByText(this.value)">
                    <button type="button" class="tab-btn" onclick="resetAllFilters()">إظهار الكل</button>
                </div>
                <div class="nav-group">
                    <span style="font-size:0.8rem; font-weight:700; color:#475569;">تصفية المجموعة:</span>
                    {group_pills_html}
                </div>
            </div>
        </div>
        <section id="view-master" class="view-section active"><div class="groups-stack">{"".join(groups_html_parts)}</div></section>
        <section id="view-surah-detail" class="view-section">
            <div class="surah-workspace">
                <div class="section-header">
                    <div><span id="det-group-label" style="font-size: 0.9rem; color: #0D9488; font-weight: 700; display: block;"></span><h2 id="det-surah-title"></h2></div>
                    <span id="det-surah-meta" class="meta-pill-header"></span>
                </div>
                <div class="surah-objective-box"><span style="color:#0D9488; font-weight:800;">🎯 المقصد الخاص للسورة: </span><span id="det-surah-objective"></span></div>
                <h4 style="color:#1E3A8A; margin-bottom:0.65rem;">📑 البناء المقطعي والموضوعي للسورة (انقر على أي مقطع لفحصه):</h4>
                <div id="det-topics-grid" class="topics-flow"></div>
                <div class="inspector-box"><h4 id="insp-topic-title"></h4><p id="insp-topic-detail" style="font-size:0.96rem; color:#0F172A;"></p></div>
            </div>
            <div class="equation-banner"><h3>المعادلة المقاصدية الحاكمة للسورة داخل مجموعتها:</h3><div id="det-surah-equation" class="equation-formula"></div></div>
            <div class="surah-footer-nav">
                <button class="tab-btn" onclick="showAllGroups()">🔙 العودة إلى المجموعات الثمانية (114 سورة)</button>
                <div style="display:flex; gap:0.5rem;">
                    <button id="btn-prev-surah" class="tab-btn">➡ السورة السابقة</button>
                    <button id="btn-next-surah" class="tab-btn active">السورة التالية ⬅</button>
                </div>
            </div>
        </section>
        <script>
            const SURAHS_DATA = {surahs_json_str};
            const SURAH_KEYS = {sorted_surah_keys};
            function showAllGroups() {{
                document.getElementById('view-master').classList.add('active');
                document.getElementById('view-surah-detail').classList.remove('active');
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.getElementById('btn-master').classList.add('active');
            }}
            function resetAllFilters() {{
                const input = document.getElementById('surahSearchFilter');
                if (input) input.value = '';
                document.querySelectorAll('.group-card').forEach(gc => gc.style.display = 'block');
                document.querySelectorAll('.surah-chip').forEach(chip => {{ chip.classList.remove('dimmed'); chip.classList.remove('matched'); }});
                showAllGroups();
            }}
            function filterByGroup(gNum) {{
                showAllGroups();
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                const pill = document.getElementById('g-pill-' + gNum);
                if (pill) pill.classList.add('active');
                document.querySelectorAll('.group-card').forEach(gc => {{ gc.style.display = (gc.id === 'group-card-' + gNum) ? 'block' : 'none'; }});
            }}
            function filterSurahsByText(query) {{
                const q = query.trim().toLowerCase();
                if (document.getElementById('view-surah-detail').classList.contains('active')) {{ showAllGroups(); }}
                document.querySelectorAll('.group-card').forEach(gc => gc.style.display = 'block');
                document.querySelectorAll('.surah-chip').forEach(chip => {{
                    if (!q) {{ chip.classList.remove('dimmed'); chip.classList.remove('matched'); return; }}
                    const text = (chip.getAttribute('data-search') || '').toLowerCase();
                    if (text.includes(q)) {{ chip.classList.remove('dimmed'); chip.classList.add('matched'); }}
                    else {{ chip.classList.add('dimmed'); chip.classList.remove('matched'); }}
                }});
            }}
            function openSurah(sKey) {{
                const data = SURAHS_DATA[sKey];
                if (!data) return;
                document.getElementById('view-master').classList.remove('active');
                document.getElementById('view-surah-detail').classList.add('active');
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                const gPill = document.getElementById('g-pill-' + data.group_num);
                if (gPill) gPill.classList.add('active');
                document.getElementById('det-group-label').textContent = data.group_name + ' — المقصد العام: ' + data.group_objective;
                document.getElementById('det-surah-title').textContent = 'سورة ' + data.surah_name + ' (رقم ' + data.surah_num + ')';
                document.getElementById('det-surah-meta').textContent = 'عدد الآيات: ' + data.total_ayahs + ' | بداية الصفحة: ' + data.start_page + ' | المقاطع: ' + data.topics.length;
                document.getElementById('det-surah-objective').textContent = data.surah_objective;
                const topicsContainer = document.getElementById('det-topics-grid');
                topicsContainer.innerHTML = '';
                data.topics.forEach((t, idx) => {{
                    const card = document.createElement('div');
                    card.className = 'topic-node-card' + (idx === 0 ? ' selected' : '');
                    card.onclick = () => selectTopicNode(sKey, idx, card);
                    card.innerHTML = `<span class="topic-index">المقطع ${{t.order}}</span><p class="topic-text">${{t.detail}}</p>`;
                    topicsContainer.appendChild(card);
                }});
                if (data.topics.length > 0) {{ renderTopicInspector(data.surah_name, data.topics[0]); }}
                const eqContainer = document.getElementById('det-surah-equation');
                eqContainer.innerHTML = `<span class="eq-box">${{data.group_name}}: ${{data.group_objective}}</span><span>+</span><span class="eq-box">مقاطع سورة ${{data.surah_name}} (${{data.topics.length}} مقاطع)</span><span>⟸</span><span class="eq-result">${{data.surah_objective}}</span>`;
                const pos = SURAH_KEYS.indexOf(sKey);
                const prevKey = SURAH_KEYS[(pos - 1 + SURAH_KEYS.length) % SURAH_KEYS.length];
                const nextKey = SURAH_KEYS[(pos + 1) % SURAH_KEYS.length];
                const prevBtn = document.getElementById('btn-prev-surah');
                prevBtn.textContent = '➡ سورة ' + SURAHS_DATA[prevKey].surah_name;
                prevBtn.onclick = () => openSurah(prevKey);
                const nextBtn = document.getElementById('btn-next-surah');
                nextBtn.textContent = 'سورة ' + SURAHS_DATA[nextKey].surah_name + ' ⬅';
                nextBtn.onclick = () => openSurah(nextKey);
            }}
            function selectTopicNode(sKey, tIdx, cardElem) {{
                document.querySelectorAll('.topic-node-card').forEach(c => c.classList.remove('selected'));
                cardElem.classList.add('selected');
                const data = SURAHS_DATA[sKey];
                renderTopicInspector(data.surah_name, data.topics[tIdx]);
            }}
            function renderTopicInspector(surahName, topic) {{
                document.getElementById('insp-topic-title').textContent = 'تفصيل المقطع رقم (' + topic.order + ') في سورة ' + surahName + ':';
                document.getElementById('insp-topic-detail').textContent = topic.detail;
            }}
        </script>
    </body>
    </html>
    """


# ==============================================================================
# التنفيذ الرئيسي للصفحة
# ==============================================================================
try:
    df_hierarchy = load_groups8_hierarchy()
    df_topics = load_groups8_topics()
    df_keywords = load_group_keywords_with_ayahs()
    ayah_pages_map = load_ayah_pages_lookup()
except Exception as e:
    st.error(f"❌ تعذّر تحميل بيانات المجموعات الثمانية من Supabase: {e}")
    st.stop()

if df_hierarchy.empty:
    st.warning("⚠️ لم يتم العثور على بيانات في العرض view_groups8_surah_hierarchy.")
    st.stop()

st.markdown(
    """
    <div class="g8-hero">
        <h2>🧪 مختبر تطوير البحث الشامل — معمارية المجموعات الثمانية</h2>
        <p>الدمج بين الاستكشاف الموجّه للمفاهيم المعتمدة + المسح التلقائي المزدوج للمصحف الشامل + الحفظ التراكمي بضغطة واحدة</p>
    </div>
    """,
    unsafe_allow_html=True,
)

c_m1, c_m2, c_m3, c_m4 = st.columns(4)
c_m1.metric("المجموعات الأساسية", f"{df_hierarchy['group_number'].nunique()} مجموعات")
c_m2.metric("السور القرآنية", f"{len(df_hierarchy)} سورة")
c_m3.metric("المقاطع الموضوعية للسور", f"{len(df_topics)} مقطعاً")
c_m4.metric("إجمالي آيات المصحف", f"{int(df_hierarchy['total_ayahs'].sum()):,} آية")

st.markdown("---")

tab_map, tab_surah_ws, tab_keywords, tab_search = st.tabs(
    [
        "🗺️ الخريطة البصرية الهرمية (8 مجموعات / 114 سورة)",
        "📖 مساحة تدبر السورة وآياتها (مع التلاوة والمصحف)",
        "🔑 الكلمات والمفاهيم المحورية داخل كل مجموعة",
        "🔍 البحث الشامل والاكتشاف الذكي (النسخة المطورة)",
    ]
)

# ==============================================================================
# التبويب 1: الخريطة البصرية
# ==============================================================================
with tab_map:
    st.info(
        "💡 انقر على أي بطاقة سورة داخل المجموعات الثمانية لفتح مساحة عملها ومقاطعها ومعادلتها المقاصدية."
    )
    components.html(
        build_groups8_visual_map_html(df_hierarchy, df_topics),
        height=1200,
        scrolling=True,
    )


# ==============================================================================
# التبويب 2: مساحة تدبر السورة
# ==============================================================================
with tab_surah_ws:
    col_g, col_s = st.columns([1.2, 1.8])
    groups_dict = {
        int(r["group_number"]): f"{r['group_name']} — {r['group_objective']}"
        for _, r in df_hierarchy[["group_number", "group_name", "group_objective"]]
        .drop_duplicates()
        .iterrows()
    }

    with col_g:
        sel_group = st.selectbox(
            "1️⃣ اختر المجموعة الثمانية:",
            options=list(groups_dict.keys()),
            format_func=lambda x: groups_dict[x],
            key="ws_group_select",
        )

    group_surahs_df = df_hierarchy[df_hierarchy["group_number"] == sel_group]
    surah_opts = {
        int(
            r["surah_number"]
        ): f"{int(r['surah_number'])}. سورة {r['surah_name']} ({int(r['total_ayahs'])} آية)"
        for _, r in group_surahs_df.iterrows()
    }

    with col_s:
        sel_surah = st.selectbox(
            "2️⃣ اختر السورة داخل المجموعة:",
            options=list(surah_opts.keys()),
            format_func=lambda x: surah_opts[x],
            key="ws_surah_select",
        )

    s_info = group_surahs_df[group_surahs_df["surah_number"] == sel_surah].iloc[0]
    s_name = str(s_info["surah_name"])
    s_start_page = int(s_info.get("start_page", 1))

    col_obj, col_jump = st.columns([3.0, 1.3])
    with col_obj:
        st.markdown(
            f"""
            <div class="surah-obj-banner">
                <div style="color:#0D9488; font-weight:800; font-size:0.92rem;">
                    {s_info['group_name']} | المقصد العام: {s_info['group_objective']}
                </div>
                <h3 style="color:#1E3A8A; margin:0.35rem 0;">🎯 مقصد سورة {s_name}:</h3>
                <p style="font-size:1.05rem; font-weight:700; color:#0F172A; margin:0;">
                    {s_info['surah_objective']}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_jump:
        if st.button(
            f"📖 فتح سورة {s_name} بالمصحف (ص {s_start_page})",
            key=f"jump_mushaf_s_{sel_surah}",
            use_container_width=True,
        ):
            st.session_state["selected_page"] = s_start_page
            st.session_state["current_page"] = s_start_page
            if os.path.exists("pages/1_📖_المصحف_المصور.py"):
                st.switch_page("pages/1_📖_المصحف_المصور.py")

    s_topics_df = df_topics[df_topics["surah_number"] == sel_surah].sort_values(
        "topic_order"
    )
    df_ayahs = load_surah_ayahs(sel_surah)

    sub_ayahs = pd.DataFrame()
    if not df_ayahs.empty:
        max_a = int(df_ayahs["ayah_number"].max())
        if max_a > 25:
            c_r1, c_r2 = st.columns(2)
            with c_r1:
                from_ayah = st.number_input(
                    "من الآية رقم:",
                    min_value=1,
                    max_value=max_a,
                    value=1,
                    key=f"from_a_{sel_surah}",
                )
            with c_r2:
                to_ayah = st.number_input(
                    "إلى الآية رقم:",
                    min_value=1,
                    max_value=max_a,
                    value=min(20, max_a),
                    key=f"to_a_{sel_surah}",
                )
        else:
            from_ayah, to_ayah = 1, max_a
        sub_ayahs = df_ayahs[
            (df_ayahs["ayah_number"] >= from_ayah)
            & (df_ayahs["ayah_number"] <= to_ayah)
        ]

    if HAS_DOCX:
        with col_jump:
            st.download_button(
                label=f"📄 بطاقة تدبر {s_name} (Word)",
                data=generate_surah_tadabbur_docx(s_info, s_topics_df, sub_ayahs),
                file_name=f"Tadabbur_Card_Surah_{sel_surah}_{s_name}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                key=f"dl_docx_s_{sel_surah}",
            )

    with st.expander(
        f"📑 المقاطع الموضوعية التفصيلية لسورة {s_name} ({len(s_topics_df)} مقطعاً)",
        expanded=True,
    ):
        if s_topics_df.empty:
            st.info("لا توجد مقاطع فرعية مسجلة لهذه السورة.")
        else:
            for _, trow in s_topics_df.iterrows():
                st.markdown(
                    f"- **المقطع {int(trow['topic_order'])}:** {trow['topic_detail']}"
                )

    st.markdown(f"### 📜 آيات سورة {s_name} بالرسم العثماني والتلاوة الصوتية")
    if not sub_ayahs.empty:
        for _, arow in sub_ayahs.iterrows():
            anum = int(arow["ayah_number"])
            pnum = int(arow["page_number"])
            jnum = int(arow["juz"])
            atext = str(arow["ayah_text"])
            st.markdown(
                f"""
                <div class="ayah-card">
                    <div class="ayah-uthmani">﴿ {atext} ﴾ <span style="color:#D97706; font-size:1.15rem;">({anum})</span></div>
                    <div>
                        <span class="ayah-meta-badge">سورة {s_name} ({sel_surah}:{anum})</span>
                        <span class="ayah-meta-badge">📄 صفحة المصحف: {pnum}</span>
                        <span class="ayah-meta-badge">الجزء: {jnum}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            c_a1, c_a2 = st.columns([3.1, 1.2])
            with c_a1:
                st.audio(get_everyayah_audio_url(sel_surah, anum), format="audio/mp3")
            with c_a2:
                if st.button(
                    "📌 أضف لأرشيف التدبر",
                    key=f"arch_ws_{sel_surah}_{anum}",
                    use_container_width=True,
                ):
                    ok, msg = save_ayah_to_memorization_archive(
                        surah_serial=sel_surah,
                        surah_name=s_name,
                        ayah_number=anum,
                        ayah_text=atext,
                        status_label=f"تدبر مقاصدي ({s_info['group_name']})",
                    )
                    st.success(msg) if ok else st.info(msg)


# ==============================================================================
# التبويب 3: الكلمات والمفاهيم المحورية داخل كل مجموعة
# ==============================================================================
with tab_keywords:
    st.subheader("🔑 الكلمات والمفاهيم القرآنية المرتبطة بكل مجموعة وسورها")
    if df_keywords.empty:
        st.info("لا توجد بيانات كلمات مفتاحية مسجلة حالياً.")
    else:
        sel_kw_group = st.selectbox(
            "اختر المجموعة لاستعراض كلماتها ومفاهيمها:",
            options=list(groups_dict.keys()),
            format_func=lambda x: groups_dict[x],
            key="kw_group_select",
        )
        g_kw_df = df_keywords[df_keywords["group_id"] == sel_kw_group].copy()
        if g_kw_df.empty:
            st.warning("لا توجد كلمات مسجلة لهذه المجموعة.")
        else:
            kw_agg = (
                g_kw_df.groupby("topic_or_keyword", as_index=False)
                .agg(
                    مرات_التكرار=("frequency_count", "sum"),
                    عدد_الآيات=("surah_number", "count"),
                    السور_المرتبطة=(
                        "surah_name",
                        lambda x: "، ".join(dict.fromkeys(x.dropna())),
                    ),
                )
                .sort_values("مرات_التكرار", ascending=False)
                .reset_index(drop=True)
            )
            all_kw_list = kw_agg["topic_or_keyword"].tolist()
            state_key_kw = f"active_kw_g_{sel_kw_group}"
            if (
                state_key_kw not in st.session_state
                or st.session_state[state_key_kw] not in all_kw_list
            ):
                st.session_state[state_key_kw] = all_kw_list[0]

            top_kws = kw_agg.head(24)
            cols_per_row = 6
            for i in range(0, len(top_kws), cols_per_row):
                row_slice = top_kws.iloc[i : i + cols_per_row]
                btn_cols = st.columns(cols_per_row)
                for col_idx, (_, krow) in enumerate(row_slice.iterrows()):
                    kw_word = str(krow["topic_or_keyword"])
                    kw_freq = int(krow["مرات_التكرار"])
                    is_selected = st.session_state[state_key_kw] == kw_word
                    with btn_cols[col_idx]:
                        if st.button(
                            f"{'✅ ' if is_selected else ''}{kw_word} ({kw_freq})",
                            key=f"kw_btn_{sel_kw_group}_{i}_{col_idx}",
                            type="primary" if is_selected else "secondary",
                            use_container_width=True,
                        ):
                            st.session_state[state_key_kw] = kw_word
                            st.rerun()

            chosen_kw = st.selectbox(
                "أو اختر أي كلمة من القائمة الكاملة للمجموعة:",
                options=all_kw_list,
                index=all_kw_list.index(st.session_state[state_key_kw]),
                key=f"kw_dropdown_{sel_kw_group}",
            )
            if chosen_kw != st.session_state[state_key_kw]:
                st.session_state[state_key_kw] = chosen_kw
                st.rerun()

            active_word = st.session_state[state_key_kw]
            matched_kw_ayahs = g_kw_df[
                g_kw_df["topic_or_keyword"] == active_word
            ].copy()

            for idx_a, arow in matched_kw_ayahs.iterrows():
                s_num = int(arow["surah_number"])
                a_num = int(arow["ayah_number"])
                s_name = str(arow.get("surah_name", ""))
                raw_atext = str(arow.get("ayah_text", ""))
                highlighted_atext = highlight_uthmani_keyword(raw_atext, active_word)
                freq_val = int(arow.get("frequency_count", 1))
                p_num, j_num = ayah_pages_map.get((s_num, a_num), (1, 1))

                with st.container(border=True):
                    st.markdown(
                        f"<div class='ayah-uthmani' style='margin-bottom:0.2rem;'>"
                        f"<span class='ayah-meta-badge'>سورة {s_name} ({s_num}:{a_num})</span>"
                        f"<span class='ayah-meta-badge'>📄 صفحة المصحف: {p_num}</span>"
                        f"<span class='ayah-meta-badge'>الجزء: {j_num}</span>"
                        f"<span class='ayah-meta-badge'>التكرار بالآية: {freq_val}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"### ﴿ {highlighted_atext} ﴾ `({a_num})`")

                c_aud_kw, c_mushaf_kw, c_arch_kw = st.columns([2.4, 1.0, 1.0])
                with c_aud_kw:
                    st.audio(get_everyayah_audio_url(s_num, a_num), format="audio/mp3")
                with c_mushaf_kw:
                    if st.button(
                        f"📖 المصحف ({p_num})",
                        key=f"kw_mushaf_{sel_kw_group}_{idx_a}_{s_num}_{a_num}",
                        use_container_width=True,
                    ):
                        st.session_state["selected_page"] = p_num
                        st.session_state["current_page"] = p_num
                        if os.path.exists("pages/1_📖_المصحف_المصور.py"):
                            st.switch_page("pages/1_📖_المصحف_المصور.py")
                with c_arch_kw:
                    if st.button(
                        "📌 أرشفة التدبر",
                        key=f"kw_arch_{sel_kw_group}_{idx_a}_{s_num}_{a_num}",
                        use_container_width=True,
                    ):
                        ok, msg = save_ayah_to_memorization_archive(
                            surah_serial=s_num,
                            surah_name=s_name,
                            ayah_number=a_num,
                            ayah_text=raw_atext,
                            status_label=f"تدبر كلمة «{active_word}» (المجموعة {sel_kw_group})",
                        )
                        st.success(msg) if ok else st.info(msg)


# ==============================================================================
# التبويب 4 المطور: الاستكشاف الموجّه + البحث المزدوج المنضبط + الحفظ الشامل
# ==============================================================================
with tab_search:
    c_s_head, c_s_ref = st.columns([3.2, 1.1])
    with c_s_head:
        st.subheader("🔍 البحث الشامل والاكتشاف الذكي في المصحف والمجموعات الثمانية")
    with c_s_ref:
        if st.button(
            "🔄 تحديث البيانات الآن",
            key="btn_refresh_g8_cache",
            use_container_width=True,
        ):
            st.cache_data.clear()
            st.rerun()

    if "g8_global_search" not in st.session_state:
        st.session_state["g8_global_search"] = ""

    # بناء فهرس جميع المفاهيم المعتمدة في قاعدة البيانات (مرتبة حسب التكرار)
    catalog_keywords = []
    if not df_keywords.empty:
        kw_summary = (
            df_keywords.groupby("topic_or_keyword", as_index=False)
            .agg(ayah_cnt=("surah_number", "count"))
            .sort_values("ayah_cnt", ascending=False)
        )
        catalog_keywords = kw_summary["topic_or_keyword"].tolist()

    # --------------------------------------------------------------------------
    # الطبقة الأولى: شريط الاستكشاف الموجّه (يغني الباحث عن تذكر الكلمات)
    # --------------------------------------------------------------------------
    st.markdown(
        """
        <div class="discovery-panel">
            <strong style="color:#1E3A8A; font-size:0.98rem;">🧭 بوصلة الاستكشاف السريع (تصفح المفاهيم المعتمدة بالحرف أو القائمة أو الاقتراح العشوائي):</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

    arabic_letters = [
        "الكل",
        "ا",
        "ب",
        "ت",
        "ث",
        "ج",
        "ح",
        "خ",
        "د",
        "ذ",
        "ر",
        "ز",
        "س",
        "ش",
        "ص",
        "ض",
        "ط",
        "ظ",
        "ع",
        "غ",
        "ف",
        "ق",
        "ك",
        "ل",
        "م",
        "ن",
        "ه",
        "و",
        "ي",
    ]

    c_let, c_cat, c_rand = st.columns([1.1, 2.3, 1.1])
    with c_let:
        sel_letter = st.selectbox(
            "1️⃣ تصفية بأول حرف:",
            options=arabic_letters,
            index=0,
            key="g8_alpha_filter",
        )

    filtered_catalog = catalog_keywords
    if sel_letter != "الكل":
        filtered_catalog = [
            kw for kw in catalog_keywords if normalize_arabic(kw).startswith(sel_letter)
        ]

    with c_cat:
        dropdown_options = ["— اختر مفهوماً معتمداً من الفهرس —"] + filtered_catalog
        sel_from_catalog = st.selectbox(
            f"2️⃣ الفهرس المعتمد ({len(filtered_catalog)} مفهوماً):",
            options=dropdown_options,
            index=0,
            key="g8_catalog_picker",
        )
        if sel_from_catalog != "— اختر مفهوماً معتمداً من الفهرس —":
            if st.session_state.get("_last_picked_kw") != sel_from_catalog:
                st.session_state["_last_picked_kw"] = sel_from_catalog
                st.session_state["g8_global_search"] = sel_from_catalog
                st.rerun()

    with c_rand:
        st.markdown("<div style='height: 1.75rem;'></div>", unsafe_allow_html=True)
        if st.button(
            "🎲 اقترح مفهوماً للتدبر",
            key="btn_random_concept",
            use_container_width=True,
        ):
            if catalog_keywords:
                rand_kw = random.choice(catalog_keywords)
                st.session_state["_last_picked_kw"] = rand_kw
                st.session_state["g8_global_search"] = rand_kw
                st.rerun()

    # مربع البحث النصي الحر (يبحث في عنوان المفهوم بالحصر + نصوص آيات المصحف الشامل فقط)
    c_inp, c_clr = st.columns([3.8, 0.7])
    with c_inp:
        q_text = st.text_input(
            "3️⃣ أو اكتب أي كلمة أو مقطع آية للبحث الفوري في الحصر المعتمد والمصحف الشامل (6,236 آية):",
            placeholder="مثال: أظلم، الحي القيوم، الصبر، أو أي كلمة قرآنية جديدة غير محفوظة...",
            key="g8_global_search",
        )
    with c_clr:
        st.markdown("<div style='height: 1.75rem;'></div>", unsafe_allow_html=True)
        if st.button("🧹 مسح", key="btn_clear_g8_search", use_container_width=True):
            st.session_state["g8_global_search"] = ""
            st.session_state["_last_picked_kw"] = ""
            st.rerun()

    # --------------------------------------------------------------------------
    # الطبقة الثانية: البحث المزدوج المنضبط (topic_or_keyword + full_quran فقط)
    # --------------------------------------------------------------------------
if q_text.strip():
    clean_q = q_text.strip()
    norm_q = normalize_arabic(clean_q)
    q_tokens = norm_q.split()

    # المسار 1: الحصر المعتمد (مطابقة نصية تامة لعنوان المفهوم topic_or_keyword فقط)
    matched_kw_records = pd.DataFrame()
    if not df_keywords.empty:
        matched_kw_records = df_keywords[
            df_keywords["topic_or_keyword"].apply(
                lambda kw: normalize_arabic(str(kw or "")) == norm_q
            )
        ]

    saved_pairs = set()
    if not matched_kw_records.empty:
        for _, kr in matched_kw_records.iterrows():
            saved_pairs.add((int(kr["surah_number"]), int(kr["ayah_number"])))

    # المسار 2: المسح الشامل للمصحف (full_quran) بتطابق الكلمة/العبارة نصاً
    raw_quran_hits = search_full_quran_stable(clean_q)
    full_quran_hits = []
    for q in raw_quran_hits:
        norm_ay = normalize_arabic(
            str(q.get("plain_ayah_text") or q.get("ayah_text") or "")
        )
        if len(q_tokens) == 1:
            # تطابق الكلمة المفردة نصاً ضمن كلمات الآية (وليس كجزء من كلمة أخرى مثل سبحان/يسبحون)
            if norm_q in norm_ay.split():
                full_quran_hits.append(q)
        else:
            # تطابق العبارة المكونة من أكثر من كلمة
            if norm_q in norm_ay:
                full_quran_hits.append(q)

    new_quran_ayahs = [
        q
        for q in full_quran_hits
        if (int(q["surah_number"]), int(q["ayah_number"])) not in saved_pairs
    ]

    # بناء خريطة السورة -> (رقم المجموعة، اسم المجموعة، مقصد المجموعة، مقصد السورة)
    surah_to_group_info = {
        int(r["surah_number"]): (
            int(r["group_number"]),
            r["group_name"],
            r["group_objective"],
            r["surah_objective"],
        )
        for _, r in df_hierarchy.iterrows()
    }
    surah_to_group_save_map = {
        s_num: (info[0], info[2]) for s_num, info in surah_to_group_info.items()
    }

    # ----------------------------------------------------------------------
    # بوابة الاعتماد والحفظ الشامل التراكمي للآيات الجديدة
    # ----------------------------------------------------------------------
    if len(new_quran_ayahs) > 0:
        is_completely_new = len(saved_pairs) == 0
        alert_title = (
            f"🆕 الكلمة/العبارة «{clean_q}» جديدة كلياً وغير مسجلة في ملف الحصر المعتمد (وُجدت في {len(new_quran_ayahs)} آية بالمصحف)."
            if is_completely_new
            else f"💡 المفهوم «{clean_q}» مسجل له ({len(saved_pairs)}) آية بالحصر، ووُجد له ({len(new_quran_ayahs)}) آية إضافية في المصحف الشامل."
        )

        with st.container(border=True):
            st.warning(
                f"**{alert_title}** هل ترغب في اعتمادها وحفظ جميع آياتها الجديدة بملف الحصر؟"
            )
            c_note_in, c_save_btn = st.columns([2.5, 1.5])
            with c_note_in:
                user_custom_note = st.text_input(
                    "ملاحظة تدبرية اختيارية تُحفظ مع السجلات (اتركها فارغة لاعتماد مقصد المجموعة تلقائياً):",
                    placeholder="اكتب ملاحظتك التدبرية هنا إن شئت...",
                    key=f"bulk_note_{clean_q}",
                )
            with c_save_btn:
                st.markdown(
                    "<div style='height: 1.75rem;'></div>", unsafe_allow_html=True
                )
                if st.button(
                    f"💾 اعتماد وحفظ الكل ({len(new_quran_ayahs)} آية)",
                    type="primary",
                    key=f"btn_bulk_save_{clean_q}",
                    use_container_width=True,
                ):
                    ok_save, msg_save = save_keyword_bulk_to_relations(
                        keyword=clean_q,
                        ayah_records=new_quran_ayahs,
                        surah_to_group_map=surah_to_group_save_map,
                        custom_note=user_custom_note,
                    )
                    if ok_save:
                        st.success(msg_save)
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.info(msg_save)

    # استخراج السور المرتبطة من الآيات الناتجة عن المسارين (1 و 2) حصراً
    kw_linked_surahs = {p[0] for p in saved_pairs}
    quran_linked_surahs = {int(q["surah_number"]) for q in full_quran_hits}
    all_linked_surahs = kw_linked_surahs | quran_linked_surahs

    matched_surahs = df_hierarchy[
        df_hierarchy["surah_number"].astype(int).isin(all_linked_surahs)
    ]

    matched_topics = df_topics[
        df_topics["surah_number"].astype(int).isin(all_linked_surahs)
    ]

    # تجهيز القائمة الموحدة للآيات (المحفوظة أولاً + الجديدة من المصحف ثانياً)
    combined_display_ayahs = []
    for _, kr in matched_kw_records.iterrows():
        s_n = int(kr["surah_number"])
        a_n = int(kr["ayah_number"])
        p_n, j_n = ayah_pages_map.get((s_n, a_n), (1, 1))
        combined_display_ayahs.append(
            {
                "source": "saved",
                "label": str(kr.get("topic_or_keyword", clean_q)),
                "surah_number": s_n,
                "surah_name": str(kr.get("surah_name", "")),
                "ayah_number": a_n,
                "ayah_text": str(kr.get("ayah_text", "")),
                "notes": str(kr.get("notes", "")).strip(),
                "page_number": p_n,
                "juz": j_n,
            }
        )

    for q in new_quran_ayahs:
        s_n = int(q["surah_number"])
        a_n = int(q["ayah_number"])
        p_n, j_n = ayah_pages_map.get(
            (s_n, a_n),
            (int(q.get("page_number", 1)), int(q.get("juz", 1))),
        )
        combined_display_ayahs.append(
            {
                "source": "quran",
                "label": clean_q,
                "surah_number": s_n,
                "surah_name": str(q.get("surah_name", "")),
                "ayah_number": a_n,
                "ayah_text": str(q.get("ayah_text", "")),
                "notes": "",
                "page_number": p_n,
                "juz": j_n,
            }
        )

    # صياغة رسالة النتائج الإحصائية الدقيقة
    saved_cnt = len(saved_pairs)
    quran_total_cnt = len(full_quran_hits)
    if saved_cnt > 0 and saved_cnt == quran_total_cnt:
        summary_msg = (
            f"📊 نتيجة البحث عن «{clean_q}»: في ملف الحصر المعتمد ظهرت ({saved_cnt}) مرة، "
            f"وهي مطابقة تماماً لعدد الآيات بالمصحف الشامل وعددها ({quran_total_cnt}) آية "
            f"(موزعة على {len(matched_surahs)} سورة و{len(matched_topics)} مقطعاً موضوعياً)."
        )
    else:
        summary_msg = (
            f"📊 نتيجة البحث عن «{clean_q}»: في ملف الحصر المعتمد ظهرت ({saved_cnt}) مرة، "
            f"بينما وردت في المصحف الشامل بعدد ({quran_total_cnt}) آية "
            f"(موزعة على {len(matched_surahs)} سورة و{len(matched_topics)} مقطعاً موضوعياً)."
        )
    st.info(summary_msg)

    # استخراج السور المرتبطة من الآيات الناتجة عن المسارين (1 و 2) حصراً
    kw_linked_surahs = {p[0] for p in saved_pairs}
    quran_linked_surahs = {int(q["surah_number"]) for q in full_quran_hits}
    all_linked_surahs = kw_linked_surahs | quran_linked_surahs

    # تصفية العمود الأول (المقاصد) والعمود الثاني (المقاطع) بناءً على سور الآيات فقط
    matched_surahs = df_hierarchy[
        df_hierarchy["surah_number"].astype(int).isin(all_linked_surahs)
    ]

    matched_topics = df_topics[
        df_topics["surah_number"].astype(int).isin(all_linked_surahs)
    ]

    # تجهيز القائمة الموحدة للآيات (المحفوظة أولاً + الجديدة من المصحف ثانياً)
    combined_display_ayahs = []
    for _, kr in matched_kw_records.iterrows():
        s_n = int(kr["surah_number"])
        a_n = int(kr["ayah_number"])
        p_n, j_n = ayah_pages_map.get((s_n, a_n), (1, 1))
        combined_display_ayahs.append(
            {
                "source": "saved",
                "label": str(kr.get("topic_or_keyword", clean_q)),
                "surah_number": s_n,
                "surah_name": str(kr.get("surah_name", "")),
                "ayah_number": a_n,
                "ayah_text": str(kr.get("ayah_text", "")),
                "notes": str(kr.get("notes", "")).strip(),
                "page_number": p_n,
                "juz": j_n,
            }
        )

    for q in new_quran_ayahs:
        s_n = int(q["surah_number"])
        a_n = int(q["ayah_number"])
        p_n, j_n = ayah_pages_map.get(
            (s_n, a_n),
            (int(q.get("page_number", 1)), int(q.get("juz", 1))),
        )
        combined_display_ayahs.append(
            {
                "source": "quran",
                "label": clean_q,
                "surah_number": s_n,
                "surah_name": str(q.get("surah_name", "")),
                "ayah_number": a_n,
                "ayah_text": str(q.get("ayah_text", "")),
                "notes": "",
                "page_number": p_n,
                "juz": j_n,
            }
        )

    if HAS_DOCX and (
        not matched_surahs.empty or not matched_topics.empty or combined_display_ayahs
    ):
        st.download_button(
            label=f"📄 تحميل بطاقة تدبر نتائج البحث عن «{clean_q}» بصيغة Word (.docx)",
            data=generate_search_tadabbur_docx(
                clean_q, matched_surahs, matched_topics, combined_display_ayahs
            ),
            file_name=f"Tadabbur_Search_{clean_q}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key="dl_search_tadabbur_docx",
        )

    # عرض النتائج في الأعمدة الثلاثة المعتمدة
    c_res1, c_res2, c_res3 = st.columns(3)

    with c_res1:
        st.markdown(f"#### 🎯 مقاصد السور المرتبطة ({len(matched_surahs)} سورة)")
        if matched_surahs.empty:
            st.info("لا توجد سور مطابقة.")
        else:
            for _, sr in matched_surahs.iterrows():
                s_id = int(sr["surah_number"])
                with st.expander(
                    f"سورة {sr['surah_name']} ({s_id}) — {sr['group_name']}",
                    expanded=True,
                ):
                    st.markdown(f"**مقصد المجموعة:** {sr['group_objective']}")
                    st.markdown(f"**مقصد السورة:** {sr['surah_objective']}")

    with c_res2:
        st.markdown(f"#### 📑 مقاطع السور المرتبطة ({len(matched_topics)} مقطعاً)")
        if matched_topics.empty:
            st.info("لا توجد مقاطع تفصيلية مطابقة.")
        else:
            for _, tr in matched_topics.head(40).iterrows():
                with st.expander(
                    f"سورة {tr['surah_name']} — المقطع {int(tr['topic_order'])} ({tr['group_name']})",
                    expanded=False,
                ):
                    st.write(tr["topic_detail"])

    with c_res3:
        st.markdown(f"#### 🔑 الشواهد القرآنية ({len(combined_display_ayahs)} شاهداً)")
        if not combined_display_ayahs:
            st.info("لم يتم العثور على آيات مطابقة في الحصر أو المصحف.")
        else:
            for idx_s, item in enumerate(combined_display_ayahs[:45]):
                s_num = item["surah_number"]
                a_num = item["ayah_number"]
                s_name = item["surah_name"]
                raw_ay = item["ayah_text"]
                hl_ay = highlight_uthmani_keyword(raw_ay, clean_q)
                note_txt = item["notes"]
                g_info = surah_to_group_info.get(s_num, (0, "المجموعة", "", ""))
                src_tag = "✅ بالحصر" if item["source"] == "saved" else "🆕 بالمصحف"

                with st.expander(
                    f"«{item['label']}» — {s_name} ({s_num}:{a_num}) [{src_tag}]",
                    expanded=True,
                ):
                    if item["source"] == "saved":
                        st.markdown(
                            '<span class="badge-saved">✅ مسجلة بالحصر المعتمد</span>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            '<span class="badge-new-quran">🆕 من المصحف الشامل (غير محفوظة بالحصر)</span>',
                            unsafe_allow_html=True,
                        )

                    st.markdown(f"**🏛️ المجموعة:** {g_info[1]} — *{g_info[2]}*")
                    if g_info[3]:
                        st.info(f"🎯 **مقصد سورة {s_name}:** {g_info[3]}")

                    st.markdown(f"﴿ {hl_ay} ﴾")
                    st.caption(
                        f"📄 صفحة المصحف: {item['page_number']} | الجزء: {item['juz']}"
                    )
                    if note_txt:
                        st.caption(f"📝 **الملاحظة المسجلة:** {note_txt}")

                    st.audio(get_everyayah_audio_url(s_num, a_num), format="audio/mp3")
                    if st.button(
                        "📌 أضف لأرشيف التدبر (صفحة 8)",
                        key=f"srch_arch_{idx_s}_{s_num}_{a_num}",
                        use_container_width=True,
                    ):
                        ok, msg = save_ayah_to_memorization_archive(
                            surah_serial=s_num,
                            surah_name=s_name,
                            ayah_number=a_num,
                            ayah_text=raw_ay,
                            status_label=f"تدبر بحث «{clean_q}» ({g_info[1]})",
                        )
                        st.success(msg) if ok else st.info(msg)
