import os
import re
import json
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from theme import apply_custom_theme, add_home_button
from database import (
    supabase,
    normalize_arabic,
    convert_df_to_excel,
    clean_dataframe_for_display,
)

# ==============================================================================
# إعدادات الصفحة الأساسية
# ==============================================================================
st.set_page_config(
    page_title="المعمارية البصرية للمجموعات الثمانية (114 سورة)",
    page_icon="🏛️",
    layout="wide",
)

# تطبيق الهوية البصرية الموحدة للتطبيق (RTL + خطوط Amiri و Cairo)
apply_custom_theme()

# زر العودة السريع للصفحة الرئيسية
add_home_button()

# ==============================================================================
# تنسيقات CSS مخصصة للصفحة 12 (متناغمة مع خلفية #FBF9F1 في theme.py)
# ==============================================================================
st.markdown(
    """
    <style>
        .g8-hero {
            background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 60%, #0D9488 100%);
            color: #FFFFFF !important;
            padding: 1.6rem 2rem;
            border-radius: 16px;
            border-bottom: 4px solid #D97706;
            margin-bottom: 1.2rem;
            box-shadow: 0 6px 20px rgba(15, 23, 42, 0.12);
        }
        .g8-hero h2 {
            font-family: 'Amiri', serif !important;
            color: #FFFFFF !important;
            text-align: center !important;
            font-size: 2rem !important;
            margin-bottom: 0.4rem !important;
        }
        .g8-hero p {
            color: #E2E8F0 !important;
            text-align: center !important;
            font-size: 1rem !important;
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
            font-size: 1.55rem !important;
            line-height: 2.2 !important;
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
        .kw-active-banner {
            background-color: #EFF6FF;
            border: 1px solid #93C5FD;
            border-right: 5px solid #1E3A8A;
            border-radius: 10px;
            padding: 0.85rem 1.2rem;
            margin: 0.8rem 0 1rem 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# دوال مساعدة لتنقية النصوص والصوتيات
# ==============================================================================
def clean_arabic_display(text: str) -> str:
    """تصحيح أخطاء التشكيل الطباعية الشائعة مثل (للهّ / الل هّ) أثناء العرض"""
    if not text:
        return ""
    s = str(text)
    s = re.sub(r"الل\s+هّ?", "الله", s)
    s = s.replace("للهّ", "لله").replace("اللهّ", "الله")
    return s.strip()


def get_everyayah_audio_url(surah_num: int, ayah_num: int) -> str:
    """بناء رابط التلاوة الصوتية للشيخ ماهر المعيقلي عبر EveryAyah"""
    return f"https://everyayah.com/data/MaherAlMuaiqly128kbps/{int(surah_num):03d}{int(ayah_num):03d}.mp3"


# ==============================================================================
# دوال جلب البيانات من Supabase مع التخزين المؤقت (@st.cache_data)
# ==============================================================================
@st.cache_data(ttl=3600)
def load_groups8_hierarchy() -> pd.DataFrame:
    """جلب هرمية المجموعات الثمانية والسور الـ 114 ومقاصدها"""
    res = (
        supabase.table("view_groups8_surah_hierarchy")
        .select("*")
        .order("group_number")
        .order("surah_number")
        .range(0, 500)
        .execute()
    )
    data = res.data if res.data else []
    df = pd.DataFrame(data)
    if not df.empty:
        df["group_objective"] = df["group_objective"].apply(clean_arabic_display)
        df["surah_objective"] = df["surah_objective"].apply(clean_arabic_display)
    return df


@st.cache_data(ttl=3600)
def load_groups8_topics() -> pd.DataFrame:
    """جلب المقاطع التفصيلية لجميع السور من view_groups8_surah_topics"""
    res = (
        supabase.table("view_groups8_surah_topics")
        .select("*")
        .order("group_number")
        .order("surah_number")
        .order("topic_order")
        .range(0, 4999)
        .execute()
    )
    data = res.data if res.data else []
    df = pd.DataFrame(data)
    if not df.empty:
        df["topic_detail"] = df["topic_detail"].apply(clean_arabic_display)
    return df


@st.cache_data(ttl=3600)
def load_surah_ayahs(surah_num: int) -> pd.DataFrame:
    """جلب آيات سورة محددة بالرسم العثماني من جدول full_quran"""
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
    data = res.data if res.data else []
    return pd.DataFrame(data)


@st.cache_data(ttl=3600)
def load_group_keywords_with_ayahs() -> pd.DataFrame:
    """جلب الكلمات والمفاهيم المرتبطة بكل مجموعة وآياتها من v_ayah_relations_with_pages"""
    res = (
        supabase.table("v_ayah_relations_with_pages")
        .select(
            "surah_number, surah_name, ayah_number, ayah_text, group_id, topic_or_keyword, frequency_count"
        )
        .order("surah_number")
        .order("ayah_number")
        .range(0, 4999)
        .execute()
    )
    data = res.data if res.data else []
    return pd.DataFrame(data)


@st.cache_data(ttl=3600)
def load_ayah_pages_lookup() -> dict:
    """جلب خريطة أرقام الصفحات والأجزاء لكل (سورة، آية) لربطها بالآيات المسترجعة"""
    res = (
        supabase.table("full_quran")
        .select("surah_number, ayah_number, page_number, juz")
        .range(0, 6500)
        .execute()
    )
    lookup = {}
    if res.data:
        for r in res.data:
            lookup[(int(r["surah_number"]), int(r["ayah_number"]))] = (
                int(r["page_number"]),
                int(r["juz"]),
            )
    return lookup


# ==============================================================================
# بناء واجهة الخريطة البصرية التفاعلية (HTML/CSS/JS) للمجموعات الثمانية (114 سورة)
# ==============================================================================
def build_groups8_visual_map_html(
    df_hier: pd.DataFrame, df_topics: pd.DataFrame
) -> str:
    """توليد الخريطة البصرية التفاعلية للطبقات الثمانية والسور الـ 114 ومقاطعها"""
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
                {
                    "order": int(trow["topic_order"]),
                    "detail": str(trow["topic_detail"]),
                }
            )

    surahs_js_dict = {}
    for _, row in df_hier.iterrows():
        snum = int(row["surah_number"])
        gnum = int(row["group_number"])
        s_topics = topics_by_surah.get(snum, [])
        if not s_topics:
            s_topics = [{"order": 1, "detail": str(row.get("surah_objective", ""))}]

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
        surah_count = len(g_df)
        total_g_ayahs = int(g_df["total_ayahs"].sum())

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
                    <div>
                        <span class="group-title">{g_name}: {g_obj}</span>
                    </div>
                    <div class="group-stats-badges">
                        <span class="g-badge">{surah_count} سورة</span>
                        <span class="g-badge">{total_g_ayahs} آية</span>
                    </div>
                </div>
                <div class="surahs-grid">
                    {"".join(chips_parts)}
                </div>
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
            body {{
                font-family: 'Cairo', sans-serif;
                background-color: #FBF9F1;
                color: #1E293B;
                direction: rtl;
                text-align: right;
                line-height: 1.7;
                padding: 0.4rem;
            }}
            .nav-bar {{
                background: #FFFFFF;
                border: 1px solid #E2D9C8;
                border-radius: 12px;
                padding: 0.75rem 1rem;
                margin-bottom: 1rem;
                box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
            }}
            .nav-controls {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 0.6rem;
            }}
            .nav-group {{
                display: flex;
                align-items: center;
                gap: 0.35rem;
                flex-wrap: wrap;
            }}
            .tab-btn {{
                background: #F1F5F9;
                border: 1px solid #CBD5E1;
                color: #1E293B;
                padding: 0.38rem 0.75rem;
                border-radius: 8px;
                font-family: 'Cairo', sans-serif;
                font-size: 0.83rem;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            .tab-btn:hover {{ background: #E2E8F0; }}
            .tab-btn.active {{
                background: #1E3A8A;
                color: #FFFFFF;
                border-color: #1E3A8A;
            }}
            .tab-btn.group-pill.active {{
                background: #0D9488;
                border-color: #0D9488;
            }}
            .search-box {{
                padding: 0.4rem 0.85rem;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                font-family: 'Cairo', sans-serif;
                font-size: 0.85rem;
                min-width: 240px;
                background: #F8FAFC;
            }}
            .view-section {{ display: none; animation: fadeIn 0.25s ease; }}
            .view-section.active {{ display: block; }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(5px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .groups-stack {{ display: flex; flex-direction: column; gap: 1.15rem; }}
            .group-card {{
                background: #FFFFFF;
                border-radius: 14px;
                box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
                border: 1px solid #E2D9C8;
                border-right: 7px solid #1E3A8A;
                padding: 1.1rem 1.3rem;
            }}
            .group-header-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 0.85rem;
                padding-bottom: 0.55rem;
                border-bottom: 1px dashed #CBD5E1;
                flex-wrap: wrap;
                gap: 0.5rem;
            }}
            .group-title {{
                font-size: 1.12rem;
                font-weight: 800;
                color: #0F172A;
            }}
            .group-stats-badges {{
                display: flex;
                gap: 0.45rem;
            }}
            .g-badge {{
                font-size: 0.78rem;
                color: #1E3A8A;
                font-weight: 700;
                background: #EFF6FF;
                border: 1px solid #BFDBFE;
                padding: 0.18rem 0.65rem;
                border-radius: 6px;
            }}
            .surahs-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(215px, 1fr));
                gap: 0.75rem;
            }}
            .surah-chip {{
                background: #F8FAFC;
                border: 1.5px solid #CBD5E1;
                border-radius: 10px;
                padding: 0.72rem 0.88rem;
                cursor: pointer;
                transition: all 0.2s ease;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }}
            .surah-chip:hover {{
                background: #EFF6FF;
                border-color: #2563EB;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(37, 99, 235, 0.14);
            }}
            .surah-chip.dimmed {{ opacity: 0.2; }}
            .surah-chip.matched {{
                background: #FEF3C7;
                border-color: #D97706;
                box-shadow: 0 4px 12px rgba(217, 119, 6, 0.22);
            }}
            .chip-top {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 0.25rem;
            }}
            .surah-num-badge {{
                font-size: 0.75rem;
                font-weight: 800;
                color: #0D9488;
            }}
            .surah-meta-mini {{
                font-size: 0.72rem;
                color: #64748B;
                font-weight: 600;
            }}
            .surah-name {{
                font-family: 'Amiri', serif;
                font-weight: 700;
                font-size: 1.25rem;
                color: #0F172A;
                display: block;
                margin-bottom: 0.2rem;
            }}
            .surah-obj-mini {{
                font-size: 0.78rem;
                color: #475569;
                line-height: 1.45;
            }}
            .surah-workspace {{
                background: #FFFFFF;
                border-radius: 14px;
                padding: 1.5rem;
                border: 1px solid #E2D9C8;
                margin-bottom: 1.2rem;
            }}
            .section-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 0.8rem;
                border-bottom: 2px solid #E2E8F0;
                padding-bottom: 0.8rem;
                margin-bottom: 1rem;
            }}
            .section-header h2 {{
                font-family: 'Amiri', serif;
                font-size: 1.85rem;
                color: #1E3A8A;
            }}
            .meta-pill-header {{
                background: #FEF3C7;
                color: #92400E;
                border: 1px solid #F59E0B;
                padding: 0.3rem 0.85rem;
                border-radius: 8px;
                font-size: 0.84rem;
                font-weight: 700;
            }}
            .surah-objective-box {{
                background: #F0FDFA;
                border-right: 5px solid #0D9488;
                padding: 0.95rem 1.2rem;
                border-radius: 8px;
                margin-bottom: 1.2rem;
                font-size: 1rem;
                font-weight: 600;
                color: #0F172A;
            }}
            .topics-flow {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
                gap: 0.85rem;
                margin-bottom: 1.2rem;
            }}
            .topic-node-card {{
                background: #F8FAFC;
                border: 2px solid #CBD5E1;
                border-radius: 10px;
                padding: 0.95rem;
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            .topic-node-card:hover, .topic-node-card.selected {{
                border-color: #0D9488;
                background: #EFF6FF;
                transform: translateY(-2px);
            }}
            .topic-index {{
                display: inline-block;
                background: #1E3A8A;
                color: #FFF;
                padding: 0.1rem 0.55rem;
                border-radius: 6px;
                font-size: 0.78rem;
                font-weight: 800;
                margin-bottom: 0.4rem;
            }}
            .topic-text {{
                font-size: 0.9rem;
                color: #1E293B;
                font-weight: 600;
            }}
            .inspector-box {{
                background: #F1F5F9;
                border-right: 5px solid #1E3A8A;
                border-radius: 10px;
                padding: 1.15rem 1.35rem;
            }}
            .inspector-box h4 {{
                color: #1E3A8A;
                font-size: 1.08rem;
                margin-bottom: 0.4rem;
            }}
            .equation-banner {{
                background: #0F172A;
                color: #FFFFFF;
                border-radius: 12px;
                padding: 1.2rem 1.5rem;
                border-right: 6px solid #D97706;
                margin-bottom: 1rem;
            }}
            .equation-banner h3 {{
                color: #FBBF24;
                font-size: 1.02rem;
                margin-bottom: 0.65rem;
            }}
            .equation-formula {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.6rem;
                flex-wrap: wrap;
                background: rgba(255, 255, 255, 0.08);
                padding: 0.85rem;
                border-radius: 8px;
                font-weight: 700;
                font-size: 0.9rem;
            }}
            .eq-box {{
                background: #1E3A8A;
                border: 1px solid #60A5FA;
                padding: 0.35rem 0.85rem;
                border-radius: 8px;
            }}
            .eq-result {{
                background: #0D9488;
                border: 1px solid #5EEAD4;
                padding: 0.35rem 0.95rem;
                border-radius: 8px;
            }}
            .surah-footer-nav {{
                display: flex;
                justify-content: space-between;
                gap: 0.8rem;
                flex-wrap: wrap;
            }}
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

        <section id="view-master" class="view-section active">
            <div class="groups-stack">
                {"".join(groups_html_parts)}
            </div>
        </section>

        <section id="view-surah-detail" class="view-section">
            <div class="surah-workspace">
                <div class="section-header">
                    <div>
                        <span id="det-group-label" style="font-size: 0.9rem; color: #0D9488; font-weight: 700; display: block;"></span>
                        <h2 id="det-surah-title"></h2>
                    </div>
                    <span id="det-surah-meta" class="meta-pill-header"></span>
                </div>

                <div class="surah-objective-box">
                    <span style="color:#0D9488; font-weight:800;">🎯 المقصد الخاص للسورة: </span>
                    <span id="det-surah-objective"></span>
                </div>

                <h4 style="color:#1E3A8A; margin-bottom:0.65rem;">📑 البناء المقطعي والموضوعي للسورة (انقر على أي مقطع لفحصه):</h4>
                <div id="det-topics-grid" class="topics-flow"></div>

                <div class="inspector-box">
                    <h4 id="insp-topic-title"></h4>
                    <p id="insp-topic-detail" style="font-size:0.96rem; color:#0F172A;"></p>
                </div>
            </div>

            <div class="equation-banner">
                <h3>المعادلة المقاصدية الحاكمة للسورة داخل مجموعتها:</h3>
                <div id="det-surah-equation" class="equation-formula"></div>
            </div>

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
                document.querySelectorAll('.surah-chip').forEach(chip => {{
                    chip.classList.remove('dimmed');
                    chip.classList.remove('matched');
                }});
                showAllGroups();
            }}

            function filterByGroup(gNum) {{
                showAllGroups();
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                const pill = document.getElementById('g-pill-' + gNum);
                if (pill) pill.classList.add('active');

                document.querySelectorAll('.group-card').forEach(gc => {{
                    gc.style.display = (gc.id === 'group-card-' + gNum) ? 'block' : 'none';
                }});
            }}

            function filterSurahsByText(query) {{
                const q = query.trim().toLowerCase();
                if (document.getElementById('view-surah-detail').classList.contains('active')) {{
                    showAllGroups();
                }}
                document.querySelectorAll('.group-card').forEach(gc => gc.style.display = 'block');
                document.querySelectorAll('.surah-chip').forEach(chip => {{
                    if (!q) {{
                        chip.classList.remove('dimmed');
                        chip.classList.remove('matched');
                        return;
                    }}
                    const text = (chip.getAttribute('data-search') || '').toLowerCase();
                    if (text.includes(q)) {{
                        chip.classList.remove('dimmed');
                        chip.classList.add('matched');
                    }} else {{
                        chip.classList.add('dimmed');
                        chip.classList.remove('matched');
                    }}
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
                    card.innerHTML = `
                        <span class="topic-index">المقطع ${{t.order}}</span>
                        <p class="topic-text">${{t.detail}}</p>
                    `;
                    topicsContainer.appendChild(card);
                }});

                if (data.topics.length > 0) {{
                    renderTopicInspector(data.surah_name, data.topics[0]);
                }}

                const eqContainer = document.getElementById('det-surah-equation');
                eqContainer.innerHTML = `
                    <span class="eq-box">${{data.group_name}}: ${{data.group_objective}}</span>
                    <span>+</span>
                    <span class="eq-box">مقاطع سورة ${{data.surah_name}} (${{data.topics.length}} مقاطع)</span>
                    <span>⟸</span>
                    <span class="eq-result">${{data.surah_objective}}</span>
                `;

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

# ترويسة الصفحة الرئيسية
st.markdown(
    """
    <div class="g8-hero">
        <h2>🏛️ المعمارية البصرية الهرمية للمجموعات الثمانية في القرآن الكريم</h2>
        <p>البناء الشمولي المتدرج: من المقصد العام للمجموعات الثمانية ⬅ إلى مقاصد السور الـ 114 ⬅ إلى المقاطع التفصيلية والآيات</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# شريط المؤشرات الإحصائية الحية
total_groups = df_hierarchy["group_number"].nunique()
total_surahs = len(df_hierarchy)
total_topics = len(df_topics)
total_quran_ayahs = int(df_hierarchy["total_ayahs"].sum())

c_m1, c_m2, c_m3, c_m4 = st.columns(4)
c_m1.metric("المجموعات الأساسية", f"{total_groups} مجموعات")
c_m2.metric("السور القرآنية", f"{total_surahs} سورة")
c_m3.metric("المقاطع الموضوعية للسور", f"{total_topics} مقطعاً")
c_m4.metric("إجمالي آيات المصحف", f"{total_quran_ayahs:,} آية")

st.markdown("---")

# التبويبات الأربعة الرئيسية
tab_map, tab_surah_ws, tab_keywords, tab_search = st.tabs(
    [
        "🗺️ الخريطة البصرية الهرمية (8 مجموعات / 114 سورة)",
        "📖 مساحة تدبر السورة وآياتها (مع التلاوة والمصحف)",
        "🔑 الكلمات والمفاهيم المحورية داخل كل مجموعة",
        "🔍 البحث الشامل في مقاصد المجموعات والسور",
    ]
)

# ==============================================================================
# التبويب 1: الخريطة البصرية التفاعلية للمجموعات الثمانية والسور الـ 114
# ==============================================================================
with tab_map:
    st.info(
        "💡 انقر على أي بطاقة سورة داخل المجموعات الثمانية لفتح مساحة عملها ومقاطعها ومعادلتها المقاصدية، أو استخدم شريط التصفية والبحث في الأعلى."
    )
    visual_html = build_groups8_visual_map_html(df_hierarchy, df_topics)
    components.html(visual_html, height=1200, scrolling=True)


# ==============================================================================
# التبويب 2: مساحة تدبر السورة ومقاطعها وآياتها بالرسم العثماني والتلاوة
# ==============================================================================
with tab_surah_ws:
    col_g, col_s = st.columns([1.2, 1.8])

    groups_dict = {}
    for _, r in (
        df_hierarchy[["group_number", "group_name", "group_objective"]]
        .drop_duplicates()
        .iterrows()
    ):
        gnum = int(r["group_number"])
        groups_dict[gnum] = f"{r['group_name']} — {r['group_objective']}"

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

    col_obj, col_jump = st.columns([3.2, 1.1])
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
        st.markdown("<br>", unsafe_allow_html=True)
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

            export_topics_df = clean_dataframe_for_display(s_topics_df).rename(
                columns={
                    "group_number": "رقم المجموعة",
                    "group_name": "اسم المجموعة",
                    "surah_number": "رقم السورة",
                    "surah_name": "اسم السورة",
                    "total_ayahs": "عدد الآيات",
                    "start_page": "صفحة البداية",
                    "topic_order": "ترتيب المقطع",
                    "topic_detail": "تفصيل المقطع",
                }
            )
            st.download_button(
                label=f"📥 تصدير البناء المقطعي لسورة {s_name} إلى Excel",
                data=convert_df_to_excel(export_topics_df, sheet_name=f"سورة_{s_name}"),
                file_name=f"Surah_{sel_surah}_{s_name}_Architecture.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    st.markdown(f"### 📜 آيات سورة {s_name} بالرسم العثماني والتلاوة الصوتية")
    df_ayahs = load_surah_ayahs(sel_surah)
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
            st.audio(get_everyayah_audio_url(sel_surah, anum), format="audio/mp3")


# ==============================================================================
# التبويب 3: الكلمات والمفاهيم المحورية داخل كل مجموعة (قابلة للنقر لعرض آياتها)
# ==============================================================================
with tab_keywords:
    st.subheader("🔑 الكلمات والمفاهيم القرآنية المرتبطة بكل مجموعة وسورها")
    st.write(
        "انقر على أي كلمة من البطاقات التفاعلية أدناه (أو اخترها من القائمة) لاستعراض جميع الآيات القرآنية التابعة لها مع التلاوة الصوتية."
    )

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

            st.success(
                f"إجمالي المفاهيم والكلمات المرتبطة بالمجموعة {sel_kw_group}: **{len(kw_agg)}** مفهوماً (انقر على أي زر لعرض آياته)."
            )

            # شبكة أزرار تفاعلية لأبرز 24 كلمة في المجموعة
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

            # قائمة اختيار شاملة لجميع كلمات المجموعة (بما يتجاوز الـ 24 زر)
            chosen_kw = st.selectbox(
                "أو اختر أي كلمة من القائمة الكاملة للمجموعة:",
                options=all_kw_list,
                index=all_kw_list.index(st.session_state[state_key_kw]),
                key=f"kw_dropdown_{sel_kw_group}",
            )
            if chosen_kw != st.session_state[state_key_kw]:
                st.session_state[state_key_kw] = chosen_kw
                st.rerun()

            # عرض الآيات التابعة للكلمة المختارة
            active_word = st.session_state[state_key_kw]
            matched_kw_ayahs = g_kw_df[
                g_kw_df["topic_or_keyword"] == active_word
            ].copy()

            st.markdown(
                f"""
                <div class="kw-active-banner">
                    <span style="font-size:1.05rem; font-weight:800; color:#1E3A8A;">
                        📌 الآيات القرآنية التابعة لمفهوم / كلمة: « {active_word} » في المجموعة {sel_kw_group}
                    </span>
                    <span style="margin-right:0.8rem; color:#0D9488; font-weight:700;">
                        (عدد الآيات: {len(matched_kw_ayahs)})
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            for idx_a, arow in matched_kw_ayahs.iterrows():
                s_num = int(arow["surah_number"])
                a_num = int(arow["ayah_number"])
                s_name = str(arow.get("surah_name", ""))
                a_text = str(arow.get("ayah_text", ""))
                freq_val = int(arow.get("frequency_count", 1))
                p_num, j_num = ayah_pages_map.get((s_num, a_num), (1, 1))

                st.markdown(
                    f"""
                    <div class="ayah-card">
                        <div class="ayah-uthmani">﴿ {a_text} ﴾ <span style="color:#D97706; font-size:1.1rem;">({a_num})</span></div>
                        <div>
                            <span class="ayah-meta-badge">سورة {s_name} ({s_num}:{a_num})</span>
                            <span class="ayah-meta-badge">📄 صفحة المصحف: {p_num}</span>
                            <span class="ayah-meta-badge">الجزء: {j_num}</span>
                            <span class="ayah-meta-badge">التكرار بالآية: {freq_val}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                c_aud_kw, c_btn_kw = st.columns([3.2, 1.1])
                with c_aud_kw:
                    st.audio(get_everyayah_audio_url(s_num, a_num), format="audio/mp3")
                with c_btn_kw:
                    if st.button(
                        f"📖 فتح صفحة المصحف ({p_num})",
                        key=f"kw_mushaf_{sel_kw_group}_{idx_a}_{s_num}_{a_num}",
                        use_container_width=True,
                    ):
                        st.session_state["selected_page"] = p_num
                        st.session_state["current_page"] = p_num
                        if os.path.exists("pages/1_📖_المصحف_المصور.py"):
                            st.switch_page("pages/1_📖_المصحف_المصور.py")

            st.markdown("---")
            st.markdown("#### 📊 الجدول الإحصائي الشامل لكلمات المجموعة")
            st.dataframe(kw_agg, use_container_width=True, hide_index=True)

            st.download_button(
                label=f"📥 تصدير كلمات المجموعة {sel_kw_group} إلى Excel",
                data=convert_df_to_excel(
                    kw_agg, sheet_name=f"كلمات_المجموعة_{sel_kw_group}"
                ),
                file_name=f"Group_{sel_kw_group}_Keywords.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )


# ==============================================================================
# التبويب 4: البحث الشامل في مقاصد المجموعات والسور ومقاطعها التفصيلية
# ==============================================================================
with tab_search:
    st.subheader("🔍 البحث النصي الشامل في مقاصد المجموعات الثمانية والسور ومقاطعها")
    q_text = st.text_input(
        "أدخل كلمة أو مفهوماً للبحث في مقاصد المجموعات الـ 8، ومقاصد السور الـ 114، والمقاطع التفصيلية:",
        placeholder="مثال: الهدى، الصراط المستقيم، التوحيد، بني إسرائيل، الابتلاء، النعم...",
        key="g8_global_search",
    )

    if q_text.strip():
        norm_q = normalize_arabic(q_text)

        matched_surahs = df_hierarchy[
            df_hierarchy.apply(
                lambda r: norm_q
                in normalize_arabic(
                    f"{r['group_name']} {r['group_objective']} {r['surah_name']} {r['surah_objective']}"
                ),
                axis=1,
            )
        ]

        matched_topics = df_topics[
            df_topics["topic_detail"].apply(
                lambda txt: norm_q in normalize_arabic(str(txt))
            )
        ]

        c_res1, c_res2 = st.columns(2)
        with c_res1:
            st.markdown(
                f"#### 🎯 السور المطابقة في المقاصد ({len(matched_surahs)} سورة)"
            )
            if matched_surahs.empty:
                st.info("لا توجد سور مطابقة في المقاصد العامة أو الخاصة.")
            else:
                for _, sr in matched_surahs.iterrows():
                    with st.expander(
                        f"سورة {sr['surah_name']} ({int(sr['surah_number'])}) — {sr['group_name']}",
                        expanded=True,
                    ):
                        st.markdown(
                            f"**المقصد العام للمجموعة:** {sr['group_objective']}"
                        )
                        st.markdown(f"**مقصد السورة:** {sr['surah_objective']}")
                        st.caption(
                            f"عدد الآيات: {int(sr['total_ayahs'])} | صفحة البداية: {int(sr['start_page'])}"
                        )

        with c_res2:
            st.markdown(
                f"#### 📑 المقاطع التفصيلية المطابقة ({len(matched_topics)} مقطعاً)"
            )
            if matched_topics.empty:
                st.info("لا توجد مقاطع تفصيلية مطابقة.")
            else:
                for _, tr in matched_topics.head(40).iterrows():
                    with st.expander(
                        f"سورة {tr['surah_name']} — المقطع {int(tr['topic_order'])} ({tr['group_name']})",
                        expanded=False,
                    ):
                        st.write(tr["topic_detail"])
