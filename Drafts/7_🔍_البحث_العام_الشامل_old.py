import os
import pandas as pd
import streamlit as st
from supabase import Client, create_client
import theme  # استدعاء ملف التنسيق المركزي لضمان اتجاه RTL والهوية الموحدة

# إعدادات الصفحة
st.set_page_config(page_title="محرك البحث العام الشامل", page_icon="🔍", layout="wide")

# تطبيق التنسيق المركزي الموحد وإضافة زر الرئيسية
theme.apply_custom_theme()
theme.add_home_button()

st.markdown("<h1>🔍 محرك البحث العام الشامل في المنصة</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: #666666;'>ابحث بالكلمة أو العبارة في"
    " كافة نصوص القرآن الكريم وموضوعات الحصر المعتمد بضغطة زر واحدة.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# الاتصال الآمن بقاعدة بيانات Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url:
    try:
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "")
    except Exception:
        pass

if not url or not key:
    st.error("❌ خطأ: لم يتم العثور على مفاتيح الاتصال بـ Supabase.")
    st.stop()

supabase: Client = create_client(url, key)

# صندوق البحث الرئيسي
search_query = st.text_input(
    "أدخل الكلمة المراد البحث عنها في كافة محتويات المنصة:",
    placeholder="مثال: الصبر، التقوى، الجنة...",
)

if search_query:
    if len(search_query.strip()) < 2:
        st.warning("⚠️ الرجاء إدخال حرفين على الأقل للبدء في البحث.")
    else:
        with st.spinner("جاري البحث في قواعد البيانات واستخراج النتائج..."):
            # 1. البحث في جدول ارتباطات الموضوعات والحصر
            rel_resp = (
                supabase.table("ayah_group_relations")
                .select(
                    "surah_serial, surah_name, ayah_number, ayah_text,"
                    " topic_or_keyword, group_id"
                )
                .ilike("topic_or_keyword", f"%{search_query.strip()}%")
                .execute()
            )
            rel_data = rel_resp.data if rel_resp.data else []

            # 2. البحث في النص القرآني العام (full_quran أو ما يعادله حسب جدولك)
            # سنعتمد مبدئياً على نتائج جدول الارتباطات والحصر كركيزة أساسية، ويمكن توسيع الاستعلام
            df_rel = pd.DataFrame(rel_data)

            st.markdown("---")
            st.markdown(f"### 📊 نتائج البحث عن: ( {search_query} )")

            if not df_rel.empty:
                st.success(
                    f"✅ تم العثور على ({len(df_rel)}) نتيجة مطابقة في موضوعات الحصر"
                    " والآيات المرتبطة."
                )

                # عرض النتائج في جدول أنيق ومتناسق
                display_df = df_rel[
                    [
                        "surah_serial",
                        "surah_name",
                        "ayah_number",
                        "ayah_text",
                        "topic_or_keyword",
                        "group_id",
                    ]
                ].copy()
                display_df.columns = [
                    "رقم السورة",
                    "اسم السورة",
                    "رقم الآية",
                    "منطوق الآية",
                    "الكلمة / الموضوع",
                    "المجموعة",
                ]

                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info(
                    "ℹ️ لم يتم العثور على نتائج مطابقة لهذه الكلمة في جدول الحصر"
                    " والموضوعات."
                )
else:
    st.info("💡 اكتب في حقل البحث أعلاه ثم اضغط Enter أو انتظر ظهور النتائج.")
