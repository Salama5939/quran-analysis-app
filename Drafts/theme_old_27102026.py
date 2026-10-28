import streamlit as st


def apply_custom_theme():
    """دالة مركزية لتطبيق التصميم العربي، الخطوط، وتنسيق الجداول مركزياً"""
    st.markdown(
        """
        <style>
            /* استيراد الخطوط الفاخرة */
            @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700&display=swap');
            
            /* الاتجاه العام والخطوط الافتراضية للتطبيق بأكمله */
            html, body, [class*="css"] {
                font-family: 'Cairo', sans-serif;
                direction: rtl;
                text-align: right;
            }
            
            /* محاذاة النصوص داخل خانات الإدخال وقوائم الاختيار لتكون من اليمين */
            .stTextInput input, .stSelectbox div[data-baseweb="select"], .stTextArea textarea {
                text-align: right;
                direction: rtl;
            }
            
            /* خط العناوين الفاخر */
            h1, h2, h3, h4 {
                font-family: 'Amiri', serif;
                font-weight: 700;
            }

            /* تنسيق وتكبير الخطوط واتجاه كافة الجداول (stDataFrame / stTable) مركزياً */
            [data-testid="stDataFrame"], .stTable {
                direction: rtl !important;
                text-align: right !important;
            }
            [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th, 
            .stTable td, .stTable th {
                direction: rtl !important;
                text-align: right !important;
                font-family: 'Amiri', serif !important;
                font-size: 18px !important;
            }
            
            /* الكود السحري لإخفاء الأيقونات الشبحية للقائمة الجانبية عند طيها */
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
