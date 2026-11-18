import streamlit as st
import streamlit.components.v1 as components
from theme import apply_custom_theme

# إعداد صفحة Streamlit وتطبيق التصميم المركزي الموحد
st.set_page_config(
    page_title="المصحف المصور التفاعلي - عرض المصحف الشريف",
    page_icon="📖",
    layout="wide",
)

# تطبيق الثيم الموحد (إخفاء الشريط العلوي والجانبي وفرض اتجاه RTL)
apply_custom_theme()

st.title("📖 المصحف المصور التفاعلي (عرض تصفح المصحف المباشر)")
st.markdown(
    "استعرض صفحات المصحف الشريف بتجربة تصفح ثنائية دقيقة ومنظمة بالاعتماد على صور المستودع السحابي."
)

# إضافة مسافة فاصلة (إزاحة عارض المصحف للأسفل بمسافة مريحة عن حقل الرسالة)
st.markdown("<br><br>", unsafe_allow_html=True)

# اختيار الصفحة الابتدائية (-1 للغلاف، 0 للبسملة، ومن 1 إلى 604 للمصحف)
selected_page = st.number_input(
    "الانتقال إلى صفحة رقم (-1: الغلاف، 0: البسملة، 1-604: صفحات المصحف):",
    min_value=-1,
    max_value=604,
    value=-1,
    step=1,
)

# إعداد روابط مستودع GitHub عبر شبكة jsDelivr CDN
github_user = "Salama5939"
repo_name = "quran-analysis-app"
branch = "main"

cover_url = f"https://cdn.jsdelivr.net/gh/{github_user}/{repo_name}@{branch}/Quran-PNG-master/quran%20gold%20cover.png"
bismallah_url = f"https://cdn.jsdelivr.net/gh/{github_user}/{repo_name}@{branch}/Quran-PNG-master/000.png"


# دالة توليد عرض الثنائي أو الصفحة الفردية بدقة تامة
def get_spread_html(p):
    if p == -1:  # غلاف المصحف (صفحة مفردة متوسّطة سوداء فخمة)
        return f"""
            <div class="spread-container">
                <div class="single-page cover-page">
                    <img src="{cover_url}" alt="غلاف المصحف الشريف">
                </div>
            </div>
        """
    elif p == 0:  # صفحة البسملة (تظهر على اليمين ويقابلها فراغ على اليسار)
        return f"""
            <div class="spread-container">
                <div class="page left-page blank-page"></div>
                <div class="page right-page bismallah-page">
                    <img src="{bismallah_url}" alt="البسملة">
                    <div class="page-footer">0</div>
                </div>
            </div>
        """
    else:
        # ضمان ظهور الفردي يميناً (مثل الفاتحة 1) والزوجي يساراً (مثل البقرة 2)
        if p % 2 == 1:
            right_p = p
            left_p = p + 1 if p + 1 <= 604 else None
        else:
            right_p = p - 1
            left_p = p

        right_url = (
            f"https://cdn.jsdelivr.net/gh/{github_user}/{repo_name}@{branch}/Quran-PNG-master/{right_p:03d}.png"
            if right_p <= 604
            else ""
        )
        left_url = (
            f"https://cdn.jsdelivr.net/gh/{github_user}/{repo_name}@{branch}/Quran-PNG-master/{left_p:03d}.png"
            if left_p and left_p <= 604
            else ""
        )

        left_html = (
            f"""
            <div class="page left-page">
                <img src="{left_url}" alt="صفحة {left_p}">
                <div class="page-footer">{left_p}</div>
            </div>
        """
            if left_p
            else '<div class="page left-page blank-page"></div>'
        )

        right_html = (
            f"""
            <div class="page right-page">
                <img src="{right_url}" alt="صفحة {right_p}">
                <div class="page-footer">{right_p}</div>
            </div>
        """
            if right_p <= 604
            else '<div class="page right-page blank-page"></div>'
        )

        return f"""
            <div class="spread-container">
                {left_html}
                {right_html}
            </div>
        """


current_spread_html = get_spread_html(selected_page)

# تنسيقات HTML و CSS للعرض المباشر
viewer_html = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
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
        .spread-container {{
            display: flex;
            flex-direction: row-reverse;
            justify-content: center;
            align-items: center;
            width: 900px;
            height: 650px;
            box-shadow: 0 15px 40px rgba(0,0,0,0.25);
            background-color: #fdfbf7;
            border-radius: 4px;
            border: 1px solid #e0d6c3;
        }}
        .page, .single-page {{
            width: 50%;
            height: 100%;
            background-color: #fdfbf7;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            box-sizing: border-box;
            border-left: 1px solid #e0d6c3;
            border-right: 1px solid #e0d6c3;
            padding: 6px;
            position: relative;
        }}
        .single-page {{
            width: 100%;
            background-color: #000000 !important;
        }}
        .page img, .single-page img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
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
        .info-bar {{
            margin-top: 12px;
            font-family: 'Amiri', serif;
            font-size: 16px;
            color: #2C221E;
            background-color: #EFECE6;
            padding: 6px 20px;
            border-radius: 6px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            font-weight: bold;
        }}
    </style>
</head>
<body>

    {current_spread_html}

    <div class="info-bar">
        <span>العرض الحالي: {'غلاف المصحف' if selected_page == -1 else ('البسملة الشريفة' if selected_page == 0 else f'صفحة {selected_page}')}</span>
    </div>

</body>
</html>
"""

components.html(viewer_html, height=760, scrolling=False)
