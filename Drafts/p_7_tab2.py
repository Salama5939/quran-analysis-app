import streamlit as st
import pandas as pd
from theme import apply_custom_theme, add_home_button
from database import convert_df_to_excel, supabase  # الاستيراد المركزي المعتمد

# إعدادات الصفحة التجريبية للتبويب الثاني
st.set_page_config(
    page_title="التبويب الثاني: استكشاف الآيات المتشابهات كلياً",
    page_icon="🔄",
    layout="wide",
)

# تطبيق التنسيق المركزي الموحد واتجاه RTL وزر الرئيسية
apply_custom_theme()
add_home_button()

st.title("🔄 استكشاف ومقارنة الآيات المتشابهات كلياً (التبويب الثاني)")
st.markdown(
    "<p style='text-align: center; color: #666666;'>استعراض الآيات التي تتطابق نصياً بالكامل في أكثر من موضع أو سورة في القرآن الكريم (معتمدة على كامل سجلات Supabase بدون قيود).</p>",
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


with st.spinner("جاري جلب كافة نصوص القرآن الكريم من قاعدة البيانات (6236 آية)..."):
    df_quran = fetch_all_full_quran()

if df_quran.empty:
    st.warning("⚠️ لا توجد بيانات متاحة في جدول full_quran حالياً.")
else:
    st.info(f"✅ تم بنجاح جلب وفحص إجمالي سجلات المصحف الشريف ({len(df_quran)} آية).")

    # معالجة النصوص وتحديد الآيات المتطابقة كلياً
    @st.cache_data
    def find_exact_duplicates(df):
        # تنظيف بسيط للنص (إزالة المسافات الزائدة وحركات التشكيل إن أردت مطابقة حرفية بحتة)
        df["clean_text"] = df["ayah_text"].str.strip()

        # تجميع الآيات حسب النص المتطابق (أكثر من مرة في المصحف)
        grouped = df.groupby("clean_text").filter(lambda x: len(x) > 1)
        if grouped.empty:
            return pd.DataFrame()

        # ترتيب النتائج حسب النص ثم رقم السورة ورقم الآية
        grouped = grouped.sort_values(by=["clean_text", "surah_number", "ayah_number"])
        return grouped

    df_exact = find_exact_duplicates(df_quran)

    if df_exact.empty:
        st.info("ℹ️ لم يتم العثور على آيات متطابقة نصياً بالكامل.")
    else:
        unique_texts_count = df_exact["clean_text"].nunique()
        total_matching_ayahs = len(df_exact)

        col_m1, col_m2 = st.columns(2)
        col_m1.metric("عدد النصوص المتشابهة (المجموعات)", f"{unique_texts_count} نص")
        col_m2.metric(
            "إجمالي الآيات الواقعة في التشابه الكلي", f"{total_matching_ayahs} آية"
        )

        st.markdown("---")
        st.subheader("📋 جدول تفاصيل الآيات المتشابهات كلياً في كامل المصحف")

        # تجهيز جدول العرض المعرب بالكامل
        display_exact_df = df_exact[
            ["surah_number", "surah_name", "ayah_number", "ayah_text", "page_number"]
        ].copy()
        display_exact_df.columns = [
            "رقم السورة",
            "اسم السورة",
            "رقم الآية",
            "منطوق الآية الكريمة",
            "رقم الصفحة",
        ]

        st.dataframe(display_exact_df, use_container_width=True, hide_index=True)

        # زر التصدير المركزي لملف Excel
        excel_data_exact = convert_df_to_excel(
            display_exact_df, sheet_name="Exact_Mutashabihahat"
        )

        col_btn, _ = st.columns([2, 5])
        with col_btn:
            st.download_button(
                label="📥 تصدير تقرير الآيات المتشابهات كلياً إلى Excel",
                data=excel_data_exact,
                file_name="Exact_Mutashabihahat_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="dl_exact_excel",
            )
