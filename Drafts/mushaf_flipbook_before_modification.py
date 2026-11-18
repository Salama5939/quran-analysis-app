import streamlit as st
import streamlit.components.v1 as components
from theme import apply_custom_theme

# إعداد صفحة Streamlit وتطبيق التصميم المركزي الموحد
st.set_page_config(
    page_title="المصحف المصور التفاعلي - تقليب الصفحات", page_icon="📖", layout="wide"
)

# تطبيق الثيم الموحد (إخفاء الشريط العلوي والجانبي وفرض اتجاه RTL)
apply_custom_theme()

st.title("📖 المصحف المصور التفاعلي (عرض تقليب الصفحات السحابي المباشر)")
st.markdown(
    "استعرض صفحات المصحف الشريف بتجربة تقليب ثلاثية الأبعاد سلسة بالاعتماد على صور المستودع السحابي."
)

# إضافة مسافة فاصلة (إزاحة عارض المصحف للأسفل بمسافة مريحة عن حقل الرسالة)
st.markdown("<br><br>", unsafe_allow_html=True)

# اختيار الصفحة الابتدائية للانتقال السريع
selected_page = st.number_input(
    "الانتقال إلى صفحة رقم (من 0 إلى 604):", min_value=0, max_value=604, value=1, step=1
)

# إعداد روابط مستودع GitHub عبر شبكة jsDelivr CDN
github_user = "Salama5939"
repo_name = "quran-analysis-app"
branch = "main"

pages_html_content = ""

# 1. صفحة الغلاف الفاخرة (Index 0 - صفحة مفردة)
cover_url = f"https://cdn.jsdelivr.net/gh/{github_user}/{repo_name}@{branch}/Quran-PNG-master/quran%20gold%20cover.png"
pages_html_content += f"""
    <div class="page cover-page">
        <img src="{cover_url}" alt="غلاف المصحف الشريف" loading="lazy">
    </div>
"""

# 2. صفحة البسملة (Index 1 - لتظهر وحدها على اليمين)
bismallah_url = f"https://cdn.jsdelivr.net/gh/{github_user}/{repo_name}@{branch}/Quran-PNG-master/000.png"
pages_html_content += f"""
    <div class="page bismallah-page">
        <img src="{bismallah_url}" alt="البسملة" loading="lazy">
    </div>
"""

# 3. صفحة بيضاء مرافقة للبسملة (Index 2 - لتظهر على اليسار وتجعل البسملة مستقلة تماماً)
pages_html_content += f"""
    <div class="page blank-page">
    </div>
"""

# 4. صفحات المصحف من 1 إلى 604 (تبدأ سورة الفاتحة 001.png في Index 3 على اليمين تماماً)
total_pages = 604
for i in range(1, total_pages + 1):
    file_name = f"{i:03d}.png"
    img_url = f"https://cdn.jsdelivr.net/gh/{github_user}/{repo_name}@{branch}/Quran-PNG-master/{file_name}"

    pages_html_content += f"""
        <div class="page">
            <img src="{img_url}" alt="صفحة {i}" loading="lazy">
            <div class="page-footer">{i}</div>
        </div>
    """

# كود HTML + JavaScript لعارض التقليب مع ضبط التنسيقات والأبعاد بدقة تامة
flipbook_html = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/page-flip@2.0.7/dist/js/page-flip.browser.js"></script>
    <style>
        body {{
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #FBF9F1;
            margin: 0;
            padding: 10px;
            height: 100vh;
            overflow: hidden;
        }}
        #book-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            height: 100%;
        }}
        #book {{
            box-shadow: 0 15px 40px rgba(0,0,0,0.25);
            background-color: #fdfbf7;
        }}
        .page {{
            background-color: #fdfbf7;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            box-sizing: border-box;
            border: 1px solid #e0d6c3;
            padding: 8px;
        }}
        .page img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
        }}
        .cover-page {{
            background-color: #000000 !important;
        }}
        .bismallah-page img {{
            max-height: 40%;
            object-fit: contain;
        }}
        .blank-page {{
            background-color: #fdfbf7;
        }}
        .page-footer {{
            position: absolute;
            bottom: 5px;
            width: 100%;
            text-align: center;
            font-size: 11px;
            color: #888;
            font-family: 'Amiri', serif;
        }}
    </style>
</head>
<body>

    <div id="book-container">
        <div id="book">
            {pages_html_content}
        </div>
    </div>

    <script>
        document.addEventListener("DOMContentLoaded", function () {{
            const bookElement = document.getElementById("book");

            try {{
                const pageFlip = new St.PageFlip(bookElement, {{
                    width: 450,
                    height: 680,
                    size: "stretch",
                    minWidth: 300,
                    maxWidth: 900,
                    minHeight: 400,
                    maxHeight: 1100,
                    maxShadowOpacity: 0.4,
                    showCover: true,
                    mobileScrollSupport: true,
                    direction: "rtl"
                }});

                pageFlip.loadFromHTML(document.querySelectorAll(".page"));

                // ربط الفهرس المطلوب بمؤشر العناصر الجديد بدقة
                let selectedPage = {selected_page}; 
                let targetIndex = 0;
                
                if (selectedPage === 0) {{
                    targetIndex = 1; // صفحة البسملة
                }} else {{
                    targetIndex = selectedPage + 2; // سورة الفاتحة وما بعدها
                }}

                if (targetIndex >= 0 && targetIndex < pageFlip.getPageCount()) {{
                    pageFlip.flip(targetIndex);
                }}
            }} catch (error) {{
                console.error("Error initializing CDN pageFlip:", error);
            }}
        }});
    </script>

</body>
</html>
"""

# عرض المكون داخل Streamlit بارتفاع مريح بصرياً
components.html(flipbook_html, height=780, scrolling=False)
