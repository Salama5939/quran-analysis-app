-- ============================================================================
-- المعمارية البصرية للتحليل البنيوي والمفاهيمي في القرآن الكريم (24 محوراً)
-- المرحلة الأولى: إنشاء الجداول المطبعة (_normalized) وتعبئة البيانات والربط مع full_quran
-- متوافق 100% مع بنية جداول Supabase PostgreSQL الحالية (full_quran, quran_topics)
-- ============================================================================

BEGIN;

-- 1. جدول الطبقات الوظيفية الخمس
CREATE TABLE IF NOT EXISTS public.arch_layers_normalized (
    layer_id INTEGER PRIMARY KEY,
    layer_order INTEGER NOT NULL UNIQUE,
    title_ar TEXT NOT NULL,
    title_en TEXT,
    color_hex VARCHAR(16) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. جدول المحاور الأربعة والعشرين
CREATE TABLE IF NOT EXISTS public.arch_axes_normalized (
    axis_id INTEGER PRIMARY KEY,
    layer_id INTEGER NOT NULL REFERENCES public.arch_layers_normalized(layer_id) ON DELETE CASCADE,
    axis_order INTEGER NOT NULL UNIQUE,
    title_ar TEXT NOT NULL,
    title_plain TEXT NOT NULL,
    archetype TEXT NOT NULL,
    summary_ar TEXT NOT NULL,
    equation_steps JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. جدول العقد والمفاهيم القرآنية (96 عقدة)
CREATE TABLE IF NOT EXISTS public.arch_nodes_normalized (
    node_id SERIAL PRIMARY KEY,
    axis_id INTEGER NOT NULL REFERENCES public.arch_axes_normalized(axis_id) ON DELETE CASCADE,
    node_order INTEGER NOT NULL,
    term_vowelled TEXT NOT NULL,
    term_plain TEXT NOT NULL,
    role_ar TEXT NOT NULL,
    linguistic_root TEXT NOT NULL,
    verses_display TEXT NOT NULL,
    analytical_desc TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (axis_id, node_order)
);

-- 4. جدول الربط العلائقي بين المفاهيم وآيات المصحف الشريف (full_quran)
CREATE TABLE IF NOT EXISTS public.arch_node_ayah_map_normalized (
    map_id SERIAL PRIMARY KEY,
    node_id INTEGER NOT NULL REFERENCES public.arch_nodes_normalized(node_id) ON DELETE CASCADE,
    surah_number INTEGER NOT NULL,
    ayah_number INTEGER NOT NULL,
    citation_label TEXT NOT NULL,
    evidence_type VARCHAR(50) DEFAULT 'شاهد تأسيسي',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (node_id, surah_number, ayah_number)
);

-- فهارس لتسريع البحث النصي غير المشكول والربط العلائقي
CREATE INDEX IF NOT EXISTS idx_arch_axes_layer ON public.arch_axes_normalized(layer_id);
CREATE INDEX IF NOT EXISTS idx_arch_nodes_axis ON public.arch_nodes_normalized(axis_id);
CREATE INDEX IF NOT EXISTS idx_arch_nodes_term_plain ON public.arch_nodes_normalized(term_plain);
CREATE INDEX IF NOT EXISTS idx_arch_map_node ON public.arch_node_ayah_map_normalized(node_id);
CREATE INDEX IF NOT EXISTS idx_arch_map_surah_ayah ON public.arch_node_ayah_map_normalized(surah_number, ayah_number);

-- تنظيف البيانات السابقة لضمان إمكانية إعادة تشغيل السكربت بأمان (Idempotent)
TRUNCATE TABLE public.arch_node_ayah_map_normalized, public.arch_nodes_normalized, public.arch_axes_normalized, public.arch_layers_normalized RESTART IDENTITY CASCADE;

-- تعبئة الطبقات الخمس
INSERT INTO public.arch_layers_normalized (layer_id, layer_order, title_ar, title_en, color_hex) VALUES (1, 1, 'الطبقة الأولى: الأنطولوجيا الإلهية والنظام الزمكاني الأعلى', 'Divine Ontology & Supreme Cosmic Order', '#0d9488');
INSERT INTO public.arch_layers_normalized (layer_id, layer_order, title_ar, title_en, color_hex) VALUES (2, 2, 'الطبقة الثانية: هندسة الإنسان والإدراك ومراتب النفس', 'Human Architecture, Perception & Soul Ranks', '#2563eb');
INSERT INTO public.arch_layers_normalized (layer_id, layer_order, title_ar, title_en, color_hex) VALUES (3, 3, 'الطبقة الثالثة: البوصلة السلوكية، الانحراف، وعبادة الحي', 'Behavioral Compass, Deviation & Worship of the Living', '#7c3aed');
INSERT INTO public.arch_layers_normalized (layer_id, layer_order, title_ar, title_en, color_hex) VALUES (4, 4, 'الطبقة الرابعة: الإدارة المجتمعية، الصوت، والتداعي', 'Societal Governance, Discourse & Knowledge Resonance', '#d97706');
INSERT INTO public.arch_layers_normalized (layer_id, layer_order, title_ar, title_en, color_hex) VALUES (5, 5, 'الطبقة الخامسة: الميزان المصيري، المقاصد، والنور المعنوي', 'Eschatological Balance, Objectives & Spiritual Light', '#dc2626');

-- تعبئة المحاور الـ 24 والعقد الـ 96 وربطها بالآيات
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (1, 1, 1, 'الأنطولوجيا الإلهية والنظام الكوني الأعلى', 'الأنطولوجيا الإلهية والنظام الكوني الأعلى', 'مصفوفة البنية والوظيفة (Structural Dualities)', 'يُفكّك هذا المحور أركان القيادة والتدبير الكوني الأعلى في اللسان القرآني، مفرّقاً بدقة بين مركز القرار وقاعدة السعة، وبين عالم المادة وعالم التفعيل اللحظي.', '["الْخَلْق (الوعاء المادي)", "الأَمْر والروح (الشفرة والمدد)", "تَدْبِير الْأَمْر من الْعَرْش", "انتظام الكون واستقراره"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (1, 1, 1, 'الْعَرْش والْكُرْسِيّ', 'العرش والكرسي', 'مركزية القيادة vs قاعدة الإحاطة', 'ع-ر-ش (السقف والعلو والملك) / ك-ر-س (القاعدة والأصل المتماسك)', 'سورة البقرة (255) • الأعراف (54) • طه (5)', 'الْعَرْش هو غرفة القيادة المركزية العليا ومقام الهيمنة وتدبير الأمر وصدور السنن الحاكمة؛ بينما الْكُرْسِيّ هو قاعدة السعة والإحاطة الفيزيائية والكونية الحافظة لاستقرار المادة والأنظمة السماوية والأرضية دون إجهاد.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (1, 2, 255, 'سورة البقرة (255)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (1, 7, 54, 'سورة الأعراف (54)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (1, 20, 5, 'سورة طه (5)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (2, 1, 2, 'تَدْبِير الْأَمْر', 'تدبير الأمر', 'الدورة الإدارية الكونية (Feedback Loop)', 'د-ب-ر (النظر في دُبُر الشيء وعاقبته ومآله)', 'سورة السجدة (5) • يونس (3) • الرعد (2)', 'النظام الإداري الديناميكي اللحظي القائم على توجيه حركة الأسباب؛ ويتجلى في دورة ثنائية: التنزيل الإداري الصادر من مركز القيادة (السماء) إلى ميدان التنفيذ (الأرض)، يعقبه عروج النتائج والتغذية الراجعة للتقييم.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (2, 32, 5, 'سورة السجدة (5)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (2, 10, 3, 'سورة يونس (3)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (2, 13, 2, 'سورة الرعد (2)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (3, 1, 3, 'الْخَلْق والأَمْر', 'الخلق والأمر', 'البنية المادية (Hardware) vs الشفرة التشغيلية (Software)', 'خ-ل-ق (التقدير والتشكيل المادي) / أ-م-ر (التوجيه والإنفاذ المباشر)', 'سورة الأعراف (54) • يس (82)', 'الْخَلْق هو المكون المادي والأجسام والبنية التحتية الخاضعة للتدرج والمراحل الزمانية؛ بينما الأَمْر هو الشفرة التشغيلية والسنن والإرادة النافذة الخاطفة اللازمكانية التي تنفذ فوراً بكلمة (كُن).');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (3, 7, 54, 'سورة الأعراف (54)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (3, 36, 82, 'سورة يس (82)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (4, 1, 4, 'الرُّوح', 'الروح', 'المدد التشغيلي العالي من عالم الأمر', 'ر-و-ح (السعة والحياة والنسمة المحيية)', 'سورة الإسراء (85) • الشورى (52) • المجادلة (22)', 'طاقة تشغيلية وشفرة عليا منبثقة حصراً من عالم ''الأمر'' وليست مخلوقة من طين؛ وظيفتها الشحن الإحيائي، التأييد الإيماني، والمدد المعرفي الذي ينقل الكائن البشري إلى مرتبة الوعي والترقية التكليفية.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (4, 17, 85, 'سورة الإسراء (85)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (4, 42, 52, 'سورة الشورى (52)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (4, 58, 22, 'سورة المجادلة (22)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (2, 1, 2, 'النشأة الإنسانية والمسار الآدمي', 'النشأة الإنسانية والمسار الآدمي', 'مخطط المسار المتدفق (Evolutionary Pipeline)', 'يرسم هذا المحور مراحل الترقية الوجودية للكائن البشري من التكوين البيولوجي المادي إلى الكائن العاقل المكلف المستخلف في الأرض.', '["تَسْوِيَة الْبَشَر (الوعاء)", "نَفْخ الرُّوح (الوعي)", "تَعْلِيمُ الأَسْمَاءِ (المعرفة)", "الإِنْسَان المستخلف المكلف"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (5, 2, 1, 'الْبَشَر مقابل الإِنْسَان', 'البشر مقابل الإنسان', 'الهيكل البيولوجي vs الكائن الإدراكي المكلف', 'ب-ش-ر (الجلد والظاهر الجسدي) / أ-ن-س (الأُنس والإدراك والتفاعل الواعي)', 'سورة الكهف (110) • الحجر (28-29) • الأحزاب (72)', 'الْبَشَر هو الهيكل البيولوجي المادي والمظهر الخارجي الخاضع للغرائز والأكل والمشي في الأسواق؛ أما الإِنْسَان فهو الكائن الإدراكي العاقل والمسؤول الذي ارتقى بنفخة الروح وتلقي الشفرة المعرفية وحمل الأمانة.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (5, 18, 110, 'سورة الكهف (110)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (5, 15, 28, 'سورة الحجر (28-29)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (5, 15, 29, 'سورة الحجر (28-29)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (5, 33, 72, 'سورة الأحزاب (72)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (6, 2, 2, 'التَّسْوِيَة والنَّفْخ', 'التسوية والنفخ', 'تجهيز الوعاء العضوي ثم شحنه بالوعي', 'س-و-ي (الاستقامة والاعتدال والاتزان) / ن-ف-خ (بث الطاقة والحركة في الجوف)', 'سورة ص (71-72) • السجدة (9)', 'التَّسْوِيَة هي التشكيل والتعديل العضوي والفيزيولوجي للجسد والدماغ والجهاز العصبي ليكون مهيئاً للتلقي؛ يعقبها النَّفْخ بربط الوعاء المادي بـ ''الروح'' وتفعيل معالج الوعي والتفكير التجريدي.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (6, 38, 71, 'سورة ص (71-72)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (6, 38, 72, 'سورة ص (71-72)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (6, 32, 9, 'سورة السجدة (9)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (7, 2, 3, 'تَعْلِيمُ الأَسْمَاءِ', 'تعليم الأسماء', 'الشفرة المعرفية والقدرة على التجريد', 'ع-ل-م (الإدراك الجازم) + س-م-و (السمة والعلامة المميزة)', 'سورة البقرة (31-33)', 'ليست الأسماء مجرد كلمات جامدة، بل هي القدرة على التجريد الذهني، صياغة المفاهيم، وقراءة شفرات وقوانين المادة والكائنات؛ وهو الممكن الأساسي الذي سمح لآدم وذريته بتسخير الكون وعمارة الأرض.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (7, 2, 31, 'سورة البقرة (31-33)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (7, 2, 32, 'سورة البقرة (31-33)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (7, 2, 33, 'سورة البقرة (31-33)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (8, 2, 4, 'الاصْطِفَاء والاستخلاف', 'الاصطفاء والاستخلاف', 'الترقية التكليفية على وجود بشري/حيوي سابق', 'ص-ف-و (استخلاص الصفوة من بين موجودات) / خ-ل-ف (التعاقب والنيابة في العمارة)', 'سورة البقرة (30) • آل عمران (33) • الأنعام (133)', 'تثبت الأدلة القرآنية الخمسة (دلالة خليفة، شهادة الملائكة بسفك الدماء، سُنّة الاصطفاء، التمايز بين البشر والإنسان، وسُنّة التناص) أن تعيين آدم خليفة جاء ترقيةً واستخلافاً على وجود حيوي سابق.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (8, 2, 30, 'سورة البقرة (30)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (8, 3, 33, 'سورة آل عمران (33)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (8, 6, 133, 'سورة الأنعام (133)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (3, 1, 3, 'منظومة التكليف، الأمانة والعمارة', 'منظومة التكليف، الأمانة والعمارة', 'الدورة التشغيلية المغلقة (Governance Cycle)', 'يضبط هذا المحور العلاقة التعاقدية بين الإنسان والكون والخالق من خلال تسخير الموارد، تحمل مسؤولية الاختيار، والاختبار الميداني لإعمار الأرض.', '["التَّسْخِير (الموارد)", "الأَمَانَة (حرية الاختيار)", "الابْتِلَاء (القياس الميداني)", "الاسْتِعْمَار والإصلاح في الأرض"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (9, 3, 1, 'التَّسْخِير وقوانينه', 'التسخير وقوانينه', 'تذليل الكون لخدمة المكلف وفق 4 قوانين', 'س-خ-ر (التذليل والتطويع لأداء وظيفة بلا مقابل)', 'سورة الجاثية (13) • إبراهيم (32-33) • الزخرف (32)', 'تذليل المادة والكائنات وتوجيهها وظيفياً لخدمة المكلف؛ وتحكمه أربعة قوانين: التبعية الكونية الشاملة، الاقتران بالمعرفة والأسماء، التكامل والتفاضل الاجتماعي، والغائية الإيمانية الشاكرة.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (9, 45, 13, 'سورة الجاثية (13)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (9, 14, 32, 'سورة إبراهيم (32-33)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (9, 14, 33, 'سورة إبراهيم (32-33)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (9, 43, 32, 'سورة الزخرف (32)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (10, 3, 2, 'الأَمَانَة', 'الأمانة', 'عقد التفويض التكليفي وحرية الاختيار', 'أ-م-ن (الائتمان والثقة والوفاء بالالتزام)', 'سورة الأحزاب (72)', 'التكليف الإرادي الحر المشفوع بحرية الاختيار ومسؤولية الحساب؛ أشفقت السماوات والأرض والجبال من حملها لأن طاعتها تكوينية حتمية لا تحتمل الخطأ، بينما احتمل الإنسان مخاطرة الاختيار.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (10, 33, 72, 'سورة الأحزاب (72)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (11, 3, 3, 'الابْتِلَاء', 'الابتلاء', 'بيئة القياس المعملية لتحويل الدعوى لاستحقاق', 'ب-ل-و (الاختبار الكاشف لما في الباطن)', 'سورة الملك (2) • الأنبياء (35) • العنكبوت (2)', 'النظام التقييمي الذي يُخرج ما استقر في سريرة الإنسان من إرادة وخيار إلى واقع عملي مشهود؛ ويكون بالسراء والضراء وبالمال والقوة لتحويل الدعوى النظرية إلى استحقاق فعلي للجزاء.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (11, 67, 2, 'سورة الملك (2)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (11, 21, 35, 'سورة الأنبياء (35)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (11, 29, 2, 'سورة العنكبوت (2)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (12, 3, 4, 'الاسْتِعْمَار فِي الْأَرْض', 'الاستعمار في الأرض', 'التكليف بإحياء الأرض وبناء الحضارة الراشدة', 'ع-م-ر (البناء والإحياء والبقاء النافع)', 'سورة هود (61)', 'التكليف الإلهي بإحياء الأرض، بناء الحضارة، استخراج الخيرات، وإشاعة الإصلاح؛ ويختلف جذرياً عن ''الاستعمار السياسي الحديث'' الذي هو في حقيقته إفساد وتدمير للحرث والنسل.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (12, 11, 61, 'سورة هود (61)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (4, 1, 4, 'سُنن التمكين والإدارة الاجتماعية', 'سنن التمكين والإدارة الاجتماعية', 'مصفوفة الأرباع المتقابلة (2×2 Matrix)', 'يُحدّد القوانين الحاكمة لصعود المجتمعات واستقرارها في الأرض في مقابل عوامل التآكل والتخريب الذاتي.', '["إيتاء السَّبَب (الأدوات)", "إتباع السَّبَب (التنفيذ الواعي)", "المنظومة الرباعية (الحج: 41)", "التَّمْكِين المستدام ودفع الْفَسَاد"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (13, 4, 1, 'الْفَسَاد (State / Output)', 'الفساد (State / Output)', 'حالة التلف والاضطراب الناتجة عن السلوك', 'ف-س-د (خروج الشيء عن الاعتدال والصلاحية)', 'سورة الروم (41)', 'حالة التلف، الاضطراب، والتعطل المادي أو المعنوي أو البيئي الناشئة كعاقبة وتراكم لسلوك البشر ومخالفة السنن الكونية والتشريعية.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (13, 30, 41, 'سورة الروم (41)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (14, 4, 2, 'الْإِفْسَاد (Active Process)', 'الإفساد (Active Process)', 'الفعل التخريبي المتعدي المنظم', 'أ-ف-س-د (صيغة إفعال للتعدية والقصد التخريبي)', 'سورة البقرة (11-12 و205) • القصص (4)', 'الفعل النشط المتعدي والعملية التخريبية المنظمة التي يمارسها المفسد لقطع الوصل، تدمير الصلاح، وإهلاك الحرث والنسل مع الادعاء الكاذب بالإصلاح.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (14, 2, 11, 'سورة البقرة (11-12)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (14, 2, 12, 'سورة البقرة (11-12)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (14, 2, 205, 'سورة البقرة (205)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (14, 28, 4, 'سورة القصص (4)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (15, 4, 3, 'التَّمْكِين وشروطه الأربعة', 'التمكين وشروطه الأربعة', 'إيجاد المقر الثابت والنفوذ والسيطرة', 'م-ك-ن (الثبات والرسوخ والقدرة)', 'سورة النور (55) • الحج (41)', 'إيجاد المقر الثابت والسيطرة وإيتاء الأسباب؛ وشروطه الأربعة: الأهلية والإيمان والعمل الصالح، المنظومة التنفيذية الرباعية (الصلاة، الزكاة، الأمر بالمعروف، النهي عن المنكر)، الأخذ بالأسباب والعدل، والحذر من الاستدراج.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (15, 24, 55, 'سورة النور (55)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (15, 22, 41, 'سورة الحج (41)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (16, 4, 4, 'الأَسْبَاب وإتباعها', 'الأسباب وإتباعها', 'معادلة ذي القرنين في الإدارة الميدانية', 'س-ب-ب (الحبل والوسيلة الموصلة للغرض)', 'سورة الكهف (84-85)', 'الأسباب هي السنن المادية والوسائط الكونية؛ وتضع سورة الكهف المعادلة الحاكمة: إيتاء السبب (توفير الأدوات والإمكانات) + إتباع السبب (العمل والتحرك الميداني بوعي) = التمكين والإنجاز.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (16, 18, 84, 'سورة الكهف (84-85)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (16, 18, 85, 'سورة الكهف (84-85)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (5, 1, 5, 'سُنن الاستبدال والتداول الحضاري', 'سنن الاستبدال والتداول الحضاري', 'مخطط المسار المتدفق (Civilizational Turnover)', 'يكشف آلية الضبط الإلهية لمسار الرسالة والاستخلاف عند نكوص الأمة المكلفة، لضمان استمرار العمران دون توقف.', '["قَبول التكليف والتمكين", "التَّوَلِّي والنكوص الميداني", "تفعيل سُنّة الاسْتِبْدَال", "إحلال جيل جديد ذي أهلية"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (17, 5, 1, 'التَّوَلِّي', 'التولي', 'الشرط الإجرائي والمؤشر النظامي للاستبدال', 'و-ل-ي (الإدبار والانصراف عن الشيء بعد الإقبال)', 'سورة محمد (38) • التوبة (39)', 'النكوص، الإدبار، والانسحاب الميداني عن التكليف بعد قَبوله وتوفر أدوات التمكين؛ ويشكل ''التولي'' الشرط المباشر والمؤشر النظامي لتفعيل سُنّة الاستبدال ونزع الأهلية الاستخلافية.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (17, 47, 38, 'سورة محمد (38)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (17, 9, 39, 'سورة التوبة (39)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (18, 5, 2, 'الْإِهْلَاك', 'الإهلاك', 'تصفية التراكم الفاسد وإنهاء الوجود المادي', 'هـ-ل-ك (السقوط والتلف والزوال التام)', 'سورة الأنعام (6) • القصص (58-59)', 'إنهاء الوجود المادي وتصفية التراكم الفاسد نتيجة طغيان الإفساد والظلم واستنفاد فرص الإمهال والإنذار، لتطهير الأرض من بؤر التعطيل.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (18, 6, 6, 'سورة الأنعام (6)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (18, 28, 58, 'سورة القصص (58-59)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (18, 28, 59, 'سورة القصص (58-59)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (19, 5, 3, 'الاسْتِبْدَال', 'الاستبدال', 'إجراء تنظيمي استراتيجي لإحلال جيل مؤهل', 'ب-د-ل (إقامة شيء مقام آخر يأخذ دوره)', 'سورة محمد (38) • المائدة (54) • إبراهيم (19-20)', 'إجراء تنظيمي استراتيجي بنزع التكليف والتمكين عن المتولين وإحلال قوم آخرين يمتلكون الأهلية والصلاحية (يحبهم ويحبونه، أذلة على المؤمنين أعزة على الكافرين) دون توقف حركة الرسالة.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (19, 47, 38, 'سورة محمد (38)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (19, 5, 54, 'سورة المائدة (54)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (19, 14, 19, 'سورة إبراهيم (19-20)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (19, 14, 20, 'سورة إبراهيم (19-20)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (6, 2, 6, 'بروتوكولات الحساب والجزاء الأخروي', 'بروتوكولات الحساب والجزاء الأخروي', 'مخطط المسار المتدفق (Eschatological Pipeline)', 'يتتبع الخطوات الإجرائية الدقيقة لانتقال الإنسان من لحظة الوفاة إلى العرض والحساب والوزن وإعلان الاستحقاق النهائي.', '["التَّوَفِّي والْمَوْت", "الْبَعْث والإخراج والنُّشُور", "الْجَمْع والْحَشْر", "الْحِسَاب والْمِيزَان وإعلان الاستحقاق"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (20, 6, 1, 'التَّوَفِّي والْمَوْت', 'التوفي والموت', 'سحب الوعي والنفس vs التعطل البيولوجي للجسد', 'و-ف-ي (استيفاء الشيء كاملاً) / م-و-ت (السكون وانقطاع الحياة المادية)', 'سورة الزمر (42) • الأنعام (61)', 'التَّوَفِّي هو استيفاء الوعي والنفس وسحب سلطتها من الجسد وإدخالها في الحفظ والقبض الإلهي؛ أما الْمَوْت فهو التعطل البيولوجي النهائي للجسد الفيزيائي وتحلل المادة.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (20, 39, 42, 'سورة الزمر (42)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (20, 6, 61, 'سورة الأنعام (61)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (21, 6, 2, 'الْبَعْث، الْإِخْرَاج، والنُّشُور', 'البعث، الإخراج، والنشور', 'التفعيل الحيوي، العبور الترابي، والانتشار الميداني', 'ب-ع-ث (الإثارة واليقظة) / خ-ر-ج (البروز) / ن-ش-ر (الانتشار والتفرق)', 'سورة الروم (19-20) • القمر (7) • التكوير (10)', 'الْبَعْث هو الشرارة التفعيلية وتنشيط اليقظة من السكون؛ الْإِخْرَاج هو العبور الفيزيائي واختراق الغلاف الترابي من باطن الأرض؛ النُّشُور هو الانتشار الميداني والتوزع الفضائي نحو موقف القضاء.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (21, 30, 19, 'سورة الروم (19-20)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (21, 30, 20, 'سورة الروم (19-20)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (21, 54, 7, 'سورة القمر (7)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (21, 81, 10, 'سورة التكوير (10)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (22, 6, 3, 'الْجَمْع والْحَشْر', 'الجمع والحشر', 'الشمول الإحصائي vs السَوْق القسري الموجه', 'ج-م-ع (الضم دون تفريط) / ح-ش-ر (السوق والضم تحت الإكراه)', 'سورة التغابن (9) • ق (44) • النمل (17)', 'الْجَمْع هو الشمول الإحصائي المطابق للأعداد دون تفريط أو فجوة استيعابية؛ أما الْحَشْر فهو السَوْق القسري والتحريك الموجه تحت سلطة الجنود والملائكة نحو الساحة.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (22, 64, 9, 'سورة التغابن (9)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (22, 50, 44, 'سورة ق (44)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (22, 27, 17, 'سورة النمل (17)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (23, 6, 4, 'الْحِسَاب والْمِيزَان', 'الحساب والميزان', 'المراجعة السجلية الكمية vs التقييم النوعي', 'ح-س-ب (العدّ والإحصاء) / و-ز-ن (تقدير الثقل والقيمة)', 'سورة الانشقاق (8) • الأعراف (8-9) • القارعة (6-9)', 'الْحِسَاب هو المراجعة الإحصائية السجلية الكمية للصحف والمدخلات والمخرجات (Audit Trail)؛ بينما الْمِيزَان هو التقييم النوعي لثقل العمل وقيمته الحقيقية بـ ''الحق'' والإخلاص (Valuation).');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (23, 84, 8, 'سورة الانشقاق (8)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (23, 7, 8, 'سورة الأعراف (8-9)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (23, 7, 9, 'سورة الأعراف (8-9)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (23, 101, 6, 'سورة القارعة (6-9)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (23, 101, 7, 'سورة القارعة (6-9)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (23, 101, 8, 'سورة القارعة (6-9)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (23, 101, 9, 'سورة القارعة (6-9)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (24, 6, 5, 'الأَعْرَاف، السِّيمَاء، والوَسْم', 'الأعراف، السيماء، والوسم', 'موقع الفرز، البصمة الذاتية، والكيّ العقابي', 'ع-ر-ف (المرتفع البارز) / س-و-م (العلامة الظاهرة) / و-س-م (الأثر بالكيّ)', 'سورة الأعراف (46-48) • الفتح (29) • القلم (16)', 'الأَعْرَاف هو المرتفع البارز على الحجاب الفاصل وموقع الفرز؛ السِّيمَاء هي البصمة الذاتية المنطبعة تلقائياً على الوجه انعكاساً للباطن؛ الوَسْم هو الكيّ القسري الخارجي لتثبيت العار على مركز الكبر.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (24, 7, 46, 'سورة الأعراف (46-48)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (24, 7, 47, 'سورة الأعراف (46-48)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (24, 7, 48, 'سورة الأعراف (46-48)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (24, 48, 29, 'سورة الفتح (29)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (24, 68, 16, 'سورة القلم (16)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (7, 2, 7, 'عالم الغيب والشهادة وأولو الألباب', 'عالم الغيب والشهادة وأولو الألباب', 'مصفوفة البنية والوظيفة (Epistemic Visibility)', 'يضبط حدود الإدراك الحسي والمجال المعرفي للإنسان، موضحاً كيف يتجاوز ''أولو الألباب'' قشرة الظواهر لالتقاط السنن الغيبية عبر البصيرة.', '["رصد عَالَم الشَّهَادَة", "التفكر بـ الْبَصِيرَة وعقل أُولِي الْأَلْبَاب", "التصديق بعَالَم الْغَيْب", "يقين راسخ وخشية واعية"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (25, 7, 1, 'عَالَمُ الشَّهَادَةِ', 'عالم الشهادة', 'مجال الرصد الحسي المباشر والقياس المادي', 'ش-هـ-د (الحضور والمعاينة والإدراك بالبصر والحواس)', 'سورة الرعد (9) • الحشر (22) • السجدة (6)', 'كل ما يقع ضمن نطاق الرصد الحسي المباشر والتجريب والقياس المادي والمكاني للمكلف؛ ويمثل ساحة المعاينة التي تُختبر فيها السنن الكونية والمادية.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (25, 13, 9, 'سورة الرعد (9)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (25, 59, 22, 'سورة الحشر (22)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (25, 32, 6, 'سورة السجدة (6)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (26, 7, 2, 'عَالَمُ الْغَيْبِ', 'عالم الغيب', 'النظام الخفي والسنن الحاكمة المحجوبة عن الحواس', 'غ-ي-ب (الاستتار والاحتجاب عن الحواس المادية)', 'سورة البقرة (3) • النمل (65) • الأنعام (59)', 'الوجود الحقيقي المحجوب عن الإدراك الحسي البشري إما لعلو مستواه (الذات الإلهية، الملائكة) أو لامتداده الزمكاني (المستقبل، البرزخ، الآخرة)؛ ولا يُدرك إلا بالوحي أو بالاستدلال العقلي المنضبط بالآيات.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (26, 2, 3, 'سورة البقرة (3)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (26, 27, 65, 'سورة النمل (65)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (26, 6, 59, 'سورة الأنعام (59)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (27, 7, 3, 'أُولُو الْأَلْبَابِ', 'أولو الألباب', 'نخبة المعالجة العميقة المستخلِصة لجوهر الحقائق', 'ل-ب-ب (اللُّب: الخالص النقي من كل شيء وجوهره الداخلي)', 'سورة آل عمران (190-191) • الزمر (18) • الرعد (19)', 'أصحاب العقول الخالصة من شوائب الهوى والتقليد؛ الذين يتجاوزون القشرة الظاهرة للأحداث في عالم الشهادة ليلتقطوا جوهر السنن وعلاقاتها بعالم الغيب، ويجمعون بين التفكر المستمر والذكر الدائم.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (27, 3, 190, 'سورة آل عمران (190-191)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (27, 3, 191, 'سورة آل عمران (190-191)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (27, 39, 18, 'سورة الزمر (18)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (27, 13, 19, 'سورة الرعد (19)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (28, 7, 4, 'الْبَصِيرَة', 'البصيرة', 'الرؤية القلبية الكاشفة لحقائق الأمور وعواقبها', 'ب-ص-ر (الإدراك النافذ والكشف الواضح)', 'سورة يوسف (108) • القيامة (14) • الأعراف (203)', 'قوة الإدراك القلبي النافذة التي تُبصر الحقائق والسنن والمآلات بوضوح تام يتجاوز حدود العين المادية، وتمنح المكلف اليقين والبرهان القاطع في دعوته وسلوكه.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (28, 12, 108, 'سورة يوسف (108)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (28, 75, 14, 'سورة القيامة (14)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (28, 7, 203, 'سورة الأعراف (203)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (8, 2, 8, 'منظومة الهداية وموانع الإدراك', 'منظومة الهداية وموانع الإدراك', 'المخطط الهرمي التصاعدي (Progressive Blocking)', 'يشرح التدرج التشريحي والوظيفي لتعطل أدوات الإدراك البشري، وكيف تتحول المعاصي المتراكمة إلى عوازل تمنع وصول الهدى إلى القلب.', '["الإعراض وتراكم الكسب", "الرَّيْن ثم الْأَكِنَّة والْغِشَاوَة", "استنفاد فرص الإنذار", "الطَّبْع والْخَتْم العقابي"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (29, 8, 1, 'الرَّيْن', 'الرين', 'طبقة الصدأ المتراكمة على سطح القلب من الكسب', 'ر-ي-ن (الغلبة والتغطية والصدأ المتراكم على السطح)', 'سورة المطففين (14)', 'طبقة الصدأ والتلوث المعرفي التي تغشى سطح القلب نتيجة تراكم الذنوب وعدم إزالتها بالاستغفار والتوبة؛ وهو مانع قابل للإزالة بالتزكية قبل أن يتحول إلى إغلاق دائم.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (29, 83, 14, 'سورة المطففين (14)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (30, 8, 2, 'الْأَكِنَّة', 'الأكنة', 'الأغطية العازلة التي تمنع نفاذ البث القرآني', 'ك-ن-ن (الستر والحفظ والعزل داخل غلاف)', 'سورة الأنعام (25) • الكهف (57) • فصلت (5)', 'أغطية وأغلفة عازلة تُحيط بالقلوب فتمنع نفاذ موجات البيان والقرآن إلى داخلها، مقترنة بالوقر في الآذان، نتيجة الإعراض المسبق والتكبر على الحق.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (30, 6, 25, 'سورة الأنعام (25)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (30, 18, 57, 'سورة الكهف (57)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (30, 41, 5, 'سورة فصلت (5)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (31, 8, 3, 'الْغِشَاوَة', 'الغشاوة', 'الستار الحاجب الذي يعطل الرؤية البصرية والفكرية', 'غ-ش-و (التغطية الشاملة التي تحجب الرؤية)', 'سورة البقرة (7) • الجاثية (23)', 'ستار حاجب يقع على الأبصار فيعطل قدرتها على قراءة الآيات الكونية والمشهودة وتحويلها إلى عبرة، حيث يرى الإنسان الحدث المادي دون أن يرى دلالته.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (31, 2, 7, 'سورة البقرة (7)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (31, 45, 23, 'سورة الجاثية (23)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (32, 8, 4, 'الطَّبْع والْخَتْم', 'الطبع والختم', 'الإغلاق العقابي النهائي بعد استنفاد الفرص', 'ط-ب-ع (نقش الأثر وإغلاق المجرى) / خ-ت-م (التوثيق النهائي بعد الفراغ)', 'سورة البقرة (7) • النساء (155) • محمد (24)', 'الطَّبْع هو الإغلاق الكلي لمنافذ القلب وسدّ مسالك الاستقبال؛ والْخَتْم هو التوثيق النهائي على هذا الإغلاق بعد استنفاد الإنذار واختيار الكفر عمداً، فلا يدخله إيمان ولا يخرج منه كفر.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (32, 2, 7, 'سورة البقرة (7)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (32, 4, 155, 'سورة النساء (155)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (32, 47, 24, 'سورة محمد (24)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (9, 2, 9, 'السنن الزمنية والتحولات الكونية الكبرى', 'السنن الزمنية والتحولات الكونية الكبرى', 'مخطط المسار المتدفق (Cosmic Timeline)', 'يفرق بدقة بين المدة الزمنية الممنوحة للمكلف أو الأمة وبين لحظة الانفجار الكوني وتحول النظام الفيزيائي للكون بأوصافه المختلفة.', '["استيفاء الْأَجَل الْمُسَمَّى", "وقوع السَّاعَة بغتة", "الْقَارِعَة والصَّاخَّة والطَّامَّة", "طيّ النظام الكوني وبداية الآخرة"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (33, 9, 1, 'الْأَجَل والْأَجَل الْمُسَمَّى', 'الأجل والأجل المسمى', 'المدة الزمنية المحددة للابتلاء vs الموعد الحتمي للانقضاء', 'أ-ج-ل (الغاية والمدة المحددة لانتهاء الشيء)', 'سورة الأنعام (2) • الأعراف (34) • نوح (4)', 'الْأَجَل هو المدة الزمنية الممنوحة للكائن أو الأمة للعمل والاختبار؛ والْأَجَل الْمُسَمَّى هو الموعد الحتمي الدقيق المحدد سلفاً في العلم الإلهي لانتهاء الدنيا والبعث، والذي لا يتقدم ولا يتأخر إذا جاء.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (33, 6, 2, 'سورة الأنعام (2)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (33, 7, 34, 'سورة الأعراف (34)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (33, 71, 4, 'سورة نوح (4)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (34, 9, 2, 'السَّاعَة', 'الساعة', 'نقطة الصفر الفاصلة بين النظام الدنيوي والأخروي', 'س-و-ع (الجزء المحدد من الزمان واللحظة الفاصلة)', 'سورة الأعراف (187) • القمر (1) • الحج (1)', 'نقطة الصفر الزمنية الخاطفة (كلمح البصر أو هو أقرب) التي ينتهي عندها زمن الدنيا والتكليف وتبدأ بها أحداث التحول الكوني الشامل.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (34, 7, 187, 'سورة الأعراف (187)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (34, 54, 1, 'سورة القمر (1)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (34, 22, 1, 'سورة الحج (1)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (35, 9, 3, 'الْقَارِعَة', 'القارعة', 'الصدمة الفيزيائية والصوتية التي تقرع الكون والقلوب', 'ق-ر-ع (الضرب الشديد بشدة وصوت مرتفع)', 'سورة القارعة (1-5) • الحاقة (4)', 'الوصف الميكانيكي والصوتي للحدث الكوني الذي يقرع الأسماع والقلوب بشدة هائلة، فتتطاير معه الجبال كالعهن المنفوش ويصبح الناس كالفراش المبثوث.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (35, 101, 1, 'سورة القارعة (1-5)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (35, 101, 2, 'سورة القارعة (1-5)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (35, 101, 3, 'سورة القارعة (1-5)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (35, 101, 4, 'سورة القارعة (1-5)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (35, 101, 5, 'سورة القارعة (1-5)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (35, 69, 4, 'سورة الحاقة (4)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (36, 9, 4, 'الصَّاخَّة والطَّامَّة', 'الصاخة والطامة', 'النفخة المصمّة للأسماع vs الغمر الكوني الشامل', 'ص-خ-خ (الصوت الشديد الذي يصمّ الآذان) / ط-م-م (العلو والغمر الذي يغطي كل شيء)', 'سورة عبس (33-37) • النازعات (34-36)', 'الصَّاخَّة هي الصيحة الهائلة التي تصمّ الآذان عن كل شواغل الدنيا وتُذهل المرء عن أقرب الناس إليه؛ والطَّامَّة الْكُبْرَى هي الداهية العظمى التي تطمّ وتغمر كل ما سواها وتكشف سجل عمل الإنسان كاملاً.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (36, 80, 33, 'سورة عبس (33-37)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (36, 80, 34, 'سورة عبس (33-37)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (36, 80, 35, 'سورة عبس (33-37)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (36, 80, 36, 'سورة عبس (33-37)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (36, 80, 37, 'سورة عبس (33-37)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (36, 79, 34, 'سورة النازعات (34-36)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (36, 79, 35, 'سورة النازعات (34-36)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (36, 79, 36, 'سورة النازعات (34-36)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (10, 2, 10, 'منظومة التدفق الاقتصادي والسلوكي', 'منظومة التدفق الاقتصادي والسلوكي', 'مصفوفة الأرباع المتقابلة (Economic Flows)', 'يضبط حركة المال داخل المجتمع القرآني بين التدوير التنموي والتزكية الإيمانية، في مقابل الاحتكار والاستغلال الربوي وأمراض النفس.', '["الْبَيْع المنتج + الْإِنْفَاق والزَّكَاة", "تطهير النفس من الْبُخْل والشُّحّ", "تحريم الرِّبَا والاحتكار", "اقتصاد متوازن ومجتمع متكافل"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (37, 10, 1, 'الْإِنْفَاق', 'الإنفاق', 'إخراج المال من نفق الاحتكار إلى دورة الحياة', 'ن-ف-ق (النفاذ والخروج من ممر إلى فضاء واسع)', 'سورة البقرة (3 و261) • سبأ (39)', 'الوظيفة الاقتصادية العامة لتحريك المال وإخراجه من نفق الاكتناز والجمود إلى دورة النفع العام والاستثمار في سبيل الله وتنمية المجتمع.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (37, 2, 3, 'سورة البقرة (3)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (37, 2, 261, 'سورة البقرة (261)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (37, 34, 39, 'سورة سبأ (39)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (38, 10, 2, 'الزَّكَاة والصَّدَقَة', 'الزكاة والصدقة', 'التطهير والنماء المؤسسي vs برهان الصدق الإيماني', 'ز-ك-و (الطهارة والنماء والبركة) / ص-د-ق (المطابقة والبرهان على الصدق)', 'سورة التوبة (60 و103) • البقرة (276)', 'الزَّكَاة هي الفريضة المالية المؤسسية التي تطهر المال والنفس وتنمي الدورة الاقتصادية؛ والصَّدَقَة هي العطاء الاختياري أو الواجب الذي يمثل برهاناً عملياً على صدق إيمان المنفق وتجرده.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (38, 9, 60, 'سورة التوبة (60)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (38, 9, 103, 'سورة التوبة (103)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (38, 2, 276, 'سورة البقرة (276)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (39, 10, 3, 'الْبَيْع مقابل الرِّبَا', 'البيع مقابل الربا', 'التبادل القيمي المنتج vs التضخم الطفيلي القسري', 'ب-ي-ع (المبادلة بالرضا وتوليد المنفعة) / ر-ب-و (الزيادة المجردة دون مقابل إنتاجي)', 'سورة البقرة (275-279) • الروم (39)', 'الْبَيْع عملية تبادل اقتصادي منتج قائم على التراضي والمخاطرة المشتركة وتوليد القيمة المضافة؛ أما الرِّبَا فهو استغلال حاجة المضطر لتوليد زيادة مالية طفيلية بلا جهد أو إنتاج، مما يؤدي إلى محق البركة وانهيار التوازن الاجتماعي.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (39, 2, 275, 'سورة البقرة (275-279)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (39, 2, 276, 'سورة البقرة (275-279)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (39, 2, 277, 'سورة البقرة (275-279)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (39, 2, 278, 'سورة البقرة (275-279)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (39, 2, 279, 'سورة البقرة (275-279)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (39, 30, 39, 'سورة الروم (39)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (40, 10, 4, 'الْبُخْل والشُّحّ', 'البخل والشح', 'إمساك الحق الواجب vs المرض النفسي الجامع للحرص', 'ب-خ-ل (المنع والإمساك عن البذل) / ش-ح-ح (الحرص الشديد مع المنع والطمع)', 'سورة النساء (37) • الحشر (9) • التغابن (16)', 'الْبُخْل هو سلوك الإمساك عن إنفاق المال الواجب أو المستحب مما في اليد؛ أما الشُّحّ فهو الداء النفسي الأعمق الذي يجمع بين البخل بما في اليد والحرص والطمع فيما في أيدي الناس.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (40, 4, 37, 'سورة النساء (37)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (40, 59, 9, 'سورة الحشر (9)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (40, 64, 16, 'سورة التغابن (16)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (11, 3, 11, 'منظومة أدوات الإدراك والوعي البشري', 'منظومة أدوات الإدراك والوعي البشري', 'مخطط المسار المتدفق (Cognitive Data Pipeline)', 'تُشكّل أدوات الإدراك البشري (الصدر، الفؤاد، القلب، العقل) معمارية معالجة متدرجة للبيانات تحول المدخلات الحسية إلى عقيدة راسخة وقرار منضبط.', '["الالتقاط الحسي (السمع والأبصار)", "انشراح الصَّدْر", "معالجة الْفُؤَاد", "ربط الْعَقْل داخل الْقَلْب ⟸ يقين وقرار منضبط"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (41, 11, 1, 'الصَّدْر', 'الصدر', 'الواجهة الاستقبالية ومستودع التفاعل الأولي (Buffer Zone)', 'ص-د-ر (مقدمة الشيء وواجهته الأمامية وموضع الورود الأول)', 'سورة الشرح (1) • الأنعام (125) • الحجر (97) • الناس (5) • غافر (19)', 'الغلاف الخارجي ومنطقة الاستقبال والفرز الأولي (Buffer) قبل وصول المعلومة إلى عمق الوعي؛ يتسع بالانشراح لاستيعاب التكليف، أو يضيق عند الضغط، ويمثل ميدان الوسوسة الخارجية ومستودع الكتمان.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (41, 94, 1, 'سورة الشرح (1)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (41, 6, 125, 'سورة الأنعام (125)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (41, 15, 97, 'سورة الحجر (97)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (41, 114, 5, 'سورة الناس (5)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (41, 40, 19, 'سورة غافر (19)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (42, 11, 2, 'الْفُؤَاد', 'الفؤاد', 'المعالج التحليلي السريع والموقد الإدراكي (Active Processor)', 'ف-أ-د (التوقّد والحركة السريعة والانفعال الحراري المعني بالإنضاج)', 'سورة النحل (78) • الملك (23) • الإسراء (36) • النجم (11) • القصص (10)', 'وحدة المعالجة المركزية السريعة التي تتسلم الإشارات الخام مباشرة من السمع والأبصار في نسق قرآني ثابت لترجمتها إلى إدراك أولي وتقييم حسي دقيق.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (42, 16, 78, 'سورة النحل (78)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (42, 67, 23, 'سورة الملك (23)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (42, 17, 36, 'سورة الإسراء (36)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (42, 53, 11, 'سورة النجم (11)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (42, 28, 10, 'سورة القصص (10)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (43, 11, 3, 'الْقَلْب', 'القلب', 'النواة المركزية ومستقر العقيدة والقيادة (Core Decision Engine)', 'ق-ل-ب (الخالِص من كل شيء ولُبّه مع قابلية التحول والتغيّر)', 'سورة الرعد (28) • الأعراف (179) • البقرة (7) • المطففين (14)', 'النواة الحاكمة ومركز القيادة واتخاذ القرار النهائي؛ حيث تستقر الحقائق التي عالجها الفؤاد لتتحول إلى إيمان راسخ وطمأنينة، وعليه يقع الإغلاق العقابي بالرين والطبع والختم.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (43, 13, 28, 'سورة الرعد (28)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (43, 7, 179, 'سورة الأعراف (179)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (43, 2, 7, 'سورة البقرة (7)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (43, 83, 14, 'سورة المطففين (14)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (44, 11, 4, 'الْعَقْل', 'العقل', 'وظيفة الربط المنطقي والضبط السلوكي (Logical Governance)', 'ع-ق-ل (الشدّ والربط والمنع كعِقال الناقة الذي يمنعها من الشرود)', 'سورة الحج (46) • الملك (10)', 'ليس عضواً مادياً مستقلاً (ولم يرد في القرآن بصيغة الاسم قط، بل بصيغة الفعل دائماً)، وإنما هو الوظيفة البرمجية التي يمارسها القلب للربط بين الآيات والسنن وكبح النفس عن الهوى.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (44, 22, 46, 'سورة الحج (46)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (44, 67, 10, 'سورة الملك (10)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (12, 3, 12, 'منظومة مستويات اليقين والتصديق', 'منظومة مستويات اليقين والتصديق', 'المخطط الهرمي التصاعدي (Stepped Hierarchy)', 'يُحدّد المراتب التصاعدية لارتباط الإنسان بالوحي، بدءاً من الانقياد الظاهري، مروراً بالتصديق القلبي، وصولاً إلى الإتقان الإحساني واليقين الكاشف.', '["الْإِسْلَام (الانقياد الظاهري)", "الْإِيمَان (التصديق القلبي)", "الْإِحْسَان (الإتقان والمراقبة)", "الْيَقِين التام (علم وعين وحق)"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (45, 12, 1, 'الْإِسْلَام', 'الإسلام', 'القاعدة التأسيسية: الانقياد السلوكي والدخول في السِّلم', 'س-ل-م (البراءة من العيوب والانقياد والخضوع السلمي)', 'سورة الحجرات (14) • آل عمران (19 و83)', 'الدائرة الأوسع والمدخل التأسيسي القائم على الاستسلام والانقياد الظاهري لأوامر الوحي ونواهيه والدخول في عقد السلم والتعايش المنضبط بالشرع.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (45, 49, 14, 'سورة الحجرات (14)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (45, 3, 19, 'سورة آل عمران (19)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (45, 3, 83, 'سورة آل عمران (83)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (46, 12, 2, 'الْإِيمَان', 'الإيمان', 'التصديق القلبي الجازم المستقر والمثمر للأمن', 'أ-م-ن (الطمأنينة والثقة والتصديق المزيل للخوف والريب)', 'سورة الحجرات (14) • الأنفال (2-4) • التغابن (11)', 'ارتقاء نوعي ينتقل فيه الحق من الانقياد الظاهري إلى الاستقرار العميق في نواة القلب (ولمّا يدخل الإيمان في قلوبكم)، فيثمر أمناً نفسياً وطاعة تلقائية وزيادة مستمرة عند سماع الآيات.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (46, 49, 14, 'سورة الحجرات (14)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (46, 8, 2, 'سورة الأنفال (2-4)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (46, 8, 3, 'سورة الأنفال (2-4)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (46, 8, 4, 'سورة الأنفال (2-4)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (46, 64, 11, 'سورة التغابن (11)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (47, 12, 3, 'الْإِحْسَان', 'الإحسان', 'ذروة الأداء النوعي والإتقان مع استحضار المراقبة', 'ح-س-ن (الجودة والكمال والجمال في الفعل والنية)', 'سورة النحل (90) • البقرة (112) • الرحمن (60)', 'أعلى مراتب الأداء السلوكي والتعبدي؛ حيث يتجاوز المؤمن مجرد أداء الواجب إلى الإتقان والبذل الجميل واستحضار رقابة الله الدائمة في السر والعلن.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (47, 16, 90, 'سورة النحل (90)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (47, 2, 112, 'سورة البقرة (112)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (47, 55, 60, 'سورة الرحمن (60)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (48, 12, 4, 'الْيَقِين ومراتبه الثلاث', 'اليقين ومراتبه الثلاث', 'المعرفة القاطعة الخالية من أدنى شك (علم • عين • حق)', 'ي-ق-ن (استقرار الماء في قراره وثبوت العلم بلا اضطراب)', 'سورة التكاثر (5-7) • الحاقة (51) • الحجر (99)', 'الرسوخ المعرفي التام الذي يزول معه كل تردد أو ظن؛ ويتدرج في القرآن عبر ثلاث درجات: عِلْمُ الْيَقِين (بالبرهان والخبر الصادق)، عَيْنُ الْيَقِين (بالمعاينة والمشاهدة)، وحَقُّ الْيَقِين (بالمباشرة والملابسة التامة).');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (48, 102, 5, 'سورة التكاثر (5-7)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (48, 102, 6, 'سورة التكاثر (5-7)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (48, 102, 7, 'سورة التكاثر (5-7)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (48, 69, 51, 'سورة الحاقة (51)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (48, 15, 99, 'سورة الحجر (99)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (13, 3, 13, 'منظومة النفس ومراتبها التشغيلية', 'منظومة النفس ومراتبها التشغيلية', 'المخطط الهرمي التصاعدي (Self Evolution States)', 'يُفكّك البنية الداخلية للنفس البشرية بوصفها الكيان الشخصي المُكلّف، ويُتتبّع مسار تزكيتها عبر حالات ثلاث متدرجة من الانقياد للغريزة إلى السكينة المطلقة.', '["كبح الْهَوَى بالمجاهدة", "الارتقاء من الْأَمَّارَة إلى اللَّوَّامَة", "التزكية المستمرة بالوحي", "بلوغ النَّفْس الْمُطْمَئِنَّة"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (49, 13, 1, 'النَّفْس والْهَوَى', 'النفس والهوى', 'الذات المكلفة القابلة للتزكية vs الميل الغريزي غير المنضبط', 'ن-ف-س (الذات والكيان الحي الواعي) / هـ-و-ي (السقوط والميل الجارف نحو الأسفل)', 'سورة الشمس (7-10) • النازعات (40-41) • الجاثية (23)', 'النَّفْس هي الذات الشخصية المسؤولة التي تُبتلى وتُحاسب وتُتوفى؛ وهي كيان محايد مهيأ للتزكية أو التدسية. أما الْهَوَى فهو الاندفاع الشهواني والميل النفسي الجامح الذي يسقط بصاحبه نحو هاوية الانحراف إن لم يُكبح بالوحي والعقل.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (49, 91, 7, 'سورة الشمس (7-10)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (49, 91, 8, 'سورة الشمس (7-10)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (49, 91, 9, 'سورة الشمس (7-10)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (49, 91, 10, 'سورة الشمس (7-10)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (49, 79, 40, 'سورة النازعات (40-41)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (49, 79, 41, 'سورة النازعات (40-41)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (49, 45, 23, 'سورة الجاثية (23)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (50, 13, 2, 'النَّفْسُ الْأَمَّارَةُ بِالسُّوءِ', 'النفس الأمارة بالسوء', 'الحالة الابتدائية: سيطرة الدافع الغريزي وتبرير المعصية', 'أ-م-ر (صيغة مبالغة ''فَعّالة'' تدل على كثرة الإلزام والإلحاح الدائم)', 'سورة يوسف (53)', 'الحالة التشغيلية التي تهيمن فيها الغرائز والأهواء على مركز القرار، فتُلحّ النفس على صاحبها بارتكاب السوء وتُزيّنه له؛ ولا تنجو من هذا الطور إلا بمدد الرحمة الإلهية ومجاهدة التزكية.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (50, 12, 53, 'سورة يوسف (53)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (51, 13, 3, 'النَّفْسُ اللَّوَّامَةُ', 'النفس اللوامة', 'الحالة الانتقالية: يقظة الرقابة الذاتية والمراجعة المستمرة', 'ل-و-م (العتاب والتقريع والمراجعة على التقصير أو الخطأ)', 'سورة القيامة (2)', 'طور اليقظة الإيمانية والصراع الداخلي الإيجابي؛ حيث يشتغل جهاز الرقابة الذاتية ليعاتب صاحبه عند الزلل أو التقصير في الطاعة، مما يدفع نحو التصحيح المستمر والاستغفار.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (51, 75, 2, 'سورة القيامة (2)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (52, 13, 4, 'النَّفْسُ الْمُطْمَئِنَّةُ', 'النفس المطمئنة', 'ذروة الاستقرار: السكينة التامة والرضا بالحق', 'ط-م-أ-ن (السكون والاستقرار التام بعد الاضطراب والتردد)', 'سورة الفجر (27-30)', 'أعلى مراتب الكمال التشغيلي للنفس؛ حيث يزول الصراع الداخلي وتستقر الذات في سكون اليقين والرضا التام بأمر الله وقضائه، فتُستدعى عند الختام بالرجوع إلى ربها راضية مرضية.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (52, 89, 27, 'سورة الفجر (27-30)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (52, 89, 28, 'سورة الفجر (27-30)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (52, 89, 29, 'سورة الفجر (27-30)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (52, 89, 30, 'سورة الفجر (27-30)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (14, 3, 14, 'منظومة التزكية والوقاية السلوكية', 'منظومة التزكية والوقاية السلوكية', 'مصفوفة البنية والوظيفة (Behavioral Governance)', 'يضبط منظومة المعايير السلوكية الوقائية والإيجابية التي تحفظ استقامة المكلف وتُحوّل الإيمان الباطن إلى عطاء متقن خالص لوجه الله.', '["التَّقْوَى (الحماية الوقائية)", "الْبِرّ والْعَمَل الصَّالِح (التنفيذ النافع)", "فلتر الْإِخْلَاص (تنقية القصد)", "القبول والحياة الطيبة"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (53, 14, 1, 'التَّقْوَى', 'التقوى', 'منظومة الحماية الاستباقية ووضع وقاية من العذاب', 'و-ق-ي (الحفظ والصيانة وجعل حاجز يقي من الأذى والضرر)', 'سورة البقرة (2 و197) • الأنفال (29) • الطلاق (2-3)', 'ليست مجرد خوف سلبي، بل هي منظومة وقاية استباقية يجعل بها العبد بينه وبين غضب الله وعقابه وقايةً من خلال الالتزام الدقيق بالأوامر واجتناب النواهي؛ وتُثمر ''الفرقان'' (القدرة على التمييز) والمخرج من الأزمات.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (53, 2, 2, 'سورة البقرة (2)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (53, 2, 197, 'سورة البقرة (197)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (53, 8, 29, 'سورة الأنفال (29)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (53, 65, 2, 'سورة الطلاق (2-3)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (53, 65, 3, 'سورة الطلاق (2-3)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (54, 14, 2, 'الْبِرّ', 'البر', 'التوسع الشامل في الخير والوفاء بالعهود والإنفاق', 'ب-ر-ر (السعة والانبساط في الفضاء والصدق في الطاعة)', 'سورة البقرة (177) • آل عمران (92)', 'السعة والشمول في أفعال الخير الظاهرة والباطنة؛ يجمع بين العقيدة الصحيحة، بذل المال المحبوب، الوفاء بالعقود، والصبر في الشدائد، ويتجاوز الشكلية الظاهرية للعبادة إلى جوهر النفع.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (54, 2, 177, 'سورة البقرة (177)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (54, 3, 92, 'سورة آل عمران (92)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (55, 14, 3, 'الْعَمَل الصَّالِح', 'العمل الصالح', 'الفعل النافع المطابق للسنن والمنضبط بالشرع', 'ص-ل-ح (الاستقامة والملاءمة والنفع الخالي من الفساد)', 'سورة العصر (3) • الكهف (110) • النحل (97)', 'كل سلوك أو جهد أو إنتاج بشري يتصف بالصلاحية والاتقان والمطابقة لمنهج الوحي، ويُحدث نفعاً حقيقياً في النفس أو المجتمع أو العمران؛ وهو القرين الملازم للإيمان في القرآن.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (55, 103, 3, 'سورة العصر (3)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (55, 18, 110, 'سورة الكهف (110)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (55, 16, 97, 'سورة النحل (97)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (56, 14, 4, 'الْإِخْلَاص', 'الإخلاص', 'تنقية القصد والعمل من شوائب الشرك والرياء', 'خ-ل-ص (التصفية والتنقية من كل شائبة أو خلط)', 'سورة البينة (5) • الزمر (2-3) • الكهف (110)', 'فلتر التنقية الأعلى الذي يُجرّد النية والعمل من كل غرض دنيوي أو مراءاة للخلق، ليكون التوجه صافياً لله وحده؛ وبدونه يفقد العمل الصالح وزنه وقَبوله.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (56, 98, 5, 'سورة البينة (5)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (56, 39, 2, 'سورة الزمر (2-3)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (56, 39, 3, 'سورة الزمر (2-3)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (56, 18, 110, 'سورة الكهف (110)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (15, 3, 15, 'منظومة الثبات، الصمود، والتوكل', 'منظومة الثبات، الصمود، والتوكل', 'الدورة التشغيلية المغلقة (Resilience Engine)', 'يُحدّد آليات إدارة الضغوط والابتلاءات في السراء والضراء، وكيف يجمع المؤمن بين بذل الأسباب المادية والاعتماد القلبي الكامل على الله.', '["الصَّبْر (في الضراء)", "الشُّكْر (في السراء)", "التَّوَكُّل والْحِلْم (اتزان القيادة)", "صمود راسخ وزيادة في المدد"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (57, 15, 1, 'الصَّبْر', 'الصبر', 'ضبط النفس والثبات الإيجابي عند الصدمات والتكاليف', 'ص-ب-ر (الحبس والشدّ والتماسك دون انهيار أو جزع)', 'سورة البقرة (153 و155-157) • آل عمران (200) • الزمر (10)', 'ليس استسلاماً سلبياً، بل هو قوة حبس النفس وتماسكها الإيجابي في ثلاثة ميادين: الصبر على مشاق الطاعة، الصبر عن مغريات المعصية، والصبر عند صدمة البلاء والمصائب مع استمرار العمل.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (57, 2, 153, 'سورة البقرة (153)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (57, 2, 155, 'سورة البقرة (155-157)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (57, 2, 156, 'سورة البقرة (155-157)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (57, 2, 157, 'سورة البقرة (155-157)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (57, 3, 200, 'سورة آل عمران (200)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (57, 39, 10, 'سورة الزمر (10)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (58, 15, 2, 'الشُّكْر', 'الشكر', 'إظهار أثر النعمة وتوظيفها في طاعة المنعم', 'ش-ك-ر (الظهور والانكشاف وامتلاء الضرع بالخير)', 'سورة إبراهيم (7) • سبأ (13) • النمل (40)', 'منظومة ثلاثية الأركان: اعتراف القلب بالمنعم، ثناء اللسان، وتوظيف الجوارح والموارد في العمل المنتج النافع (اعملوا آل داود شكراً)؛ وهو الضمان التشغيلي لاستدامة النعم وزيادتها.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (58, 14, 7, 'سورة إبراهيم (7)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (58, 34, 13, 'سورة سبأ (13)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (58, 27, 40, 'سورة النمل (40)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (59, 15, 3, 'التَّوَكُّل', 'التوكل', 'تفويض النتيجة لله بعد استيفاء الأسباب الممكنة', 'و-ك-ل (الاعتماد والتفويض وإسناد الأمر إلى كافٍ قدير)', 'سورة آل عمران (159) • الطلاق (3) • هود (123)', 'معادلة تجمع بين أقصى درجات الأخذ بالأسباب المادية والتخطيط (فإذا عزمت) وبين الاعتماد القلبي الخالص على الله في النتائج والمآلات (فتوكل على الله)، مما يزيل القلق ويمنح الشجاعة.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (59, 3, 159, 'سورة آل عمران (159)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (59, 65, 3, 'سورة الطلاق (3)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (59, 11, 123, 'سورة هود (123)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (60, 15, 4, 'الْحِلْم', 'الحلم', 'ضبط الانفعال والقدرة على التجاوز مع التمكن', 'ح-ل-م (الأناة والتثبت وضبط النفس عند الغضب)', 'سورة التوبة (114) • هود (75) • الفرقان (63)', 'الرزانة وضبط النفس عن ردود الأفعال المتسرعة أو الانتقام عند الإساءة رغم القدرة، وتغليب الحكمة والمآلات البعيدة على الاندفاع العاطفي اللحظي.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (60, 9, 114, 'سورة التوبة (114)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (60, 11, 75, 'سورة هود (75)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (60, 25, 63, 'سورة الفرقان (63)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (16, 4, 16, 'بروتوكول التوبة والتعافي من الانحراف', 'بروتوكول التوبة والتعافي من الانحراف', 'مخطط المسار المتدفق (Recovery Protocol)', 'يضع الخريطة الإجرائية لتشخيص المخالفات السلوكية وتصحيح المسار عبر إزالة الأثر العقابي ثم الرجوع الكامل إلى خط الاستقامة.', '["الاعتراف بـ الذَّنْب والْإِثْم", "طلب الاسْتِغْفَار (محو الأثر)", "التَّوْبَة النَّصُوح والإصلاح", "تبديل السيئات حسنات واستعادة الاستقامة"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (61, 16, 1, 'الذَّنْب', 'الذنب', 'المخالفة ذات التبعة والعاقبة التي تلاحق صاحبها', 'ذ-ن-ب (الذَّنَب: ما يتبع الشيء ويعقبه من أثر أو نتيجة)', 'سورة آل عمران (135) • غافر (3) • الزمر (53)', 'كل مخالفة أو تقصير يترك تبعةً وعاقبةً سيئة تلاحق فاعله في الدنيا أو الآخرة إن لم تُمحَ؛ ويشمل التقصير في حق الله أو حقوق الخلق.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (61, 3, 135, 'سورة آل عمران (135)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (61, 40, 3, 'سورة غافر (3)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (61, 39, 53, 'سورة الزمر (53)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (62, 16, 2, 'الْإِثْم', 'الإثم', 'الفعل الموجب للبطء والتأخر عن الخير والكمال', 'أ-ث-م (التباطؤ والتقاعس والتأخر عن بلوغ الفضيلة)', 'سورة البقرة (219) • المائدة (2) • الأنعام (120)', 'المخالفة التي تُثقل حركة الإنسان وتُبطئ سيره المعنوي والأخلاقي وتحرمه من الثواب والارتقاء؛ ويُفرّق القرآن بين ظاهره وباطنه.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (62, 2, 219, 'سورة البقرة (219)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (62, 5, 2, 'سورة المائدة (2)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (62, 6, 120, 'سورة الأنعام (120)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (63, 16, 3, 'الاسْتِغْفَار', 'الاستغفار', 'طلب الستر والمحو وتطهير سجل المخالفات (Cleanup)', 'غ-ف-ر (التغطية والستر والوقاية كالمِغْفَر الذي يقي الرأس)', 'سورة نوح (10-12) • هود (3 و52) • آل عمران (135)', 'الخطوة التصحيحية الأولى لطلب محو أثر الذنب وستره والوقاية من عقوبته؛ ويُفعّل استجابة كونية مباشرة تفتح أبواب الرزق والقوة والمدد.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (63, 71, 10, 'سورة نوح (10-12)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (63, 71, 11, 'سورة نوح (10-12)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (63, 71, 12, 'سورة نوح (10-12)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (63, 11, 3, 'سورة هود (3)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (63, 11, 52, 'سورة هود (52)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (63, 3, 135, 'سورة آل عمران (135)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (64, 16, 4, 'التَّوْبَة النَّصُوح', 'التوبة النصوح', 'الرجوع الكامل وتصحيح المسار وإصلاح الخلل (System Reset)', 'ت-و-ب (الرجوع والعودة التامة) / ن-ص-ح (الخلوص والالتئام بعد التمزق)', 'سورة التحريم (8) • الفرقان (70-71) • البقرة (160)', 'العملية التحويلية الشاملة التي تتجاوز مجرد طلب المغفرة إلى الإقلاع الفوري، الندم الصادق، العزم على عدم العودة، وإصلاح ما أفسده الذنب؛ فتُبدّل بها السيئات حسنات.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (64, 66, 8, 'سورة التحريم (8)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (64, 25, 70, 'سورة الفرقان (70-71)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (64, 25, 71, 'سورة الفرقان (70-71)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (64, 2, 160, 'سورة البقرة (160)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (17, 4, 17, 'الموازين الاجتماعية والحاكمية', 'الموازين الاجتماعية والحاكمية', 'مصفوفة الأرباع المتقابلة (Social Governance)', 'يُحدّد الأصول الأربعة التي يقوم عليها بناء المجتمع المتماسك وإدارة النزاعات وتحقيق التوازن الحقوقي بين أفراده.', '["الاحتكام إلى الْحَقّ", "تطبيق الْعَدْل والْقِسْط", "ممارسة الْإِصْلَاح المستمر", "مجتمع متماسك وعمران آمن"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (65, 17, 1, 'الْحَقّ', 'الحق', 'المرجعية الثابتة المطابقة للسنن والواقع', 'ح-ق-ق (الثبوت والرسوخ والمطابقة التامة دون باطل)', 'سورة يونس (32) • المؤمنون (71) • الإسراء (81)', 'المرجعية العليا الثابتة والقاعدة المعيارية المستقلة عن أهواء البشر؛ وهو المعيار الذي تُقاس به الأقوال والأحكام والأنظمة لتمييز الصواب من الباطل.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (65, 10, 32, 'سورة يونس (32)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (65, 23, 71, 'سورة المؤمنون (71)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (65, 17, 81, 'سورة الإسراء (81)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (66, 17, 2, 'الْعَدْل', 'العدل', 'التوازن والمساواة الموضوعية في الحكم وإعطاء الحقوق', 'ع-د-ل (الاستواء والتعادل والموازنة بين طرفين)', 'سورة النحل (90) • النساء (58) • المائدة (8)', 'الاستقامة في الحكم والفصل بين الخصوم بموضوعية تامة دون ميل مع قرابة أو مصلحة أو خصومة (ولا يجرمنكم شنآن قوم على ألا تعدلوا).');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (66, 16, 90, 'سورة النحل (90)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (66, 4, 58, 'سورة النساء (58)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (66, 5, 8, 'سورة المائدة (8)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (67, 17, 3, 'الْقِسْط', 'القسط', 'إيتاء كل ذي حق نصيبه المحدد بدقة ورفع الظلم', 'ق-س-ط (النصيب العادل والحصة المحددة بالقسطاس)', 'سورة الحديد (25) • الرحمن (9) • النساء (135)', 'التطبيق العملي والدقيق للعدل في المعاملات والمكاييل وتوزيع الحقوق والواجبات بحيث ينال كل طرف نصيبه المستحق بلا بخس ولا تطفيف؛ وهو الغاية الكبرى لإرسال الرسل وإنزال الميزان.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (67, 57, 25, 'سورة الحديد (25)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (67, 55, 9, 'سورة الرحمن (9)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (67, 4, 135, 'سورة النساء (135)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (68, 17, 4, 'الْإِصْلَاح', 'الإصلاح', 'العملية البنائية لترميم الخلل وإزالة التنازع', 'ص-ل-ح (إزالة الفساد وإعادة الشيء إلى حالته النافعة)', 'سورة الحجرات (9-10) • الأعراف (56) • هود (88)', 'التدخل الإيجابي البناء لترميم العلاقات الاجتماعية، رأب الصدع بين المتنازعين، وتقويم الانحرافات المؤسسية لمنع تفاقم الفساد.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (68, 49, 9, 'سورة الحجرات (9-10)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (68, 49, 10, 'سورة الحجرات (9-10)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (68, 7, 56, 'سورة الأعراف (56)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (68, 11, 88, 'سورة هود (88)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (18, 4, 18, 'منظومة السلطة، الشورى، والطاعة', 'منظومة السلطة، الشورى، والطاعة', 'الدورة التشغيلية المغلقة (Political Governance)', 'يضبط العلاقة المؤسسية بين القيادة والقاعدة الاجتماعية في القرآن، محدداً آلية اتخاذ القرار، حدود الطاعة، وسبل الوقاية من الفتنة.', '["أُولُو الْأَمْر الأمناء", "ممارسة الشُّورَى المؤسسية", "الطَّاعَة المنضبطة بالمرجعية", "درء الْفِتْنَة واستقرار الجماعة"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (69, 18, 1, 'أُولُو الْأَمْر', 'أولو الأمر', 'القيادات التنفيذية والعلمية المؤتمنة على الشأن العام', 'أ-م-ر (التنظيم والتدبير وإدارة شؤون الجماعة)', 'سورة النساء (59 و83)', 'أصحاب الولاية والتدبير وأهل الاختصاص والخبرة في الشؤون العامة والعلمية والتنفيذية؛ وهم ليسوا مصدر تشريع مستقل بل منفذون أمناء تحت مرجعية الله ورسوله.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (69, 4, 59, 'سورة النساء (59)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (69, 4, 83, 'سورة النساء (83)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (70, 18, 2, 'الشُّورَى', 'الشورى', 'آلية التداول الجماعي لاستخلاص الرأي الأصوب', 'ش-و-ر (استخراج العسل من الخلية وإظهار الرأي وتمحيصه)', 'سورة الشورى (38) • آل عمران (159)', 'العملية المؤسسية لتبادل الرأي وتمحيص الخيارات بين أهل الخبرة والأمة لاستخلاص القرار الأصوب في الشؤون العامة، مما يمنع الاستبداد ويُشرك المجتمع في المسؤولية.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (70, 42, 38, 'سورة الشورى (38)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (70, 3, 159, 'سورة آل عمران (159)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (71, 18, 3, 'الطَّاعَة المنضبطة', 'الطاعة المنضبطة', 'الالتزام التنفيذي بالمعروف تحت مرجعية الوحي', 'ط-و-ع (الانقياد والامتثال الاختياري للأمر)', 'سورة النساء (59) • الممتحنة (12)', 'الالتزام النظامي بقرارات القيادة المنبثقة عن الشورى والعدل لتحقيق وحدة الصف؛ وهي طاعة تابعة ومقيدة بعدم مخالفة أمر الله ورسوله، فإذا وقع التنازع رُدّ الأمر إلى المرجعية العليا.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (71, 4, 59, 'سورة النساء (59)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (71, 60, 12, 'سورة الممتحنة (12)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (72, 18, 4, 'الْفِتْنَة', 'الفتنة', 'الاختبار الضاغط والاضطراب المهدد لوحدة الصف', 'ف-ت-ن (إدخال الذهب النار لاختبار نقائه وكشف شوائبه)', 'سورة الأنفال (25) • البقرة (191) • العنكبوت (2-3)', 'الابتلاء الشديد أو الاضطراب الاجتماعي والفكري الذي يختبر صلابة الجماعة ويمحص الصادقين من المتذبذبين؛ ويُحذّر القرآن من الفتنة العامة التي لا تصيب الظالمين وحدهم بل تعم آثارها الجميع.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (72, 8, 25, 'سورة الأنفال (25)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (72, 2, 191, 'سورة البقرة (191)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (72, 29, 2, 'سورة العنكبوت (2-3)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (72, 29, 3, 'سورة العنكبوت (2-3)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (19, 4, 19, 'منظومة التواصل، الخطاب، والبيان', 'منظومة التواصل، الخطاب، والبيان', 'مخطط المسار المتدفق (Communication Spectrum)', 'يُميّز بدقة هندسية بين درجات التعبير اللساني والتواصلي في القرآن، من مطلق اللفظ إلى الخطاب المؤثر، فالنص المتجدد، وصولاً إلى ذروة الكشف والإيضاح التام.', '["الْقَوْل (اللبنة اللفظية)", "الْكَلَام (الخطاب المؤثر)", "الْحَدِيث (الخبر المتجدد)", "الْبَيَان (الكشف القاطع والحجة البالغة)"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (73, 19, 1, 'الْقَوْل', 'القول', 'مطلق اللفظ والرأي المعبّر عن الموقف والنية', 'ق-و-ل (الخفة والحركة باللسان لإبراز الرأي والموقف)', 'سورة الأحزاب (70) • الإسراء (53) • طه (44)', 'كل لفظ أو عبارة تصدر عن المتكلم مُعبّرة عن موقفه أو حكمه أو نيته؛ وهو الوحدة الأساسية للتعبير، ويُحاسب الإنسان على صدقه وسداده ولينه.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (73, 33, 70, 'سورة الأحزاب (70)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (73, 17, 53, 'سورة الإسراء (53)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (73, 20, 44, 'سورة طه (44)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (74, 19, 2, 'الْكَلَام', 'الكلام', 'الخطاب المترابط المؤثر في المتلقي (الجرح أو التسكين)', 'ك-ل-م (الكَلْم: الجرح والتأثير العميق في الكيان)', 'سورة النساء (164) • التوبة (6) • البقرة (75)', 'النسق اللغوي المتكامل الذي يترك أثراً عميقاً في نفس السامع وعقله كأثر الجرح أو النقش؛ ولذلك سُمّي الوحي ''كلام الله'' لقوة نفاذه وتأثيره التحويلي في القلوب.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (74, 4, 164, 'سورة النساء (164)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (74, 9, 6, 'سورة التوبة (6)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (74, 2, 75, 'سورة البقرة (75)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (75, 19, 3, 'الْحَدِيث', 'الحديث', 'الخبر المتجدد والرواية المنقولة للأحداث', 'ح-د-ث (التجدد والحدوث والوقوع بعد أن لم يكن)', 'سورة الزمر (23) • الكهف (6) • الطور (34)', 'الخبر والرواية والنبأ المتجدد الذي يُنقل بين الناس عن الوقائع والقصص والمواقف؛ ويُقدّم القرآن نفسه بوصفه ''أحسن الحديث'' لتجدد معانيه وصلاحيته الدائمة.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (75, 39, 23, 'سورة الزمر (23)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (75, 18, 6, 'سورة الكهف (6)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (75, 52, 34, 'سورة الطور (34)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (76, 19, 4, 'الْبَيَان', 'البيان', 'ذروة الكشف والإيضاح والفصل الحاسم للحقائق', 'ب-ي-ن (البَيْن: الظهور والانكشاف والانفصال الواضح عن اللبس)', 'سورة الرحمن (1-4) • آل عمران (138) • النحل (89)', 'أعلى مراتب الأداء اللغوي والمعرفي؛ وهو القدرة على كشف الحقائق الخفية وإيضاحها وفصلها عن كل شبهة أو غموض بحيث تصبح جليةً للعقل والبصيرة بلا التباس.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (76, 55, 1, 'سورة الرحمن (1-4)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (76, 55, 2, 'سورة الرحمن (1-4)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (76, 55, 3, 'سورة الرحمن (1-4)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (76, 55, 4, 'سورة الرحمن (1-4)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (76, 3, 138, 'سورة آل عمران (138)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (76, 16, 89, 'سورة النحل (89)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (20, 5, 20, 'البنية المعرفية والإحكام', 'البنية المعرفية والإحكام', 'المخطط الهرمي التصاعدي (Epistemic Mastery)', 'يرسم التدرج النوعي للمعرفة في المنهج القرآني، من إدراك الحقائق اليقينية، إلى الغوص في مقاصدها، ثم وضعها في موضعها الصحيح، مع استحضارها الدائم.', '["الْعِلْم (الإدراك البرهاني)", "الْفِقْه (فهم المقاصد)", "الْحِكْمَة (الإتقان والتوظيف)", "الذِّكْر (الاستحضار الدائم والطمأنينة)"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (77, 20, 1, 'الْعِلْم', 'العلم', 'الإدراك الجازم المطابق للواقع القائم على البرهان', 'ع-ل-م (العلامة والأثر الدال على حقيقة الشيء بيقين)', 'سورة فاطر (28) • المجادلة (11) • طه (114)', 'الإدراك اليقيني الجازم لحقائق الوجود والسنن الكونية والتشريعية، المقابل للظن والجهل والهوى؛ وهو المولّد الحقيقي لخشية الله الراقية.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (77, 35, 28, 'سورة فاطر (28)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (77, 58, 11, 'سورة المجادلة (11)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (77, 20, 114, 'سورة طه (114)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (78, 20, 2, 'الْفِقْه', 'الفقه', 'الفهم العميق للمقاصد والعلل الخفية للنصوص والأحداث', 'ف-ق-هـ (الشق والفتح للوصول إلى باطن الشيء وعمقه)', 'سورة التوبة (122) • النساء (78) • الأعراف (179)', 'تجاوز القشرة الظاهرية للألفاظ والأحداث إلى الغوص في بواطنها، إدراك عللها ومقاصدها التشريعية والسننية، واستنباط دلالاتها الدقيقة.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (78, 9, 122, 'سورة التوبة (122)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (78, 4, 78, 'سورة النساء (78)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (78, 7, 179, 'سورة الأعراف (179)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (79, 20, 3, 'الْحِكْمَة', 'الحكمة', 'إحكام القول والفعل ووضع كل شيء في موضعه الأمثل', 'ح-ك-م (المنع من الفساد والإتقان كحَكَمة اللجام الضابطة)', 'سورة البقرة (269) • النحل (125) • لقمان (12)', 'الملكة التشغيلية العليا التي تجمع بين العلم العميق والتنفيذ المتقن؛ وهي وضع كل قول أو قرار أو إجراء في موضعه الدقيق وزمانه المناسب بما يمنع الفساد ويحقق الخير الكثير.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (79, 2, 269, 'سورة البقرة (269)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (79, 16, 125, 'سورة النحل (125)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (79, 31, 12, 'سورة لقمان (12)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (80, 20, 4, 'الذِّكْر', 'الذكر', 'الاستحضار الواعي الدائم للحق ومنع النسيان والغفلة', 'ذ-ك-ر (الحفظ والاستحضار في الوعي واللسان)', 'سورة الرعد (28) • طه (124) • الحجر (9)', 'الربط المستمر بين الذاكرة المعرفية والسلوك الحي؛ حيث يظل الوحي ومراقبة الله حاضرين في قلب المؤمن ولسانه وعمله فيمنعان انزلاقه في الغفلة.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (80, 13, 28, 'سورة الرعد (28)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (80, 20, 124, 'سورة طه (124)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (80, 15, 9, 'سورة الحجر (9)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (21, 5, 21, 'المرجعية العقائدية والانتماء', 'المرجعية العقائدية والانتماء', 'مصفوفة الأرباع المتقابلة (Referential Integrity)', 'يضبط الموقف الوجودي للإنسان تجاه الخالق والمرجعية العليا، مفرقاً بين وحدة المرجعية الصافية وبين أشكال التشتت والجحود والازدواجية.', '["التَّوْحِيد والْإِخْلَاص (وحدة المرجعية)", "البراءة من الشِّرْك (نقاء الولاء)", "اجتناب الْكُفْر والنِّفَاق (تطابق الظاهر والباطن)", "استقامة العقيدة والأمن التام"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (81, 21, 1, 'التَّوْحِيد والْإِخْلَاص', 'التوحيد والإخلاص', 'وحدة المرجعية المطلقة وتجريد الولاء لله وحده', 'و-ح-د (الانفراد وعدم التعدد) / خ-ل-ص (الصفاء التام من الشوائب)', 'سورة الإخلاص (1-4) • الأنعام (162-163) • الزمر (11)', 'إفراد الله تعالى بالربوبية والألوهية والأسماء والصفات والحاكمية؛ بحيث تتوحد وجهة الإنسان ومرجعيته وقيمه في مصدر واحد مطلق، مما يحرره من العبودية لغير الله.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (81, 112, 1, 'سورة الإخلاص (1-4)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (81, 112, 2, 'سورة الإخلاص (1-4)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (81, 112, 3, 'سورة الإخلاص (1-4)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (81, 112, 4, 'سورة الإخلاص (1-4)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (81, 6, 162, 'سورة الأنعام (162-163)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (81, 6, 163, 'سورة الأنعام (162-163)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (81, 39, 11, 'سورة الزمر (11)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (82, 21, 2, 'الشِّرْك', 'الشرك', 'تعدد المرجعيات وتسوية المخلوق بالخالق في الولاء', 'ش-ر-ك (الاختلاط وتعدد الأنصباء والشركاء)', 'سورة لقمان (13) • النساء (48) • الزمر (29)', 'إدخال ندّ أو شريك مع الله في العبادة أو الطاعة المطلقة أو التشريع أو المحبة؛ وهو ''ظلم عظيم'' لأنه يضع الشيء في غير موضعه ويمزق الإنسان بين متشاكسين.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (82, 31, 13, 'سورة لقمان (13)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (82, 4, 48, 'سورة النساء (48)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (82, 39, 29, 'سورة الزمر (29)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (83, 21, 3, 'الْكُفْر', 'الكفر', 'تغطية الحق الفطري وجحود النعمة والبرهان بعد المعرفة', 'ك-ف-ر (الستر والتغطية كالزارع الذي يغطي البذرة بالتراب)', 'سورة البقرة (6) • النمل (14) • إبراهيم (34)', 'فعل إرادي يقوم على ستر وتغطية الحق الواضح والفطرة السليمة والآيات الدالة على الخالق، وجحود نعمه وآلائه عناداً واستكباراً.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (83, 2, 6, 'سورة البقرة (6)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (83, 27, 14, 'سورة النمل (14)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (83, 14, 34, 'سورة إبراهيم (34)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (84, 21, 4, 'النِّفَاق', 'النفاق', 'الازدواجية الهيكلية: إظهار الإيمان وإبطان الكفر', 'ن-ف-ق (النَّفَق: السرب ذو المدخلين للظهور من جهة والاختفاء من أخرى)', 'سورة البقرة (8-16) • المنافقون (1-4) • النساء (142-145)', 'أخطر اختلالات الانتماء؛ حيث ينفصل الظاهر المعلن عن الباطن المضمر، فيتخذ المنافق الإيمان ستاراً للمصالح والمخادعة مع موالاة أعداء الحق في الخفاء.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (84, 2, 8, 'سورة البقرة (8-16)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (84, 2, 9, 'سورة البقرة (8-16)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (84, 2, 10, 'سورة البقرة (8-16)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (84, 2, 11, 'سورة البقرة (8-16)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (84, 2, 12, 'سورة البقرة (8-16)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (84, 2, 13, 'سورة البقرة (8-16)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (84, 2, 14, 'سورة البقرة (8-16)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (84, 2, 15, 'سورة البقرة (8-16)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (84, 2, 16, 'سورة البقرة (8-16)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (84, 63, 1, 'سورة المنافقون (1-4)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (84, 63, 2, 'سورة المنافقون (1-4)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (84, 63, 3, 'سورة المنافقون (1-4)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (84, 63, 4, 'سورة المنافقون (1-4)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (84, 4, 142, 'سورة النساء (142-145)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (84, 4, 143, 'سورة النساء (142-145)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (84, 4, 144, 'سورة النساء (142-145)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (84, 4, 145, 'سورة النساء (142-145)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (22, 5, 22, 'منظومة الارتباط والتواصل الحي مع الخالق', 'منظومة الارتباط والتواصل الحي مع الخالق', 'الدورة التشغيلية المغلقة (Continuous Uplink)', 'يُبيّن القنوات التشغيلية التي يرتبط بها العبد بخالقه في كل لحظة، من شمول الطاعة الحياتية إلى التنزيه الكوني، فالصلاة الدورية، فالدعاء المباشر.', '["الْعِبَادَة (الإطار الحياتي الشامل)", "التَّسْبِيح (التنزيه والانسجام الكوني)", "الصَّلَاة (الصلة الدورية الموقوتة)", "الدُّعَاء (النداء اللحظي والاستجابة)"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (85, 22, 1, 'الْعِبَادَة', 'العبادة', 'منهج الخضوع الشامل والطاعة الطوعية في كل الحياة', 'ع-ب-د (التذلل والخضوع والانقياد التام كالطريق المُعبَّد)', 'سورة الذاريات (56) • البينة (5) • الأنعام (162)', 'الغاية الوجودية الكبرى للمكلف؛ وهي مظلة شاملة تستوعب كل حركات الإنسان وسكناته وعمله وإعماره للأرض متى انضبطت بأمر الله وابتُغي بها وجهه.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (85, 51, 56, 'سورة الذاريات (56)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (85, 98, 5, 'سورة البينة (5)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (85, 6, 162, 'سورة الأنعام (162)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (86, 22, 2, 'التَّسْبِيح', 'التسبيح', 'تنزيه الخالق عن كل نقص ومواكبة حركة الكون', 'س-ب-ح (السَّبْح: الجري والانسياب السريع في الماء أو الفضاء)', 'سورة الإسراء (44) • الحديد (1) • طه (130)', 'تنزيه الله المطلق عن كل عجز أو شريك أو عبث؛ وهو التردد الكوني المشترك الذي تسبح به السماوات والأرض وكل ذرة في الوجود وفق وظيفتها المسخرة لها.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (86, 17, 44, 'سورة الإسراء (44)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (86, 57, 1, 'سورة الحديد (1)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (86, 20, 130, 'سورة طه (130)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (87, 22, 3, 'الصَّلَاة', 'الصلاة', 'الصلة الدورية الموقوتة لإعادة شحن الوعي والنهي عن الفحشاء', 'ص-ل-و (الصلة والارتباط الوثيق والملازمة)', 'سورة العنكبوت (45) • النساء (103) • طه (14)', 'محطات الاتصال الدورية الموقوتة التي تفصل المؤمن عن ضجيج الدنيا ليعيد ضبط بوصلته القلبية مع الخالق؛ وهي أداة الضبط السلوكي التي تنهى عن الفحشاء والمنكر.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (87, 29, 45, 'سورة العنكبوت (45)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (87, 4, 103, 'سورة النساء (103)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (87, 20, 14, 'سورة طه (14)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (88, 22, 4, 'الدُّعَاء', 'الدعاء', 'النداء المباشر المفتوح لطلب المدد والعون بلا حجاب', 'د-ع-و (النداء والطلب والتوجه والإمالة نحو المدعو)', 'سورة البقرة (186) • غافر (60) • النمل (62)', 'قناة الاتصال اللحظية المفتوحة بلا وسائط ولا مواقيت؛ يعبر فيها العبد عن افتقاره الكامل ويطلب المدد من القريب المجيب، وهو جوهر العبادة ومفتاح الفرج.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (88, 2, 186, 'سورة البقرة (186)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (88, 40, 60, 'سورة غافر (60)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (88, 27, 62, 'سورة النمل (62)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (23, 5, 23, 'منظومة أطوار الوجود الأربعة', 'منظومة أطوار الوجود الأربعة', 'مخطط المسار المتدفق (Existential Continuum)', 'يرسم الخريطة الزمنية والوجودية الكاملة لمسار الإنسان عبر عوالم الوجود الأربعة، محدداً وظيفة كل طور وقوانينه الفيزيائية والتكليفية.', '["الدُّنْيَا (طور العمل والابتلاء)", "الْبَرْزَخ (طور الانتقال والحفظ)", "الْآخِرَة (طور الحساب والجزاء)", "الْخُلُود (طور الديمومة والاستقرار الأبدي)"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (89, 23, 1, 'الدُّنْيَا', 'الدنيا', 'الطور الأول: دار الابتلاء والعمل والكسب المحدود', 'د-ن-و (القرب والدنو الزمني والمكاني باعتبارها المرحلة الأقرب)', 'سورة الملك (2) • الأنعام (32) • القصص (77)', 'المرحلة الزمنية القريبة والمحدودة المخصصة للتكليف والعمل والاختيار الحر؛ وهي مزرعة وممر لإنتاج رصيد الأعمال وليست دار قرار أو استيفاء نهائي للجزاء.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (89, 67, 2, 'سورة الملك (2)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (89, 6, 32, 'سورة الأنعام (32)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (89, 28, 77, 'سورة القصص (77)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (90, 23, 2, 'الْبَرْزَخ', 'البرزخ', 'الطور الثاني: الحاجز الانتقالي الفاصل بين الموت والبعث', 'ب-ر-ز-خ (الحاجز الفاصل بين شيئين يمنع اختلاطهما)', 'سورة المؤمنون (99-100) • الرحمن (20)', 'الطور الانتقالي والحاجز الزمني والوجودي الممتد من لحظة التوفي والموت إلى يوم يُبعثون؛ تتوقف فيه القدرة على الرجوع للعمل الدنيوي ويبدأ فيه التمهيد للمآل.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (90, 23, 99, 'سورة المؤمنون (99-100)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (90, 23, 100, 'سورة المؤمنون (99-100)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (90, 55, 20, 'سورة الرحمن (20)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (91, 23, 3, 'الْآخِرَة', 'الآخرة', 'الطور الثالث: دار العرض والحساب والجزاء الكامل', 'أ-خ-ر (المتأخر في الترتيب والغاية التي ينتهي إليها المسار)', 'سورة العنكبوت (64) • الأعلى (17) • الضحى (4)', 'الطور الوجودي الأبقى والأكمل الذي تبدأ أحداثه بالساعة والبعث والحشر والحساب والميزان؛ حيث تُكشف الحقائق وتُوفّى كل نفس ما كسبت بالعدل التام.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (91, 29, 64, 'سورة العنكبوت (64)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (91, 87, 17, 'سورة الأعلى (17)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (91, 93, 4, 'سورة الضحى (4)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (92, 23, 4, 'الْخُلُود', 'الخلود', 'الطور الرابع: الديمومة المطلقة والاستقرار الأبدي بلا فناء', 'خ-ل-د (البقاء الدائم والثبات المستمر الذي لا يعتريه تغير أو زوال)', 'سورة ق (34) • هود (107-108) • البقرة (81-82)', 'حالة البقاء الأبدي والديمومة المطلقة بعد استقرار أهل الجنة في الجنة وأهل النار في النار؛ حيث ينتفي الزمن الفاني والموت إلى الأبد.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (92, 50, 34, 'سورة ق (34)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (92, 11, 107, 'سورة هود (107-108)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (92, 11, 108, 'سورة هود (107-108)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (92, 2, 81, 'سورة البقرة (81-82)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (92, 2, 82, 'سورة البقرة (81-82)');
INSERT INTO public.arch_axes_normalized (axis_id, layer_id, axis_order, title_ar, title_plain, archetype, summary_ar, equation_steps) VALUES (24, 5, 24, 'منظومة النور والظلمات والهدى والضلال', 'منظومة النور والظلمات والهدى والضلال', 'مصفوفة الأرباع المتقابلة (2×2 Quadrant Matrix)', 'فصل هندسي دقيق بين طاقة الإضاءة الكاشفة وخريطة الملاحة من جهة، وبين تراكم الحجب والتيه من جهة أخرى.', '["النُّور (إضاءة البيئة)", "الْهُدَى (البوصلة والخريطة)", "تبديد الظُّلُمَات واجتناب الضَّلَال", "سير آمن وبلوغ الغاية"]'::jsonb);
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (93, 24, 1, 'النُّور', 'النور', 'طاقة الإضاءة الكاشفة والبيان الموحد (يأتي مفرداً دائماً)', 'ن-و-ر (الإشراق والانكشاف وانتشار الشعاع الكاشف دون إتلاف)', 'سورة المائدة (15-16) • الأنعام (122) • الحديد (28)', 'الإشعاع المعرفي والبياني الكاشف الذي يُبدد العتمة عن عالمي الشهادة والغيب ويُفعّل الأبصار والأفئدة لرؤية السنن ومواضع القدم.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (93, 5, 15, 'سورة المائدة (15-16)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (93, 5, 16, 'سورة المائدة (15-16)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (93, 6, 122, 'سورة الأنعام (122)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (93, 57, 28, 'سورة الحديد (28)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (94, 24, 2, 'الظُّلُمَات', 'الظلمات', 'تراكم الحُجُب المتعددة وتشتت الرؤية (يأتي جمعاً دائماً)', 'ظ-ل-م (التغطية والستر والسواد ووضع الشيء في غير موضعه)', 'سورة البقرة (257) • النور (40) • إبراهيم (1)', 'بيئة الانحجاب المعرفي وتراكب الأغطية الحاجزة (الجهل، الهوى، التقليد، الغفلة) التي تعزل القلب والحواس عن إدراك الحقائق.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (94, 2, 257, 'سورة البقرة (257)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (94, 24, 40, 'سورة النور (40)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (94, 14, 1, 'سورة إبراهيم (1)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (95, 24, 3, 'الْهُدَى', 'الهدى', 'خريطة الطريق السديدة والدلالة الموصلة (Navigation)', 'هـ-د-ي (التقدم والإرشاد اللطيف وإبانة المسلك الصحيح)', 'سورة الفاتحة (6) • البقرة (2) • محمد (17)', 'نظام الملاحة وخارطة الطريق السديدة التي تحدد للمكلف الاتجاه والخطوات العملية والغاية النهائية داخل البيئة التي كشفها النور.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (95, 1, 6, 'سورة الفاتحة (6)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (95, 2, 2, 'سورة البقرة (2)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (95, 47, 17, 'سورة محمد (17)');
INSERT INTO public.arch_nodes_normalized (node_id, axis_id, node_order, term_vowelled, term_plain, role_ar, linguistic_root, verses_display, analytical_desc) VALUES (96, 24, 4, 'الضَّلَال', 'الضلال', 'التيه والانحراف عن المسار وفقدان الوجهة (Disorientation)', 'ض-ل-ل (الضياع والغياب والعدول عن الطريق وتبدد الجهد)', 'سورة الكهف (103-104) • القصص (50)', 'حالة التيه والانحراف الملاحي التي يفقد فيها السائر البوصلة والوجهة الصحيحة؛ فيبذل جهداً وحركة في الاتجاه الخاطئ مما ينتهي بضياع سعيه.');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (96, 18, 103, 'سورة الكهف (103-104)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (96, 18, 104, 'سورة الكهف (103-104)');
INSERT INTO public.arch_node_ayah_map_normalized (node_id, surah_number, ayah_number, citation_label) VALUES (96, 28, 50, 'سورة القصص (50)');

-- تحديث تسلسل المفاتيح التلقائية (Sequences)
SELECT setval(pg_get_serial_sequence('public.arch_nodes_normalized', 'node_id'), COALESCE(MAX(node_id), 1)) FROM public.arch_nodes_normalized;
SELECT setval(pg_get_serial_sequence('public.arch_node_ayah_map_normalized', 'map_id'), COALESCE(MAX(map_id), 1)) FROM public.arch_node_ayah_map_normalized;

-- 5. إنشاء عروض تحليلية (Views) تربط المعمارية مباشرة بجدول المصحف (full_quran) وجدول الموضوعات (quran_topics)
CREATE OR REPLACE VIEW public.view_arch_full_evidence AS
SELECT
    l.layer_id,
    l.title_ar AS layer_title,
    l.color_hex AS layer_color,
    a.axis_id,
    a.title_ar AS axis_title,
    a.archetype,
    n.node_id,
    n.node_order,
    n.term_vowelled,
    n.term_plain,
    n.role_ar,
    n.linguistic_root,
    n.analytical_desc,
    m.surah_number,
    fq.surah_name,
    m.ayah_number,
    fq.ayah_text,
    fq.plain_ayah_text,
    fq.juz,
    fq.page_number,
    m.citation_label
FROM public.arch_layers_normalized l
JOIN public.arch_axes_normalized a ON a.layer_id = l.layer_id
JOIN public.arch_nodes_normalized n ON n.axis_id = a.axis_id
JOIN public.arch_node_ayah_map_normalized m ON m.node_id = n.node_id
LEFT JOIN public.full_quran fq
    ON fq.surah_number = m.surah_number
   AND fq.ayah_number = m.ayah_number;

-- عرض كشف التقاطعات المفاهيمية: الآيات التي تشترك في أكثر من محور أو مفهوم قرآني
CREATE OR REPLACE VIEW public.view_arch_cross_axis_intersections AS
SELECT
    m.surah_number,
    fq.surah_name,
    m.ayah_number,
    fq.ayah_text,
    fq.page_number,
    COUNT(DISTINCT a.axis_id) AS shared_axes_count,
    COUNT(DISTINCT n.node_id) AS shared_nodes_count,
    STRING_AGG(DISTINCT ('المحور ' || a.axis_id || ': ' || n.term_vowelled), ' | ') AS intersecting_concepts
FROM public.arch_node_ayah_map_normalized m
JOIN public.arch_nodes_normalized n ON n.node_id = m.node_id
JOIN public.arch_axes_normalized a ON a.axis_id = n.axis_id
LEFT JOIN public.full_quran fq
    ON fq.surah_number = m.surah_number
   AND fq.ayah_number = m.ayah_number
GROUP BY m.surah_number, fq.surah_name, m.ayah_number, fq.ayah_text, fq.page_number
HAVING COUNT(DISTINCT n.node_id) > 1
ORDER BY shared_axes_count DESC, shared_nodes_count DESC, m.surah_number, m.ayah_number;

COMMIT;
