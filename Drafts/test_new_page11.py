import os
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
    page_title="المعمارية البصرية والمفاهيمية للقرآن الكريم (24 محوراً)",
    page_icon="🧭",
    layout="wide",
)

# تطبيق الهوية البصرية الموحدة للتطبيق (RTL + خطوط Amiri و Cairo + إخفاء Sidebar)
apply_custom_theme()

# زر العودة السريع للصفحة الرئيسية
add_home_button()

# ==============================================================================
# تنسيقات CSS تكميلية مخصصة لهذه الصفحة (متناغمة مع خلفية #FBF9F1 في theme.py)
# ==============================================================================
st.markdown(
    """
    <style>
        .arch-hero {
            background: linear-gradient(135deg, #1E293B 0%, #1E3A8A 65%, #0D9488 100%);
            color: #FFFFFF !important;
            padding: 1.6rem 2rem;
            border-radius: 16px;
            border-bottom: 4px solid #D97706;
            margin-bottom: 1.2rem;
            box-shadow: 0 6px 20px rgba(15, 23, 42, 0.12);
        }
        .arch-hero h2 {
            font-family: 'Amiri', serif !important;
            color: #FFFFFF !important;
            text-align: center !important;
            font-size: 2rem !important;
            margin-bottom: 0.4rem !important;
        }
        .arch-hero p {
            color: #E2E8F0 !important;
            text-align: center !important;
            font-size: 1rem !important;
            margin: 0 !important;
        }
        .ayah-card {
            background-color: #FFFFFF;
            border: 1px solid #E2D9C8;
            border-right: 5px solid #0D9488;
            border-radius: 12px;
            padding: 1.1rem 1.4rem;
            margin-bottom: 0.85rem;
            box-shadow: 0 2px 8px rgba(44, 34, 30, 0.05);
        }
        .ayah-uthmani {
            font-family: 'Amiri', serif !important;
            font-size: 1.55rem !important;
            line-height: 2.2 !important;
            color: #1E293B !important;
            text-align: right !important;
            direction: rtl !important;
            margin-bottom: 0.5rem;
        }
        .ayah-meta-badge {
            display: inline-block;
            background-color: #F3EFE4;
            color: #2C221E;
            border: 1px solid #D6CBB8;
            padding: 0.2rem 0.75rem;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 700;
            margin-left: 0.5rem;
        }
        .concept-pill {
            display: inline-block;
            background-color: #FEF3C7;
            color: #92400E;
            border: 1px solid #F59E0B;
            padding: 0.2rem 0.7rem;
            border-radius: 6px;
            font-size: 0.82rem;
            font-weight: 700;
            margin: 0.15rem 0.25rem;
        }
        .equation-box-st {
            background-color: #0F172A;
            color: #FFFFFF;
            border-right: 6px solid #D97706;
            border-radius: 12px;
            padding: 1.1rem 1.4rem;
            margin: 0.8rem 0 1.2rem 0;
        }
        .eq-step-chip {
            display: inline-block;
            background-color: #1E3A8A;
            border: 1px solid #60A5FA;
            color: #FFFFFF;
            padding: 0.35rem 0.85rem;
            border-radius: 8px;
            font-weight: 700;
            font-size: 0.92rem;
            margin: 0.2rem;
        }
        .eq-final-chip {
            display: inline-block;
            background-color: #0D9488;
            border: 1px solid #5EEAD4;
            color: #FFFFFF;
            padding: 0.35rem 0.95rem;
            border-radius: 8px;
            font-weight: 700;
            font-size: 0.95rem;
            margin: 0.2rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# دوال جلب البيانات من Supabase مع التخزين المؤقت (@st.cache_data)
# ==============================================================================
@st.cache_data(ttl=3600)
def load_architecture_core():
    """جلب الطبقات الـ 5 والمحاور الـ 24 والعقد الـ 96 من الجداول المطبعة"""
    layers_res = (
        supabase.table("arch_layers_normalized")
        .select("*")
        .order("layer_order")
        .execute()
    )
    axes_res = (
        supabase.table("arch_axes_normalized")
        .select("*")
        .order("axis_order")
        .execute()
    )
    nodes_res = (
        supabase.table("arch_nodes_normalized")
        .select("*")
        .order("axis_id")
        .order("node_order")
        .execute()
    )

    layers = layers_res.data if layers_res.data else []
    axes = axes_res.data if axes_res.data else []
    nodes = nodes_res.data if nodes_res.data else []
    return layers, axes, nodes


@st.cache_data(ttl=3600)
def load_full_evidence_view() -> pd.DataFrame:
    """جلب الشواهد القرآنية الكاملة المربوطة بـ full_quran من العرض التحليلي"""
    res = (
        supabase.table("view_arch_full_evidence")
        .select("*")
        .order("axis_id")
        .order("node_order")
        .order("surah_number")
        .order("ayah_number")
        .range(0, 4999)
        .execute()
    )
    data = res.data if res.data else []
    return pd.DataFrame(data)


@st.cache_data(ttl=3600)
def load_cross_axis_intersections() -> pd.DataFrame:
    """جلب الآيات المحورية التي تتقاطع فيها عدة محاور أو مفاهيم"""
    res = (
        supabase.table("view_arch_cross_axis_intersections")
        .select("*")
        .range(0, 4999)
        .execute()
    )
    data = res.data if res.data else []
    return pd.DataFrame(data)


def get_everyayah_audio_url(surah_num: int, ayah_num: int) -> str:
    """بناء رابط التلاوة الصوتية للشيخ ماهر المعيقلي عبر EveryAyah"""
    return f"https://everyayah.com/data/MaherAlMuaiqly128kbps/{int(surah_num):03d}{int(ayah_num):03d}.mp3"


# ==============================================================================
# بناء واجهة الخريطة البصرية التفاعلية (HTML/CSS/JS) من بيانات Supabase الحية
# ==============================================================================
def build_interactive_visual_map_html(layers: list, axes: list, nodes: list) -> str:
    """توليد الخريطة البصرية التفاعلية الكاملة ديناميكياً من جداول Supabase"""
    layer_map = {l["layer_id"]: l for l in layers}
    nodes_by_axis = {}
    for n in nodes:
        nodes_by_axis.setdefault(n["axis_id"], []).append(n)

    axes_js_dict = {}
    for a in axes:
        aid = str(a["axis_id"])
        lid = a["layer_id"]
        layer_title = layer_map.get(lid, {}).get("title_ar", "")
        eq_steps = a.get("equation_steps", [])
        if isinstance(eq_steps, str):
            try:
                eq_steps = json.loads(eq_steps)
            except Exception:
                eq_steps = []

        axis_nodes_list = []
        for n in nodes_by_axis.get(a["axis_id"], []):
            axis_nodes_list.append(
                {
                    "term": n.get("term_vowelled", ""),
                    "role": n.get("role_ar", ""),
                    "root": n.get("linguistic_root", ""),
                    "verses": n.get("verses_display", ""),
                    "desc": n.get("analytical_desc", ""),
                }
            )

        axes_js_dict[aid] = {
            "num": f"المحور {aid}",
            "layer": layer_title,
            "title": a.get("title_ar", ""),
            "archetype": a.get("archetype", ""),
            "summary": a.get("summary_ar", ""),
            "nodes": axis_nodes_list,
            "equation": eq_steps,
        }

    # بناء أزرار المحاور 1 - 24
    pills_html = "".join(
        [
            f"<button id=\"pill-{a['axis_id']}\" class=\"tab-btn axis-pill\" onclick=\"openAxis('{a['axis_id']}')\">{a['axis_id']}</button>"
            for a in axes
        ]
    )

    # بناء بطاقات الطبقات الخمس والمحاور التابعة لها
    layers_html_parts = []
    axes_by_layer = {}
    for a in axes:
        axes_by_layer.setdefault(a["layer_id"], []).append(a)

    for l in layers:
        lid = l["layer_id"]
        color_hex = l.get("color_hex", "#1E3A8A")
        chips_parts = []
        for a in axes_by_layer.get(lid, []):
            aid = a["axis_id"]
            terms_preview = " • ".join(
                [n.get("term_plain", "") for n in nodes_by_axis.get(aid, [])]
            )
            chips_parts.append(
                f"""
                <div class="module-chip" onclick="openAxis('{aid}')">
                    <span class="ready-badge">مُفعّل ↗</span>
                    <span class="module-num">المحور {aid}</span>
                    <span class="module-name">{a.get("title_ar", "")}</span>
                    <span class="module-terms">{terms_preview}</span>
                </div>
                """
            )
        layers_html_parts.append(
            f"""
            <div class="layer-card" style="border-right-color: {color_hex};">
                <div class="layer-title-row">
                    <span class="layer-title">{l.get("title_ar", "")}</span>
                    <span class="layer-en">{l.get("title_en", "")}</span>
                </div>
                <div class="modules-grid">
                    {"".join(chips_parts)}
                </div>
            </div>
            """
        )

    axes_json_str = json.dumps(axes_js_dict, ensure_ascii=False)
    active_keys_json = json.dumps([str(a["axis_id"]) for a in axes], ensure_ascii=False)

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
                gap: 0.32rem;
                flex-wrap: wrap;
            }}
            .tab-btn {{
                background: #F1F5F9;
                border: 1px solid #CBD5E1;
                color: #1E293B;
                padding: 0.38rem 0.68rem;
                border-radius: 8px;
                font-family: 'Cairo', sans-serif;
                font-size: 0.82rem;
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
            .tab-btn.axis-pill.active {{
                background: #0D9488;
                border-color: #0D9488;
            }}
            .search-box {{
                padding: 0.4rem 0.85rem;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                font-family: 'Cairo', sans-serif;
                font-size: 0.85rem;
                min-width: 220px;
                background: #F8FAFC;
            }}
            .view-section {{ display: none; animation: fadeIn 0.25s ease; }}
            .view-section.active {{ display: block; }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(5px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .layers-stack {{ display: flex; flex-direction: column; gap: 1.1rem; }}
            .layer-card {{
                background: #FFFFFF;
                border-radius: 14px;
                box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
                border: 1px solid #E2D9C8;
                border-right: 6px solid #1E3A8A;
                padding: 1.1rem 1.3rem;
            }}
            .layer-title-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 0.8rem;
                flex-wrap: wrap;
                gap: 0.5rem;
            }}
            .layer-title {{ font-size: 1.1rem; font-weight: 800; color: #0F172A; }}
            .layer-en {{
                font-size: 0.78rem;
                color: #64748B;
                font-weight: 600;
                background: #F1F5F9;
                padding: 0.2rem 0.6rem;
                border-radius: 6px;
            }}
            .modules-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
                gap: 0.8rem;
            }}
            .module-chip {{
                background: #EFF6FF;
                border: 1.5px solid #2563EB;
                border-radius: 10px;
                padding: 0.8rem 0.95rem;
                position: relative;
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            .module-chip:hover {{
                background: #DBEAFE;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(37, 99, 235, 0.16);
            }}
            .module-chip.dimmed {{ opacity: 0.22; }}
            .module-chip.matched {{
                background: #FEF3C7;
                border-color: #D97706;
                box-shadow: 0 4px 12px rgba(217, 119, 6, 0.22);
            }}
            .module-num {{
                font-size: 0.78rem;
                font-weight: 800;
                color: #0D9488;
                display: block;
                margin-bottom: 0.15rem;
            }}
            .module-name {{
                font-weight: 700;
                font-size: 0.94rem;
                color: #0F172A;
                display: block;
            }}
            .module-terms {{
                font-size: 0.8rem;
                color: #475569;
                margin-top: 0.25rem;
                display: block;
            }}
            .ready-badge {{
                position: absolute;
                top: 0.6rem;
                left: 0.6rem;
                background: #0D9488;
                color: #FFF;
                font-size: 0.66rem;
                font-weight: 700;
                padding: 0.1rem 0.45rem;
                border-radius: 4px;
            }}
            .axis-workspace {{
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
                font-size: 1.65rem;
                color: #1E3A8A;
            }}
            .archetype-tag {{
                background: #FEF3C7;
                color: #92400E;
                border: 1px solid #F59E0B;
                padding: 0.28rem 0.8rem;
                border-radius: 8px;
                font-size: 0.82rem;
                font-weight: 700;
            }}
            .axis-summary {{
                background: #F8FAFC;
                border-right: 4px solid #0D9488;
                padding: 0.85rem 1.1rem;
                border-radius: 8px;
                margin-bottom: 1.2rem;
                font-size: 0.95rem;
            }}
            .nodes-flow {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 0.9rem;
                margin-bottom: 1.2rem;
            }}
            .node-card {{
                background: #F8FAFC;
                border: 2px solid #CBD5E1;
                border-radius: 10px;
                padding: 1rem;
                cursor: pointer;
                transition: all 0.2s ease;
                position: relative;
            }}
            .node-card:hover, .node-card.selected {{
                border-color: #0D9488;
                background: #F0FDFA;
                transform: translateY(-2px);
            }}
            .node-index {{
                display: inline-block;
                background: #1E3A8A;
                color: #FFF;
                width: 24px;
                height: 24px;
                line-height: 24px;
                text-align: center;
                border-radius: 50%;
                font-size: 0.8rem;
                font-weight: 800;
                margin-bottom: 0.4rem;
            }}
            .node-term {{
                font-family: 'Amiri', serif;
                font-size: 1.35rem;
                color: #1E3A8A;
                font-weight: 700;
                display: block;
            }}
            .node-role {{
                font-size: 0.8rem;
                color: #0D9488;
                font-weight: 700;
                display: block;
                margin-bottom: 0.35rem;
            }}
            .node-short {{
                font-size: 0.84rem;
                color: #475569;
            }}
            .inspector-box {{
                background: #F1F5F9;
                border-right: 5px solid #1E3A8A;
                border-radius: 10px;
                padding: 1.2rem 1.4rem;
            }}
            .inspector-box h4 {{
                color: #1E3A8A;
                font-size: 1.15rem;
                margin-bottom: 0.5rem;
            }}
            .inspector-meta {{
                display: flex;
                gap: 0.7rem;
                flex-wrap: wrap;
                margin-bottom: 0.75rem;
                font-size: 0.85rem;
            }}
            .meta-tag {{
                background: #FFFFFF;
                padding: 0.25rem 0.75rem;
                border-radius: 6px;
                border: 1px solid #CBD5E1;
                font-weight: 700;
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
                font-size: 1.05rem;
                margin-bottom: 0.6rem;
            }}
            .equation-formula {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.6rem;
                flex-wrap: wrap;
                background: rgba(255, 255, 255, 0.08);
                padding: 0.8rem;
                border-radius: 8px;
                font-weight: 700;
            }}
            .eq-box {{
                background: #1E3A8A;
                border: 1px solid #60A5FA;
                padding: 0.32rem 0.8rem;
                border-radius: 8px;
            }}
            .eq-result {{
                background: #0D9488;
                border: 1px solid #5EEAD4;
                padding: 0.32rem 0.9rem;
                border-radius: 8px;
            }}
            .axis-footer-nav {{
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
                    <button id="btn-master" class="tab-btn active" onclick="showMaster()">🗺️ الخريطة الشاملة (24)</button>
                    <input type="search" id="quranTermFilter" class="search-box" placeholder="🔍 تمييز مصطلح أو محور..." oninput="highlightModules(this.value)">
                    <button type="button" class="tab-btn" onclick="resetFilter()">إظهار الكل</button>
                </div>
                <div class="nav-group">
                    {pills_html}
                </div>
            </div>
        </div>

        <section id="view-master" class="view-section active">
            <div class="layers-stack">
                {"".join(layers_html_parts)}
            </div>
        </section>

        <section id="view-axis-detail" class="view-section">
            <div class="axis-workspace">
                <div class="section-header">
                    <div>
                        <span id="det-layer" style="font-size: 0.85rem; color: #0D9488; font-weight: 700; display: block;"></span>
                        <h2 id="det-title"></h2>
                    </div>
                    <span id="det-archetype" class="archetype-tag"></span>
                </div>
                <div id="det-summary" class="axis-summary"></div>
                <div id="det-nodes" class="nodes-flow"></div>
                <div class="inspector-box">
                    <h4 id="insp-title"></h4>
                    <div class="inspector-meta">
                        <span class="meta-tag" id="insp-root"></span>
                        <span class="meta-tag" id="insp-verses"></span>
                    </div>
                    <p id="insp-desc"></p>
                </div>
            </div>
            <div class="equation-banner">
                <h3>المعادلة التشغيلية الحاكمة للمحور:</h3>
                <div id="det-equation" class="equation-formula"></div>
            </div>
            <div class="axis-footer-nav">
                <button class="tab-btn" onclick="showMaster()">🔙 العودة إلى الخريطة الشاملة</button>
                <div style="display:flex; gap:0.5rem;">
                    <button id="btn-prev-axis" class="tab-btn">➡ المحور السابق</button>
                    <button id="btn-next-axis" class="tab-btn active">المحور التالي ⬅</button>
                </div>
            </div>
        </section>

        <script>
            const AXES_DATA = {axes_json_str};
            const ACTIVE_KEYS = {active_keys_json};

            function showMaster() {{
                document.getElementById('view-master').classList.add('active');
                document.getElementById('view-axis-detail').classList.remove('active');
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.getElementById('btn-master').classList.add('active');
            }}

            function resetFilter() {{
                const input = document.getElementById('quranTermFilter');
                if (input) input.value = '';
                document.querySelectorAll('.module-chip').forEach(chip => {{
                    chip.classList.remove('dimmed');
                    chip.classList.remove('matched');
                }});
            }}

            function highlightModules(query) {{
                const q = query.trim().toLowerCase();
                if (document.getElementById('view-axis-detail').classList.contains('active')) {{
                    showMaster();
                }}
                document.querySelectorAll('.module-chip').forEach(chip => {{
                    if (!q) {{
                        chip.classList.remove('dimmed');
                        chip.classList.remove('matched');
                        return;
                    }}
                    const text = chip.textContent.toLowerCase();
                    if (text.includes(q)) {{
                        chip.classList.remove('dimmed');
                        chip.classList.add('matched');
                    }} else {{
                        chip.classList.add('dimmed');
                        chip.classList.remove('matched');
                    }}
                }});
            }}

            function openAxis(key) {{
                const data = AXES_DATA[key];
                if (!data) return;

                document.getElementById('view-master').classList.remove('active');
                document.getElementById('view-axis-detail').classList.add('active');

                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                const pill = document.getElementById('pill-' + key);
                if (pill) pill.classList.add('active');

                document.getElementById('det-layer').textContent = data.layer;
                document.getElementById('det-title').textContent = data.num + ': ' + data.title;
                document.getElementById('det-archetype').textContent = 'القالب الهندسي: ' + data.archetype;
                document.getElementById('det-summary').textContent = data.summary;

                const nodesContainer = document.getElementById('det-nodes');
                nodesContainer.innerHTML = '';
                data.nodes.forEach((node, idx) => {{
                    const card = document.createElement('div');
                    card.className = 'node-card' + (idx === 0 ? ' selected' : '');
                    card.onclick = () => selectNode(key, idx, card);
                    card.innerHTML = `
                        <span class="node-index">${{idx + 1}}</span>
                        <span class="node-term">${{node.term}}</span>
                        <span class="node-role">${{node.role}}</span>
                        <p class="node-short">${{node.desc}}</p>
                    `;
                    nodesContainer.appendChild(card);
                }});

                if (data.nodes.length > 0) {{
                    renderInspector(data.nodes[0]);
                }}

                const eqContainer = document.getElementById('det-equation');
                eqContainer.innerHTML = '';
                data.equation.forEach((step, idx) => {{
                    const span = document.createElement('span');
                    if (idx === data.equation.length - 1) {{
                        span.className = 'eq-result';
                        span.textContent = step;
                        eqContainer.appendChild(span);
                    }} else {{
                        span.className = 'eq-box';
                        span.textContent = step;
                        eqContainer.appendChild(span);

                        const op = document.createElement('span');
                        op.textContent = (idx === data.equation.length - 2) ? '⟸' : '+';
                        eqContainer.appendChild(op);
                    }}
                }});

                const pos = ACTIVE_KEYS.indexOf(key);
                const prevKey = ACTIVE_KEYS[(pos - 1 + ACTIVE_KEYS.length) % ACTIVE_KEYS.length];
                const nextKey = ACTIVE_KEYS[(pos + 1) % ACTIVE_KEYS.length];

                const prevBtn = document.getElementById('btn-prev-axis');
                prevBtn.textContent = '➡ ' + AXES_DATA[prevKey].num;
                prevBtn.onclick = () => openAxis(prevKey);

                const nextBtn = document.getElementById('btn-next-axis');
                nextBtn.textContent = 'الانتقال إلى ' + AXES_DATA[nextKey].num + ' ⬅';
                nextBtn.onclick = () => openAxis(nextKey);
            }}

            function selectNode(axisKey, nodeIdx, cardElem) {{
                document.querySelectorAll('.node-card').forEach(c => c.classList.remove('selected'));
                cardElem.classList.add('selected');
                renderInspector(AXES_DATA[axisKey].nodes[nodeIdx]);
            }}

            function renderInspector(node) {{
                document.getElementById('insp-title').textContent = 'التحليل التفصيلي: ' + node.term + ' — ' + node.role;
                document.getElementById('insp-root').textContent = 'الجذر اللساني: ' + node.root;
                document.getElementById('insp-verses').textContent = 'الشواهد القرآنية: ' + node.verses;
                document.getElementById('insp-desc').textContent = node.desc;
            }}
        </script>
    </body>
    </html>
    """


# ==============================================================================
# التنفيذ الرئيسي للصفحة
# ==============================================================================
try:
    layers_data, axes_data, nodes_data = load_architecture_core()
    df_evidence = load_full_evidence_view()
    df_intersections = load_cross_axis_intersections()
except Exception as e:
    st.error(f"❌ تعذّر تحميل بيانات المعمارية من Supabase: {e}")
    st.stop()

# ترويسة الصفحة الرئيسية
st.markdown(
    """
    <div class="arch-hero">
        <h2>🧭 المعمارية البصرية للتحليل البنيوي والمفاهيمي في القرآن الكريم</h2>
        <p>المنظومة المرجعية المتكاملة عبر الطبقات الوظيفية الخمس والمحاور الأربعة والعشرين وفق قاعدة نفي الترادف الصفري (0%)</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# شريط الإحصاءات الحية من قاعدة البيانات
m1, m2, m3, m4 = st.columns(4)
m1.metric("الطبقات الوظيفية", f"{len(layers_data)} طبقات")
m2.metric("المحاور البنيوية", f"{len(axes_data)} محوراً")
m3.metric("العقد والمفاهيم القرآنية", f"{len(nodes_data)} مفهوماً")
m4.metric("الشواهد المربوطة بالمصحف", f"{len(df_evidence)} شاهداً")

st.markdown("---")

# التبويبات الرئيسية الأربعة
tab_map, tab_explorer, tab_intersections, tab_search = st.tabs(
    [
        "🗺️ الخريطة البصرية التفاعلية (24 محوراً)",
        "📖 المستكشف التحليلي والشواهد الصوتية",
        "🔗 شبكة التقاطعات المفاهيمية للآيات",
        "🔍 البحث الجذري والمفاهيمي الشامل",
    ]
)

# ==============================================================================
# التبويب 1: الخريطة البصرية التفاعلية المدمجة مباشرة من Supabase
# ==============================================================================
with tab_map:
    st.info(
        "💡 انقر على أي بطاقة محور في الطبقات الخمس أدناه أو اختر رقمه من الشريط العلوي لعرض التفكيك الجذري والمعادلة التشغيلية الحاكمة."
    )
    visual_map_html = build_interactive_visual_map_html(layers_data, axes_data, nodes_data)
    components.html(visual_map_html, height=1180, scrolling=True)


# ==============================================================================
# التبويب 2: المستكشف التحليلي للمحاور والعقد والشواهد القرآنية الصوتية
# ==============================================================================
with tab_explorer:
    col_l, col_a, col_n = st.columns([1.2, 1.4, 1.4])

    layer_options = {0: "جميع الطبقات الوظيفية (5)"}
    for l in layers_data:
        layer_options[l["layer_id"]] = l["title_ar"]

    with col_l:
        selected_layer_id = st.selectbox(
            "1️⃣ اختر الطبقة الوظيفية:",
            options=list(layer_options.keys()),
            format_func=lambda x: layer_options[x],
            key="exp_layer_select",
        )

    filtered_axes = (
        axes_data
        if selected_layer_id == 0
        else [a for a in axes_data if a["layer_id"] == selected_layer_id]
    )
    axis_options = {
        a["axis_id"]: f"المحور {a['axis_id']}: {a['title_ar']}" for a in filtered_axes
    }

    with col_a:
        selected_axis_id = st.selectbox(
            "2️⃣ اختر المحور البنيوي:",
            options=list(axis_options.keys()),
            format_func=lambda x: axis_options[x],
            key="exp_axis_select",
        )

    current_axis = next((a for a in axes_data if a["axis_id"] == selected_axis_id), None)
    axis_nodes = [n for n in nodes_data if n["axis_id"] == selected_axis_id]
    node_options = {0: "عرض جميع مفاهيم المحور (4 مفاهيم)"}
    for n in axis_nodes:
        node_options[n["node_id"]] = f"{n['node_order']}. {n['term_vowelled']} — {n['role_ar']}"

    with col_n:
        selected_node_id = st.selectbox(
            "3️⃣ اختر المفهوم (العقدة):",
            options=list(node_options.keys()),
            format_func=lambda x: node_options[x],
            key="exp_node_select",
        )

    if current_axis:
        st.markdown(f"### المحور {current_axis['axis_id']}: {current_axis['title_ar']}")
        st.caption(f"📐 **القالب الهندسي:** {current_axis['archetype']}")
        st.write(current_axis["summary_ar"])

        # عرض المعادلة التشغيلية الحاكمة للمحور
        eq_steps = current_axis.get("equation_steps", [])
        if isinstance(eq_steps, str):
            try:
                eq_steps = json.loads(eq_steps)
            except Exception:
                eq_steps = []

        if eq_steps:
            eq_html_parts = []
            for idx, step in enumerate(eq_steps):
                if idx == len(eq_steps) - 1:
                    eq_html_parts.append(f'<span class="eq-final-chip">{step}</span>')
                else:
                    eq_html_parts.append(f'<span class="eq-step-chip">{step}</span>')
                    op = "⟸" if idx == len(eq_steps) - 2 else "+"
                    eq_html_parts.append(f'<span style="color:#FBBF24; font-weight:800; margin:0 4px;">{op}</span>')

            st.markdown(
                f"""
                <div class="equation-box-st">
                    <div style="color:#FBBF24; font-weight:700; margin-bottom:0.5rem;">⚙️ المعادلة التشغيلية الحاكمة للمحور:</div>
                    <div style="text-align:center;">{"".join(eq_html_parts)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # عرض بطاقات المفاهيم التفصيلية
        target_nodes = (
            axis_nodes
            if selected_node_id == 0
            else [n for n in axis_nodes if n["node_id"] == selected_node_id]
        )

        for n in target_nodes:
            with st.expander(
                f"🔹 {n['term_vowelled']} | {n['role_ar']} (الجذر: {n['linguistic_root']})",
                expanded=True,
            ):
                st.markdown(f"**التحليل الوظيفي الدقيق:** {n['analytical_desc']}")
                st.markdown(f"**الشواهد المرجعية:** `{n['verses_display']}`")

                # جلب الآيات الشاهدة من العرض view_arch_full_evidence
                if not df_evidence.empty:
                    node_verses = df_evidence[df_evidence["node_id"] == n["node_id"]]
                    if not node_verses.empty:
                        st.markdown("---")
                        st.markdown("##### 📜 الآيات الشاهدة من المصحف الشريف (مع التلاوة الصوتية):")
                        for _, row in node_verses.iterrows():
                            s_num = int(row["surah_number"])
                            a_num = int(row["ayah_number"])
                            s_name = row.get("surah_name", "")
                            p_num = row.get("page_number", "")
                            j_num = row.get("juz", "")
                            a_text = row.get("ayah_text", "")

                            st.markdown(
                                f"""
                                <div class="ayah-card">
                                    <div class="ayah-uthmani">﴿ {a_text} ﴾</div>
                                    <div>
                                        <span class="ayah-meta-badge">سورة {s_name} ({s_num}:{a_num})</span>
                                        <span class="ayah-meta-badge">📄 صفحة المصحف: {p_num}</span>
                                        <span class="ayah-meta-badge">الجزء: {j_num}</span>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                            st.audio(get_everyayah_audio_url(s_num, a_num), format="audio/mp3")

        # زر تصدير بيانات المحور إلى Excel باستخدام الدالة المركزية في database.py
        if not df_evidence.empty:
            axis_export_df = df_evidence[df_evidence["axis_id"] == selected_axis_id].copy()
            axis_export_df = clean_dataframe_for_display(axis_export_df)
            if not axis_export_df.empty:
                excel_bytes = convert_df_to_excel(
                    axis_export_df, sheet_name=f"المحور_{selected_axis_id}"
                )
                st.download_button(
                    label=f"📥 تصدير شواهد المحور {selected_axis_id} إلى ملف Excel",
                    data=excel_bytes,
                    file_name=f"Quran_Architecture_Axis_{selected_axis_id}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )


# ==============================================================================
# التبويب 3: شبكة التقاطعات المفاهيمية (الآيات الجامعة لعدة محاور)
# ==============================================================================
with tab_intersections:
    st.subheader("🔗 الآيات القرآنية الجامعة لأكثر من محور أو مفهوم بنيوي")
    st.write(
        "يكشف هذا التحليل العلائقي الآيات التي تعمل كنقاط التقاء مركزية (Hub Verses) بين محاور المعمارية الـ 24."
    )

    if df_intersections.empty:
        st.warning("لا توجد تقاطعات مسجلة حالياً.")
    else:
        c1, c2 = st.columns([2, 1])
        with c1:
            surah_filter_list = ["جميع السور"] + sorted(
                df_intersections["surah_name"].dropna().unique().tolist(),
                key=lambda s: df_intersections[df_intersections["surah_name"] == s]["surah_number"].iloc[0],
            )
            chosen_surah = st.selectbox(
                "تصفية حسب السورة:", surah_filter_list, key="inter_surah_filter"
            )
        with c2:
            min_nodes = st.slider(
                "الحد الأدنى لعدد المفاهيم المتقاطعة في الآية:",
                min_value=2,
                max_value=int(df_intersections["shared_nodes_count"].max()),
                value=2,
                key="inter_min_nodes",
            )

        filtered_inter = df_intersections[
            df_intersections["shared_nodes_count"] >= min_nodes
        ].copy()
        if chosen_surah != "جميع السور":
            filtered_inter = filtered_inter[filtered_inter["surah_name"] == chosen_surah]

        st.success(f"عدد الآيات المتقاطعة المطابقة للتصفية: **{len(filtered_inter)}** آية.")

        for _, row in filtered_inter.iterrows():
            s_num = int(row["surah_number"])
            a_num = int(row["ayah_number"])
            s_name = row.get("surah_name", "")
            p_num = row.get("page_number", "")
            a_text = row.get("ayah_text", "")
            concepts_str = str(row.get("intersecting_concepts", ""))
            concepts_list = [c.strip() for c in concepts_str.split("|") if c.strip()]
            pills = "".join([f'<span class="concept-pill">{c}</span>' for c in concepts_list])

            st.markdown(
                f"""
                <div class="ayah-card">
                    <div class="ayah-uthmani">﴿ {a_text} ﴾</div>
                    <div style="margin-bottom:0.5rem;">
                        <span class="ayah-meta-badge">سورة {s_name} ({s_num}:{a_num})</span>
                        <span class="ayah-meta-badge">📄 صفحة المصحف: {p_num}</span>
                        <span class="ayah-meta-badge">محاور مشتركة: {row['shared_axes_count']} | مفاهيم: {row['shared_nodes_count']}</span>
                    </div>
                    <div>{pills}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.expander(f"🔊 استماع لتلاوة الآية ({s_name}: {a_num})"):
                st.audio(get_everyayah_audio_url(s_num, a_num), format="audio/mp3")

        # جدول ملخص وتصدير Excel
        st.markdown("#### 📊 الجدول الإحصائي للتقاطعات المفاهيمية")
        display_inter_df = clean_dataframe_for_display(filtered_inter).rename(
            columns={
                "surah_number": "رقم السورة",
                "surah_name": "اسم السورة",
                "ayah_number": "رقم الآية",
                "ayah_text": "نص الآية",
                "page_number": "رقم الصفحة",
                "shared_axes_count": "عدد المحاور",
                "shared_nodes_count": "عدد المفاهيم",
                "intersecting_concepts": "المفاهيم المتقاطعة",
            }
        )
        st.dataframe(display_inter_df, use_container_width=True, hide_index=True)

        excel_inter = convert_df_to_excel(display_inter_df, sheet_name="التقاطعات_المفاهيمية")
        st.download_button(
            label="📥 تصدير جدول التقاطعات المفاهيمية إلى Excel",
            data=excel_inter,
            file_name="Quran_Conceptual_Intersections.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


# ==============================================================================
# التبويب 4: البحث الجذري والمفاهيمي الشامل (يعتمد على normalize_arabic في database.py)
# ==============================================================================
with tab_search:
    st.subheader("🔍 البحث في العقد الـ 96 والجذور اللسانية والتحليل الوظيفي")
    search_query = st.text_input(
        "أدخل مصطلحاً قرآنياً أو جذراً لسانياً أو كلمة مفتاحية (بدون تشكيل أو بالتشكيل):",
        placeholder="مثال: القلب، الغشاوة، التسخير، البرزخ، خ-ل-ق، الأمانة...",
        key="arch_global_search_input",
    )

    if search_query.strip():
        norm_q = normalize_arabic(search_query)
        matched_nodes = []
        axis_lookup = {a["axis_id"]: a for a in axes_data}
        layer_lookup = {l["layer_id"]: l for l in layers_data}

        for n in nodes_data:
            combined_text = " ".join(
                [
                    str(n.get("term_plain", "")),
                    str(n.get("term_vowelled", "")),
                    str(n.get("role_ar", "")),
                    str(n.get("linguistic_root", "")),
                    str(n.get("analytical_desc", "")),
                ]
            )
            if norm_q in normalize_arabic(combined_text):
                matched_nodes.append(n)

        if not matched_nodes:
            st.warning(f"لم يتم العثور على مفاهيم مطابقة لعبارة: **{search_query}**")
        else:
            st.success(f"تم العثور على **{len(matched_nodes)}** مفهوماً مطابقاً:")
            for n in matched_nodes:
                ax = axis_lookup.get(n["axis_id"], {})
                ly = layer_lookup.get(ax.get("layer_id"), {})
                with st.expander(
                    f"📌 {n['term_vowelled']} — المحور {n['axis_id']}: {ax.get('title_ar', '')}",
                    expanded=True,
                ):
                    st.markdown(f"**الطبقة الوظيفية:** {ly.get('title_ar', '')}")
                    st.markdown(f"**الدور البنيوي:** {n['role_ar']}")
                    st.markdown(f"**الجذر اللساني:** `{n['linguistic_root']}`")
                    st.markdown(f"**التحليل الوظيفي:** {n['analytical_desc']}")
                    st.markdown(f"**الشواهد القرآنية:** `{n['verses_display']}`")
