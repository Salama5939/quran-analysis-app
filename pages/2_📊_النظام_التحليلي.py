import os
import pandas as pd
import streamlit as st
import theme  # استدعاء ملف التنسيق المركزي
from database import (
    supabase,
    search_ayah_group_relations_stable,
    search_full_quran_stable,
    get_or_create_word_code,
    normalize_arabic,
)

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="النظام التحليلي للتدبر القرآني والبحث",
    page_icon="📊",
    layout="wide",
)

# تطبيق التنسيق المركزي وزر الرئيسية
theme.apply_custom_theme()
theme.add_home_button()

st.markdown(
    "<h1 style='text-align: center; color: #F1C40F;'>📊 النظام التحليلي والبحث الموضوعي</h1>",
    unsafe_allow_html=True,
)
st.markdown("---")


# دالة قراءة ملف تقسيم السور محلياً
@st.cache_data
def load_surah_mapping_details():
    mapping_file = "تقسيم سور القرآن حسب الجزء و الربع و المجموعة.xlsx"
    surah_details = {}
    if os.path.exists(mapping_file):
        df_map = pd.read_excel(mapping_file, sheet_name="السور_نصف_ربع_مجموعة")
        for _, row in df_map.iterrows():
            s_name = str(row["إسم السورة"]).strip()
            surah_details[s_name] = {
                "group_id": int(row["كود المجموعة"]),
                "half_code": int(row["كود النصف"]),
                "quarter_code": int(row["كود الربع "]),
            }
    return surah_details


surah_mapping_db = load_surah_mapping_details()

# التبويبات الأربعة الكاملة
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🔍 البحث والتدبر الذكي",
        "📊 البحث التحليلي والموضوعي",
        "📖 استعراض السور والمقاصد",
        "📈 تقرير الكلمات المحصورة",
    ]
)

