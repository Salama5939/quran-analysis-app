import streamlit as st

def apply_custom_theme():
    """دالة مركزية لتطبيق التصميم الفاتح الموحد، الخطوط الفاخرة، وتنسيق القائمة

    الجانبية، وإخفاء شريط النشر العلوي (Deploy) والشريط الجانبي بالكامل،
    وإتاحة التمرير لجميع القوائم المنسدلة في كافة صفحات التطبيق.
    """
    st.markdown(
        """
        <style>
            /* إخفاء الشريط العلوي بالكامل (زر Deploy، القائمة، والثلاث نقاط) */
            header[data-testid="stHeader"] {
                display: none !important;
            }
            
            /* إخفاء شريط التذييل (Footer) الافتراضي لـ Streamlit */
            footer {
                display: none !important;
            }

            /* إخفاء الشريط الجانبي (Sidebar) والخط الفاصل تماماً لتعمل الشاشة بكامل المساحة */
            [data-testid="stSidebar"] {
                display: none !important;
            }
            [data-testid="collapsedControl"] {
                display: none !important;
            }
            section[data-testid="stSidebarNav"] {
                display: none !important;
            }

            /* فرض ظهور شريط التمرير وارتفاع كافٍ لجميع القوائم المنبثقة والقوائم المنسدلة */
            div[data-baseweb="popover"], div[role="listbox"], ul[role="listbox"] {
                max-height: 400px !important;
                overflow-y: auto !important;
            }
            
            div[data-baseweb="menu"] {
                max-height: 400px !important;
                overflow-y: auto !important;
            }

            /* استيراد الخطوط الفاخرة */
            @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700&display=swap');
            
            /* خلفية التطبيق العامة فاتحة ومريحة للعين */
            .stApp {
                background-color: #FBF9F1 !important;
            }
            
            /* الاتجاه العام والخطوط الافتراضية للتطبيق بأكمله */
            html, body, [class*="css"] {
                font-family: 'Cairo', sans-serif;
                direction: rtl;
                text-align: right;
            }
            
            /* محاذاة النصوص داخل خانات الإدخال وقوائم الاختيار */
            .stTextInput input, .stSelectbox div[data-baseweb="select"], .stTextArea textarea {
                text-align: right;
                direction: rtl;
            }
            
            /* فرض توحيد وتوسيط عناوين الصفحات الرئيسية (h1) في كافة صفحات التطبيق بصفة قاطعة */
            h1, .stMarkdown h1 {
                font-family: 'Amiri', serif !important;
                color: #2C221E !important;
                text-align: center !important;
                font-weight: 700 !important;
                direction: rtl !important;
            }
            
            h2, h3, h4 {
                font-family: 'Amiri', serif;
                font-weight: 700;
                color: #2C221E;
                direction: rtl;
                text-align: right;
            }

            /* تنسيق وتكبير الخطوط واتجاه كافة الجداول مركزياً */
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
        </style>
    """,
        unsafe_allow_html=True,
    )


def add_home_button():
    """دالة مساعدة لإضافة زر سريع للعودة للصفحة الرئيسية في أعلى الصفحات الفرعية"""
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        if st.button("🏠 الرئيسية", width="stretch", key="global_home_btn"):
            st.switch_page("Home.py")
