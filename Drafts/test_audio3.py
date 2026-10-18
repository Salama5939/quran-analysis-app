import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="اختبار التلاوة الصوتية", page_icon="🎧", layout="centered"
)

# ضبط اتجاه الصفحة ليكون من اليمين لليسار
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
        body, .stApp { direction: rtl; text-align: right; font-family: 'Cairo', sans-serif; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    "<h1 style='text-align: center; color: #27AE60;'>🎧 نظام التلاوة التلقائية (ماهر المعيقلي)</h1>",
    unsafe_allow_html=True,
)
st.markdown("---")

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
        ayah_end = st.number_input("إلى آية رقم:", min_value=1, value=1, step=1)

if st.button(
    "▶️ تشغيل الآيات متتالية (تلقائياً)", type="primary", use_container_width=True
):
    if ayah_start > ayah_end:
        st.error("❌ خطأ: يجب أن تكون آية البداية أصغر من أو تساوي آية النهاية.")
    else:
        st.success(
            f"✅ تم تجهيز سورة {surah_name} من آية {ayah_start} إلى آية {ayah_end}"
        )

        # 1. تجميع الروابط وأرقام الآيات في قوائم (Lists)
        audio_urls = []
        ayah_numbers = []
        surah_str = f"{surah_num:03d}"

        for ayah in range(ayah_start, ayah_end + 1):
            ayah_str = f"{ayah:03d}"
            audio_urls.append(
                f"https://everyayah.com/data/Maher_AlMuaiqly_64kbps/{surah_str}{ayah_str}.mp3"
            )
            ayah_numbers.append(str(ayah))

        # 2. تحويل القوائم إلى نصوص تناسب لغة JavaScript
        js_urls = str(audio_urls)
        js_ayahs = str(ayah_numbers)

        # 3. بناء واجهة مشغل مخصص (Custom HTML/JS Player) للتشغيل المتتالي
        html_player = f"""
        <div style="direction: rtl; text-align: right; font-family: 'Cairo', sans-serif; background-color: #2C3E50; padding: 15px; border-radius: 10px; color: white;">
            <h3 id="status-text" style="color: #F1C40F; margin-top: 0;">جاري التجهيز...</h3>
            <audio id="quran-player" controls autoplay style="width: 100%; border-radius: 5px; outline: none;">
                متصفحك لا يدعم تشغيل الصوت.
            </audio>
        </div>

        <script>
            // استقبال البيانات من بايثون
            const urls = {js_urls};
            const ayahs = {js_ayahs};
            let currentIndex = 0;
            
            const player = document.getElementById("quran-player");
            const statusText = document.getElementById("status-text");

            // دالة تشغيل الآية بناءً على الترتيب
            function playAyah(index) {{
                if(index < urls.length) {{
                    player.src = urls[index];
                    statusText.innerText = "🎧 جاري تلاوة الآية رقم (" + ayahs[index] + ")";
                    player.play();
                }} else {{
                    statusText.innerText = "✅ انتهت تلاوة الآيات المحددة.";
                }}
            }}

            // عند انتهاء المقطع الحالي، انتقل للمقطع التالي تلقائياً
            player.addEventListener("ended", function() {{
                currentIndex++;
                playAyah(currentIndex);
            }});

            // تشغيل أول آية فوراً
            playAyah(currentIndex);
        </script>
        """

        # عرض المشغل المخصص داخل Streamlit
        components.html(html_player, height=150)
