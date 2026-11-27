import base64
import os
from datetime import datetime
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import theme
from database import supabase

# 1. إعدادات الصفحة المستقلة
st.set_page_config(
    page_title="المصحف المصور والتلاوة الذكية والحفظ",
    page_icon="📖",
    layout="wide",
)

# تطبيق التنسيق المركزي الموحد وزر الرئيسية
theme.apply_custom_theme()
theme.add_home_button()

# ==============================================================================
# حقن التنسيق البصري الموحد (مطابق لهوية البوابات 4، 5، 6، 7 والواجهة الرئيسية)
# ==============================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700&display=swap');

    .g1-hero-box {
        background: linear-gradient(135deg, rgba(27, 77, 62, 0.10) 0%, rgba(212, 175, 55, 0.12) 100%);
        border: 1px solid rgba(212, 175, 55, 0.45);
        border-right: 6px solid #1B4D3E;
        border-radius: 14px;
        padding: 20px 26px;
        margin-bottom: 18px;
        text-align: center;
        font-family: 'Cairo', sans-serif;
    }
    .g1-hero-title {
        color: #1B4D3E;
        font-size: 1.85rem;
        font-weight: 700;
        margin: 0 0 6px 0;
    }
    .g1-hero-sub {
        color: #555555;
        font-size: 1.02rem;
        margin: 0;
    }
    .g1-kpi-card {
        background: #FFFFFF;
        border: 1px solid #E6E2D6;
        border-top: 4px solid #D4AF37;
        border-radius: 12px;
        padding: 14px 16px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        font-family: 'Cairo', sans-serif;
    }
    .g1-kpi-label {
        color: #666666;
        font-size: 0.90rem;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .g1-kpi-val {
        color: #1B4D3E;
        font-size: 1.65rem;
        font-weight: 700;
    }
    .g1-tajweed-legend {
        background: #FCFBF7;
        border: 1px solid #E2D9C5;
        border-radius: 10px;
        padding: 8px 14px;
        margin: 8px 0 12px 0;
        text-align: center;
        font-family: 'Cairo', sans-serif;
        font-size: 0.88rem;
        direction: rtl;
    }
    .g1-ayah-card {
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
    .g1-ayah-card-saved {
        background: #F4FAF7;
        border: 1px solid #B7DEC9;
        border-right: 5px solid #15803D;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        direction: rtl;
        text-align: right;
    }
    .g1-ayah-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 8px;
        font-family: 'Cairo', sans-serif;
    }
    .g1-badge-surah {
        background: #1B4D3E;
        color: #FFFFFF;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 600;
    }
    .g1-badge-saved {
        background: rgba(21, 128, 61, 0.14);
        color: #15803D;
        border: 1px solid rgba(21, 128, 61, 0.45);
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
    }
    .g1-badge-new {
        background: rgba(212, 175, 55, 0.22);
        color: #7A5C00;
        border: 1px solid rgba(212, 175, 55, 0.6);
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
    }
    .g1-ayah-text {
        font-family: 'Amiri', serif;
        font-size: 1.52rem;
        line-height: 2.25;
        color: #1E293B;
        margin: 6px 0 4px 0;
    }
    .g1-objective-box {
        background: rgba(27, 77, 62, 0.07);
        border: 1px solid rgba(27, 77, 62, 0.22);
        border-right: 5px solid #D4AF37;
        border-radius: 10px;
        padding: 12px 18px;
        margin: 10px 0 16px 0;
        font-family: 'Cairo', sans-serif;
        font-size: 0.96rem;
        color: #1E293B;
        direction: rtl;
        text-align: right;
    }
    div[data-baseweb="select"] ul li div {
        font-family: 'Cairo', sans-serif !important;
    }
    .stMultiSelect [data-baseweb="tag"] {
        direction: rtl !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# تعريف القراء الثلاثة المعتمدين (EveryAyah 128kbps High-Quality MP3)
# ==============================================================================
RECITERS_CONFIG = {
    "🎙️ الشيخ ماهر المعيقلي": {
        "ayah_folder": "MaherAlMuaiqly128kbps",
        "page_folder": "MaherAlMuaiqly128kbps/PageMp3s",
    },
    "🎙️ الشيخ سعود الشريم": {
        "ayah_folder": "Saood_ash-Shuraym_128kbps",
        "page_folder": "Saood_ash-Shuraym_128kbps/PageMp3s",
    },
    "🎙️ الشيخ محمود خليل الحصري (المرتل)": {
        "ayah_folder": "Husary_128kbps",
        "page_folder": "Husary_128kbps/PageMp3s",
    },
}


# ==============================================================================
# جلب البيانات من Supabase
# ==============================================================================
@st.cache_data(ttl=300)
def load_surah_page_mapping_from_supabase():
    try:
        response = (
            supabase.table("surah_pages").select("*").order("surah_serial").execute()
        )
        if response.data:
            return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"❌ خطأ أثناء جلب بيانات السور من قاعدة البيانات: {e}")
    return pd.DataFrame()


@st.cache_data(ttl=60)
def load_archive_kpis():
    saved_cnt = 0
    reviews_sum = 0
    try:
        resp = (
            supabase.table("user_memorization_archive")
            .select("id, review_count")
            .execute()
        )
        rows = resp.data or []
        saved_cnt = len(rows)
        reviews_sum = sum(int(r.get("review_count") or 0) for r in rows)
    except Exception:
        pass
    return saved_cnt, reviews_sum


df_surah_map = load_surah_page_mapping_from_supabase()
saved_ayahs_cnt, total_reviews_cnt = load_archive_kpis()

# الترويسة البصرية الموحدة
st.markdown(
    """
    <div class="g1-hero-box">
        <div class="g1-hero-title">📖 المصحف المصور والتلاوة الذكية والحفظ</div>
        <p class="g1-hero-sub">تصفح مصحف التجويد الملون والمصحف العثماني عالي الدقة، مع التلاوة الصوتية للقراء الثلاثة وإدارة الحفظ والمراجعة</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# بطاقات المؤشرات العليا (KPI Cards)
k1, k2, k3, k4 = st.columns(4)
kpi_items = [
    (k1, "آيات القرآن الكريم", "6,236 آية"),
    (k2, "صفحات المصحف الشريف", "604 صفحة"),
    (k3, "الآيات المحفوظة بأرشيفك", f"{saved_ayahs_cnt:,} آية"),
    (k4, "إجمالي جلسات المراجعة", f"{total_reviews_cnt:,} مراجعة"),
]
for col_box, lbl, val in kpi_items:
    with col_box:
        st.markdown(
            f"""
            <div class="g1-kpi-card">
                <div class="g1-kpi-label">{lbl}</div>
                <div class="g1-kpi-val">{val}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# تقسيم الشاشة إلى تبويبين رئيسيين
# ==============================================================================
tab1, tab2 = st.tabs(
    [
        "📖 التبويب الأول: المصحف المصور التفاعلي (التجويد والعثماني)",
        "🔍 التبويب الثاني: التلاوة الذكية للآيات، التدبر، وأرشيف الحفظ",
    ]
)

# ------------------------------------------------------------------------------
# التبويب الأول: المصحف التفاعلي المزدوج (التجويد الملون + العثماني + تلاوة الصفحة اختيارياً)
# ------------------------------------------------------------------------------
with tab1:
    st.subheader("📖 المصحف المصور عالي الدقة (عرض الصفحتين المتقابلتين)")

    # تهيئة مفتاح موحد لرقم الصفحة لضمان عمل الأزرار ومربع الرقم بتزامن تام
    if "g1_page_num_widget" not in st.session_state:
        st.session_state["g1_page_num_widget"] = 1

    def go_next_spread():
        cur = int(st.session_state["g1_page_num_widget"])
        if cur < 1:
            st.session_state["g1_page_num_widget"] = cur + 1
        else:
            st.session_state["g1_page_num_widget"] = min(604, cur + 2)

    def go_prev_spread():
        cur = int(st.session_state["g1_page_num_widget"])
        if cur <= 1:
            st.session_state["g1_page_num_widget"] = max(-1, cur - 1)
        elif cur == 2:
            st.session_state["g1_page_num_widget"] = 1
        else:
            st.session_state["g1_page_num_widget"] = max(1, cur - 2)

    c_nav1, c_nav2, c_nav3, c_nav4 = st.columns([2.2, 1.8, 1.0, 1.0])
    with c_nav1:
        mushaf_edition = st.radio(
            "🎨 اختر طبعة المصحف:",
            options=[
                "مصحف التجويد الملون (High-Res)",
                "مصحف المدينة العثماني الكلاسيكي",
            ],
            horizontal=True,
            key="g1_mushaf_edition",
        )
    with c_nav2:
        selected_page = st.number_input(
            "📄 رقم الصفحة (-1 غلاف، 0 بسملة، 1-604):",
            min_value=-1,
            max_value=604,
            step=1,
            key="g1_page_num_widget",
        )
    with c_nav3:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        st.button(
            "▶ الصفحة التالية",
            width="stretch",
            key="g1_next_page",
            on_click=go_next_spread,
        )
    with c_nav4:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        st.button(
            "الصفحة السابقة ◀",
            width="stretch",
            key="g1_prev_page",
            on_click=go_prev_spread,
        )

    is_tajweed = mushaf_edition.startswith("مصحف التجويد")
    if is_tajweed:
        st.markdown(
            """
            <div class="g1-tajweed-legend">
                🎨 <b>دليل ألوان مصحف التجويد:</b>
                &nbsp;&nbsp;<span style="color:#DC2626; font-weight:700;">■ الأحمر:</span> المدود (اللازم والواجب والجائز)
                &nbsp;|&nbsp;<span style="color:#16A34A; font-weight:700;">■ الأخضر:</span> الغنّة والإخفاء والإدغام بغنة
                &nbsp;|&nbsp;<span style="color:#2563EB; font-weight:700;">■ الأزرق:</span> القلقلة
                &nbsp;|&nbsp;<span style="color:#6B7280; font-weight:700;">■ الرمادي:</span> حروف تُكتب ولا تُنطق
            </div>
            """,
            unsafe_allow_html=True,
        )

    github_user = "Salama5939"
    repo_name = "quran-analysis-app"
    branch = "main"

    def get_local_tajweed_data_uri(page_idx: int) -> str | None:
        """قراءة صفحة مصحف التجويد مباشرة من المجلد المحلي Quran-Tajweed-PNG بأقصى سرعة"""
        for ext, mime in [
            ("png", "image/png"),
            ("jpg", "image/jpeg"),
            ("jpeg", "image/jpeg"),
        ]:
            for fname in [f"{page_idx}.{ext}", f"{page_idx:03d}.{ext}"]:
                fpath = os.path.join("Quran-Tajweed-PNG", fname)
                if os.path.exists(fpath) and os.path.getsize(fpath) > 1024:
                    with open(fpath, "rb") as img_f:
                        b64_str = base64.b64encode(img_f.read()).decode("utf-8")
                    return f"data:{mime};base64,{b64_str}"
        return None

    def get_mushaf_image_chain(page_idx: int) -> tuple[str, str, str]:
        """سلسلة تحميل ثلاثية: (1) التجويد المحلي -> (2) التجويد من مستودعك على GitHub -> (3) العثماني"""
        uthmani_cdn = f"https://cdn.jsdelivr.net/gh/{github_user}/{repo_name}@{branch}/Quran-PNG-master/{page_idx:03d}.png"
        uthmani_raw = f"https://raw.githubusercontent.com/{github_user}/{repo_name}/{branch}/Quran-PNG-master/{page_idx:03d}.png"
        if is_tajweed and 1 <= page_idx <= 604:
            local_uri = get_local_tajweed_data_uri(page_idx)
            tajweed_github = f"https://raw.githubusercontent.com/{github_user}/{repo_name}/{branch}/Quran-Tajweed-PNG/{page_idx}.png"
            primary_src = local_uri if local_uri else tajweed_github
            return primary_src, tajweed_github, uthmani_cdn
        return uthmani_cdn, uthmani_raw, uthmani_raw

    def render_special_img(filename: str, alt_text: str) -> str:
        local_path = os.path.join("Quran-PNG-master", filename.replace("%20", " "))
        p_url = f"https://cdn.jsdelivr.net/gh/{github_user}/{repo_name}@{branch}/Quran-PNG-master/{filename}"
        f_url = f"https://raw.githubusercontent.com/{github_user}/{repo_name}/{branch}/Quran-PNG-master/{filename}"
        if os.path.exists(local_path) and os.path.getsize(local_path) > 1024:
            with open(local_path, "rb") as img_f:
                b64_str = base64.b64encode(img_f.read()).decode("utf-8")
            p_url = f"data:image/png;base64,{b64_str}"
        return (
            f'<img src="{p_url}" data-fb1="{f_url}" '
            f"onerror=\"if(!this.dataset.r1){{this.dataset.r1='1';this.src=this.dataset.fb1;}}\" "
            f'alt="{alt_text}">'
        )

    def render_page_img(page_idx: int) -> str:
        u1, u2, u3 = get_mushaf_image_chain(page_idx)
        return (
            f'<img src="{u1}" data-fb1="{u2}" data-fb2="{u3}" '
            f"onerror=\"if(!this.dataset.r1){{this.dataset.r1='1';this.src=this.dataset.fb1;}}"
            f"else if(!this.dataset.r2){{this.dataset.r2='1';this.src=this.dataset.fb2;}}\" "
            f'alt="صفحة {page_idx}">'
        )

    def get_spread_html(p: int) -> str:
        if p == -1:
            cover_img = render_special_img(
                "quran%20gold%20cover.png", "غلاف المصحف الشريف"
            )
            return f"""
                <div class="spread-container">
                    <div class="single-page cover-page">{cover_img}</div>
                </div>
            """
        if p == 0:
            bismallah_img = render_special_img("000.png", "البسملة")
            return f"""
                <div class="spread-container">
                    <div class="page left-page blank-page"></div>
                    <div class="page right-page bismallah-page">
                        {bismallah_img}
                        <div class="page-footer">0</div>
                    </div>
                </div>
            """

        if p % 2 == 1:
            right_p = p
            left_p = p + 1 if p + 1 <= 604 else None
        else:
            right_p = p - 1
            left_p = p

        left_html = (
            f"""
            <div class="page left-page">
                {render_page_img(left_p)}
                <div class="page-footer">{left_p}</div>
            </div>
            """
            if (left_p and left_p <= 604)
            else '<div class="page left-page blank-page"></div>'
        )
        right_html = (
            f"""
            <div class="page right-page">
                {render_page_img(right_p)}
                <div class="page-footer">{right_p}</div>
            </div>
            """
            if right_p <= 604
            else '<div class="page right-page blank-page"></div>'
        )
        return f'<div class="spread-container">{left_html}{right_html}</div>'

    current_spread_html = get_spread_html(selected_page)
    edition_badge = "مصحف التجويد الملون" if is_tajweed else "مصحف المدينة العثماني"

    viewer_html = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                background-color: transparent;
                margin: 0;
                padding: 4px;
                height: 100vh;
                overflow: hidden;
            }}
            .spread-container {{
                display: flex;
                flex-direction: row-reverse;
                justify-content: center;
                align-items: center;
                width: 940px;
                height: 670px;
                box-shadow: 0 14px 36px rgba(27, 77, 62, 0.22);
                background-color: #fdfbf7;
                border-radius: 8px;
                border: 2px solid #D4AF37;
            }}
            .page, .single-page {{
                width: 50%;
                height: 100%;
                background-color: #fdfbf7;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                overflow: hidden;
                box-sizing: border-box;
                border-left: 1px solid #e0d6c3;
                border-right: 1px solid #e0d6c3;
                padding: 6px;
                position: relative;
            }}
            .single-page {{
                width: 100%;
                background-color: #0F172A !important;
            }}
            .page img, .single-page img {{
                width: 100%;
                height: 100%;
                object-fit: contain;
            }}
            .bismallah-page img {{
                max-height: 40%;
                object-fit: contain;
            }}
            .blank-page {{
                background-color: #fdfbf7;
            }}
            .page-footer {{
                position: absolute;
                bottom: 4px;
                width: 100%;
                text-align: center;
                font-size: 12px;
                color: #1B4D3E;
                font-weight: bold;
                font-family: 'Cairo', sans-serif;
            }}
            .info-bar {{
                margin-top: 10px;
                font-family: 'Cairo', sans-serif;
                font-size: 14px;
                color: #1B4D3E;
                background-color: #FCFBF7;
                border: 1px solid #D4AF37;
                padding: 5px 22px;
                border-radius: 20px;
                font-weight: 700;
            }}
        </style>
    </head>
    <body>
        {current_spread_html}
        <div class="info-bar">
            <span>📖 {edition_badge} &nbsp;|&nbsp; العرض الحالي: {'غلاف المصحف الشريف' if selected_page == -1 else ('البسملة الشريفة' if selected_page == 0 else f'صفحة {selected_page}')}</span>
        </div>
    </body>
    </html>
    """
    components.html(viewer_html, height=745, scrolling=False)

    # خيار الاستماع لكامل الصفحة الحالية (اختياري)
    if 1 <= selected_page <= 604:
        with st.expander(
            f"🎧 استماع اختياري لتلاوة الصفحة رقم ({selected_page}) كاملة",
            expanded=False,
        ):
            c_pg_rec1, c_pg_rec2 = st.columns([2.2, 2.8])
            with c_pg_rec1:
                page_reciter_name = st.selectbox(
                    "اختر القارئ لتلاوة الصفحة:",
                    options=list(RECITERS_CONFIG.keys()),
                    key="g1_tab1_page_reciter",
                )
            with c_pg_rec2:
                page_folder = RECITERS_CONFIG[page_reciter_name]["page_folder"]
                page_mp3_url = f"https://everyayah.com/data/{page_folder}/Page{selected_page:03d}.mp3"
                st.markdown(
                    f"<div style='margin-top:6px; font-family:Cairo,sans-serif; font-size:0.90rem; color:#1B4D3E; font-weight:700;'>🔊 تلاوة صفحة ({selected_page}) بصوت {page_reciter_name}:</div>",
                    unsafe_allow_html=True,
                )
                st.audio(page_mp3_url, format="audio/mp3")


# ------------------------------------------------------------------------------
# التبويب الثاني: التلاوة الذكية للآيات، التدبر، وأرشيف الحفظ (بدون أي جداول)
# ------------------------------------------------------------------------------
with tab2:
    st.subheader(
        "🔍 استعراض الآيات بالرسم العثماني، مقاصد السور، والتلاوة الذكية للحفظ"
    )

    if df_surah_map.empty:
        st.error("❌ تعذر الاتصال بجدول 'surah_pages' في قاعدة البيانات.")
    else:
        surah_list_t2 = df_surah_map["surah_name"].str.strip().tolist()

        col_a1, col_a2, col_a3, col_a4 = st.columns([2.0, 1.2, 1.2, 2.2])
        with col_a1:
            selected_surah_t2 = st.selectbox(
                "1️⃣ اختر السورة:", surah_list_t2, key="g1_surah_select_t2"
            )
            surah_row = df_surah_map[
                df_surah_map["surah_name"].str.strip() == selected_surah_t2
            ]
            surah_num = (
                int(str(surah_row["surah_serial"].values[0]))
                if not surah_row.empty
                else 1
            )

        with col_a2:
            start_ayah = st.number_input(
                "2️⃣ من آية:",
                min_value=1,
                max_value=286,
                value=1,
                key="g1_start_ayah_t2",
            )
        with col_a3:
            end_ayah = st.number_input(
                "3️⃣ إلى آية:",
                min_value=1,
                max_value=286,
                value=7,
                key="g1_end_ayah_t2",
            )
        with col_a4:
            selected_reciter_t2 = st.selectbox(
                "4️⃣ اختر القارئ للتلاوة:",
                options=list(RECITERS_CONFIG.keys()),
                key="g1_reciter_select_t2",
            )

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            search_btn = st.button(
                "🔍 استعراض بطاقات الآيات وتجهيز التلاوة",
                key="g1_btn_search_t2",
                type="primary",
                width="stretch",
            )
        with col_b2:
            new_request_btn = st.button(
                "🔄 طلب تلاوة جديد (إعادة ضبط الشاشة)",
                key="g1_btn_new_request_t2",
                width="stretch",
                help="يقوم بتفريغ الذاكرة بالكامل لتلقي طلب بحث وتلاوة جديد.",
            )

        if new_request_btn:
            for k in [
                "tab2_held_ayahs",
                "tab2_surah_name",
                "tab2_surah_num",
                "tab2_start_ayah",
                "tab2_end_ayah",
                "tab2_archived_dict",
                "tab2_objective",
                "tab2_quran_multiselect",
                "tab2_repeat_count",
            ]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

        if search_btn:
            if start_ayah > end_ayah:
                st.error(
                    "⚠️ خطأ: آية البداية يجب أن تكون أقل من أو مساوية لآية النهاية."
                )
            else:
                with st.spinner("جاري جلب بطاقات الآيات والمقاصد وحالة الأرشيف..."):
                    try:
                        response = (
                            supabase.table("full_quran")
                            .select("ayah_number, ayah_text, page_number")
                            .eq("surah_name", selected_surah_t2)
                            .gte("ayah_number", start_ayah)
                            .lte("ayah_number", end_ayah)
                            .order("ayah_number")
                            .execute()
                        )
                        ayahs_data = response.data or []

                        archive_resp = (
                            supabase.table("user_memorization_archive")
                            .select("ayah_number, review_count")
                            .eq("surah_serial", surah_num)
                            .execute()
                        )
                        archived_dict = {
                            item["ayah_number"]: item.get("review_count", 0)
                            for item in (archive_resp.data or [])
                        }

                        obj_resp = (
                            supabase.table("surah_objectives")
                            .select("surah_objective")
                            .eq("surah_number", surah_num)
                            .execute()
                        )
                        surah_objective_text = (
                            obj_resp.data[0]["surah_objective"]
                            if obj_resp.data
                            else "غير مسجل"
                        )

                        st.session_state["tab2_held_ayahs"] = ayahs_data
                        st.session_state["tab2_surah_name"] = selected_surah_t2
                        st.session_state["tab2_surah_num"] = surah_num
                        st.session_state["tab2_start_ayah"] = start_ayah
                        st.session_state["tab2_end_ayah"] = end_ayah
                        st.session_state["tab2_archived_dict"] = archived_dict
                        st.session_state["tab2_objective"] = surah_objective_text

                        if "tab2_quran_multiselect" in st.session_state:
                            del st.session_state["tab2_quran_multiselect"]

                    except Exception as e:
                        st.error(f"❌ حدث خطأ أثناء الاستعلام: {e}")

        if st.session_state.get("tab2_held_ayahs"):
            h_surah_name = st.session_state["tab2_surah_name"]
            h_surah_num = st.session_state["tab2_surah_num"]
            h_start = st.session_state["tab2_start_ayah"]
            h_end = st.session_state["tab2_end_ayah"]
            ayahs_data = st.session_state["tab2_held_ayahs"]
            archived_dict = st.session_state["tab2_archived_dict"]
            h_objective = st.session_state.get("tab2_objective", "")

            st.markdown("---")
            st.success(
                f"✅ **سورة {h_surah_name}** | النطاق: من آية ({h_start}) إلى آية ({h_end}) | عدد الآيات: **{len(ayahs_data)}** آية"
            )

            if h_objective:
                st.markdown(
                    f"""
                    <div class="g1-objective-box">
                        🎯 <b>مقصد سورة {h_surah_name}:</b> {h_objective}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            multiselect_options = []
            options_map = {}

            for item in ayahs_data:
                a_num = item["ayah_number"]
                a_text = item["ayah_text"]
                p_num = item.get("page_number", "—")
                is_saved = a_num in archived_dict
                rev_cnt = archived_dict.get(a_num, 0)

                card_cls = "g1-ayah-card-saved" if is_saved else "g1-ayah-card"
                badge_html = (
                    f"<span class='g1-badge-saved'>⭐ محفوظة بالأرشيف (مراجعات: {rev_cnt}) | صفحة {p_num}</span>"
                    if is_saved
                    else f"<span class='g1-badge-new'>🆕 جديدة للاستزادة | صفحة {p_num}</span>"
                )

                st.markdown(
                    f"""
                    <div class="{card_cls}">
                        <div class="g1-ayah-header">
                            <span class="g1-badge-surah">📖 سورة {h_surah_name} — الآية ({a_num})</span>
                            {badge_html}
                        </div>
                        <div class="g1-ayah-text">﴿ {a_text} ﴾</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                label = f"آية ({a_num}) — {a_text[:45]}... ({'محفوظة' if is_saved else 'جديدة'})"
                multiselect_options.append(label)
                options_map[label] = {
                    "ayah_number": a_num,
                    "ayah_text": a_text,
                    "is_saved": is_saved,
                    "rev_cnt": rev_cnt,
                }

            st.markdown("---")
            st.subheader("🎧 مشغل التلاوة الذكي للحفظ وإدارة الأرشيف:")

            selected_labels = st.multiselect(
                "اختر الآيات المطلوبة من النطاق أعلاه لتشغيل التلاوة أو الحفظ في الأرشيف:",
                options=multiselect_options,
                default=multiselect_options,
                key="tab2_quran_multiselect",
            )

            col_r1, col_r2 = st.columns([1.6, 2.4])
            with col_r1:
                repeat_count = st.number_input(
                    "🔄 عدد مرات تكرار كل آية (للحفظ والتثبيت):",
                    min_value=1,
                    max_value=10,
                    value=1,
                    key="tab2_repeat_count",
                )
            with col_r2:
                action_choice = st.radio(
                    "اختر العملية المطلوبة للآيات المحددة:",
                    [
                        "💾 حفظ الآيات الجديدة المحددة في الأرشيف",
                        "🔄 تسجيل مراجعة للآيات المحددة مسبقاً",
                    ],
                    horizontal=True,
                    key="tab2_action_radio",
                )

            execute_btn = st.button(
                "🚀 تنفيذ عملية الأرشيف للآيات المحددة",
                type="primary",
                width="stretch",
                key="g1_btn_execute_tab2",
            )

            if execute_btn:
                if not selected_labels:
                    st.warning("⚠️ لم تقم بتحديد أي آية من القائمة!")
                else:
                    if "حفظ الآيات الجديدة" in action_choice:
                        to_save = []
                        for lbl in selected_labels:
                            info = options_map[lbl]
                            if not info["is_saved"]:
                                to_save.append(
                                    {
                                        "surah_serial": h_surah_num,
                                        "surah_name": h_surah_name,
                                        "ayah_number": info["ayah_number"],
                                        "ayah_text": info["ayah_text"],
                                        "memorization_status": "تم الحفظ",
                                        "review_count": 0,
                                    }
                                )

                        if to_save:
                            try:
                                supabase.table("user_memorization_archive").insert(
                                    to_save
                                ).execute()
                                load_archive_kpis.clear()
                                st.success(
                                    f"✅ تم حفظ ({len(to_save)}) آية جديدة في أرشيفك بنجاح!"
                                )
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ خطأ أثناء الحفظ: {e}")
                        else:
                            st.warning(
                                "⚠️ جميع الآيات المحددة مسجلة مسبقاً في الأرشيف بالفعل."
                            )
                    else:
                        to_review = []
                        for lbl in selected_labels:
                            info = options_map[lbl]
                            if info["is_saved"]:
                                to_review.append(
                                    {
                                        "ayah_number": info["ayah_number"],
                                        "current_rev": info["rev_cnt"],
                                    }
                                )

                        if to_review:
                            try:
                                current_time = datetime.utcnow().isoformat()
                                for r in to_review:
                                    new_count = r["current_rev"] + 1
                                    supabase.table("user_memorization_archive").update(
                                        {
                                            "review_count": new_count,
                                            "last_reviewed_at": current_time,
                                        }
                                    ).eq("surah_serial", h_surah_num).eq(
                                        "ayah_number", r["ayah_number"]
                                    ).execute()

                                load_archive_kpis.clear()
                                st.success(
                                    f"✅ تم تسجيل المراجعة بنجاح لـ ({len(to_review)}) آية!"
                                )
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ خطأ أثناء تسجيل المراجعة: {e}")
                        else:
                            st.warning(
                                "⚠️ لم تقم بتحديد أي آيات محفوظة مسبقاً لتسجيل المراجعة."
                            )

            st.markdown("<br>", unsafe_allow_html=True)

            if selected_labels and repeat_count > 0:
                audio_urls = []
                ayah_numbers = []
                surah_str = f"{h_surah_num:03d}"
                ayah_folder = RECITERS_CONFIG[selected_reciter_t2]["ayah_folder"]

                for lbl in selected_labels:
                    info = options_map[lbl]
                    curr_num = info["ayah_number"]
                    ayah_str = f"{curr_num:03d}"
                    url_item = f"https://everyayah.com/data/{ayah_folder}/{surah_str}{ayah_str}.mp3"
                    for _ in range(repeat_count):
                        audio_urls.append(url_item)
                        ayah_numbers.append(str(curr_num))

                js_urls = str(audio_urls)
                js_ayahs = str(ayah_numbers)
                player_title = (
                    f"🎧 {selected_reciter_t2} ({repeat_count} مرات لكل آية):"
                )

                html_player = f"""
                <div style="direction: rtl; text-align: right; font-family: 'Cairo', sans-serif; background: linear-gradient(135deg, #1B4D3E 0%, #143D30 100%); padding: 18px; border-radius: 12px; border-top: 4px solid #D4AF37; color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                    <h4 id="status-text" style="color: #FDE68A; margin-top: 0; font-size: 16px;">{player_title} جاري التجهيز...</h4>
                    <audio id="quran-player" controls autoplay style="width: 100%; border-radius: 6px; outline: none;">
                        متصفحك لا يدعم تشغيل الصوت.
                    </audio>
                    <div id="replay-prompt" style="display: none; margin-top: 14px; background-color: rgba(255,255,255,0.08); padding: 12px; border-radius: 8px; text-align: center; border: 1px solid #D4AF37;">
                        <p style="margin: 0 0 10px 0; font-weight: bold; color: #FFFFFF; font-size: 15px;">هل تريد إعادة التلاوة على نفس الآيات المختارة؟</p>
                        <div style="display: flex; flex-direction: row; justify-content: center; align-items: center; gap: 20px;">
                            <button onclick="restartPlayback()" style="background-color: #16A34A; color: white; border: none; padding: 8px 28px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px;">نعم، أعد التلاوة</button>
                            <button onclick="dismissPrompt()" style="background-color: #DC2626; color: white; border: none; padding: 8px 28px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px;">لا، شكراً</button>
                        </div>
                    </div>
                </div>

                <script>
                    const urls = {js_urls};
                    const ayahs = {js_ayahs};
                    let currentIndex = 0;

                    const player = document.getElementById("quran-player");
                    const statusText = document.getElementById("status-text");
                    const replayPrompt = document.getElementById("replay-prompt");

                    function playAyah(index) {{
                        if (index < urls.length) {{
                            player.src = urls[index];
                            statusText.innerText = "{player_title} جاري تلاوة الآية رقم (" + ayahs[index] + ")";
                            player.play();
                        }} else {{
                            statusText.innerText = "✅ تمت تلاوة جميع الآيات المختارة بنجاح تام.";
                            replayPrompt.style.display = "block";
                        }}
                    }}

                    player.addEventListener("ended", function() {{
                        currentIndex++;
                        playAyah(currentIndex);
                    }});

                    function restartPlayback() {{
                        currentIndex = 0;
                        replayPrompt.style.display = "none";
                        playAyah(currentIndex);
                    }}

                    function dismissPrompt() {{
                        replayPrompt.style.display = "none";
                        statusText.innerText = "✅ انتهت جلسة التلاوة بنجاح.";
                    }}

                    playAyah(currentIndex);
                </script>
                """
                components.html(html_player, height=245)
            else:
                st.info(
                    "💡 اختر آية واحدة أو أكثر من القائمة أعلاه لتشغيل مشغل التلاوة المتسلسل."
                )
