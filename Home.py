import os
import streamlit as st
import theme  # استدعاء ملف التنسيق المركزي

# إعدادات الصفحة
st.set_page_config(
    page_title="المصحف الشريف - مشروع المصحف الإلكتروني",
    page_icon="📖",
    layout="wide",
)

# تطبيق التنسيق المركزي الموحد
theme.apply_custom_theme()

# العنوان الرئيسي للتطبيق
st.markdown(
    "<h1 style='text-align: center; color: #F1C40F;'>📖 النظام التحليلي الشامل"
    " للتدبر القرآن العظيم و البحث الذكي</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #BDC3C7;'>منصة رقمية أكاديمية"
    " متقدمة لتدبر سور وآيات القرآن العظيم، والاستعراض البصري بالرسم العثماني"
    " الأصلي.</p>",
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

# إضافة زر تحميل دليل المُتدبّر على الجانب الأيسر (أو في المنتصف العلوي تحت العنوان الرئيسي)
col_space, col_dl_btn, col_right_space = st.columns([1.5, 2, 1.5])
with col_dl_btn:
    pdf_filename = "دليل_المتدبر_للقرآن_الكريم.pdf"
    if os.path.exists(pdf_filename):
        with open(pdf_filename, "rb") as f:
            pdf_data = f.read()
        st.download_button(
            label="📥 تحميل دليل المُتدبّر الشامل (PDF)",
            data=pdf_data,
            file_name="دليل_المتدبر_للقرآن_الكريم.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    else:
        st.warning("⚠️ ملف دليل المتدبر غير موجود حالياً في مجلد المشروع.")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

st.markdown(
    "<h3 style='text-align: center; color: #E67E22;'>🎯 اختر البوابة التفاعلية"
    " للبدء الفوري</h3>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #7F8C8D; font-size: 14px;'>انقر على أي"
    " زر أدناه للانتقال السريع للقسم المطلوب.</p>",
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

# تصميم بوابات الانتقال التفاعلية الثمانية في صفوف متناسقة
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("#### 📖 المصحف المصور")
    st.markdown(
        "<p style='font-size: 13px; color: #95A5A6;'>استعراض صفحات المصحف"
        " الشريف، بالرسم العثماني الدقيق لقرائته والاستماع إليه والحفظ"
        " والمراجعة.</p>",
        unsafe_allow_html=True,
    )
    if st.button("انتقل إلى المصحف المصور 👈", key="btn_quran"):
        st.switch_page("pages/1_📖_المصحف_المصور.py")

with c2:
    st.markdown("#### 🔍 نظام البحث الذكي بالكلمة أو المقطع")
    st.markdown(
        "<p style='font-size: 13px; color: #95A5A6;'>البحث الفوري في المصحف"
        " المعتقد، استقراء المجموعات، ومقاصد السور والتقارير.</p>",
        unsafe_allow_html=True,
    )
    if st.button("انتقل إلى النظام التحليلي 👈", key="btn_search"):
        st.switch_page("pages/2_📊_النظام_التحليلي.py")

with c3:
    st.markdown("#### 🔗 حصر التشابه والتناظر بين السور")
    st.markdown(
        "<p style='font-size: 13px; color: #95A5A6;'>استعراض وجوه التشابه"
        " والتناظر الموضوعي بين السور القرآنية الكريمة.</p>",
        unsafe_allow_html=True,
    )
    if st.button("انتقل إلى التناظر والموضوعات 👈", key="btn_similarity"):
        st.switch_page("pages/3_🔗_التناظر_والموضوعات.py")

with c4:
    st.markdown("#### 🌐 الربط الموضوعي")
    st.markdown(
        "<p style='font-size: 13px; color: #95A5A6;'>محرك الربط الموضوعي والمقاصدي"
        " الذكي وتوزيع الكلمات على المجموعات الثماني.</p>",
        unsafe_allow_html=True,
    )
    if st.button("انتقل إلى الربط الموضوعي 👈", key="btn_thematic"):
        st.switch_page("pages/4_🌐_الربط_الموضوعي.py")

st.markdown("<br>", unsafe_allow_html=True)

c5, c6, c7, c8 = st.columns(4)
with c5:
    st.markdown("#### 📈 الخريطة الإحصائية")
    st.markdown(
        "<p style='font-size: 13px; color: #95A5A6;'>لوحة المؤشرات التحليلية"
        " والرسوم البيانية التفاعلية لتوزيع الكلمات والمجموعات والموضوعات"
        " المحصورة.</p>",
        unsafe_allow_html=True,
    )
    if st.button("انتقل إلى الخريطة الإحصائية 👈", key="btn_stats"):
        st.switch_page("pages/5_📈_الخريطة_الإحصائية.py")

with c6:
    st.markdown("#### 🔁 الآيات المحورية المكررة")
    st.markdown(
        "<p style='font-size: 13px; color: #95A5A6;'>التحليل الفكري للآيات التي"
        " تتقاطع فيها الموضوعات المرتبطة بتسلسل المصحف.</p>",
        unsafe_allow_html=True,
    )
    if st.button("انتقل إلى الآيات المحورية 👈", key="btn_recurring"):
        st.switch_page("pages/6_🔁_الايات_المحورية.py")

with c7:
    st.markdown("#### 🔎 البحث العام الشامل")
    st.markdown(
        "<p style='font-size: 13px; color: #95A5A6;'>محرك البحث الشامل عبر كافة"
        " النصوص، والجدول، والآيات والمقاصد في قاعدة البيانات.</p>",
        unsafe_allow_html=True,
    )
    if st.button("انتقل إلى البحث الشامل 👈", key="btn_global"):
        st.switch_page("pages/7_🔎_البحث_الشامل.py")

with c8:
    st.markdown("#### 🗂️ أرشيف الحفظ والتدبر")
    st.markdown(
        "<p style='font-size: 13px; color: #95A5A6;'>لوحة متابعة وإدارة رحلتك"
        " القرانية في حفظ وتدبر الآيات الكريمة وتسجيل المراجعات.</p>",
        unsafe_allow_html=True,
    )
    if st.button("انتقل إلى أرشيف التدبر 👈", key="btn_archive"):
        st.switch_page("pages/8_🗂️_ارشيف_التدبر.py")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #F39C12; font-size: 12px;'>💡 لإرشادات"
    " الاستخدام، يمكنك أيضاً الانتقال من الإشراف في أي وقت عبر القائمة الجانبية"
    " (Sidebar) الظاهرة على اليسار.</p>",
    unsafe_allow_html=True,
)
