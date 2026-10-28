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
# 2. تحميل بيانات السور والصفحات من Supabase
# ==========================================
@st.cache_data
def load_surah_page_mapping_from_supabase():
    try:
        response = (
            supabase.table("surah_pages").select("*").order("surah_serial").execute()
        )
        if response.data:
            df = pd.DataFrame(response.data)
            return df
    except Exception as e:
        st.error(f"خطأ أثناء جلب بيانات السور من قاعدة البيانات: {e}")
    return None


df_surah_map = load_surah_page_mapping_from_supabase()

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
        surah_list_t1 = df_surah_map["surah_name"].str.strip().tolist()
        selected_surah_t1 = st.selectbox(
            "اختر السورة الكريمة للاستعراض البصري:",
            surah_list_t1,
            key="surah_select_t1",
        )

        if st.button("تحميل وعرض السورة المختارة 🌟", key="btn_load_t1"):
            row_data = df_surah_map[
                df_surah_map["surah_name"].str.strip() == selected_surah_t1
            ]
            if not row_data.empty:
                start_page = int(float(str(row_data["start_page"].values[0])))
                end_page = int(float(str(row_data["end_page"].values[0])))

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
                st.error("⚠️ لم يتم العثور على بيانات السورة في القاعدة.")
    else:
        st.error("❌ تعذر الاتصال بجدول 'surah_pages' في قاعدة البيانات.")


