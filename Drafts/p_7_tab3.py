import streamlit as st
import pandas as pd
from theme import apply_custom_theme, add_home_button
from database import convert_df_to_excel, supabase  # الاستيراد المركزي المعتمد

# إعدادات الصفحة التجريبية للتبويب الثالث
st.set_page_config(
    page_title="التبويب الثالث: الاستخراج التلقائي للمقاطع المشتركة", page_icon="🧩", layout="wide"
)

# تطبيق التنسيق المركزي الموحد واتجاه RTL وزر الرئيسية
apply_custom_theme()
add_home_button()

st.title("🧩 الاستخراج التلقائي للمقاطع المشتركة جزئياً داخل الآيات (التبويب الثالث)")
st.markdown(
    "<p style='text-align: center; color: #666666;'>يقوم الكود استخراجياً وبشكل تلقائي بحصر المقاطع والكلمات المتكررة في كامل المصحف الشريف (معتمدة على سجلات Supabase).</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# جلب كافة بيانات القرآن الكريم من Supabase على دفعات لتجاوز حد الـ Limit
@st.cache_data(ttl=60)
def fetch_all_full_quran():
    try:
        all_data = []
        batch_size = 1000
        start = 0
        
        while True:
            response = (
                supabase.table("full_quran")
                .select("surah_number, surah_name, ayah_number, ayah_text, page_number")
                .range(start, start + batch_size - 1)
                .execute()
            )
            batch = response.data if response.data else []
            if not batch:
                break
            all_data.extend(batch)
            if len(batch) < batch_size:
                break
            start += batch_size
            
        return pd.DataFrame(all_data) if all_data else pd.DataFrame()
    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء جلب بيانات القرآن: {e}")
        return pd.DataFrame()

with st.spinner("جاري جلب نصوص المصحف الشريف وتحليل المقاطع تلقائياً (6236 آية)..."):
    df_quran = fetch_all_full_quran()

if df_quran.empty:
    st.warning("⚠️ لا توجد بيانات متاحة في جدول full_quran حالياً.")
else:
    st.info("💡 **دليل الاستخراج التلقائي:** يتيح لك هذا التبويب تحديد طول المقطع (عدد الكلمات) ليقوم النظام آلياً باستخراج المقاطع المتكررة في المصحف الشريف.")

    # خيار تحديد عدد الكلمات في المقطع المراد استخراجه
    col_opt1, _ = st.columns([2, 2])
    with col_opt1:
        ngram_size = st.slider(
            "اختر عدد الكلمات المتتالية في المقطع المشترك:",
            min_value=2,
            max_value=5,
            value=3,
            help="مثال: اختيار 3 يعني البحث عن كل 3 كلمات متتالية تتكرر في الآيات."
        )

    @st.cache_data
    def extract_shared_snippets(df, n=3):
        records = []
        for _, row in df.iterrows():
            words = row["ayah_text"].split()
            if len(words) >= n:
                # استخراج كافة المقاطع بطول n كلمة داخل الآية الواحدة
                for i in range(len(words) - n + 1):
                    snippet = " ".join(words[i:i+n])
                    records.append({
                        "snippet": snippet,
                        "surah_number": row["surah_number"],
                        "surah_name": row["surah_name"],
                        "ayah_number": row["ayah_number"],
                        "ayah_text": row["ayah_text"],
                        "page_number": row["page_number"]
                    })
        
        if not records:
            return pd.DataFrame()
            
        snippet_df = pd.DataFrame(records)
        
        # تصفية المقاطع التي تكررت في أكثر من موضع بالمصحف
        counts = snippet_df.groupby("snippet")["ayah_text"].nunique().reset_index()
        repeated_snippets = counts[counts["ayah_text"] > 1]["snippet"]
        
        filtered_result = snippet_df[snippet_df["snippet"].isin(repeated_snippets)]
        return filtered_result.sort_values(by=["snippet", "surah_number", "ayah_number"])

    with st.spinner(f"جاري استخراج وتحليل المقاطع بطول ({ngram_size} كلمات) عبر كامل المصحف..."):
        df_snippets = extract_shared_snippets(df_quran, n=ngram_size)

    if df_snippets.empty:
        st.info("ℹ️ لم يتم العثور على مقاطع متشابهة متكررة بهذه الشروط.")
    else:
        unique_snippets_count = df_snippets["snippet"].nunique()
        total_occurrences = len(df_snippets)

        col_m1, col_m2 = st.columns(2)
        col_m1.metric("عدد المقاطع المشتركة المستخرجة", f"{unique_snippets_count} مقطع")
        col_m2.metric("إجمالي مواضع الورود في المصحف", f"{total_occurrences} موضع")

        st.markdown("---")
        st.subheader("📋 جدول الاستخراج التلقائي للمقاطع المشتركة")

        # تجهيز جدول العرض المعرب
        display_snippet_df = df_snippets[["snippet", "surah_number", "surah_name", "ayah_number", "ayah_text", "page_number"]].copy()
        display_snippet_df.columns = [
            "المقطع المشترك المستخرج",
            "رقم السورة",
            "اسم السورة",
            "رقم الآية",
            "منطوق الآية الكريمة",
            "رقم الصفحة"
        ]

        st.dataframe(display_snippet_df, use_container_width=True, hide_index=True)

        # زر التصدير إلى Excel
        excel_data_snippets = convert_df_to_excel(display_snippet_df, sheet_name="Automatic_Snippet_Analysis")
        
        col_btn, _ = st.columns([2, 5])
        with col_btn:
            st.download_button(
                label="📥 تصدير تقرير المقاطع المستخرجة تلقائياً إلى Excel",
                data=excel_data_snippets,
                file_name=f"Automatic_Snippets_{ngram_size}_words.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="dl_snippet_auto_excel",
            )