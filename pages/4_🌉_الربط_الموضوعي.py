import os
import pandas as pd
import streamlit as st
from supabase import Client, create_client
import theme  # استدعاء ملف التنسيق المركزي لضمان اتجاه RTL والقائمة يميناً

# إعدادات الصفحة المستقلة
st.set_page_config(
    page_title="محرك الربط الموضوعي والمقاصدي الذكي", page_icon="🌉", layout="wide"
)

# تطبيق التنسيق المركزي الموحد
theme.apply_custom_theme()

# إضافة زر العودة السريع للرئيسية
theme.add_home_button()

st.markdown(
    "<h1 style='text-align: center; color: #F1C40F;'>🌉 محرك الربط الموضوعي"
    " والمقاصدي الذكي</h1>",
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

st.markdown(
    "استعرض بطاقة الترابط الموضوعي، توزيع المجموعات، والمقاصد المرتبطة بأي كلمة"
    " مختارة فوراً بأعلى سرعة."
)


# جلب قائمة فريدة بالكلمات والموضوعات المتاحة للاختيار
@st.cache_data
def get_unique_keywords():
    res = supabase.from_("ayah_group_relations").select("topic_or_keyword").execute()
    if res.data:
        words = sorted(
            list(set(r["topic_or_keyword"] for r in res.data if r["topic_or_keyword"]))
        )
        return words
    return []


keywords_list = get_unique_keywords()

if keywords_list:
    # اختيار الكلمة المستهدفة
    selected_keyword = st.selectbox(
        "اختر الكلمة أو الموضوع للتحليل الموضوعي والمقاصدي:",
        keywords_list,
        key="semantic_word_select_page",
    )

    if st.button(
        "🔗 عرض بطاقة الربط الموضوعي الذكي",
        type="primary",
        key="btn_semantic_bridge",
    ):
        with st.spinner("جاري جلب شبكة الترابط الموضوعي والمقاصدي من الخادم..."):

            # استدعاء دالة الـ SQL الخاصة بالربط الموضوعي عبر RPC
            response = supabase.rpc(
                "get_semantic_bridge_card", {"target_keyword": selected_keyword}
            ).execute()

            bridge_data = response.data if response.data else []

            if bridge_data:
                st.success(
                    f"✅ تم بنجاح تحليل شبكة الارتباط للكلمة: **({selected_keyword})**"
                )

                # عرض ملخص الإحصائيات في بطاقات (Metrics)
                total_occurrences = sum(row["total_ayahs"] for row in bridge_data)
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.metric(
                        label="إجمالي الآيات المرتبطة بالكلمة", value=total_occurrences
                    )
                with col_m2:
                    st.metric(
                        label="عدد المجموعات الثمانية التي تظهر فيها",
                        value=len(bridge_data),
                    )

                st.markdown("---")
                st.markdown("### 📊 تفصيل التوزيع والمقاصد حسب المجموعات الثمانية:")

                # تلميح إرشادي للمستخدم للنقر المزدوج للحقول الطويلة
                st.info(
                    "💡 **تلميح للاستخدام:** يمكنك النقر المزدوج (Double Click) على خلية"
                    " (المقاصد / ملاحظات المرتبطة) لتوسعتها وعرضها بالكامل."
                )

                # تجهيز جدول العرض للبطاقة
                bridge_rows = []
                for idx, row in enumerate(bridge_data, 1):
                    bridge_rows.append(
                        {
                            "مسلسل": idx,
                            "رقم المجموعة": row.get("group_id", "-"),
                            "عدد الآيات": row.get("total_ayahs", 0),
                            "المقاصد / ملاحظات المرتبطة": row.get("unique_notes", "-"),
                        }
                    )

                df_bridge = pd.DataFrame(bridge_rows)

                # عرض الجدول مع التنسيق المتقدم للأعمدة ومحاذاة الأرقام
                st.dataframe(
                    df_bridge,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "مسلسل": st.column_config.NumberColumn(
                            "مسلسل", width="small", format="%d"
                        ),
                        "رقم المجموعة": st.column_config.NumberColumn(
                            "رقم المجموعة", width="small", format="%d"
                        ),
                        "عدد الآيات": st.column_config.NumberColumn(
                            "عدد الآيات", width="small", format="%d"
                        ),
                        "المقاصد / ملاحظات المرتبطة": st.column_config.TextColumn(
                            "المقاصد / ملاحظات المرتبطة",
                            width="large",
                            help="انقر مرتين للتوسعة والعرض الكامل",
                        ),
                    },
                )
            else:
                st.warning("⚠️ لم يتم العثور على بيانات ارتباط موضوعي لهذه الكلمة.")
else:
    st.warning("⚠️ عذراً، لم يتم العثور على كلمات مسجلة في قاعدة البيانات.")