# ------------------------------------------
# التبويب الثاني: البحث والاستعراض مع تثبيت الذاكرة (Session State Hold)
# ------------------------------------------
with tab2:
    st.subheader("استعراض ونطاق الآيات الكريمة بالرسم العثماني من قاعدة البيانات")

    if df_surah_map is not None:
        surah_list_t2 = df_surah_map["surah_name"].str.strip().tolist()

        col_a1, col_a2, col_a3 = st.columns(3)
        with col_a1:
            selected_surah_t2 = st.selectbox(
                "اختر السورة:", surah_list_t2, key="surah_select_t2"
            )
            surah_row = df_surah_map[
                df_surah_map["surah_name"].str.strip() == selected_surah_t2
            ]
            surah_serial = (
                surah_row["surah_serial"].values[0] if not surah_row.empty else None
            )
            surah_num = (
                int(float(str(surah_serial)))
                if surah_serial is not None
                and str(surah_serial).strip().lower() not in {"nan", "<na>", "none"}
                else 1
            )

        with col_a2:
            start_ayah = st.number_input(
                "من آية رقم:", min_value=1, max_value=286, value=1, key="start_ayah_t2"
            )
        with col_a3:
            end_ayah = st.number_input(
                "إلى آية رقم:", min_value=1, max_value=286, value=7, key="end_ayah_t2"
            )

        # زر البحث لتحديث أو جلب البيانات وتثبيتها في الذاكرة الدائمة
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

                        # تثبيت النتائج في الذاكرة الدائمة (Hold State) لمنع اختفائها
                        st.session_state["held_surah_name"] = selected_surah_t2
                        st.session_state["held_surah_num"] = surah_num
                        st.session_state["held_start_ayah"] = start_ayah
                        st.session_state["held_end_ayah"] = end_ayah
                        st.session_state["held_ayahs_data"] = ayahs_data
                        st.session_state["held_archived_dict"] = archived_dict

                        # حذف مفتاح الـ multiselect بأمان لتفريغ القائمة عند البحث الجديد
                        if "stable_quran_multiselect" in st.session_state:
                            del st.session_state["stable_quran_multiselect"]

                        st.success("✅ تم تحديث وتثبيت نطاق الآيات بنجاح!")

                    except Exception as e:
                        st.error(f"حدث خطأ أثناء الاستعلام: {e}")

        # ------------------------------------------
        # عرض المحتوى المثبت في الذاكرة (Hold Region)
        # ------------------------------------------
        if (
            "held_ayahs_data" in st.session_state
            and st.session_state["held_ayahs_data"]
        ):
            h_surah_name = st.session_state["held_surah_name"]
            h_surah_num = st.session_state["held_surah_num"]
            h_start = st.session_state["held_start_ayah"]
            h_end = st.session_state["held_end_ayah"]
            ayahs_data = st.session_state["held_ayahs_data"]
            archived_dict = st.session_state["held_archived_dict"]

            st.markdown("---")
            st.success(
                f"✅ **سورة {h_surah_name}** | النطاق المثبت: من ({h_start}) إلى ({h_end}) | إجمالي الآيات: {len(ayahs_data)}"
            )
            st.info(
                "💡 **تلميح:** الشاشة مثبتة الآن في الذاكرة. حدد الآيات من القائمة أدناه بكل هدوء واستقرار، ثم اختر العملية واضغط على زر التنفيذ."
            )

            # عرض جدول الآيات
            table_rows = []
            for item in ayahs_data:
                a_num = item["ayah_number"]
                a_text = item["ayah_text"]
                is_saved = a_num in archived_dict
                rev_cnt = archived_dict.get(a_num, 0)
                status_label = (
                    f"⭐ محفوظة (مراجعات: {rev_cnt})" if is_saved else "جديدة للاستزادة"
                )
                table_rows.append(
                    {
                        "رقم الآية": a_num,
                        "منطوق الآية بالرسم العثماني": a_text,
                        "حالة الأرشيف": status_label,
                    }
                )

            st.dataframe(
                pd.DataFrame(table_rows), use_container_width=True, hide_index=True
            )

            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("🎯 قائمة الاختيار والتنفيذ الذكي (المثبتة):")

            multiselect_options = []
            options_map = {}

            for item in ayahs_data:
                a_num = item["ayah_number"]
                a_text = item["ayah_text"]
                is_saved = a_num in archived_dict
                label = f"آية {a_num}: {a_text[:40]}... ({'محفوظة' if is_saved else 'جديدة'})"
                multiselect_options.append(label)
                options_map[label] = {
                    "ayah_number": a_num,
                    "ayah_text": a_text,
                    "is_saved": is_saved,
                    "rev_cnt": archived_dict.get(a_num, 0),
                }

            selected_labels = st.multiselect(
                "اختر الآيات المطلوبة من القائمة أدناه:",
                options=multiselect_options,
                key="stable_quran_multiselect",
            )

            st.markdown("<br>", unsafe_allow_html=True)

            action_choice = st.radio(
                "اختر العملية المطلوبة للآيات المحددة:",
                [
                    "💾 حفظ الآيات الجديدة المحددة في الأرشيف",
                    "🔄 تسجيل مراجعة للآيات المحددة مسبقاً (زيادة عداد المراجعات)",
                ],
                horizontal=True,
                key="stable_action_radio",
            )

            if st.button(
                "🚀 تنفيذ العملية المطلوبة دفعة واحدة",
                type="primary",
                use_container_width=True,
                key="btn_execute_stable",
            ):
                if not selected_labels:
                    st.warning("⚠️ لم تقم بتحديد أي آية من القائمة!")
                else:
                    if "حفظ الآيات الجديدة" in action_choice:
                        to_save = []
                        for lbl in selected_labels:
                            info = options_map[lbl]
                            if not info["is_saved"]:
                                to_save.append(
                                    {
                                        "surah_serial": h_surah_num,
                                        "surah_name": h_surah_name,
                                        "ayah_number": info["ayah_number"],
                                        "ayah_text": info["ayah_text"],
                                        "memorization_status": "تم الحفظ",
                                        "review_count": 0,
                                    }
                                )

                        if to_save:
                            try:
                                supabase.table("user_memorization_archive").insert(
                                    to_save
                                ).execute()

                                # حذف المفتاح بأمان لإفراغ القائمة بعد الحفظ الناجح
                                if "stable_quran_multiselect" in st.session_state:
                                    del st.session_state["stable_quran_multiselect"]

                                st.success(
                                    f"✅ تم حفظ ({len(to_save)}) آية جديدة في أرشيفك بنجاح!"
                                )
                                st.rerun()
                            except Exception as e:
                                st.error(f"خطأ أثناء الحفظ: {e}")
                        else:
                            st.warning(
                                "⚠️ جميع الآيات المحددة مسجلة مسبقاً في الأرشيف بالفعل."
                            )
                    else:
                        to_review = []
                        for lbl in selected_labels:
                            info = options_map[lbl]
                            if info["is_saved"]:
                                to_review.append(
                                    {
                                        "ayah_number": info["ayah_number"],
                                        "current_rev": info["rev_cnt"],
                                    }
                                )

                        if to_review:
                            try:
                                current_time = datetime.utcnow().isoformat()
                                for r in to_review:
                                    new_count = r["current_rev"] + 1
                                    supabase.table("user_memorization_archive").update(
                                        {
                                            "review_count": new_count,
                                            "last_reviewed_at": current_time,
                                        }
                                    ).eq("surah_serial", h_surah_num).eq(
                                        "ayah_number", r["ayah_number"]
                                    ).execute()

                                # حذف المفتاح بأمان لإفراغ القائمة بعد المراجعة الناجحة
                                if "stable_quran_multiselect" in st.session_state:
                                    del st.session_state["stable_quran_multiselect"]

                                st.success(
                                    f"✅ تم تسجيل المراجعة بنجاح لـ ({len(to_review)}) آية!"
                                )
                                st.rerun()
                            except Exception as e:
                                st.error(f"خطأ أثناء تسجيل المراجعة: {e}")
                        else:
                            st.warning(
                                "⚠️ لم تقم بتحديد أي آيات **محفوظة مسبقاً** لتسجيل المراجعة."
                            )

            st.markdown("<br>", unsafe_allow_html=True)

            # 5. مشغل التلاوة التلقائية
            audio_urls = []
            ayah_numbers = []
            surah_str = f"{h_surah_num:03d}"

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
        st.error("❌ تعذر الاتصال بجدول 'surah_pages' في قاعدة البيانات.")
