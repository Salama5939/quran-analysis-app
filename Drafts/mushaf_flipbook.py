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
    "الانتقال إلى صفحة رقم (من 0 إلى 604):بالضغط على زر الماوس الأيسر",
    min_value=0,
    max_value=604,
    value=1,
    step=1,
)

# إعداد روابط مستودع GitHub عبر شبكة jsDelivr CDN
github_user = "Salama5939"
repo_name = "quran-analysis-app"
branch = "main"

pages_html_content = ""

# 1. صفحة الغلاف الفاخرة (Index 0)
cover_url = f"https://cdn.jsdelivr.net/gh/{github_user}/{repo_name}@{branch}/Quran-PNG-master/quran%20gold%20cover.png"
pages_html_content += f"""
    <div class="page cover-page">
        <img src="{cover_url}" alt="غلاف المصحف الشريف" loading="lazy">
    </div>
"""

# 2. إعداد صفحة البسملة (Index 1 فارغة، Index 2 البسملة يميناً)
bismallah_url = f"https://cdn.jsdelivr.net/gh/{github_user}/{repo_name}@{branch}/Quran-PNG-master/000.png"
pages_html_content += f"""
    <div class="page blank-page"></div>
    <div class="page bismallah-page">
        <img src="{bismallah_url}" alt="البسملة" loading="lazy">
    </div>
"""

# 3. صفحات المصحف من 1 إلى 604 (الزوجي يسار أولاً، ثم الفردي يمين ثانياً)
total_pages = 604
for n in range(1, (total_pages // 2) + 1):
    left_page_num = 2 * n
    right_page_num = 2 * n - 1

    # صفحة اليسار
    left_file = f"{left_page_num:03d}.png"
    left_url = f"https://cdn.jsdelivr.net/gh/{github_user}/{repo_name}@{branch}/Quran-PNG-master/{left_file}"
    pages_html_content += f"""
        <div class="page">
            <img src="{left_url}" alt="صفحة {left_page_num}" loading="lazy">
            <div class="page-footer">{left_page_num}</div>
        </div>
    """

    # صفحة اليمين
    right_file = f"{right_page_num:03d}.png"
    right_url = f"https://cdn.jsdelivr.net/gh/{github_user}/{repo_name}@{branch}/Quran-PNG-master/{right_file}"
    pages_html_content += f"""
        <div class="page">
            <img src="{right_url}" alt="صفحة {right_page_num}" loading="lazy">
            <div class="page-footer">{right_page_num}</div>
        </div>
    """

# كود HTML + JavaScript لعارض التقليب مع أزرار التنقل الذكية المبرمجة بالمعادلة الرياضية
flipbook_html = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/page-flip@2.0.7/dist/js/page-flip.browser.js"></script>
    <style>
        body {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background-color: #FBF9F1;
            margin: 0;
            padding: 5px;
            height: 100vh;
            overflow: hidden;
        }}
        #book-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            height: 88%;
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
            padding: 4px;
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
            bottom: 4px;
            width: 100%;
            text-align: center;
            font-size: 11px;
            color: #888;
            font-family: 'Amiri', serif;
        }}
        /* شريط أزرار التنقل السفلي الفاخر */
        .nav-bar {{
            display: flex;
            gap: 15px;
            margin-top: 8px;
            align-items: center;
        }}
        .nav-btn {{
            background-color: #2C221E;
            color: #FBF9F1;
            border: none;
            padding: 6px 18px;
            border-radius: 6px;
            cursor: pointer;
            font-family: 'Amiri', serif;
            font-size: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: background 0.2s;
        }}
        .nav-btn:hover {{
            background-color: #4A3B32;
        }}
        #page-indicator {{
            font-family: 'Amiri', serif;
            font-size: 16px;
            color: #2C221E;
            font-weight: bold;
        }}
    </style>
</head>
<body>

    <div id="book-container">
        <div id="book">
            {pages_html_content}
        </div>
    </div>

    <div class="nav-btn-container nav-bar">
        <button class="nav-btn" id="prev-btn">◀ الصفحة السابقة</button>
        <span id="page-indicator">الصفحة: -</span>
        <button class="nav-btn" id="next-btn">الصفحة التالية ▶</button>
    </div>

    <script>
        document.addEventListener("DOMContentLoaded", function () {{
            const bookElement = document.getElementById("book");

            try {{
                const pageFlip = new St.PageFlip(bookElement, {{
                    width: 420,
                    height: 678,
                    size: "stretch",
                    minWidth: 280,
                    maxWidth: 850,
                    minHeight: 400,
                    maxHeight: 1150,
                    maxShadowOpacity: 0.4,
                    showCover: true,
                    mobileScrollSupport: true,
                    direction: "rtl"
                }});

                pageFlip.loadFromHTML(document.querySelectorAll(".page"));

                // دوال التحويل الرياضي بين صفحة القرآن وفهرس الـ DOM
                function quranPageToDOM(p) {{
                    if (p === -1) return 0; // غلاف
                    if (p === 0) return 2;  // بسملة
                    if (p % 2 === 1) return p + 3; // فردي يمين
                    return p + 1;                  // زوجي يسار
                }}

                function DOMToQuranPage(index) {{
                    if (index === 0) return -1;
                    if (index === 1 || index === 2) return 0;
                    if (index % 2 === 0) return index - 3; // زوجي DOM = يمين
                    return index - 1;                      // فردي DOM = يسار
                }}

                // الانتقال للصفحة المطلوبة من بايثون
                let targetQuranPage = {selected_page};
                let targetIndex = quranPageToDOM(targetQuranPage);
                
                if (targetIndex >= 0 && targetIndex < pageFlip.getPageCount()) {{
                    pageFlip.flip(targetIndex);
                }}

                // تحديث مؤشر رقم الصفحة المعروض
                function updateIndicator(index) {{
                    let qPage = DOMToQuranPage(index);
                    let label = qPage === -1 ? "غلاف المصحف" : (qPage === 0 ? "البسملة" : "صفحة " + qPage);
                    document.getElementById("page-indicator").innerText = label;
                }}

                updateIndicator(pageFlip.getCurrentPageIndex());

                // تفعيل أزرار التنقل الذكية بناءً على الترتيب القرآني الصحيح
                document.getElementById("next-btn").addEventListener("click", () => {{
                    let currIndex = pageFlip.getCurrentPageIndex();
                    let currQuran = DOMToQuranPage(currIndex);
                    if (currQuran < {total_pages}) {{
                        let nextQuran = currQuran === -1 ? 0 : currQuran + 1;
                        pageFlip.flip(quranPageToDOM(nextQuran));
                    }}
                }});

                document.getElementById("prev-btn").addEventListener("click", () => {{
                    let currIndex = pageFlip.getCurrentPageIndex();
                    let currQuran = DOMToQuranPage(currIndex);
                    if (currQuran > -1) {{
                        let prevQuran = currQuran === 0 ? -1 : currQuran - 1;
                        pageFlip.flip(quranPageToDOM(prevQuran));
                    }}
                }});

                pageFlip.on('flip', (e) => {{
                    updateIndicator(e.data);
                }});

            }} catch (error) {{
                console.error("Error initializing CDN pageFlip with custom nav:", error);
            }}
        }});
    </script>

</body>
</html>
"""

components.html(flipbook_html, height=830, scrolling=False)
