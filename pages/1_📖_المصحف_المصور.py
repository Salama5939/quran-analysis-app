import os
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from supabase import Client, create_client
import theme  # استدعاء ملف التنسيق المركزي

st.set_page_config(
    page_title="تجربة المصحف المصور والبحث المتقدم",
    page_icon="📖",
    layout="wide",
)

# تطبيق التنسيق المركزي
theme.apply_custom_theme()

# تنسيق إضافي خاص بجدول هذه الصفحة فقط (لتكبير خط الرسم العثماني)
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

supabase: Client = create_client(url, key)

# ==========================================
# 2. تحميل ملف الإكسل المساعد لصفحات السور
# ==========================================
EXCEL_FILE = "Relational TBL between Start and End Pages for each Surah.xlsx"


@st.cache_data
def load_surah_page_mapping():
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE, sheet_name=0)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    return None


df_surah_map = load_surah_page_mapping()

st.markdown(
    "<h1>🧪 شاشة تجربة المصحف المصور والبحث النصي المتقدم</h1>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ==========================================
# تقسيم الشاشة إلى تبويبين (Tab 1 & Tab 2)
# ==========================================
tab1, tab2 = st.tabs(
    [
        "📖 التبويب الأول: استعراض السورة الكاملة (SVG)",
        "🔍 التبويب الثاني: البحث واستعراض الآيات بالرسم العثماني",
    ]
)

# ------------------------------------------
# التبويب الأول: استعراض السورة الكاملة بالمصحف المصور
# ------------------------------------------
with tab1:
    st.subheader("استعراض صفحات السورة بالرسم العثماني الأصلي")

    if df_surah_map is not None:
        surah_list_t1 = df_surah_map["إسم السورة"].str.strip().tolist()
        selected_surah_t1 = st.selectbox(
            "اختر السورة الكريمة للاستعراض البصري:",
            surah_list_t1,
            key="surah_select_t1",
        )

        if st.button("تحميل وعرض السورة المختارة 🌟", key="btn_load_t1"):
            row_data = df_surah_map[
                df_surah_map["إسم السورة"].str.strip() == selected_surah_t1
            ]
            if not row_data.empty:
                start_page = int(
                    float(str(row_data["رقم صفحة البداية للسورة"].values[0]))
                )
                end_page = int(
                    float(str(row_data["رقم صفحة النهاية للسورة"].values[0]))
                )

                st.success(
                    f"✅ سورة **{selected_surah_t1}** تبدأ من الصفحة {start_page} إلى"
                    f" الصفحة {end_page}"
                )

                for p in range(start_page, end_page + 1):
                    svg_filename = f"{p:03d}.svg"
                    svg_path = os.path.join("quran_svg", svg_filename)

                    if os.path.exists(svg_path):
                        with open(svg_path, "r", encoding="utf-8") as f:
                            svg_content = f.read()

                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown(svg_content, unsafe_allow_html=True)
                    else:
                        st.warning(
                            f"⚠️ ملف الصفحة '{svg_filename}' غير موجود في المجلد."
                        )
            else:
                st.error("⚠️ لم يتم العثور على بيانات السورة في الملف المساعد.")
    else:
        st.error(f"❌ لم يتم العثور على ملف الإكسل المساعد '{EXCEL_FILE}'.")


# ------------------------------------------
# التبويب الثاني: البحث واستعراض الآيات بالرسم العثماني مع التلاوة
# ------------------------------------------
with tab2:
    st.subheader("استعراض ونطاق الآيات الكريمة بالرسم العثماني من قاعدة البيانات")

    if df_surah_map is not None:
        surah_list_t2 = df_surah_map["إسم السورة"].str.strip().tolist()

        col_a1, col_a2, col_a3 = st.columns(3)
        with col_a1:
            selected_surah_t2 = st.selectbox(
                "اختر السورة:", surah_list_t2, key="surah_select_t2"
            )
            # استخراج رقم السورة برمجياً بناءً على موقعها في القائمة (يبدأ من 0 فنضيف 1)
            surah_num = surah_list_t2.index(selected_surah_t2) + 1

        with col_a2:
            start_ayah = st.number_input(
                "من آية رقم:", min_value=1, max_value=286, value=1, key="start_ayah_t2"
            )
        with col_a3:
            end_ayah = st.number_input(
                "إلى آية رقم:", min_value=1, max_value=286, value=7, key="end_ayah_t2"
            )

        if st.button(
            "بحث واستعراض الآيات وتشغيل التلاوة 🔍", key="btn_search_t2", type="primary"
        ):
            if start_ayah > end_ayah:
                st.error(
                    "⚠️ خطأ: آية البداية يجب أن تكون أقل من أو مساوية لأية النهاية."
                )
            else:
                with st.spinner("جاري جلب الآيات والتلاوة..."):
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

                        if ayahs_data:
                            # 1. شريط العنوان الأنيق (بديل المربع الضخم)
                            st.success(
                                f"✅ **سورة {selected_surah_t2}** | عرض الآيات من ({start_ayah}) إلى ({end_ayah}) | إجمالي الآيات المستعرضة: {len(ayahs_data)}"
                            )

                            # 2. التلميح الذكي لتوسيع الآيات الطويلة
                            st.info(
                                "💡 **تلميح:** إذا كانت الآية طويلة، قم بالضغط مرتين (Double Click) على نص الآية لتوسيع الخلية وقراءتها كاملة."
                            )

                            # 3. عرض الجدول بالرسم العثماني
                            df_ayahs = pd.DataFrame(ayahs_data)
                            df_ayahs = df_ayahs[["ayah_number", "ayah_text"]]
                            df_ayahs.columns = [
                                "رقم الآية",
                                "منطوق الآية بالرسم العثماني",
                            ]

                            st.dataframe(
                                df_ayahs,
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "رقم الآية": st.column_config.NumberColumn(
                                        "رقم الآية", width="small", format="%d"
                                    ),
                                    "منطوق الآية بالرسم العثماني": (
                                        st.column_config.TextColumn(
                                            "منطوق الآية بالرسم العثماني",
                                            width="large",
                                        )
                                    ),
                                },
                            )

                            st.markdown("<br>", unsafe_allow_html=True)

                            # 4. دمج مشغل الصوت التلقائي (HTML/JS Player)
                            audio_urls = []
                            ayah_numbers = []
                            surah_str = f"{surah_num:03d}"

                            for item in ayahs_data:
                                current_ayah_num = item["ayah_number"]
                                ayah_str = f"{current_ayah_num:03d}"
                                audio_urls.append(
                                    f"https://everyayah.com/data/Maher_AlMuaiqly_64kbps/{surah_str}{ayah_str}.mp3"
                                )
                                ayah_numbers.append(str(current_ayah_num))

                            js_urls = str(audio_urls)
                            js_ayahs = str(ayah_numbers)

                            html_player = f"""
                            <div style="direction: rtl; text-align: right; font-family: 'Cairo', sans-serif; background-color: #2C3E50; padding: 15px; border-radius: 8px; border-top: 4px solid #27AE60; color: white;">
                                <h4 id="status-text" style="color: #F1C40F; margin-top: 0;">🎧 التلاوة التلقائية: جاري التجهيز...</h4>
                                <audio id="quran-player" controls autoplay style="width: 100%; border-radius: 5px; outline: none;">
                                    متصفحك لا يدعم تشغيل الصوت.
                                </audio>
                            </div>

                            <script>
                                const urls = {js_urls};
                                const ayahs = {js_ayahs};
                                let currentIndex = 0;
                                
                                const player = document.getElementById("quran-player");
                                const statusText = document.getElementById("status-text");

                                function playAyah(index) {{
                                    if(index < urls.length) {{
                                        player.src = urls[index];
                                        statusText.innerText = "🎧 جاري تلاوة الآية رقم (" + ayahs[index] + ")";
                                        player.play();
                                    }} else {{
                                        statusText.innerText = "✅ انتهت تلاوة الآيات المحددة.";
                                    }}
                                }}

                                player.addEventListener("ended", function() {{
                                    currentIndex++;
                                    playAyah(currentIndex);
                                }});

                                playAyah(currentIndex);
                            </script>
                            """
                            components.html(html_player, height=120)

                        else:
                            st.warning(
                                "⚠️ لم يتم العثور على آيات مطابقة لهذا النطاق في قاعدة البيانات."
                            )

                    except Exception as e:
                        st.error(f"حدث خطأ أثناء الاستعلام: {e}")
    else:
        st.error(f"❌ لم يتم العثور على ملف الإكسل المساعد '{EXCEL_FILE}'.")
