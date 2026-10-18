import streamlit as st


def apply_custom_theme():
    """دالة مركزية لتطبيق التصميم العربي وإصلاح مشاكل الواجهة"""
    st.markdown(
        """
        <style>
            /* استيراد الخطوط */
            @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700&display=swap');
            
            /* الاتجاه العام والخطوط */
            html, body, [class*="css"] {
                font-family: 'Cairo', sans-serif;
                direction: rtl;
                text-align: right;
            }
            
            /* محاذاة النصوص داخل خانات الإدخال */
            .stTextInput input, .stSelectbox div[data-baseweb="select"], .stTextArea textarea {
                text-align: right;
            }
            
            /* خط العناوين */
            h1, h2, h3, h4 {
                font-family: 'Amiri', serif;
                font-weight: 700;
            }
            
            /* ========================================= */
            /* الكود السحري لإخفاء الأيقونات الشبحية للقائمة */
            /* ========================================= */
            [data-testid="stSidebar"][aria-expanded="false"] {
                overflow: hidden !important;
            }
            [data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarNav"] {
                display: none !important;
                opacity: 0 !important;
                visibility: hidden !important;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )
