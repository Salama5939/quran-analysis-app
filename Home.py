import os
import streamlit as st
import theme  # استدعاء ملف التنسيق المركزي

# إعداد الصفحة مع إبقاء القائمة الجانبية ظاهرة وثابتة
st.set_page_config(
    page_title="النظام التحليلي الشامل للتدبر القرآني",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# تطبيق التنسيق المركزي وزر الرئيسية
theme.apply_custom_theme()

# رأس الصفحة الترحيبي البصري
st.markdown(
    """
    <div style="text-align: center; padding: 20px; background-color: #F4E8C1; border-radius: 10px; border-bottom: 4px solid #2C221E; margin-bottom: 25px;">
        <h1 style="color: #2C221E; font-family: 'Amiri', serif; margin: 0;">📖 النظام التحليلي الشامل للتدبر القرآني والإضافة الذكية</h1>
        <p style="color: #5C4033; font-size: 18px; margin-top: 10px;">منصة رقمية أكاديمية متقدمة لتدبر سور وآيات كلمات القرآن العظيم، والاستعراض البصري بالرسم العثماني الأصلي.</p>
    </div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <h3 style="text-align: center; color: #2C221E; font-family: 'Cairo', sans-serif; margin-bottom: 20px;">
        🧭 اختر البوابة التفاعلية للبدء الفوري
    </h3>
    <p style="text-align: center; color: #7F8C8D; font-size: 14px; margin-top: -15px;">
        انقر على أي زر أسفل البوابات للانتقال السريع للقسم المطلوب.
    </p>
""",
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# شبكة البوابات الرئيسية (4 أعمدة × صفين لـ 8 صفحات)
# ==========================================

# الصف الأول (الأعمدة الأربعة الأولى)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        """
        <div style="background-color: #FBF9F1; padding: 15px; border-radius: 8px; border: 1px solid #E2D9C2; min-height: 160px; text-align: right;">
            <h4 style="color: #2C221E; margin-top: 0;">📖 المصحف المصور</h4>
            <p style="color: #666; font-size: 13px;">استعراض صفحات المصحف الشريف بالرسم العثماني الدقيق وبجودة عالية للتصفح البصري.</p>
        </div>
    """,
        unsafe_allow_html=True,
    )
    if st.button("انتقل إلى المصحف المصور 👈", key="nav_p1", use_container_width=True):
        st.switch_page("pages/1_📖_المصحف_المصور.py")

with col2:
    st.markdown(
        """
        <div style="background-color: #FBF9F1; padding: 15px; border-radius: 8px; border: 1px solid #E2D9C2; min-height: 160px; text-align: right;">
            <h4 style="color: #2C221E; margin-top: 0;">📊 النظام التحليلي</h4>
            <p style="color: #666; font-size: 13px;">البحث الفوري في المصحف المعتمد، استقراء المجموعات، ومقاصد السور والتقارير.</p>
        </div>
    """,
        unsafe_allow_html=True,
    )
    if st.button(
        "انتقل إلى النظام التحليلي 👈", key="nav_p2", use_container_width=True
    ):
        st.switch_page("pages/2_📊_النظام_التحليلي.py")

with col3:
    st.markdown(
        """
        <div style="background-color: #FBF9F1; padding: 15px; border-radius: 8px; border: 1px solid #E2D9C2; min-height: 160px; text-align: right;">
            <h4 style="color: #2C221E; margin-top: 0;">🔗 التناظر والموضوعات</h4>
            <p style="color: #666; font-size: 13px;">استعراض وجوه التشابه والتناظر الموضوعي بين الآيات والسور القرآنية الكريمة.</p>
        </div>
    """,
        unsafe_allow_html=True,
    )
    if st.button(
        "انتقل إلى التناظر والموضوعات 👈", key="nav_p3", use_container_width=True
    ):
        st.switch_page("pages/3_🔗_التناظر_والموضوعات.py")

with col4:
    st.markdown(
        """
        <div style="background-color: #FBF9F1; padding: 15px; border-radius: 8px; border: 1px solid #E2D9C2; min-height: 160px; text-align: right;">
            <h4 style="color: #2C221E; margin-top: 0;">📚 الربط الموضوعي</h4>
            <p style="color: #666; font-size: 13px;">محرك الربط الموضوعي والمقاصدي الذكي وتوزيع الكلمات على المجموعات.</p>
        </div>
    """,
        unsafe_allow_html=True,
    )
    if st.button("انتقل إلى الربط الموضوعي 👈", key="nav_p4", use_container_width=True):
        st.switch_page("pages/4_📚_الربط_الموضوعي.py")

st.markdown("<br>", unsafe_allow_html=True)

# الصف الثاني (الأعمدة الأربعة الأخرى)
col5, col6, col7, col8 = st.columns(4)

with col5:
    st.markdown(
        """
        <div style="background-color: #FBF9F1; padding: 15px; border-radius: 8px; border: 1px solid #E2D9C2; min-height: 160px; text-align: right;">
            <h4 style="color: #2C221E; margin-top: 0;">📈 الخريطة الإحصائية</h4>
            <p style="color: #666; font-size: 13px;">لوحة المؤشرات التحليلية والرسوم البيانية التفاعلية وتصدير إحصاءات المجموعات.</p>
        </div>
    """,
        unsafe_allow_html=True,
    )
    if st.button(
        "انتقل إلى الخريطة الإحصائية 👈", key="nav_p5", use_container_width=True
    ):
        st.switch_page("pages/5_📈_الخريطة_الإحصائية.py")

with col6:
    st.markdown(
        """
        <div style="background-color: #FBF9F1; padding: 15px; border-radius: 8px; border: 1px solid #E2D9C2; min-height: 160px; text-align: right;">
            <h4 style="color: #2C221E; margin-top: 0;">🔄 الآيات المحورية المكررة</h4>
            <p style="color: #666; font-size: 13px;">تحليل الآيات الكبرى التي تتقاطع فيها الموضوعات المرتبطة بتسلسل المصحف.</p>
        </div>
    """,
        unsafe_allow_html=True,
    )
    if st.button(
        "انتقل إلى الآيات المحورية 👈", key="nav_p6", use_container_width=True
    ):
        st.switch_page("pages/6_🔄_الآيات_المحورية_المكررة.py")

with col7:
    st.markdown(
        """
        <div style="background-color: #FBF9F1; padding: 15px; border-radius: 8px; border: 1px solid #E2D9C2; min-height: 160px; text-align: right;">
            <h4 style="color: #2C221E; margin-top: 0;">🔍 البحث العام الشامل</h4>
            <p style="color: #666; font-size: 13px;">محرك البحث الشامل عبر كافة النصوص والجداول والآيات والمقاصد في قاعدة البيانات.</p>
        </div>
    """,
        unsafe_allow_html=True,
    )
    if st.button("انتقل إلى البحث الشامل 👈", key="nav_p7", use_container_width=True):
        st.switch_page("pages/7_🔍_البحث_العام_الشامل.py")

with col8:
    st.markdown(
        """
        <div style="background-color: #FBF9F1; padding: 15px; border-radius: 8px; border: 1px solid #E2D9C2; min-height: 160px; text-align: right;">
            <h4 style="color: #2C221E; margin-top: 0;">🎯 أرشيف الحفظ والتدبر</h4>
            <p style="color: #666; font-size: 13px;">لوحة متابعة وإدارة رحلتك القرآنية في حفظ وتدبر الآيات الكريمة وتسجيل المراجعات.</p>
        </div>
    """,
        unsafe_allow_html=True,
    )
    if st.button("انتقل إلى أرشيف التدبر 👈", key="nav_p8", use_container_width=True):
        st.switch_page("pages/8_🎯_أرشيف_الحفظ_والتدبر.py")

st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(
    """
    <p style="text-align: center; color: #7F8C8D; font-size: 13px;">
        💡 <b>إرشادات الاستخدام:</b> يمكنك أيضاً الانتقال بين الأقسام في أي وقت عبر القائمة الجانبية (Sidebar) الظاهرة على اليسار.
    </p>
""",
    unsafe_allow_html=True,
)
