import os
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from supabase import Client, create_client

# ==========================================
# 1. إعدادات الصفحة والتصميم
# ==========================================
st.set_page_config(
    page_title="المصحف المصور - تلاوة وتدبر", page_icon="📖", layout="wide"
)

# إزالة تصميم المربع الكحلي الضخم، والاعتماد على التنسيق الافتراضي المتوافق مع الوضعين (Dark/Light)
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700&display=swap');
        
        body, .stApp { 
            direction: rtl; 
            text-align: right; 
            font-family: 'Cairo', sans-serif; 
        }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 2. الاتصال بقاعدة بيانات Supabase
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
    st.error("❌ خطأ: لم يتم العثور على مفاتيح الاتصال بـ Supabase.")
    st.stop()

supabase: Client = create_client(url, key)

# ==========================================
# 3. واجهة البحث والاختيار
# ==========================================
surahs = [
    "الفاتحة",
    "البقرة",
    "آل عمران",
    "النساء",
    "المائدة",
    "الأنعام",
    "الأعراف",
    "الأنفال",
    "التوبة",
    "يونس",
    "هود",
    "يوسف",
    "الرعد",
    "إبراهيم",
    "الحجر",
    "النحل",
    "الإسراء",
    "الكهف",
    "مريم",
    "طه",
    "الأنبياء",
    "الحج",
    "المؤمنون",
    "النور",
    "الفرقان",
    "الشعراء",
    "النمل",
    "القصص",
    "العنكبوت",
    "الروم",
    "لقمان",
    "السجدة",
    "الأحزاب",
    "سبأ",
    "فاطر",
    "يس",
    "الصافات",
    "ص",
    "الزمر",
    "غافر",
    "فصلت",
    "الشورى",
    "الزخرف",
    "الدخان",
    "الجاثية",
    "الأحقاف",
    "محمد",
    "الفتح",
    "الحجرات",
    "ق",
    "الذاريات",
    "الطور",
    "النجم",
    "القمر",
    "الرحمن",
    "الواقعة",
    "الحديد",
    "المجادلة",
    "الحشر",
    "الممتحنة",
    "الصف",
    "الجمعة",
    "المنافقون",
    "التغابن",
    "الطلاق",
    "التحريم",
    "الملك",
    "القلم",
    "الحاقة",
    "المعارج",
    "نوح",
    "الجن",
    "المزمل",
    "المدثر",
    "القيامة",
    "الإنسان",
    "المرسلات",
    "النبأ",
    "النازعات",
    "عبس",
    "التكوير",
    "الانفطار",
    "المطففين",
    "الانشقاق",
    "البروج",
    "الطارق",
    "الأعلى",
    "الغاشية",
    "الفجر",
    "البلد",
    "الشمس",
    "الليل",
    "الضحى",
    "الشرح",
    "التين",
    "العلق",
    "القدر",
    "البينة",
    "الزلزلة",
    "العاديات",
    "القارعة",
    "التكاثر",
    "العصر",
    "الهمزة",
    "الفيل",
    "قريش",
    "الماعون",
    "الكوثر",
    "الكافرون",
    "النصر",
    "المسد",
    "الإخلاص",
    "الفلق",
    "الناس",
]

col2, col1 = st.columns([1, 1])
with col2:
    surah_name = st.selectbox("اختر السورة:", surahs)
    surah_num = surahs.index(surah_name) + 1
with col1:
    c_start, c_end = st.columns(2)
    with c_start:
        ayah_start = st.number_input("من آية رقم:", min_value=1, value=1, step=1)
    with c_end:
        ayah_end = st.number_input("إلى آية رقم:", min_value=1, value=7, step=1)

# ==========================================
# 4. المعالجة عند الضغط على زر التشغيل
# ==========================================
if st.button("📖 عرض الآيات وتشغيل التلاوة", type="primary", use_container_width=True):
    if ayah_start > ayah_end:
        st.error("❌ خطأ: آية البداية يجب أن تكون أصغر من أو تساوي آية النهاية.")
    else:
        with st.spinner("جاري جلب الآيات والتلاوة..."):

            # --- أ. جلب النص القرآني من قاعدة البيانات ---
            response = (
                supabase.table("full_quran")
                .select("ayah_number, ayah_text")
                .eq("surah_number", surah_num)
                .gte("ayah_number", ayah_start)
                .lte("ayah_number", ayah_end)
                .order("ayah_number")
                .execute()
            )

            quran_data = response.data if response.data else []
            total_ayahs = len(quran_data)

            if total_ayahs == 0:
                st.warning("⚠️ لم يتم العثور على آيات في هذا النطاق.")
            else:
                # --- ب. استبدال المربع الضخم بشريط معلومات أنيق ومدمج ---
                st.success(
                    f"✅ **سورة {surah_name}** | عرض الآيات من ({ayah_start}) إلى ({ayah_end}) | إجمالي الآيات المستعرضة: {total_ayahs}"
                )

                # --- ج. التلميح الذكي للآيات الطويلة (يتوافق تلقائياً مع الوضع المظلم والفاتح) ---
                st.info(
                    "💡 **تلميح:** إذا كانت الآية طويلة، قم بالضغط مرتين (Double Click) على نص الآية لتوسيع الخلية وقراءتها كاملة."
                )

                # تحويل البيانات لـ DataFrame لعرضها كجدول
                df = pd.DataFrame(quran_data)
                df = df.rename(
                    columns={
                        "ayah_number": "رقم الآية",
                        "ayah_text": "منطوق الآية بالرسم العثماني",
                    }
                )

                # عرض الجدول
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "رقم الآية": st.column_config.NumberColumn(
                            "رقم الآية", width="small", format="%d"
                        ),
                        "منطوق الآية بالرسم العثماني": st.column_config.TextColumn(
                            "منطوق الآية بالرسم العثماني", width="large"
                        ),
                    },
                )

                st.markdown("<br>", unsafe_allow_html=True)

                # --- د. مشغل الصوت التلقائي أسفل الجدول ---
                audio_urls = []
                ayah_numbers = []
                surah_str = f"{surah_num:03d}"

                for item in quran_data:
                    current_ayah_num = item["ayah_number"]
                    ayah_str = f"{current_ayah_num:03d}"
                    audio_urls.append(
                        f"https://everyayah.com/data/Maher_AlMuaiqly_64kbps/{surah_str}{ayah_str}.mp3"
                    )
                    ayah_numbers.append(str(current_ayah_num))

                js_urls = str(audio_urls)
                js_ayahs = str(ayah_numbers)

                # تصميم المشغل الصوتي بلوحة تحكم داكنة ليتناسب مع جميع الأوضاع بوضوح
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