# ==========================================
# التبويب الأول: البحث والتدبر الذكي والترحيل
# ==========================================
with tab1:
    st.subheader(
        "البحث الفوري المتكامل في الحصر المعتمد والمصحف الشامل (بالاستعلام المباشر والذكي)"
    )

    if st.session_state.get("clear_screen_flag_master", False):
        st.session_state.search_results_master = {"hsor": [], "quran": []}
        st.session_state.searched_word_master = ""
        st.session_state.search_input_table_master = ""
        st.session_state.clear_screen_flag_master = False

    search_query = st.text_input(
        "أدخل الكلمة أو العبارة بدقة (مثل: استوى، المتعال، المجيد):",
        placeholder="اكتب هنا...",
        key="search_input_table_master",
    )

    if "search_results_master" not in st.session_state:
        st.session_state.search_results_master = {"hsor": [], "quran": []}
    if "searched_word_master" not in st.session_state:
        st.session_state.searched_word_master = ""

    col_s1, _ = st.columns([1, 5])
    with col_s1:
        search_button = st.button(
            "🔍 بحث شامل", key="btn_t1_search_master", type="primary"
        )

    if search_button and search_query:
        with st.spinner("جاري البحث اللغوي المباشر وتحليل النتائج..."):
            raw_query = search_query.strip()
            st.session_state.searched_word_master = raw_query

            # استخدام الدوال المستقرة من المكتبة المركزية
            hsor_results = search_ayah_group_relations_stable(raw_query)

            for item in hsor_results:
                s_name = str(item.get("surah_name", "")).strip()
                item["_group_id"] = surah_mapping_db.get(s_name, {}).get("group_id", 1)

            hsor_results = sorted(
                hsor_results,
                key=lambda x: (
                    x.get("_group_id", 1),
                    x.get("surah_serial", 0),
                    x.get("ayah_number", 0),
                ),
            )

            quran_results = search_full_quran_stable(raw_query)

            st.session_state.search_results_master = {
                "hsor": hsor_results,
                "quran": quran_results,
            }

    res_hsor = st.session_state.search_results_master.get("hsor", [])
    res_quran = st.session_state.search_results_master.get("quran", [])
    current_word = st.session_state.searched_word_master

    if current_word:
        if res_hsor:
            st.success(
                f"✅ تم العثور على {len(res_hsor)} نتيجة مطابقة في **حصرك المعتمد** لـ: '{current_word}'"
            )
            table_data_hsor = []
            for idx, row in enumerate(res_hsor, 1):
                table_data_hsor.append(
                    {
                        "مسلسل البحث": idx,
                        "كلمة البحث": row.get("topic_or_keyword", current_word),
                        "رقم المجموعة": row.get("_group_id", 1),
                        "رقم السورة": row.get("surah_serial", 1),
                        "إسم السورة": row.get("surah_name", "-"),
                        "رقم الآية": row.get("ayah_number", 1),
                        "منطوق الآية": row.get("ayah_text", "-"),
                        "المقصد": row.get("notes", "-"),
                    }
                )
            df_hsor_view = pd.DataFrame(table_data_hsor)
            st.dataframe(
                df_hsor_view,
                width= "stretch",
                hide_index=True,
                column_config={
                    "منطوق الآية": st.column_config.TextColumn(
                        "منطوق الآية", width="large"
                    ),
                    "المقصد": st.column_config.TextColumn("المقصد", width="large"),
                    "إسم السورة": st.column_config.TextColumn(
                        "إسم السورة", width="medium"
                    ),
                },
            )
        else:
            st.info(
                f"ℹ️ لا توجد سجلات مطابقة لـ '{current_word}' في حصرك المعتمد حالياً."
            )

        st.markdown("---")

        if res_quran:
            count_hsor = len(res_hsor)
            count_quran = len(res_quran)

            st.markdown(
                f"### 🌍 نتائج المصحف الشامل لـ: '{current_word}' (إجمالي الآيات في القرآن: {count_quran})"
            )

            if count_hsor >= count_quran:
                st.success(
                    "🎉 **ممتاز!** النتائج المخزنة في حصرك المعتمد مطابقة أو تغطي بالكامل النتائج الموجودة في القرآن لهذه الكلمة."
                )
            else:
                st.warning(
                    f"⚠️ العدد المخزن في الحصر ({count_hsor}) أقل من إجمالي الوجوه في القرآن ({count_quran}). يمكنك مراجعة الجدول أدناه واختيار الآيات المراد ترحيلها."
                )

            existing_ayahs = set()
            for r in res_hsor:
                try:
                    s_ser = int(r.get("surah_serial", 0))
                    a_num = int(r.get("ayah_number", 0))
                    existing_ayahs.add((s_ser, a_num))
                except:
                    pass

            table_data_quran = []
            for idx, q in enumerate(res_quran, 1):
                s_num = int(q.get("surah_number", 0))
                a_num = int(q.get("ayah_number", 0))
                is_already_saved = (s_num, a_num) in existing_ayahs

                table_data_quran.append(
                    {
                        "اختيار للترحيل": False,
                        "مسلسل": idx,
                        "رقم السورة": s_num,
                        "إسم السورة": q.get("surah_name"),
                        "رقم الآية": a_num,
                        "منطوق الآية": q.get("ayah_text"),
                        "حالة الحفظ": (
                            "مخزن مسبقاً (مكرر)"
                            if is_already_saved
                            else "جديد غير مخزن"
                        ),
                    }
                )

            df_quran_view = pd.DataFrame(table_data_quran)

            edited_df = st.data_editor(
                df_quran_view,
                width= "stretch",
                hide_index=True,
                column_config={
                    "اختيار للترحيل": st.column_config.CheckboxColumn(
                        "هل تريد ترحيل هذه الآية؟ (نعم/لا)",
                        help="حدد مربع الاختيار للآيات التي تود إضافتها لقاعدة البيانات",
                        default=False,
                    ),
                    "منطوق الآية": st.column_config.TextColumn(
                        "منطوق الآية", width="large"
                    ),
                },
                key="editor_quran_verses_master",
            )

            if st.button("📥 تنفيذ وفحص ترحيل الآيات المحددة", type="primary"):
                migrated_count = 0
                duplicate_attempt_count = 0
                duplicate_details = []

                target_word_code = get_or_create_word_code(current_word)

                surah_objs_res = (
                    supabase.table("surah_objectives")
                    .select("surah_number, surah_objective")
                    .execute()
                )
                surah_objectives_map = {}
                if surah_objs_res.data:
                    for so in surah_objs_res.data:
                        surah_objectives_map[int(so["surah_number"])] = so[
                            "surah_objective"
                        ]

                for _, row in edited_df.iterrows():
                    if row["اختيار للترحيل"] == True:
                        s_name = row["إسم السورة"]
                        s_num = int(row["رقم السورة"])
                        a_num = int(row["رقم الآية"])
                        a_text = row["منطوق الآية"]

                        if (s_num, a_num) in existing_ayahs:
                            duplicate_attempt_count += 1
                            duplicate_details.append(f"سورة {s_name} - آية {a_num}")
                            continue

                        surah_info = surah_mapping_db.get(s_name, {})
                        default_g = surah_info.get("group_id", 1)
                        half_c = surah_info.get("half_code", 0)
                        quarter_c = surah_info.get("quarter_code", 0)

                        dynamic_note = surah_objectives_map.get(
                            s_num, "مقصد السورة غير محدد"
                        )

                        insert_data = {
                            "word_code": target_word_code,
                            "topic_or_keyword": current_word,
                            "group_id": default_g,
                            "surah_serial": s_num,
                            "surah_name": s_name,
                            "ayah_number": a_num,
                            "ayah_text": a_text,
                            "notes": dynamic_note,
                            "half_code": half_c,
                            "quarter_code": quarter_c,
                            "frequency_count": 1,
                        }
                        try:
                            supabase.table("ayah_group_relations").insert(
                                insert_data
                            ).execute()
                            migrated_count += 1
                            existing_ayahs.add((s_num, a_num))
                        except Exception as e:
                            st.error(f"خطأ أثناء ترحيل آية {a_num} سورة {s_name}: {e}")

                if migrated_count > 0:
                    st.success(
                        f"🎉 تم بنجاح ترحيل وإضافة ({migrated_count}) آية برقم مسلسل موحد (word_code = {target_word_code}) مع جلب مقصدها الحقيقي من قاعدة البيانات!"
                    )

                if duplicate_attempt_count > 0:
                    st.warning(
                        f"⚠️ تنبيه ذكي: تم استثناء وتجاهل ({duplicate_attempt_count}) آية لاختيارك ترحيلها بينما هي مسجلة مسبقاً في حصرك المعتمد وهي: {', '.join(duplicate_details)}"
                    )

                if migrated_count == 0 and duplicate_attempt_count == 0:
                    st.warning(
                        "⚠️ لم تقم بتحديد أي آية للترحيل. يرجى اختيار آية واحدة على الأقل عبر خانة الاختيار."
                    )
                else:
                    st.markdown("---")
                    if st.button(
                        "🔄 إدخال كلمة جديدة وبحث جديد (مسح الشاشة)",
                        type="primary",
                        key="btn_clear_screen_master",
                    ):
                        st.session_state.clear_screen_flag_master = True
                        st.rerun()
        else:
            st.warning(
                f"❌ لم يتم العثور على أي نتائج في المصحف الشامل لـ: '{current_word}'."
            )

