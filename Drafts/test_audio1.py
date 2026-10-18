import streamlit as st

st.set_page_config(
    page_title="اختبار التلاوة الصوتية", page_icon="🎧", layout="centered"
)

st.markdown(
    "<h1 style='text-align: center; color: #27AE60;'>🎧 نظام اختبار التلاوة الصوتية (ماهر المعيقلي)</h1>",
    unsafe_allow_html=True,
)
st.markdown("---")

# 1. إدخال رقم السورة ورقم الآية
col1, col2 = st.columns(2)
with col1:
    surah_num = st.number_input(
        "أدخل رقم السورة (1 إلى 114):", min_value=1, max_value=114, value=1, step=1
    )
with col2:
    ayah_num = st.number_input(
        "أدخل رقم الآية:", min_value=1, max_value=286, value=1, step=1
    )

# 2. زر التشغيل
if st.button("▶️ جلب وتشغيل الآية", type="primary", use_container_width=True):
    with st.spinner("جاري الاتصال بالخادم وجلب التلاوة..."):
        # 3. بناء الرابط بتهيئة الأرقام لتكون من 3 خانات (مثال: 1 يصبح 001)
        surah_str = f"{surah_num:03d}"
        ayah_str = f"{ayah_num:03d}"

        # رابط خادم EveryAyah للشيخ ماهر المعيقلي
        audio_url = f"https://everyayah.com/data/Maher_AlMuaiqly_64kbps/{surah_str}{ayah_str}.mp3"

        st.success(f"✅ تم جلب سورة رقم {surah_num} - آية رقم {ayah_num}")

        # 4. عرض مشغل الصوت
        st.audio(audio_url, format="audio/mp3")

        st.info("💡 ملاحظة: يتم البث المباشر من الإنترنت دون تحميل الملف على جهازك.")
