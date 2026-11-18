import os
from datetime import datetime
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client
import theme  # استدعاء ملف التنسيق المركزي

st.set_page_config(
    page_title="المصحف المصور والبحث التدبري المتقدم",
    page_icon="📖",
    layout="wide",
)

# تطبيق التنسيق المركزي وزر الرئيسية
theme.apply_custom_theme()
theme.add_home_button()

# تنسيق الجداول والخطوط وتصغير صندوق "No results" في الـ multiselect
st.markdown(
    """
    <style>
        [data-testid="stDataFrame"] {
            direction: rtl;
            text-align: right;
        }
        [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
            direction: rtl !important;
            text-align: right !important;
            font-family: 'Amiri', serif !important;
            font-size: 22px !important;
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

# ==========================================
# 1. الاتصال بقاعدة بيانات Supabase
# ==========================================
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url:
    try:
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "")
    except Exception:
        pass

if not url or not key:
    st.error("Supabase credentials are not configured.")
    st.stop()

supabase = create_client(url, key)


# ==========================================
# 2. تحميل بيانات السور والصفحات من Supabase
# ==========================================
@st.cache_data
def load_surah_page_mapping_from_supabase():
    try:
        response = (
            supabase.table("surah_pages").select("*").order("surah_serial").execute()
        )
        if response.data:
            return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"خطأ أثناء جلب بيانات السور من قاعدة البيانات: {e}")
    return None


df_surah_map = load_surah_page_mapping_from_supabase()

st.markdown(
    "<h1>📖 شاشة المصحف المصور والبحث التدبري المتقدم</h1>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ==========================================
# تقسيم الشاشة إلى تبويبين رئيسيين فقط
# ==========================================
tab1, tab2 = st.tabs(
    [
        "📖 التبويب الأول: المصحف التفاعلي (عرض تصفح الصفحات)",
        "🔍 التبويب الثاني: البحث، التدبر، الحفظ، والتلاوة الذكية",
    ]
)

# ------------------------------------------
# التبويب الأول: المصحف التفاعلي المزدوج (عرض تصفح الصفحات)
# ------------------------------------------
with tab1:
    st.subheader("📖 المصحف المصور التفاعلي (عرض تصفح المصحف المزدوج)")
    st.markdown(
        "استعرض صفحات المصحف الشريف بتجربة تصفح ثنائية دقيقة ومنظمة بالاعتماد على صور المستودع السحابي."
    )
    st.markdown("<br>", unsafe_allow_html=True)

    selected_page = st.number_input(
        "الانتقال إلى صفحة رقم (-1: الغلاف، 0: البسملة، 1-604: صفحات المصحف):",
        min_value=-1,
        max_value=604,
        value=-1,
        step=1,
        key="flipbook_page_input",
    )

    github_user = "Salama5939"
    repo_name = "quran-analysis-app"
    branch = "main"

    cover_url = f"https://cdn.jsdelivr.net/gh/{github_user}/{repo_name}@{branch}/Quran-PNG-master/quran%20gold%20cover.png"
    bismallah_url = f"https://cdn.jsdelivr.net/gh/{github_user}/{repo_name}@{branch}/Quran-PNG-master/000.png"

    def get_spread_html(p):
        if p == -1:
            return f"""
                <div class="spread-container">
                    <div class="single-page cover-page">
                        <img src="{cover_url}" alt="غلاف المصحف الشريف">
                    </div>
                </div>
            """
        elif p == 0:
            return f"""
                <div class="spread-container">
                    <div class="page left-page blank-page"></div>
                    <div class="page right-page bismallah-page">
                        <img src="{bismallah_url}" alt="البسملة">
                        <div class="page-footer">0</div>
                    </div>
                </div>
            """
        else:
            if p % 2 == 1:
                right_p = p
                left_p = p + 1 if p + 1 <= 604 else None
            else:
                right_p = p - 1
                left_p = p

            right_url = (
                f"https://cdn.jsdelivr.net/gh/{github_user}/{repo_name}@{branch}/Quran-PNG-master/{right_p:03d}.png"
                if right_p <= 604
                else ""
            )
            left_url = (
                f"https://cdn.jsdelivr.net/gh/{github_user}/{repo_name}@{branch}/Quran-PNG-master/{left_p:03d}.png"
                if left_p and left_p <= 604
                else ""
            )

            left_html = (
                f"""
                <div class="page left-page">
                    <img src="{left_url}" alt="صفحة {left_p}">
                    <div class="page-footer">{left_p}</div>
                </div>
            """
                if left_p
                else '<div class="page left-page blank-page"></div>'
            )

            right_html = (
                f"""
                <div class="page right-page">
                    <img src="{right_url}" alt="صفحة {right_p}">
                    <div class="page-footer">{right_p}</div>
                </div>
            """
                if right_p <= 604
                else '<div class="page right-page blank-page"></div>'
            )

            return f"""
                <div class="spread-container">
                    {left_html}
                    {right_html}
                </div>
            """

    current_spread_html = get_spread_html(selected_page)

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
                background-color: #FBF9F1;
                margin: 0;
                padding: 5px;
                height: 100vh;
                overflow: hidden;
            }}
            .spread-container {{
                display: flex;
                flex-direction: row-reverse;
                justify-content: center;
                align-items: center;
                width: 900px;
                height: 650px;
                box-shadow: 0 15px 40px rgba(0,0,0,0.25);
                background-color: #fdfbf7;
                border-radius: 4px;
                border: 1px solid #e0d6c3;
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
                background-color: #000000 !important;
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
                font-size: 11px;
                color: #888;
                font-family: 'Amiri', serif;
            }}
            .info-bar {{
                margin-top: 12px;
                font-family: 'Amiri', serif;
                font-size: 16px;
                color: #2C221E;
                background-color: #EFECE6;
                padding: 6px 20px;
                border-radius: 6px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        {current_spread_html}
        <div class="info-bar">
            <span>العرض الحالي: {'غلاف المصحف' if selected_page == -1 else ('البسملة الشريفة' if selected_page == 0 else f'صفحة {selected_page}')}</span>
        </div>
    </body>
    </html>
    """

    components.html(viewer_html, height=760, scrolling=False)


# ------------------------------------------
# التبويب الثاني: الشامل (البحث، الاستعراض، التدبر، الأرشيف، والتلاوة المشروطة)
# ------------------------------------------
with tab2:
    st.subheader("🔍 استعراض الآيات، مقاصد السورة، الأرشيف، وتكرار التلاوة للحفظ")

    if df_surah_map is not None:
        surah_list_t2 = df_surah_map["surah_name"].str.strip().tolist()

        col_a1, col_a2, col_a3 = st.columns(3)
        with col_a1:
            selected_surah_t2 = st.selectbox(
                "اختر السورة:", surah_list_t2, key="surah_select_t2"
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
                "من آية رقم:", min_value=1, max_value=286, value=1, key="start_ayah_t2"
            )
        with col_a3:
            end_ayah = st.number_input(
                "إلى آية رقم:", min_value=1, max_value=286, value=7, key="end_ayah_t2"
            )

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            search_btn = st.button(
                "بحث واستعراض الآيات والتدبر 🔍",
                key="btn_search_t2",
                type="primary",
                width="stretch",
            )
        with col_b2:
            new_request_btn = st.button(
                "🔄 طلب تلاوة جديد (إعادة ضبط الشاشة)",
                key="btn_new_request_t2",
                width="stretch",
                help="يقوم بتفريغ الذاكرة بالكامل لتلقي طلب بحث وتلاوة جديد.",
            )

        if new_request_btn:
            keys_to_clear = [
                "tab2_held_ayahs",
                "tab2_surah_name",
                "tab2_surah_num",
                "tab2_start_ayah",
                "tab2_end_ayah",
                "tab2_archived_dict",
                "tab2_objective",
                "tab2_quran_multiselect",
                "tab2_repeat_count",
            ]
            for k in keys_to_clear:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

        if search_btn:
            if start_ayah > end_ayah:
                st.error(
                    "⚠️ خطأ: آية البداية يجب أن تكون أقل من أو مساوية لأية النهاية."
                )
            else:
                with st.spinner("جاري جلب الآيات والتحقق من الأرشيف والمقاصد..."):
                    try:
                        response = (
                            supabase.table("full_quran")
                            .select("ayah_number, ayah_text")
                            .eq("surah_name", selected_surah_t2)
                            .gte("ayah_number", start_ayah)
                            .lte("ayah_number", end_ayah)
                            .order("ayah_number")
                            .execute()
                        )
                        ayahs_data = response.data

                        archive_resp = (
                            supabase.table("user_memorization_archive")
                            .select("ayah_number, review_count")
                            .eq("surah_serial", surah_num)
                            .execute()
                        )
                        archived_dict = {
                            item["ayah_number"]: item.get("review_count", 0)
                            for item in (archive_resp.data if archive_resp.data else [])
                        }

                        obj_resp = (
                            supabase.table("surah_objectives_normalized")
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

                        st.success(
                            "✅ تم تحديث وجلب بيانات النطاق بنجاح! تابع أسفل الصفحة لإكمال خيارات الحفظ والتلاوة."
                        )

                    except Exception as e:
                        st.error(f"حدث خطأ أثناء الاستعلام: {e}")

        if (
            "tab2_held_ayahs" in st.session_state
            and st.session_state["tab2_held_ayahs"]
        ):
            h_surah_name = st.session_state["tab2_surah_name"]
            h_surah_num = st.session_state["tab2_surah_num"]
            h_start = st.session_state["tab2_start_ayah"]
            h_end = st.session_state["tab2_end_ayah"]
            ayahs_data = st.session_state["tab2_held_ayahs"]
            archived_dict = st.session_state["tab2_archived_dict"]
            h_objective = st.session_state.get("tab2_objective", "")

            st.markdown("---")
            st.success(
                f"✅ **سورة {h_surah_name}** | النطاق: ({h_start}) إلى ({h_end}) | إجمالي الآيات: {len(ayahs_data)}"
            )

            if h_objective:
                st.info(f"🎯 **مقصد السورة الكريمة:** {h_objective}")

            table_rows = []
            for item in ayahs_data:
                a_num = item["ayah_number"]
                a_text = item["ayah_text"]
                is_saved = a_num in archived_dict
                rev_cnt = archived_dict.get(a_num, 0)
                status_label = (
                    f"⭐ محفوظة (مراجعات: {rev_cnt})" if is_saved else "جديدة للاستزادة"
                )
                table_rows.append(
                    {
                        "رقم الآية": a_num,
                        "منطوق الآية بالرسم العثماني": a_text,
                        "حالة الأرشيف": status_label,
                    }
                )

            st.dataframe(pd.DataFrame(table_rows), width="stretch", hide_index=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("🎯 قائمة الاختيار، إدارة الأرشيف، وتحديد التكرار الصوتي:")

            multiselect_options = []
            options_map = {}

            for item in ayahs_data:
                a_num = item["ayah_number"]
                a_text = item["ayah_text"]
                is_saved = a_num in archived_dict
                label = f"آية {a_num}: {a_text[:40]}... ({'محفوظة' if is_saved else 'جديدة'})"
                multiselect_options.append(label)
                options_map[label] = {
                    "ayah_number": a_num,
                    "ayah_text": a_text,
                    "is_saved": is_saved,
                    "rev_cnt": archived_dict.get(a_num, 0),
                }

            selected_labels = st.multiselect(
                "اختر الآيات المطلوبة من القائمة أدناه (لتفعيل التلاوة والحفظ):",
                options=multiselect_options,
                key="tab2_quran_multiselect",
            )

            col_r1, col_r2 = st.columns(2)
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
                "🚀 تنفيذ عملية الأرشيف دفعة واحدة",
                type="primary",
                width="stretch",
                key="btn_execute_tab2",
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
                                st.success(
                                    f"✅ تم حفظ ({len(to_save)}) آية جديدة في أرشيفك بنجاح!"
                                )
                                st.rerun()
                            except Exception as e:
                                st.error(f"خطأ أثناء الحفظ: {e}")
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

                                st.success(
                                    f"✅ تسجيل المراجعة بنجاح لـ ({len(to_review)}) آية!"
                                )
                                st.rerun()
                            except Exception as e:
                                st.error(f"خطأ أثناء تسجيل المراجعة: {e}")
                        else:
                            st.warning(
                                "⚠️ لم تقم بتحديد أي آيات محفوظة مسبقاً لتسجيل المراجعة."
                            )

            st.markdown("<br>", unsafe_allow_html=True)

            if selected_labels and repeat_count > 0:
                audio_urls = []
                ayah_numbers = []
                surah_str = f"{h_surah_num:03d}"

                for lbl in selected_labels:
                    info = options_map[lbl]
                    curr_num = info["ayah_number"]
                    ayah_str = f"{curr_num:03d}"
                    url_item = f"https://everyayah.com/data/Maher_AlMuaiqly_64kbps/{surah_str}{ayah_str}.mp3"
                    for _ in range(repeat_count):
                        audio_urls.append(url_item)
                        ayah_numbers.append(str(curr_num))

                js_urls = str(audio_urls)
                js_ayahs = str(ayah_numbers)
                player_title = (
                    f"🎧 مشغل التلاوة الذكي للحفظ ({repeat_count} مرات لكل آية):"
                )

                # زيادة ارتفاع الحاوية إلى 240 لضمان ظهور الزرين بوضوح تام ودون أي اقتطاع
                html_player = f"""
                <div style="direction: rtl; text-align: right; font-family: 'Cairo', sans-serif; background-color: #2C3E50; padding: 18px; border-radius: 8px; border-top: 4px solid #E74C3C; color: white;">
                    <h4 id="status-text" style="color: #F1C40F; margin-top: 0; font-size: 16px;">{player_title} جاري التجهيز...</h4>
                    <audio id="quran-player" controls autoplay style="width: 100%; border-radius: 5px; outline: none;">
                        متصفحك لا يدعم تشغيل الصوت.
                    </audio>
                    <div id="replay-prompt" style="display: none; margin-top: 15px; background-color: #34495E; padding: 12px; border-radius: 8px; text-align: center; border: 2px solid #F1C40F;">
                        <p style="margin: 0 0 10px 0; font-weight: bold; color: #ECF0F1; font-size: 15px;">هل تريد إعادة التلاوة على نفس الآيات المختارة؟</p>
                        <div style="display: flex; flex-direction: row; justify-content: center; align-items: center; gap: 20px;">
                            <button onclick="restartPlayback()" style="background-color: #27AE60; color: white; border: none; padding: 8px 28px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">نعم</button>
                            <button onclick="dismissPrompt()" style="background-color: #C0392B; color: white; border: none; padding: 8px 28px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">لا</button>
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
                        if(index < urls.length) {{
                            player.src = urls[index];
                            statusText.innerText = "{player_title} جاري تلاوة الآية رقم (" + ayahs[index] + ")";
                            player.play();
                        }} else {{
                            statusText.innerText = "✅ لقد تم تلاوة ما طلبه المستخدم بنجاح تام.";
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
                components.html(html_player, height=240)
            else:
                st.info(
                    "💡 **يرجى اختيار آية واحدة أو أكثر وتحديد عدد مرات التكرار من الحقول أعلاه لتشغيل مشغل التلاوة.**"
                )
    else:
        st.error("❌ تعذر الاتصال بجدول 'surah_pages' في قاعدة البيانات.")