# ==========================================
# التبويب الثاني: البحث التحليلي والموضوعي
# ==========================================
with tab2:
    st.subheader("البحث المتقدم في الكلمات المحصورة والمقاصد والمجموعات الثمانية")

    col_input, col_group = st.columns([3, 2])
    with col_input:
        search_input = st.text_input(
            "أدخل الكلمة أو الموضوع للبحث في التحليلات:",
            placeholder="مثال: الحمد، المتعال...",
            key="analysis_search_main",
        )
    with col_group:
        group_choice = st.selectbox(
            "تصفية حسب المجموعة الثمانية (اختياري):",
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
            key="t2_group_sel_main",
        )

    if st.button("🔍 بحث تحليلي سريع", key="btn_t2_search_main", type="primary"):
        with st.spinner("جاري جلب البيانات مباشرة عبر دالة SQL في Supabase..."):
            g_val = None
            if group_choice != "الكل":
                g_val = int(group_choice.replace("المجموعة ", ""))

            q_val = search_input.strip() if search_input else None

            response = supabase.rpc(
                "search_ayah_relations", {"search_query": q_val, "filter_group": g_val}
            ).execute()

            data = response.data if response.data else []

            if data:
                st.success(f"✅ تم العثور على ({len(data)}) سجل تحليلي مطابق.")
                st.info(
                    "💡 **تلميح للاستخدام:** يمكنك النقر المزدوج (Double Click) على أي خلايا نصية طويلة لتوسعتها."
                )

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

                df_main_t2 = pd.DataFrame(table_rows)
                st.dataframe(
                    df_main_t2,
                    width= "stretch",
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
                            "منطوق الآية", width="large"
                        ),
                        "المقصد / ملاحظات": st.column_config.TextColumn(
                            "المقصد / ملاحظات", width="large"
                        ),
                    },
                )
            else:
                st.warning("❌ لم يتم العثور على نتائج تحليلية مطابقة لشروط البحث.")

