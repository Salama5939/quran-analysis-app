import os
import streamlit as st
import theme  # استدعاء ملف التنسيق المركزي

st.set_page_config(
    page_title="النظام التحليلي الشامل للتدبر القرآني", page_icon="📖", layout="wide"
)

# تطبيق التنسيق المركزي الموحد
theme.apply_custom_theme()

# تنسيقات CSS مخصصة للبطاقات والنصوص لضمان المحاذاة اليمنى تماماً
st.markdown(
    """
    <style>
        /* ترويحة الهيدر الفاخرة (Hero Section) بألوان بيج وذهبي هادئة */
        .hero-box-light {
            background: linear-gradient(135deg, #F4E8C1 0%, #EFE5C1 100%);
            padding: 40px;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 30px;
            border: 2px solid #D4AF37;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        .hero-box-light h1 {
            color: #2C221E !important;
            font-family: 'Amiri', serif;
            font-size: 2.4rem;
        }
        .hero-box-light p {
            color: #555555 !important;
            font-size: 1.2rem;
            font-family: 'Cairo', sans-serif;
        }

        /* تنسيق بطاقات البوابات التفاعلية الفاتحة مع محاذاة النص لليمين */
        .portal-card {
            background-color: #FFFFFF;
            padding: 24px;
            border-radius: 12px;
            border: 1px solid #E2D9C2;
            border-right: 5px solid #5C765D;
            box-shadow: 0 3px 8px rgba(0,0,0,0.04);
            margin-bottom: 12px;
            min-height: 150px;
            text-align: right !important;
            direction: rtl !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .portal-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 14px rgba(92,118,93,0.15);
            border-color: #5C765D;
        }
        .portal-title {
            color: #2C221E !important;
            font-family: 'Amiri', serif;
            font-size: 1.3rem;
            font-weight: bold;
            margin-bottom: 8px;
            text-align: right !important;
        }
        .portal-desc {
            color: #666666 !important;
            font-size: 0.95rem;
            font-family: 'Cairo', sans-serif;
            text-align: right !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# --- الترحيب والواجهة الرئيسية الهادئة ---
st.markdown(
    """
    <div class="hero-box-light">
        <h1>📖 النظام التحليلي الشامل للتدبر القرآني والإضافة الذكية</h1>
        <p>
            منصة رقمية أكاديمية متقدمة لتدبر سور وآيات كلمات القرآن العظيم، والاستعراض البصري بالرسم العثماني الأصلي.
        </p>
    </div>
""",
    unsafe_allow_html=True,
)

st.markdown("---")
st.markdown(
    '<h2 style=\'text-align: center; color: #2C221E; font-family: "Amiri",'
    " serif;'>🧭 اختر البوابة التفاعلية للبدء الفوري</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #666666;'>انقر على أي زر أسفل البوابات"
    " للانتقال السريع للقسم المطلوب.</p>",
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

# --- الصفحات الست وتوزيعها التفاعلي في 3 أعمدة مطابقة لمجلد pages ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="portal-card">
            <div class="portal-title">📖 المصحف المصور</div>
            <div class="portal-desc">استعراض صفحات المصحف الشريف بالرسم العثماني المتجه بدقة عالية للتصفح البصري.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("انتقل إلى المصحف المصور 👈", key="btn_p1", use_container_width=True):
        st.switch_page("pages/1_📖_المصحف_المصور.py")

    st.markdown(
        """
        <div class="portal-card" style="margin-top: 25px;">
            <div class="portal-title">🌉 الربط الموضوعي</div>
            <div class="portal-desc">محرك الربط الموضوعي والمقاصدي الذكي وتوزيع الكلمات على المجموعات.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("انتقل إلى الربط الموضوعي 👈", key="btn_p4", use_container_width=True):
        st.switch_page("pages/4_🌉_الربط_الموضوعي.py")

with col2:
    st.markdown(
        """
        <div class="portal-card">
            <div class="portal-title">📊 النظام التحليلي</div>
            <div class="portal-desc">البحث الفوري في الحصر المعتمد، استقراء المجموعات، ومقاصد السور والتقارير.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(
        "انتقل إلى النظام التحليلي 👈", key="btn_p2", use_container_width=True
    ):
        st.switch_page("pages/2_📊_النظام_التحليلي.py")

    st.markdown(
        """
        <div class="portal-card" style="margin-top: 25px;">
            <div class="portal-title">📈 الخريطة الإحصائية</div>
            <div class="portal-desc">لوحة المؤشرات التحليلية والرسوم البيانية التفاعلية وتصدير إحصاءات المجموعات.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(
        "انتقل إلى الخريطة الإحصائية 👈", key="btn_p5", use_container_width=True
    ):
        st.switch_page("pages/5_📈_الخريطة_الإحصائية.py")

with col3:
    st.markdown(
        """
        <div class="portal-card">
            <div class="portal-title">🔗 التناظر والموضوعات</div>
            <div class="portal-desc">استعراض وجوه التشابه والتناظر الموضوعي بين الآيات والسور القرآنية الكريمة.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(
        "انتقل إلى التناظر والموضوعات 👈", key="btn_p3", use_container_width=True
    ):
        st.switch_page("pages/3_🔗_التناظر_والموضوعات.py")

    st.markdown(
        """
        <div class="portal-card" style="margin-top: 25px;">
            <div class="portal-title">🔁 الآيات المحورية المكررة</div>
            <div class="portal-desc">تحليل الآيات الكبرى التي تتقاطع فيها الموضوعات المرتبطة بتسلسل المصحف.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(
        "انتقل إلى الآيات المحورية 👈", key="btn_p6", use_container_width=True
    ):
        st.switch_page("pages/6_🔁_الآيات_المحورية_المكررة.py")

st.markdown("---")
st.info(
    "💡 **إرشاد الاستخدام:** يمكنك أيضاً التنقل بين الأقسام في أي وقت عبر القائمة"
    " الجانبية (Sidebar) الظاهرة على اليمين."
)
