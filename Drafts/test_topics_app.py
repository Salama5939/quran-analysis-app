import streamlit as st
from supabase import create_client

# إعداد صفحة التجربة المستقلة
st.set_page_config(page_title="تجربة فهرس المواضيع", page_icon="🧪", layout="wide")

st.title("🧪 بيئة تجربة واجهة فهرس المواضيع (Standalone Test)")
st.markdown(
    "هذه الصفحة مخصصة للاختبار والتحقق من دقة النتائج قبل دمجها في النظام الرئيسي."
)

# الاتصال بقاعدة بيانات Supabase باستخدام أسرار المشروع
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
    st.success("تم الاتصال بقاعدة بيانات Supabase بنجاح!")
except Exception as e:
    st.error(f"فشل الاتصال بقاعدة البيانات: {e}")
    st.stop()

# جلب البيانات من الـ View الذي أنشأناه
try:
    response = supabase.table("v_quran_topics_with_ayahs").select("*").execute()
    data = response.data

    if data:
        st.info(
            f"إجمالي عدد السجلات المسترجعة من جدول المواضيع المرتبط: **{len(data)}** سجل."
        )

        # فلترة سريعة للتجربة
        categories = sorted(
            list(
                set(
                    [
                        item.get("topic_category")
                        for item in data
                        if item.get("topic_category")
                    ]
                )
            )
        )
        selected_cat = st.selectbox(
            "اختر للتصفية حسب التصنيف العام:", ["الكل"] + categories
        )

        filtered_data = (
            data
            if selected_cat == "الكل"
            else [d for d in data if d.get("topic_category") == selected_cat]
        )

        st.markdown(f"### عرض النتائج ({len(filtered_data)} نتيجة):")

        for idx, row in enumerate(filtered_data, 1):
            with st.expander(
                f"{idx}. [{row.get('topic_category', 'عام')}] - {row.get('topic_sub_category', 'بدون عنوان فرعي')} (سورة {row.get('surah_name_ar')} - آية {row.get('start_ayah')})"
            ):
                st.markdown(f"**منطوق الآية:** {row.get('ayah_text')}")
                if row.get("topic_description"):
                    st.markdown(f"**الوصف أو الإيضاح:** {row.get('topic_description')}")
                st.markdown(f"**رقم الصفحة بالمصحف:** {row.get('page_number')}")
    else:
        st.warning(
            "الجدول أو الـ View لا يحتوي على بيانات حالياً. تأكد من إدخال بيانات في جدول `quran_topics` عبر لوحة تحكم Supabase."
        )

except Exception as e:
    st.error(f"حدث خطأ أثناء استعلام البيانات: {e}")