# ==========================================
# التبويب الثالث: استعراض السور والمقاصد
# ==========================================
with tab3:
    st.subheader("📖 الجدول الشامل لمقاصد السور وربطها بالمجموعات الثمانية")

    col_t3_1, col_t3_2 = st.columns([2, 2])
    with col_t3_1:
        selected_t3_group = st.selectbox(
            "تصفية السور حسب المجموعة الثمانية:",
            [
                "جميع المجموعات (114 سورة)",
                "المجموعة 1",
                "المجموعة 2",
                "المجموعة 3",
                "المجموعة 4",
                "المجموعة 5",
                "المجموعة 6",
                "المجموعة 7",
                "المجموعة 8",
            ],
            key="t3_group_filter",
        )

    with col_t3_2:
        search_surah_name = st.text_input(
            "بحث سريع عن سورة:",
            placeholder="اكتب اسم السورة...",
            key="t3_surah_search",
        )

    query_t3 = supabase.table("surah_objectives").select("*")

    if selected_t3_group != "جميع المجموعات (114 سورة)":
        g_id_val = int(selected_t3_group.replace("المجموعة ", ""))
        query_t3 = query_t3.eq("group_id", g_id_val)

    if search_surah_name.strip():
        query_t3 = query_t3.ilike("surah_name", f"%{search_surah_name.strip()}%")

    response_t3 = query_t3.order("surah_number").execute()
    surah_objs_data = response_t3.data

    if surah_objs_data:
        st.success(f"✅ تم العثور على {len(surah_objs_data)} سورة مطابقة.")
        df_surahs_view = pd.DataFrame(surah_objs_data)[
            ["surah_number", "surah_name", "group_id", "surah_objective"]
        ]
        df_surahs_view.columns = [
            "مسلسل",
            "اسم السورة",
            "المجموعة",
            "تفاصيل مقصد السورة",
        ]

        st.dataframe(
            df_surahs_view,
            width= "stretch",
            hide_index=True,
            column_config={
                "مسلسل": st.column_config.NumberColumn(
                    "مسلسل", width="small", format="%d"
                ),
                "اسم السورة": st.column_config.TextColumn("اسم السورة", width="medium"),
                "المجموعة": st.column_config.NumberColumn(
                    "المجموعة", width="small", format="%d"
                ),
                "تفاصيل مقصد السورة": st.column_config.TextColumn(
                    "تفاصيل مقصد السورة", width="large"
                ),
            },
        )
    else:
        st.warning("❌ لم يتم العثور على سور مطابقة لشروط البحث أو الفلترة.")

