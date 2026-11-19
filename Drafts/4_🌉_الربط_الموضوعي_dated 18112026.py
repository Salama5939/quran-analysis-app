import os
import pandas as pd
import streamlit as st
from supabase import Client, create_client
import theme  # استدعاء ملف التنسيق المركزي لضمان اتجاه RTL والقائمة يميناً
from database import convert_df_to_excel  # الاستفادة من دالة التصدير المركزية

# إعدادات الصفحة المستقلة
st.set_page_config(
    page_title="محرك الربط الموضوعي والمقاصدي الذكي", page_icon="🌉", layout="wide"
)

# تطبيق التنسيق المركزي الموحد
theme.apply_custom_theme()

# إضافة زر العودة السريع للرئيسية
theme.add_home_button()

st.markdown(
    "<h1 style='text-align: center; color: #F1C40F;'>🌉 محرك الربط الموضوعي والمقاصدي الذكي</h1>",
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
    "استعرض بطاقة الترابط الموضوعي، توزيع المجموعات، والمقاصد المرتبطة بأي كلمة مختارة فوراً بأعلى سرعة، مع إمكانية استعراض تفاصيل آيات أي مجموعة بشكل تفاعلي."
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
        # حفظ الكلمة المختارة في session_state لضمان ثباتها أثناء تفاعل القائمة السفلية
        st.session_state.active_semantic_keyword = selected_keyword

    # التحقق مما إذا كانت هناك كلمة مفعلة للعرض
    active_keyword = st.session_state.get("active_semantic_keyword", None)

    if active_keyword:
        with st.spinner("جاري جلب شبكة الترابط الموضوعي والمقاصدي من الخادم..."):

            # استدعاء دالة الـ SQL الخاصة بالربط الموضوعي عبر RPC
            response = supabase.rpc(
                "get_semantic_bridge_card", {"target_keyword": active_keyword}
            ).execute()

            bridge_data = response.data if response.data else []

            if bridge_data:
                st.success(
                    f"✅ تم بنجاح تحليل شبكة الارتباط للكلمة: **({active_keyword})**"
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

                st.info(
                    "💡 **تلميح للاستخدام:** يمكنك النقر المزدوج (Double Click) على خلية "
                    "(المقاصد / ملاحظات المرتبطة) لتوسعتها وعرضها بالكامل، أو استخدام قائمة استعراض الآيات أدناه."
                )

                # تجهيز جدول العرض للبطاقة
                bridge_rows = []
                available_groups = []
                for idx, row in enumerate(bridge_data, 1):
                    g_id = row.get("group_id", 1)
                    available_groups.append(g_id)
                    bridge_rows.append(
                        {
                            "مسلسل": idx,
                            "رقم المجموعة": g_id,
                            "عدد الآيات": row.get("total_ayahs", 0),
                            "المقاصد / ملاحظات المرتبطة": row.get("unique_notes", "-"),
                        }
                    )

                df_bridge = pd.DataFrame(bridge_rows)

                # عرض الجدول الرئيسي
                st.dataframe(
                    df_bridge,
                    width="stretch",
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

                # ==========================================================
                # الإضافة التفاعلية الجديدة: استعراض تفاصيل الآيات حسب المجموعة المختارة
                # ==========================================================
                st.markdown("---")
                st.markdown("### 🔍 الاستعراض التفصيلي لآيات المجموعة:")
                st.markdown(
                    "اختر رقم المجموعة من القائمة أدناه لعرض تفاصيل الآيات والنصوص الخاصة بها لهذه الكلمة:"
                )

                selected_group_drill = st.selectbox(
                    "🎯 اختر رقم المجموعة لاستعراض آياتها:",
                    options=available_groups,
                    format_func=lambda x: f"المجموعة رقم ({x})",
                    key="select_drill_group",
                )

                if selected_group_drill:
                    # جلب تفاصيل الآيات لهذه الكلمة وهذه المجموعة مباشرة من الجدول
                    res_ayahs = (
                        supabase.table("ayah_group_relations")
                        .select(
                            "surah_serial, surah_name, ayah_number, ayah_text, notes"
                        )
                        .eq("topic_or_keyword", active_keyword)
                        .eq("group_id", int(selected_group_drill))
                        .order("surah_serial")
                        .order("ayah_number")
                        .execute()
                    )

                    ayahs_data = res_ayahs.data if res_ayahs.data else []

                    if ayahs_data:
                        st.success(
                            f"✅ تم العثور على ({len(ayahs_data)}) آية في المجموعة ({selected_group_drill}) للكلمة ({active_keyword})."
                        )

                        drill_rows = []
                        for i, a_row in enumerate(ayahs_data, 1):
                            drill_rows.append(
                                {
                                    "مسلسل": i,
                                    "رقم السورة": a_row.get("surah_serial", "-"),
                                    "اسم السورة": a_row.get("surah_name", "-"),
                                    "رقم الآية": a_row.get("ayah_number", "-"),
                                    "منطوق الآية": a_row.get("ayah_text", "-"),
                                    "المقصد / ملاحظات": a_row.get("notes", "-"),
                                }
                            )

                        df_drill = pd.DataFrame(drill_rows)

                        st.dataframe(
                            df_drill,
                            width="stretch",
                            hide_index=True,
                            column_config={
                                "مسلسل": st.column_config.NumberColumn(
                                    "مسلسل", width="small", format="%d"
                                ),
                                "رقم السورة": st.column_config.NumberColumn(
                                    "رقم السورة", width="small", format="%d"
                                ),
                                "رقم الآية": st.column_config.NumberColumn(
                                    "رقم الآية", width="small", format="%d"
                                ),
                                "اسم السورة": st.column_config.TextColumn(
                                    "اسم السورة", width="medium"
                                ),
                                "منطوق الآية": st.column_config.TextColumn(
                                    "منطوق الآية", width="large"
                                ),
                                "المقصد / ملاحظات": st.column_config.TextColumn(
                                    "المقصد / ملاحظات", width="large"
                                ),
                            },
                        )

                        # زر تصدير آيات هذه المجموعة إلى Excel
                        excel_drill_bytes = convert_df_to_excel(
                            df_drill, sheet_name=f"مجموعة_{selected_group_drill}"
                        )
                        col_dl_d1, _ = st.columns([2, 5])
                        with col_dl_d1:
                            st.download_button(
                                label=f"📥 تصدير آيات المجموعة ({selected_group_drill}) إلى Excel",
                                data=excel_drill_bytes,
                                file_name=f"Ayahs_Group_{selected_group_drill}_{active_keyword}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                width="stretch",
                            )
                    else:
                        st.warning("⚠️ لا توجد آيات تفصيلية مسجلة لهذه المجموعة.")

            else:
                st.warning("⚠️ لم يتم العثور على بيانات ارتباط موضوعي لهذه الكلمة.")
else:
    st.warning("⚠️ عذراً، لم يتم العثور على كلمات مسجلة في قاعدة البيانات.")
