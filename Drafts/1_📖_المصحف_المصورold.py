import os
from datetime import datetime
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from supabase import Client, create_client
import theme  # استدعاء ملف التنسيق المركزي

st.set_page_config(
    page_title="تجربة المصحف المصور والبحث المتقدم",
    page_icon="📖",
    layout="wide",
)

# تطبيق التنسيق المركزي وزر الرئيسية
theme.apply_custom_theme()
theme.add_home_button()

# تنسيق الجداول والخطوط
st.markdown(
    """
    <style>
        [data-testid="stDataFrame"] {
            direction: rtl;
            text-align: right;
        }
        [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
            direction: rtl !important;
            text-align: right !important;
            font-family: 'Amiri', serif !important;
            font-size: 22px !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 1. الاتصال بقاعدة بيانات Supabase
# ==========================================
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url:
    try:
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "")
    except Exception:
        pass

if not url or not key:
    st.error("Supabase credentials are not configured.")
    st.stop()

supabase: Client = create_client(url, key)

# ==========================================
# 2. تحميل ملف الإكسل المساعد لصفحات السور
# ==========================================
EXCEL_FILE = "Relational TBL between Start and End Pages for each Surah.xlsx"


@st.cache_data
def load_surah_page_mapping():
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE, sheet_name=0)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    return None


df_surah_map = load_surah_page_mapping()

st.markdown(
    "<h1>🧪 شاشة تجربة المصحف المصور والبحث النصي المتقدم</h1>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ==========================================
# تقسيم الشاشة إلى تبويبين
# ==========================================
tab1, tab2 = st.tabs(
    [
        "📖 التبويب الأول: استعراض السورة الكاملة (SVG)",
        "🔍 التبويب الثاني: البحث واستعراض الآيات بالرسم العثماني",
    ]
)

# ------------------------------------------
# التبويب الأول: استعراض السورة الكاملة
# ------------------------------------------
with tab1:
    st.subheader("استعراض صفحات السورة بالرسم العثماني الأصلي")

    if df_surah_map is not None:
        surah_list_t1 = df_surah_map["إسم السورة"].str.strip().tolist()
        selected_surah_t1 = st.selectbox(
            "اختر السورة الكريمة للاستعراض البصري:",
            surah_list_t1,
            key="surah_select_t1",
        )

        if st.button("تحميل وعرض السورة المختارة 🌟", key="btn_load_t1"):
            row_data = df_surah_map[
                df_surah_map["إسم السورة"].str.strip() == selected_surah_t1
            ]
            if not row_data.empty:
                start_page = int(
                    float(str(row_data["رقم صفحة البداية للسورة"].values[0]))
                )
                end_page = int(
                    float(str(row_data["رقم صفحة النهاية للسورة"].values[0]))
                )

                st.success(
                    f"✅ سورة **{selected_surah_t1}** تبدأ من الصفحة {start_page} إلى"
                    f" الصفحة {end_page}"
                )

                for p in range(start_page, end_page + 1):
                    svg_filename = f"{p:03d}.svg"
                    svg_path = os.path.join("quran_svg", svg_filename)

                    if os.path.exists(svg_path):
                        with open(svg_path, "r", encoding="utf-8") as f:
                            svg_content = f.read()

                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown(svg_content, unsafe_allow_html=True)
                    else:
                        st.warning(
                            f"⚠️ ملف الصفحة '{svg_filename}' غير موجود في المجلد."
                        )
            else:
                st.error("⚠️ لم يتم العثور على بيانات السورة في الملف المساعد.")
    else:
        st.error(f"❌ لم يتم العثور على ملف الإكسل المساعد '{EXCEL_FILE}'.")


# ------------------------------------------
# التبويب الثاني: البحث والاستعراض (النسخة المستقرة بالجدول التفاعلي الآمن)
# ------------------------------------------
with tab2:
    st.subheader("استعراض ونطاق الآيات الكريمة بالرسم العثماني من قاعدة البيانات")

    if df_surah_map is not None:
        surah_list_t2 = df_surah_map["إسم السورة"].str.strip().tolist()

        col_a1, col_a2, col_a3 = st.columns(3)
        with col_a1:
            selected_surah_t2 = st.selectbox(
                "اختر السورة:", surah_list_t2, key="surah_select_t2"
            )
            surah_num = surah_list_t2.index(selected_surah_t2) + 1

        with col_a2:
            start_ayah = st.number_input(
                "من آية رقم:", min_value=1, max_value=286, value=1, key="start_ayah_t2"
            )
        with col_a3:
            end_ayah = st.number_input(
                "إلى آية رقم:", min_value=1, max_value=286, value=7, key="end_ayah_t2"
            )

        if st.button(
            "بحث واستعراض الآيات وتشغيل التلاوة 🔍", key="btn_search_t2", type="primary"
        ):
            if start_ayah > end_ayah:
                st.error(
                    "⚠️ خطأ: آية البداية يجب أن تكون أقل من أو مساوية لأية النهاية."
                )
            else:
                with st.spinner("جاري جلب الآيات والتحقق من الأرشيف..."):
                    try:
                        # 1. جلب الآيات من قاعدة البيانات
                        response = (
                            supabase.table("full_quran")
                            .select("ayah_number, ayah_text")
                            .eq("surah_name", selected_surah_t2)
                            .gte("ayah_number", start_ayah)
                            .lte("ayah_number", end_ayah)
                            .order("ayah_number")
                            .execute()
                        )
                        ayahs_data = response.data

                        # 2. جلب الأرشيف لنفس السورة لمعرفة المحفوظ مسبقاً
                        archive_resp = (
                            supabase.table("user_memorization_archive")
                            .select("ayah_number, review_count")
                            .eq("surah_serial", surah_num)
                            .execute()
                        )
                        archived_dict = {
                            item["ayah_number"]: item.get("review_count", 0)
                            for item in (archive_resp.data if archive_resp.data else [])
                        }

                        if ayahs_data:
                            st.success(
                                f"✅ **سورة {selected_surah_t2}** | عرض الآيات من ({start_ayah}) إلى ({end_ayah}) | إجمالي الآيات: {len(ayahs_data)}"
                            )
                            st.info(
                                "💡 **تلميح:** حدد الآيات المطلوبة بكل هدوء واستقرار من الجدول أدناه، ثم اختر العملية واضغط على زر التنفيذ."
                            )

                            st.markdown("### 📋 جدول اختيار الآيات الذكي:")

                            # تجهيز بيانات الجدول التفاعلي الآمن
                            table_rows = []
                            for item in ayahs_data:
                                a_num = item["ayah_number"]
                                a_text = item["ayah_text"]
                                is_saved = a_num in archived_dict
                                rev_cnt = archived_dict.get(a_num, 0)
                                status_label = (
                                    f"⭐ محفوظة (مراجعات: {rev_cnt})"
                                    if is_saved
                                    else "جديدة للاستزادة"
                                )

                                table_rows.append(
                                    {
                                        "تحديد": False,
                                        "رقم الآية": a_num,
                                        "منطوق الآية بالرسم العثماني": a_text,
                                        "حالة الأرشيف": status_label,
                                    }
                                )

                            df_editable = pd.DataFrame(table_rows)

                            # استخدام st.data_editor الخالي تماماً من الـ Rerun المزعج أثناء الاختيار
                            edited_df = st.data_editor(
                                df_editable,
                                use_container_width=True,
                                hide_index=True,
                                key="quran_selection_editor",
                                column_config={
                                    "تحديد": st.column_config.CheckboxColumn(
                                        "تحديد",
                                        help="حدد الآية للحفظ أو المراجعة",
                                        default=False,
                                    ),
                                    "رقم الآية": st.column_config.NumberColumn(
                                        "رقم الآية", format="%d"
                                    ),
                                    "منطوق الآية بالرسم العثماني": (
                                        st.column_config.TextColumn(
                                            "منطوق الآية بالرسم العثماني",
                                            width="large",
                                        )
                                    ),
                                    "حالة الأرشيف": st.column_config.TextColumn(
                                        "حالة الأرشيف"
                                    ),
                                },
                            )

                            st.markdown("<br>", unsafe_allow_html=True)

                            action_choice = st.radio(
                                "اختر العملية المطلوبة للآيات المحددة:",
                                [
                                    "💾 حفظ الآيات الجديدة المحددة في الأرشيف",
                                    (
                                        "🔄 تسجيل مراجعة للآيات المحددة مسبقاً"
                                        " (زيادة عداد المراجعات)"
                                    ),
                                ],
                                horizontal=True,
                                key="editor_action_radio",
                            )

                            if st.button(
                                "🚀 تنفيذ العملية المطلوبة دفعة واحدة",
                                type="primary",
                                use_container_width=True,
                                key="btn_execute_editor",
                            ):
                                # استخراج الصفوف التي تم تحديدها بـ True في الجدول
                                selected_rows = edited_df[edited_df["تحديد"] == True]

                                if selected_rows.empty:
                                    st.warning("⚠️ لم تقم بتحديد أي آية في الجدول!")
                                else:
                                    if "حفظ الآيات الجديدة" in action_choice:
                                        to_save = []
                                        for _, row in selected_rows.iterrows():
                                            a_num = int(row["رقم الآية"])
                                            if a_num not in archived_dict:
                                                original_text = next(
                                                    item["ayah_text"]
                                                    for item in ayahs_data
                                                    if item["ayah_number"] == a_num
                                                )
                                                to_save.append(
                                                    {
                                                        "surah_serial": surah_num,
                                                        "surah_name": (
                                                            selected_surah_t2
                                                        ),
                                                        "ayah_number": a_num,
                                                        "ayah_text": original_text,
                                                        "memorization_status": (
                                                            "تم الحفظ"
                                                        ),
                                                        "review_count": 0,
                                                    }
                                                )

                                        if to_save:
                                            try:
                                                supabase.table(
                                                    "user_memorization_archive"
                                                ).insert(to_save).execute()
                                                st.success(
                                                    f"✅ تم حفظ ({len(to_save)})"
                                                    " آية جديدة في أرشيفك بنجاح!"
                                                )
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"خطأ أثناء الحفظ: {e}")
                                        else:
                                            st.warning(
                                                "⚠️ الآيات المحددة مسجلة مسبقاً"
                                                " في الأرشيف بالفعل."
                                            )
                                    else:
                                        to_review = []
                                        for _, row in selected_rows.iterrows():
                                            a_num = int(row["رقم الآية"])
                                            if a_num in archived_dict:
                                                to_review.append(
                                                    {
                                                        "ayah_number": a_num,
                                                        "current_rev": archived_dict[
                                                            a_num
                                                        ],
                                                    }
                                                )

                                        if to_review:
                                            try:
                                                current_time = (
                                                    datetime.utcnow().isoformat()
                                                )
                                                for r in to_review:
                                                    new_count = r["current_rev"] + 1
                                                    supabase.table(
                                                        "user_memorization_archive"
                                                    ).update(
                                                        {
                                                            "review_count": new_count,
                                                            "last_reviewed_at": (
                                                                current_time
                                                            ),
                                                        }
                                                    ).eq(
                                                        "surah_serial",
                                                        surah_num,
                                                    ).eq(
                                                        "ayah_number",
                                                        r["ayah_number"],
                                                    ).execute()
                                                st.success(
                                                    f"✅ تم تسجيل المراجعة بنجاح"
                                                    f" لـ ({len(to_review)}) آية!"
                                                )
                                                st.rerun()
                                            except Exception as e:
                                                st.error(
                                                    f"خطأ أثناء تسجيل المراجعة:" f" {e}"
                                                )
                                        else:
                                            st.warning(
                                                "⚠️ لم تقم بتحديد أي آيات"
                                                " **محفوظة مسبقاً** لتسجيل"
                                                " المراجعة."
                                            )

                            st.markdown("<br>", unsafe_allow_html=True)

                            # 5. مشغل التلاوة التلقائية
                            audio_urls = []
                            ayah_numbers = []
                            surah_str = f"{surah_num:03d}"

                            for item in ayahs_data:
                                current_ayah_num = item["ayah_number"]
                                ayah_str = f"{current_ayah_num:03d}"
                                audio_urls.append(
                                    f"https://everyayah.com/data/Maher_AlMuaiqly_64kbps/{surah_str}{ayah_str}.mp3"
                                )
                                ayah_numbers.append(str(current_ayah_num))

                            js_urls = str(audio_urls)
                            js_ayahs = str(ayah_numbers)

                            html_player = f"""
                            <div style="direction: rtl; text-align: right; font-family: 'Cairo', sans-serif; background-color: #2C3E50; padding: 15px; border-radius: 8px; border-top: 4px solid #27AE60; color: white;">
                                <h4 id="status-text" style="color: #F1C40F; margin-top: 0;">🎧 التلاوة التلقائية: جاري التجهيز...</h4>
                                <audio id="quran-player" controls autoplay style="width: 100%; border-radius: 5px; outline: none;">
                                    متصفحك لا يدعم تشغيل الصوت.
                                </audio>
                            </div>

                            <script>
                                const urls = {js_urls};
                                const ayahs = {js_ayahs};
                                let currentIndex = 0;
                                
                                const player = document.getElementById("quran-player");
                                const statusText = document.getElementById("status-text");

                                function playAyah(index) {{
                                    if(index < urls.length) {{
                                        player.src = urls[index];
                                        statusText.innerText = "🎧 جاري تلاوة الآية رقم (" + ayahs[index] + ")";
                                        player.play();
                                    }} else {{
                                        statusText.innerText = "✅ انتهت تلاوة الآيات المحددة.";
                                    }}
                                }}

                                player.addEventListener("ended", function() {{
                                    currentIndex++;
                                    playAyah(currentIndex);
                                }});

                                playAyah(currentIndex);
                            </script>
                            """
                            components.html(html_player, height=120)

                        else:
                            st.warning("⚠️ لم يتم العثور على آيات مطابقة لهذا النطاق.")

                    except Exception as e:
                        st.error(f"حدث خطأ أثناء الاستعلام: {e}")
    else:
        st.error(f"❌ لم يتم العثور على ملف الإكسل المساعد '{EXCEL_FILE}'.")