# ==========================================
# التبويب الرابع: تقرير الكلمات المحصورة
# ==========================================
with tab4:
    st.subheader("📈 التقرير التحليلي للكلمات المحصورة (حسب المجموعة والترتيب الأبجدي)")

    col_rep1, col_rep2 = st.columns([2, 2])
    with col_rep1:
        selected_group_filter = st.selectbox(
            "اختر المجموعة للعرض:",
            [
                "جميع المجموعات",
                "المجموعة 1",
                "المجموعة 2",
                "المجموعة 3",
                "المجموعة 4",
                "المجموعة 5",
                "المجموعة 6",
                "المجموعة 7",
                "المجموعة 8",
            ],
            key="rep_group_sel",
        )

    with col_rep2:
        st.write("")
        st.write("")
        run_report = st.button(
            "📊 عرض وتحديث التقرير المنظم", key="btn_report_filtered"
        )

    if run_report:
        with st.spinner("جاري استخراج وتحليل كافة البيانات من قاعدة البيانات..."):
            query = supabase.table("ayah_group_relations").select(
                "topic_or_keyword, group_id, frequency_count"
            )

            if selected_group_filter != "جميع المجموعات":
                g_num = int(selected_group_filter.replace("المجموعة ", ""))
                query = query.eq("group_id", g_num)

            rep_res = query.range(0, 99999).execute()
            rep_data = rep_res.data

            if rep_data:
                df_rep = pd.DataFrame(rep_data)
                df_rep["group_id"] = pd.to_numeric(
                    df_rep["group_id"], errors="coerce"
                ).fillna(1)

                def get_unique_groups(series):
                    unique_g = sorted(
                        list(set([int(x) for x in series if pd.notna(x)]))
                    )
                    return ", ".join([str(g) for g in unique_g])

                df_grouped = (
                    df_rep.groupby("topic_or_keyword")
                    .agg(
                        عدد_الآيات_المسجلة=("topic_or_keyword", "count"),
                        إجمالي_التكرارات=("frequency_count", "sum"),
                        المجموعات_المرتبطة=("group_id", get_unique_groups),
                    )
                    .reset_index()
                )

                df_grouped = df_grouped.sort_values(
                    by="topic_or_keyword", ascending=True
                )

                st.markdown("---")
                word_search_filter = st.text_input(
                    "🔍 بحث سريع عن كلمة محصورة في التقرير:",
                    placeholder="اكتب الكلمة...",
                    key="rep_word_search",
                )

                if word_search_filter.strip():
                    norm_rep_search = normalize_arabic(word_search_filter.strip())
                    df_grouped = df_grouped[
                        df_grouped["topic_or_keyword"].apply(
                            lambda x: norm_rep_search in normalize_arabic(str(x))
                        )
                    ]

                st.success(
                    f"✅ إجمالي عدد الكلمات الفريدة الناتجة في ({selected_group_filter}): **{len(df_grouped)} كلمة**"
                )
                st.dataframe(
                    df_grouped.rename(
                        columns={
                            "topic_or_keyword": "الكلمة / الموضوع",
                            "المجموعات_المرتبطة": "رقم المجموعة (المجموعات)",
                        }
                    ),
                    width= "stretch",
                    hide_index=True,
                )
            else:
                st.warning(
                    f"⚠️ لا توجد بيانات مسجلة مطابقة لـ ({selected_group_filter})."
                )
    else:
        st.info(
            "💡 اختر المجموعة من القائمة واضغط على زر **عرض وتحديث التقرير المنظم** لبدء الاستعراض الشامل."
        )
