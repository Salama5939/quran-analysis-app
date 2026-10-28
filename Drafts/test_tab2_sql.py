import os
import pandas as pd
import streamlit as st
from supabase import Client, create_client
import theme  # استدعاء ملف التنسيق المركزي

# إعدادات الصفحة التجريبية
st.set_page_config(
    page_title="اختبار استعلامات SQL المباشرة للتبويب الثاني",
    page_icon="🧪",
    layout="wide",
)

# تطبيق التنسيق المركزي لضبط اتجاه الصفحة بالكامل (RTL) والجداول
theme.apply_custom_theme()

st.markdown(
    "<h1 style='text-align: center; color: #F1C40F;'>🧪 صفحة اختبار دالة SQL"
    " للتبويب الثاني</h1>",
    unsafe_allow_html=True,
)
st.markdown("---")

# الاتصال بقاعدة بيانات Supabase
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

# واجهة البحث (حقل إدخال الكلمة في اليمين، والمجموعة في اليسار)
col_input, col_group = st.columns([3, 2])
with col_input:
    search_input = st.text_input(
        "أدخل كلمة للبحث التجريبي (مثل: الحمد، فسيروا):",
        placeholder="اكتب هنا...",
    )
with col_group:
    group_choice = st.selectbox(
        "اختر المجموعة (اختياري):",
        [
            "الكل",
            "المجموعة 1",
            "المجموعة 2",
            "المجموعة 3",
            "المجموعة 4",
            "المجموعة 5",
            "المجموعة 6",
            "المجموعة 7",
            "المجموعة 8",
        ],
    )

if st.button("🚀 اختبار استدعاء دالة SQL", type="primary"):
    with st.spinner("جاري جلب البيانات مباشرة عبر دالة SQL المخزنة في Supabase..."):

        g_val = None
        if group_choice != "الكل":
            g_val = int(group_choice.replace("المجموعة ", ""))

        q_val = search_input.strip() if search_input else None

        # استدعاء دالة الـ SQL المخزنة باستخدام rpc
        response = supabase.rpc(
            "search_ayah_relations", {"search_query": q_val, "filter_group": g_val}
        ).execute()

        data = response.data if response.data else []

        if data:
            st.success(f"✅ تم جلب ({len(data)}) سجل بنجاح وبسرعة فائقة!")

            # رسالة إرشادية للمستخدم لتوضيح خاصية التوسعة والنقر المزدوج للحقول النصية الطويلة
            st.info(
                "💡 **تلميح للاستخدام:** يمكنك النقر المزدوج (Double Click) على أي خلايا"
                " نصية طويلة مثل (منطوق الآية) أو (المقصد / ملاحظات) لتوسعتها وعرضها"
                " بالكامل لراحة التدبر والقراءة."
            )

            # تجهيز الجدول مع ترتيب الأعمدة
            table_rows = []
            for idx, row in enumerate(data, 1):
                table_rows.append(
                    {
                        "مسلسل": idx,
                        "الكلمة / الموضوع": row.get("topic_or_keyword", "-"),
                        "رقم المجموعة": row.get("group_id", 1),
                        "رقم السورة": row.get("surah_serial", 1),
                        "إسم السورة": row.get("surah_name", "-"),
                        "رقم الآية": row.get("ayah_number", 1),
                        "منطوق الآية": row.get("ayah_text", "-"),
                        "المقصد / ملاحظات": row.get("notes", "-"),
                    }
                )

            df_test = pd.DataFrame(table_rows)

            # عرض الجدول مع تخصيص العروض (تصغير المساحات الرقمية لتوفر المساحة الكبرى للنصوص)
            st.dataframe(
                df_test,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "مسلسل": st.column_config.NumberColumn(
                        "مسلسل", width="small", format="%d"
                    ),
                    "الكلمة / الموضوع": st.column_config.TextColumn(
                        "الكلمة / الموضوع", width="medium"
                    ),
                    "رقم المجموعة": st.column_config.NumberColumn(
                        "رقم المجموعة", width="small", format="%d"
                    ),
                    "رقم السورة": st.column_config.NumberColumn(
                        "رقم السورة", width="small", format="%d"
                    ),
                    "إسم السورة": st.column_config.TextColumn(
                        "إسم السورة", width="medium"
                    ),
                    "رقم الآية": st.column_config.NumberColumn(
                        "رقم الآية", width="small", format="%d"
                    ),
                    "منطوق الآية": st.column_config.TextColumn(
                        "منطوق الآية",
                        width="large",
                        help="انقر مرتين لتوسعة وعرض الآية بالكامل",
                    ),
                    "المقصد / ملاحظات": st.column_config.TextColumn(
                        "المقصد / ملاحظات",
                        width="large",
                        help="انقر مرتين لتوسعة وعرض النص بالكامل",
                    ),
                },
            )
        else:
            st.warning("⚠️ لم يتم العثور على نتائج مطابقة لشروط البحث.")
