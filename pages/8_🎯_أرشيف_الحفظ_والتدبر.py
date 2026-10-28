import os
import pandas as pd
import streamlit as st
from supabase import Client, create_client
import theme

# إعدادات الصفحة
st.set_page_config(
    page_title="أرشيف الحفظ والتدبر الشخصي", page_icon="🎯", layout="wide"
)

# تطبيق التنسيق المركزي الموحد وزر الرئيسية
theme.apply_custom_theme()
theme.add_home_button()

st.markdown("<h1>🎯 أرشيف الحفظ والتدبر الشخصي</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: #666666;'>لوحة متابعة وإدارة رحلتك"
    " القرآنية في حفظ وتدبر الآيات الكريمة.</p>",
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

# جلب البيانات من جدول الأرشيف
try:
    response = (
        supabase.table("user_memorization_archive")
        .select("*")
        .order("surah_serial", desc=False)
        .order("ayah_number", desc=False)
        .execute()
    )
    data = response.data if response.data else []
except Exception as e:
    st.error(f"حدث خطأ أثناء جلب البيانات: {e}")
    data = []

df = pd.DataFrame(data)

if not df.empty:
    # إحصائيات سريعة (KPIs) في الأعلى
    total_ayahs = len(df)
    total_surahs = df["surah_name"].nunique()

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="📖 إجمالي الآيات المحفوظة في الأرشيف", value=f"{total_ayahs} آية"
        )
    with col2:
        st.metric(
            label="📚 إجمالي السور التي أتممت حفظ آيات منها",
            value=f"{total_surahs} سورة",
        )

    st.markdown("---")
    st.subheader("📋 قائمة الآيات المسجلة في أرشيفك:")

    # عرض جدول البيانات بصورة أنيقة
    display_df = df[
        [
            "surah_serial",
            "surah_name",
            "ayah_number",
            "ayah_text",
            "memorization_status",
            "saved_at",
        ]
    ].copy()
    display_df.columns = [
        "رقم السورة",
        "اسم السورة",
        "رقم الآية",
        "منطوق الآية",
        "الحالة",
        "تاريخ الإضافة",
    ]

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # خيار لحذف آية من الأرشيف عند الحاجة
    st.markdown("---")
    with st.expander("إدارة الآيات") if hasattr(st, "expander") else st.container():
        st.subheader("🗑️ إدارة الآيات (حذف سجل):")
        selected_id = st.selectbox(
            "اختر الآية المراد إزالتها من الأرشيف (برقم التسجيل):",
            options=df["id"].tolist(),
            format_func=lambda x: (
                f"مُعرف {x}: سورة {df[df['id'] == x]['surah_name'].values[0]} - آية"
                f" {df[df['id'] == x]['ayah_number'].values[0]}"
            ),
        )
        if st.button("حذف الآية المحددة من الأرشيف"):
            try:
                supabase.table("user_memorization_archive").delete().eq(
                    "id", selected_id
                ).execute()
                st.success("✅ تم حذف الآية من الأرشيف بنجاح. يرجى تحديث الصفحة.")
                st.rerun()
            except Exception as e:
                st.error(f"خطأ أثناء الحذف: {e}")

else:
    st.info(
        "📭 أرشيف الحفظ فارغ حالياً. يمكنك البدء بإضافة الآيات من شاشات التلاوة"
        " والاستعراض."
    )
