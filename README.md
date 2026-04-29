# APD-ML-ES — كاشف التصيد الاحتيالي في البريد

## الفهرس

1. [نظرة عامة على المشروع](#نظرة-عامة-على-المشروع)
2. [المصطلحات التقنية المشروحة](#المصطلحات-التقنية-المشروحة)
3. [هيكل الملفات الكامل](#هيكل-الملفات-الكامل)
4. [متطلبات التشغيل](#متطلبات-التشغيل)
5. [خطوات التثبيت والتشغيل](#خطوات-التثبيت-والتشغيل)
6. [جلب البريد عبر IMAP (الإعداد والاستخدام)](#جلب-البريد-عبر-imap-الإعداد-والاستخدام)
7. [شرح كل ملف كود مع مقتطفات](#شرح-كل-ملف-كود-مع-مقتطفات)
8. [شرح نموذج تعلم الآلة المستخدم](#شرح-نموذج-تعلم-الآلة-المستخدم)
9. [API Endpoints](#api-endpoints)
10. [قاعدة البيانات](#قاعدة-البيانات)
11. [الخصائص والميزات الكاملة](#الخصائص-والميزات-الكاملة)
12. [الأخطاء الشائعة وحلولها](#الأخطاء-الشائعة-وحلولها)
13. [معلومات الفريق](#معلومات-الفريق)
14. [بنية المجلدات (شجرة كاملة)](#بنية-المجلدات-شجرة-كاملة)
15. [المصادقة، لوحة المستخدم، ولوحة الإدارة](#المصادقة-لوحة-المستخدم-ولوحة-الإدارة)
16. [ملفات `templates` و`static` و`assets`](#ملفات-templates-وstatic-وassets)
17. [خدمة IMAP البرمجية (`services/imap_fetch.py`)](#خدمة-imap-البرمجية-servicesimap_fetchpy)
18. [اعتماديات `requirements.txt`](#اعتماديات-requirementstxt)
19. [مسارات الإدارة وواجهات JSON الخاصة بها](#مسارات-الإدارة-واجهات-json-الخاصة-بها)
20. [بيانات الإدارة الافتراضية](#بيانات-الإدارة-الافتراضية)

---

## نظرة عامة على المشروع

**APD-ML-ES** اختصار لـ **An Application for Phishing Detection Using Machine Learning in Email Systems**. التطبيق يحلّل نص رسائل البريد الإلكتروني ليصنّفها إلى **تصيد احتيالي** أو **بريد شرعي** باستخدام **TF-IDF** و**Random Forest** من مكتبة **scikit-learn**، مع واجهة ويب عربية (اتجاه RTL) مبنية على **Flask** و**SQLite** لتخزين التحليلات والإحصاءات.

**إضافات وظيفية:** تسجيل مستخدمين (جلسة + ملف شخصي) لربط التحليلات بالحساب؛ جلب **IMAP** لآخر الرسائل وتحليلها محلياً (بعد الموافقة وفي نطاق جلسة مسجّل)؛ دعم **مرفقات** (`multipart` مع استخراج نص من PDF/HTML/صور مع OCR اختياري)؛ **لوحة إدارة** على مسار مُهيأ في الإعداد (ليست رابطاً عاماً) لإدارة السجلات وإعادة الحساب.

---

## المصطلحات التقنية المشروحة

- **التصيد الاحتيالي (Phishing):** محاولة خداع المستخدم لكشف بيانات حساسة عبر رسالة تبدو رسمية. *مثال:* «رسالة تدّعي أنها من البنك الأهلي وتطلب منك إدخال كلمة مرورك في رابط مزيف».

- **تعلم الآلة (Machine Learning):** النظام يتعلم من أمثلة كثيرة لربط أنماط النص بالتصنيف. *مثال:* «مثل طفل يتعلم التمييز بين التفاح والبرتقال برؤية آلاف الأمثلة».

- **TF-IDF:** طريقة تمثيل النص كأرقام تعكس أهمية الكلمة في الرسالة مقارنة ببقية الرسائل. *مثال:* «الكلمات النادرة والمميزة غالباً تحصل على أوزان أعلى».

- **Random Forest:** مجموعة أشجار قرار تدمج نتائجها (تصويت/تجميع). *مثال:* «خبراء متعددون يصوّتون — الأغلبية تحدد القرار».

- **Flask:** إطار ويب بسيط يستقبل الطلبات ويعيد الاستجابات. *مثال:* «مثل نادل المطعم — يستقبل طلبك ويعود بالنتيجة».

- **SQLite:** قاعدة بيانات ملف واحد مناسبة للتخزين المحلي. *مثال:* «ملف قاعدة بيانات بسيط يُخزّن سجلات التحليل».

- **Accuracy (الدقة):** نسبة التنبؤات الصحيحة على مجموعة الاختبار. *مثال:* «من كل 100 بريد في الاختبار — كم أصاب النموذج تصنيفه».

- **Confidence (الثقة):** أعلى احتمال يعطيه النموذج للفئة المتوقعة. *مثال:* «مدى تأكد النموذج من قراره — مثل طبيب يقول أنا متأكد 95%».

---

## هيكل الملفات الكامل

| المسار | الوصف |
|--------|--------|
| `app.py` | تشغيل Flask وتهيئة قاعدة البيانات والنموذج |
| `config.py` | إعدادات مركزية مثل `SECRET_KEY` |
| `requirements.txt` | حزم Python المطلوبة |
| `README.md` | هذا الملف — التوثيق |
| `assets/images/Logo.png` | شعار المشروع |
| `assets/fonts/` | خط IBM Plex Sans Arabic |
| `static/css/style.css` | الأنماط |
| `static/js/main.js` | سلوك الواجهة (طلبات API، الجدول، العداد) |
| `static/fonts/` | نسخ الخطوط للربط من CSS |
| `templates/` | قوالب HTML: `base`, `index`, `dashboard`, `about` |
| `routes/main.py` | صفحات `/` و`/dashboard` و`/about` ومسار صور `assets` |
| `routes/api.py` | مسارات `/api/*` للتحليل والسجل والإحصاء |
| `database/db.py` | اتصال SQLite و`init_db` |
| `database/models.py` | أسماء الجداول والأعمدة |
| `database/seed.py` | بيانات افتراضية و`recompute_statistics` |
| `ml/preprocessor.py` | تنظيف النص وتمييعه |
| `ml/trainer.py` | توليد البيانات إن لزم، التدريب، حفظ النموذج |
| `ml/predictor.py` | تحميل النموذج والتنبؤ |
| `data/phishing_dataset.csv` | يُنشأ تلقائياً عند التدريب |
| `data/apd_ml_es.db` | قاعدة البيانات (تُنشأ عند التشغيل) |
| `ml/model.pkl` | النموذج المدرب |
| `ml/vectorizer.pkl` | محوّل TF-IDF المحفوظ |
| `data/phishing_external.csv` | يُحمَّل اختيارياً من الإنترنت لدمج بيانات إضافية عند تدريب غير مكتفٍ بملف `phishing_dataset.csv` |
| `services/imap_fetch.py` | تجميع نص الرسالة من IMAP (عناوين، نصوص، مرفقات) لـ `POST /api/mail/fetch-analyze` |
| `ml/attachment_extract.py` | دمج نص الحقل + المرفقات (PDF/صور/HTML/نص) مع حد أحرف |
| `ml/corpus_builtins.py` | عينات نصوص `PHIS` / `HAM` ودالة `expanded_rows()` لتوليد بيانات تدريب احتياطية |
| `routes/auth.py` | تسجيل، دخول، خروج، ملف شخصي، مزخرف `@login_required` |
| `routes/admin.py` | لوحة إدارة على مسار سرّي + حذف/تفريغ/إعادة حساب إحصاء |
| `static/css/admin.css` | أنماط لوحة الإدارة |
| `static/js/admin.js` | جدول الإدارة، فلتر، حذف، إعادة حساب، تفريغ |
| `templates/auth/*.html` | `login`, `register`, `profile` |
| `templates/admin/*.html` | `base`, `login`, `panel` |
| `.gitignore` | قواعد تجاهل الملفات لـ Git |

### بنية المجلدات (شجرة كاملة)

**شجرة المشروع (جميع الملفات المعروفة دون استثناء):**

```text
APD-ML-ES/
├── .gitignore
├── README.md
├── app.py
├── config.py
├── requirements.txt
├── assets/
│   ├── fonts/
│   │   ├── IBMPlexSansArabic-Bold.ttf
│   │   ├── IBMPlexSansArabic-Regular.ttf
│   │   └── OFL.txt
│   └── images/          (الشعار Logo.png مذكور في القوالب؛ قد يُضاف محلياً)
├── data/
│   ├── apd_ml_es.db
│   └── phishing_dataset.csv
├── database/
│   ├── db.py
│   ├── models.py
│   └── seed.py
├── ml/
│   ├── attachment_extract.py
│   ├── corpus_builtins.py
│   ├── model.pkl
│   ├── preprocessor.py
│   ├── predictor.py
│   ├── trainer.py
│   └── vectorizer.pkl
├── routes/
│   ├── admin.py
│   ├── api.py
│   ├── auth.py
│   └── main.py
├── services/
│   └── imap_fetch.py
├── static/
│   ├── css/
│   │   ├── admin.css
│   │   └── style.css
│   ├── fonts/             (نسخ من assets للربط)
│   │   ├── IBMPlexSansArabic-Bold.ttf
│   │   └── IBMPlexSansArabic-Regular.ttf
│   └── js/
│       ├── admin.js
│       └── main.js
└── templates/
    ├── about.html
    ├── base.html
    ├── dashboard.html
    ├── index.html
    ├── admin/
    │   ├── base.html
    │   ├── login.html
    │   └── panel.html
    └── auth/
        ├── login.html
        ├── profile.html
        └── register.html
```

---

## متطلبات التشغيل

- **Python 3.10** أو أحدث (يُنصح بالتحقق بـ `python --version`).
- متصفح حديث للوصول إلى `http://localhost:5000`.
- اتصال إنترنت **عند أول تشغيل** لتحميل موارد **NLTK** (`stopwords`, `punkt`) إن لم تكن مخزّنة محلياً، ولتحميل **بيانات CSV خارجية** اختيارياً أثناء `train_model` إن كان ملف `data/phishing_dataset.csv` غير كافٍ.
- (اختياري) **Tesseract OCR** + حزمة **pytesseract** لاستخراج نص من صور المرفقات في `ml/attachment_extract.py` — بدونها تُعاد رسائل نصيّة توضيحية عن الصور.

---

## خطوات التثبيت والتشغيل

```text
# 1. تأكد أن Python 3.10+ مثبّت
python --version

# 2. افتح Command Prompt وانتقل لمجلد المشروع
cd D:\VSCode\Projects\APD-ML-ES

# 3. ثبّت المكتبات المطلوبة
pip install -r requirements.txt

# 4. شغّل التطبيق
python app.py
# سيقوم تلقائياً بـ: تهيئة قاعدة البيانات + إضافة البيانات التجريبية + تدريب النموذج + تشغيل الخادم

# 5. افتح المتصفح
# http://localhost:5000
#
# 6. (اختياري) لوحة الإدارة — انظر قسم "بيانات الإدارة الافتراضية" للرابط وكلمة المرور
```

---

## بيانات الإدارة الافتراضية

**مهم — كيف يعمل دخول «المشرف» في هذا المشروع:**  
لوحة الإدارة **ليس** فيها بريد إلكتروني ولا اسم مستخدم ولا صف `users` في قاعدة البيانات. يوجد **فقط** صفحة ويب يُدخل فيها **كلمة مرور واحدة** (قيمتها `ADMIN_PASSWORD` في `config.py`). لذلك «حساب الأدمن» عندنا = **الرابط السري + كلمة المرور** فقط.

### بيانات الدخول (للتجربة المحلية الافتراضية)

| ماذا تملأ؟ | القيمة |
|------------|--------|
| **رابط تسجيل الدخول** (الصقه في المتصفح بعد تشغيل `python app.py`) | `http://localhost:5000/c9a4m7-p2k8-qv1r/login` |
| **كلمة مرور المشرف** (الحقل الوحيد في النموذج) | `Adm!APD2026#Local` |
| **اسم المستخدم / البريد** | **لا يوجد** — اترك الفكرة؛ النموذج يطلب كلمة المرور فقط |

بعد إدخال كلمة المرور بشكل صحيح تُفتح **اللوحة** (`/panel`). الخروج من `.../logout`.

**ملخص سطر واحد:** الرابط أعلاه → أنشئ كلمة المرور `Adm!APD2026#Local` → دخول.

---

مصدر الإعدادات: الملف `config.py` — الصنف `Config`. التفصيل التقني:

| الحقل في `Config` | القيمة الافتراضية | ملاحظة |
|-------------------|-------------------|--------|
| `ADMIN_PATH` | `c9a4m7-p2k8-qv1r` | بادئة URL لكل مسارات الأدمن (مسار «سري» بدل `/admin` العلني) |
| `ADMIN_PASSWORD` | `Adm!APD2026#Local` | نفس كلمة «بيانات الدخول» في الجدول أعلاه — جلسة `adm` |

**روابط مباشرة (خادم محلي، منفذ 5000):**

- صفحة **تسجيل دخول الإدارة:** `http://localhost:5000/c9a4m7-p2k8-qv1r/login`
- بعد نجاح الدخول: **اللوحة** `http://localhost:5000/c9a4m7-p2k8-qv1r/panel` (أو تُعاد التوجيه تلقائياً)
- **خروج:** `http://localhost:5000/c9a4m7-p2k8-qv1r/logout`

**تعديل البيانات:** حرّر `d:\VSCode\Projects\APD-ML-ES\config.py` (أو المسار المناظر) وغيّر `ADMIN_PATH` و/أو `ADMIN_PASSWORD`، ثم أعد تشغيل التطبيق. لا تضع رابط الإدارة في واجهة الموقع العامة.

**مقتطف من الكود:**

```python
class Config:
    SECRET_KEY = 'apd-ml-es-dev-key-change-in-production'
    ADMIN_PATH = 'c9a4m7-p2k8-qv1r'
    ADMIN_PASSWORD = 'Adm!APD2026#Local'
```

---

## جلب البريد عبر IMAP (الإعداد والاستخدام)

يوفّر المشروع في الصفحة الرئيسية قسماً **جلب وتحليل من صندوق البريد (IMAP)**: الاتصال يتم **من جهازك (محلياً)** بخادم البريد، ثم تُجلب آخر الرسائل (بحد أعلى تضبطه في الواجهة)، ويُستخرج النص ويُحلَّل عبر نفس نموذج التصيد. **كلمة مرور IMAP لا تُخزَّن في قاعدة بيانات المشروع**؛ تُستخدم فقط داخل طلب الـ API لتلك الجلسة.

**المسار البرمجي (للتأكد):** `POST /api/mail/fetch-analyze` — **يجب أن يكون المستخدم قد سجّل الدخول** (وإلا الاستجابة `401`)؛ وفي JSON: `consent: true`، و`host`، و`user`، و`password`، ويمكن تمرير `port` (افتراضي 993)، `use_ssl` (افتراضي true)، `limit` (1–25).

### معنى الحقول في الواجهة

| الحقل | الوظيفة | مثال شائع (Gmail) |
|--------|---------|-------------------|
| عنوان خادم IMAP | اسم الخادم الذي يحدده مزوّد البريد | `imap.gmail.com` |
| المنفذ | عادة 993 عند التشفير (SSL) | `993` |
| البريد الإلكتروني | نفس العنوان الذي تسجّل به الدخول | `name@gmail.com` |
| كلمة المرور | حسب المزوّد (Gmail: غالباً **كلمة مرور تطبيق**) | — |
| عدد الرسائل | آخر *n* رسالة تُجلب للتحليل | مثلاً `10` |
| تشفير SSL | يُفضّل تفعيله مع المنفذ 993 | مفعّل |

### إعداد Gmail (الأكثر شيوعاً)

1. **تفعيل IMAP من ويب Gmail:**  
   *الإعدادات* (ترس) → *عرض كافة إعدادات البريد* → تبويب *التحويل والتعبئة / Forwarding and POP/IMAP* → في قسم **IMAP** اختر **تفعيل IMAP** → احفظ التغييرات.

2. **كلمة مرور ليست بالضرورة كلمة حسابك:** إن كان الحساب يستخدم **التحقق بخطوتين**، عادة يُشترط **كلمة مرور التطبيق** (App password) بدل كلمة الدخول العادية:  
   - من [أمان Google](https://myaccount.google.com/security) تأكد من تفعيل **التحقق بخطوتين**.  
   - ثم أنشئ **كلمات مرور التطبيقات** (App passwords) — اختر بريد / جهاز — وانسخ الـ 16 رمزاً والصقها في حقل كلمة المرور داخل APD-ML-ES.

3. **قيم جاهزة لـ Gmail:**

   - Host: `imap.gmail.com`  
   - Port: `993`  
   - SSL: مفعّل  

### مزوّدون آخرون (مختصر)

- **Microsoft 365 / Outlook:** غالباً `outlook.office365.com`، منفذ `993`، SSL. قد تفرض مؤسستك صلاحيات أو مصادقة إضافية.  
- **استضافة بريد (cPanel وغيرها):** عادة `mail.اسم-النطاق` أو العنوان الذي يعطيك مزوّد الاستضافة في وثائق IMAP.  
- التزم دائماً بما ينشره **مزوّد البريد** رسمياً (خادم، منفذ، SSL/TLS).

### خطوات الاستخدام من الواجهة

0. **سجّل الدخول** بحسابك (جلب IMAP يرتبط بجلستك ويُحفَظ في سجلك); بدون دخول يعيد الخادم `401`.  
1. املأ خادم IMAP، المنفذ، البريد، وكلمة المرور (أو كلمة تطبيق Gmail).  
2. اضبط **عدد الرسائل** (ابدأ بقيمة صغيرة للتجربة، مثل 5–10).  
3. فعّل **تشفير SSL** عند استخدام 993.  
4. **يجب** تفعيل مربع الموافقة: *أوافق على جلب آخر الرسائل…*  
5. اضغط **جلب وتحليل** وانتظر رسالة الحالة أسفل النموذج أو نتائج التحليل. إن فشل الاتصال، تظهر رسالة خطأ من الخادم (مثلاً بيانات خاطئة أو حظر جدار ناري لمنفذ 993).

### أمان وخصوصية

- الاتصال بخادم البريد يُنشأ **من عملية Python على جهازك** ما لم تعدّل المشروع ليعمل على خادم بعيد.  
- **لا** تشارك **كلمة مرور التطبيق** أو ترفع لقطات شاشة تُظهرها.  
- النتائج تُسجّل في قاعدة بيانات المشروع **كتحليلات** (نص/معاينة/تصنيف) مثل باقي التحليل اليدوي، لا تُحفظ بيانات اعتماد IMAP.

### أخطاء شائعة عند IMAP

| العرض | سبب محتمل |
|--------|------------|
| فشل الاتصال / رفض الخادم | كلمة عادية بدل **كلمة تطبيق** (Gmail)، أو IMAP غير مفعّل، أو بريد/خادم خاطئ |
| timeout | جدار ناري، أو مزوّد يحجب 993 |
| دخول ثم فشل | تغييرات أمان الحساب؛ أنشئ كلمة تطبيق جديدة |

---

## شرح كل ملف كود مع مقتطفات

> أدناه شرح **كل** ملف برمجي/تنسيق في المشروع مع **مقتطفات** من الكود الفعلي. ثوابت مثل `SECRET_KEY` و`ADMIN_PASSWORD` مذكورة هنا لأغراض التوثيق؛ **غيّرها في الإنتاج** ولا ترفع أسراراً إلى مستودع عام.

### `app.py`

**الهدف:** إنشاء تطبيق Flask، تسجيل المسارات، وتشغيل التهيئة عند البدء.

**الواردات:** `Flask`، `Config`، Blueprints: `auth_bp`، `main_bp`، `api_bp`، `admin_bp`، ثم `init_db`، `seed_data`، `train_model`، `load_model`.

**تسجيل المخططات (ترتيب التحميل):** المصادقة أولاً، ثم الصفحات العامة، ثم API تحت `/api`، ثم **لوحة الإدارة** تحت `/<Config.ADMIN_PATH>` (مثلاً `/c9a4m7-p2k8-qv1r` حسب `config.py`).

**الثوابت:** `ROOT` = مجلد المشروع؛ `MODEL_PKL` = `ml/model.pkl`.

**الدوال:** `initialize_app()` — تهيئة قاعدة البيانات، البذر، تدريب النموذج عند غياب الملفات، ثم تحميل النموذج في الذاكرة.

```python
def initialize_app():
    init_db()
    seed_data()
    if not os.path.exists(MODEL_PKL):
        print('جارٍ تدريب النموذج...')
        train_model()
    load_model()
    print('تم تهيئة التطبيق بنجاح')
```

**عند `__main__`:** `app_context()` يستدعي `initialize_app()` ثم `app.run(debug=True, host='0.0.0.0', port=5000)`.

**المتغيرات المهمة:** `MODEL_PKL` يشير إلى `ml/model.pkl` لمعرفة إن كان التدريب مطلوباً. كائن `app` يضبط `static_folder='static'` و`template_folder='templates'` و`static_url_path='/static'`.

**مقتطف تسجيل المخططات:**

```python
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/' + Config.ADMIN_PATH.strip('/'))
```

---

### `config.py`

**الهدف:** تخزين `SECRET_KEY` وإعدادات قابلة للتوسعة، **ومسار وكلمة مرور الإدارة**.

**الثوابت:** `BASE_DIR` = مجلد المشروع. داخل `Config`: `SECRET_KEY`، `ADMIN_PATH` (مسار سري لصفحات الأدمن بدل `/admin` العلني)، `ADMIN_PASSWORD` (كلمة دخول لوحة الإدارة).

```python
class Config:
    SECRET_KEY = 'apd-ml-es-dev-key-change-in-production'
    # غيّر المسار والكلمة قبل النشر. لا تُضف رابط الإدارة في واجهة الموقع.
    ADMIN_PATH = 'c9a4m7-p2k8-qv1r'
    ADMIN_PASSWORD = 'Adm!APD2026#Local'
```

---

### `database/db.py`

**الهدف:** مسار قاعدة البيانات ودالة الاتصال وإنشاء الجداول + **هجرة بسيطة** للأعمدة الجديدة.

**`DB_PATH`:** `data/apd_ml_es.db`.

**`get_connection()`:** يربط بـ `sqlite3` ويضبط `row_factory = sqlite3.Row` لقراءة الأعمدة بالاسم.

**`init_db()`:** ينفّر `executescript` لإنشاء:
- `analyses` (مع `user_id` اختياري لربط التحليل بمستخدم)
- `statistics` (صف افتراضي `id=1`)
- `users` (بريد فريد، `password_hash`، `full_name`، `phone`، `bio`، `created_at`)

**`_migrate_schema()`:** يفحص `PRAGMA table_info` ويضيف `user_id` لجدد قديم، و`phone`/`bio` لجد `users` إن نقصا.

```python
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'apd_ml_es.db')
```

```python
def _migrate_schema(conn, cursor):
    """إضافة أعمدة لقواعد قديمة دون فقد بيانات."""
    cursor.execute('PRAGMA table_info(analyses)')
    a_cols = {row[1] for row in cursor.fetchall()}
    if 'user_id' not in a_cols:
        cursor.execute('ALTER TABLE analyses ADD COLUMN user_id INTEGER')
```

---

### `database/models.py`

**الهدف:** ثوابت أسماء الجداول والأعمدة لاستخدامها في استعلامات مرتبة (لا تُشغّل الـ ORM).

**`TABLE_*`، `COLUMNS_*`:** محدودة بـ `analyses` و`statistics` — **لاحظ:** عمود `user_id` وحقول `users` الأحدث **موجودة في المخطط في `db.py`** وقد يُستورد اسم العمود يدوياً في الاستعلامات.

```python
COLUMNS_ANALYSES = (
    'id', 'email_text', 'email_preview', 'result', 'is_phishing',
    'confidence', 'analyzed_at',
)
```

---

### `database/seed.py`

**الهدف:** إدراج 30 تحليلاً افتراضياً (15 تصيد + 15 شرعي) عند كون جدول `analyses` فارغاً، ثم `recompute_statistics()`.

**الدوال:**  
- `_preview_text(full_text, length=120)` — معاينة قصيرة مع `…`.  
- `recompute_statistics()` — يحسب `COUNT` و`SUM(is_phishing)` من `analyses` ويحدّث `statistics` حيث `id=1`.  
- `seed_data()` — إن وُجدت سجلات مسبقاً تستدعي `recompute_statistics()` فقط وتخرج؛ وإلا تُدخل 15 `phishing_bodies` و15 `legit_bodies` بثقة عشوائية وتوقيت خلال 30 يوماً.

**مقتطف من `recompute_statistics`:**

```python
cur.execute('SELECT COUNT(*) AS c, COALESCE(SUM(is_phishing),0) AS ph FROM analyses')
# ...
cur.execute('''UPDATE statistics SET total_analyzed = ?, total_phishing = ?,
    total_legitimate = ?, last_updated = CURRENT_TIMESTAMP WHERE id = 1''', (total, ph, leg))
```

---

### `routes/api.py`

**الهدف:** واجهات JSON للتحليل، البريد، الإحصاء، السجل، والحذف.

**الثوابت:** `MAX_COMBINED = 100_000` — اقتصار النص المدموج (بريد + مرفقات) عند التحليل.

**`_store_analysis(full_text, res, user_id=None)`:** يبني `email_preview` (200 حرفاً + `…`)، يُدرج في `analyses` مع `datetime('now','localtime')`، يستدعي `recompute_statistics()` ويعيد `analyzed_at`.

**المسارات:**  
- `POST /api/analyze` — إن كان الطلب `multipart/form-data` يجمع `email_text` + `files` (حد أقصى 10) عبر `merge_email_and_files`؛ وإلا JSON `email_text` فقط. يستدعي `predict_email` ويحفظ مع `session['user_id']` إن وُجد. يردّ `attachments_parsed` (أسماء الملفات).  
- `POST /api/mail/fetch-analyze` — **يتطلب تسجيل دخول**؛ `consent`، `host`، `user`، `password`، `port` (افتراضي 993)، `use_ssl`، `limit` 1–25؛ يستدعي `fetch_inbox_analyze` ثم لكل رسالة `predict_email` + `_store_analysis`.  
- `GET /api/statistics` — إن وُجد `user_id` في الجلسة: إحصاء **المستخدم** فقط (`_get_stats_for_user` من `main`)؛ وإلا إحصاء **عام** من جدول `statistics` (`_get_stats_for_dashboard`).  
- `GET /api/history` — **يتطلب تسجيل دخول**؛ سجل التحليلات حيث `user_id` الحالي، حتى 100.  
- `DELETE /api/history/<id>` — حذف **إن كان السجل لنفس المستخدم**، ثم `recompute_statistics`.

**مقتطف:**

```python
@api_bp.route('/analyze', methods=['POST'])
def analyze():
    # multipart أو JSON
    res = predict_email(full_text)
    uid = session.get('user_id')
    analyzed_at = _store_analysis(full_text, res, user_id=uid)
```

```python
@api_bp.route('/mail/fetch-analyze', methods=['POST'])
def mail_fetch_analyze():
    if not session.get('user_id'):
        return jsonify({...}), 401
```

---

### `routes/main.py`

**الهدف:** الصفحات العامة، لوحة المستخدم (بعد تسجيل الدخول)، وخدمة صور `assets`.

**`main_bp`:** Blueprint بدون بادئة URL.

**الدوال الداخلية:**  
- `_get_stats_for_dashboard()` — يقرأ `statistics` حيث `id=1` ويحسب `phishing_percentage` و`legitimate_percentage`.  
- `_get_stats_for_user(user_id)` — يحسب العدد والتصيد من `analyses WHERE user_id = ?`.

**المسارات:**  
- `GET /` → `index.html`  
- `GET /dashboard` — `@login_required` → `dashboard.html` مع `stats` من `_get_stats_for_user`  
- `GET /about` → `about.html`  
- `GET /assets/images/<path>` — `send_from_directory` لمجلد `assets/images`

**مقتطف:**

```python
@main_bp.route('/dashboard')
@login_required
def dashboard():
    stats = _get_stats_for_user(session.get('user_id'))
    return render_template('dashboard.html', stats=stats)
```

---

### `routes/auth.py`

**الهدف:** تسجيل، دخول، خروج، ملف شخصي، ومزخرف جلسة.

**الثوابت:** `EMAIL_RE` = تعبير لتحقق بسيط من شكل البريد.

**`login_required(view)`:** إن لم تكن `session['user_id']` يعيد توجيهاً إلى `auth.login?next=...`.

**دوال DB:** `_get_user_by_email`، `_get_user_by_id`، `_get_user_with_hash`.

**المسارات:**  
- `GET/POST /register` — `generate_password_hash`، تخزين `users`، ثم تعبئة الجلسة.  
- `GET/POST /login` — `check_password_hash`، حماية `next` من open redirect.  
- `GET /logout` — مسح `user_id`، `user_email`، `user_name`.  
- `GET/POST /profile` — تحديث الاسم/الهاتف/السيرة/البريد/كلمة المرور مع التحقق من كلمة حالية عند تغيير بريد أو كلمة.

**`inject_auth`:** يسجّل `current_user_id`، `current_user_email`، `current_user_name` لجميع القوالب.

**مقتطف المزخرف:**

```python
def login_required(view):
    @wraps(view)
    def inner(*a, **kw):
        if not session.get('user_id'):
            return redirect(url_for('auth.login', next=request.path))
        return view(*a, **kw)
    return inner
```

---

### `routes/admin.py`

**الهدف:** لوحة إدارة (مسار تُعرفه `Config.ADMIN_PATH`) — دخول بكلمة مرور ثابتة **ليست** حساب مستخدم عادي، جلسة `session['adm']`.

**الثوابت:** `MODEL_PKL`، `DB_FILE` — لعرض حالة الملف في القالب.

**الدوال:** `_get_stats()`، `_list_analyses(limit=500)`، `admin_required`، `admin_required_json` (لـ API من الواجهة).

**الصفحات:**  
- `GET /<ADMIN_PATH>/` — إن مسجّل أدمن → `panel`، وإلا `login`  
- `GET/POST .../login` — يطابق `Config.ADMIN_PASSWORD`  
- `GET .../logout`  
- `GET .../panel` — إحصاء + جدول 500 سجل + `model_exists`، `db_path`

**إجراءات JSON (POST):**  
- `/action/recompute` — `recompute_statistics`  
- `/action/delete` — حذف تحليل بالـ `id` (لجميع المستخدمين — إدارة شاملة)  
- `/action/purge` — `DELETE FROM analyses`  
- `GET /data/refresh` — JSON للإحصاء والقائمة

**مقتطف:**

```python
@admin_bp.route('/action/purge', methods=['POST'])
@admin_required_json
def action_purge():
    # DELETE FROM analyses ثم recompute_statistics
```

---

### `services/imap_fetch.py`

**الهدف:** الاتصال بـ IMAP، جلب آخر `limit` رسالة (1–30 داخلياً في `fetch_inbox_analyze`)، استخراج نص الرسالة والمرفقات (مختصر) عبر `text_from_bytes` و`build_imap_combined_text`.

**دوال مساعدة:** `_decode_header`، `_strip_html` (BeautifulSoup إن وُجد)، `_message_text`، `_attachments_excerpt` (حتى 5 مرفقات، 60k حرفاً)، `build_imap_combined_text` (Subject/From/To + نص + مرفقات، حد `MAX_TEXT_LEN` من `attachment_extract`).

**الإرجاع:** قائمة قواميس: `subject`، `from_addr`، `preview`، `combined_text`.

---

### `ml/preprocessor.py`

**الهدف:** دالة `preprocess_text(text)` لإزالة الروابط والبريد والأرقام وعلامات الترقيم وتطبيق **PorterStemmer** وإزالة **stopwords** الإنجليزية (NLTK).

**عالمي:** `stemmer`، `stop_words` — بعد `nltk.download('stopwords')` و`('punkt')` بصمت.

```python
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'http\S+|www\S+', ' رابط ', text)
    # ...
    tokens = [stemmer.stem(w) for w in tokens if w not in stop_words and len(w) > 2]
    return ' '.join(tokens)
```

---

### `ml/trainer.py`

**الهدف:** بناء/تحديث `data/phishing_dataset.csv` (أو استخدامه إن كبيراً >=1000 سطر مع أعمدة `text`/`label`)، دمج `corpus_builtins.expanded_rows()` واختيارياً `phishing_external.csv` من روابط `URL_CANDIDATES`، ثم تدريب **TF-IDF** + **Random Forest** وحفظ `model.pkl` و`vectorizer.pkl`.

**الدوال:** `_try_download_one`، `_load_external_dataframe`، `ensure_dataset_file`، `train_model`.

**المعاملات:** `TfidfVectorizer(max_features=5000, ngram_range=(1,2))`، `RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)`، `train_test_split` 80/20 مع `stratify` عند الإمكان.

**مثال مخرجات التدريب:** طباعة `accuracy_score` و`classification_report` بأسماء `['شرعي','تصيد']`.

---

### `ml/corpus_builtins.py`

**الهدف:** قوائم نصوص `PHIS` (تصيد) و`HAM` (شرعي) + دالة `expanded_rows()` تكرر العينات بوسوم `variant` و`noise` لزيادة حجم بيانات التدريب الاحتياطي.

```python
def expanded_rows():
    rows = []
    for i, t in enumerate(PHIS):
        rows.append((t + f' [variant p-{i}]', 1))
    # ... HAM ونسخ مع noise
    return rows
```

---

### `ml/attachment_extract.py`

**الهدف:** `text_from_bytes(data, filename, mime)` لاستخراج نص من txt/html/pdf/صور (اختيارياً **pytesseract** + `PIL` إن مُنصَّب)؛ `merge_email_and_files(email_text, file_storage_list)` يدمج مع اقتصار `_trunc` بـ `MAX_TEXT_LEN` (120k). مرفقات >6MB تُتخطى مع إشارة في `meta`.

**ثوابت:** `MAX_PDF_PAGES = 8`، `MAX_IMAGE_DIM = 4000`.

---

### `ml/predictor.py`

**الهدف:** `load_model()` (تحميل عالمي `model`، `vectorizer` من joblib) و`predict_email(text)`.

**مخرجات `predict_email`:** قاموس `label` (عربي)، `is_phishing`، `confidence` (%)، `raw_prediction` (0/1).

```python
def predict_email(text):
    cleaned = preprocess_text(text)
    vector = vectorizer.transform([cleaned])
    prediction = model.predict(vector)[0]
    probability = model.predict_proba(vector)[0]
    confidence = round(float(max(probability)) * 100, 2)
```

---

### `static/js/main.js`

**الهدف:** الواجهة العامة ولوحة المستخدم: `loadStatistics`، `analyzeEmail` (FormData + مرفقات إلى `/api/analyze`)، `fetchAndAnalyzeMail` (IMAP — يتطلب تسجيل دخول)، `updateCharCount`، `clearForm`، `loadHistory`، `deleteAnalysis`، `updateDashboardStats`، `loadDashboardStats`، `updateFileHint`، `escapeHtml` — كلها `fetch` + `async/await` و`credentials: 'same-origin'`.

**مقتطف تحليل مع مرفقات:**

```javascript
const fd = new FormData();
fd.append('email_text', text);
if (hasFiles) {
    for (let i = 0; i < files.length; i++) {
        fd.append('files', files[i]);
    }
}
const res = await fetch('/api/analyze', { method: 'POST', body: fd, credentials: 'same-origin' });
```

---

### `static/js/admin.js`

**الهدف:** لوحة الإدارة: `applyStats`، `buildRow`، `onDelete` (POST JSON `{id}`) ثم `data-url-refresh`، `onRefresh`، `onRecompute`، `onPurge`، `runFilter` للجدول. يتوقع عنصر `#admin-app` بخصائص `data-url-*` للمسارات.

---

### `static/css/style.css` و`static/css/admin.css`

**الهدف:** تنسيق الموقع العام (RTL، ألوان، بطاقات، نتائج التحليل، لوحة المستخدم) وتنسيق منفصل لـ **لوحة الإدارة** (جدول، شارات، أزرار، فلتر).

---

### قوالب `templates/`

- **`base.html`:** هيكل الصفحة، شريط تنقل (Font Awesome من CDN)، روابط: رئيسية، لوحة تحكم، عن المشروع، دخول/تسجيل/ملفي/خروج حسب `current_user_id`.  
- **`index.html`:** نموذج لصق النص + مرفقات + زر تحليل + مربع نتيجة + قسم IMAP.  
- **`dashboard.html`:** إحصاءات المستخدم، جدول سجل، شريط توزيع.  
- **`about.html`:** معلومات المشروع.  
- **`auth/login.html`، `register.html`، `profile.html`:** نماذج المصادقة والملف الشخصي.  
- **`admin/base.html`، `login.html`، `panel.html`:** واجهة الأدمن (كلمة مرور واحدة) وجدول التحليلات وأدوات إعادة الحساب/التفريغ.

---

### `.gitignore`

**الهدف:** منع تتبع ملفات بيئية/IDE مثل `__pycache__`، `.env`، قواعد اختيارية — راجع الملف لقائمة القواعد الحالية.

---

## شرح نموذج تعلم الآلة المستخدم

1. **المعالجة المسبقة:** تحويل النص إلى صيغة موحّدة (حروف صغيرة، استبدال روابط وجيميل وأرقام، إزالة علامات الترقيم، stemming، إزالة كلمات التوقف الإنجليزية) عبر `ml.preprocessor.preprocess_text`.
2. **TF-IDF:** تحويل النصوص إلى مصفوفات نادرة مع `max_features=5000` و`ngram_range=(1,2)`.
3. **Random Forest:** `n_estimators=200`، `random_state=42`، `n_jobs=-1`، مع تقسيم 80% تدريب و20% اختبار (`stratify` عند توفر تسميتين).
4. **المخرجات:** التنبؤ الصنفي (0 شرعي، 1 تصيد) و`predict_proba` لحساب نسبة الثقة (أعلى احتمال × 100).

**تغذية البيانات (قبل التدريب):** `ml.trainer.ensure_dataset_file()` — إن كان `phishing_dataset.csv` غير منتجٍ بما يكفي، يجمع `ml.corpus_builtins.expanded_rows()` (عينات مدمجة) ويحاول دمج `phishing_external.csv` المحمّل من روابط عامة في `URL_CANDIDATES` (أعمدة CSV مرنة: `v1`/`v2` أو `text`/`label`، إلخ). الحد الأدنى لحجم بيانات التدريب يُفحص قبل الفشل بخطأ واضح.

**الملفات المولَّدة:** `ml/model.pkl` (كائن `RandomForestClassifier` محفوظ بـ `joblib`) و`ml/vectorizer.pkl` (كائن `TfidfVectorizer` مدرَّب). يحمّلها `ml.predictor.load_model()` مرة عند التشغيل (أو عند أول `predict_email`).

---

## API Endpoints

### `POST /api/analyze`

يدعم نمطين: **JSON** (`Content-Type: application/json`) لحقل `email_text` فقط، أو **`multipart/form-data`** مع الحقول `email_text` و`files` (تكرار المفتاح `files` لعدة مرفقات، بحد **10** ملفات). عند اقتصار النص يُقتطع إلى `MAX_COMBINED` (100,000) حرفاً. إن وُجد مستخدم في الجلسة تُسجّل التحليلات مع `user_id`.

**الطلب (JSON):**

```json
{
  "email_text": "Dear customer, your PayPal account is limited. Click here to verify now within 24 hours."
}
```

**الاستجابة (نجاح):**

```json
{
  "success": true,
  "result": {
    "label": "تصيد احتيالي",
    "is_phishing": true,
    "confidence": 94.5,
    "analyzed_at": "2026-01-15 14:30:00"
  },
  "attachments_parsed": ["file1.txt", "doc.pdf"]
}
```

حقل `attachments_parsed` قائمة أسماء مرفقات وُفّي استخراج نص منها (أو وصف اختياري عند تخطي ملف كبير جداً).

**أخطاء شائعة:** `400` إن النص المدمج فارغ أو ≤10 أحرف؛ `400` إن مرفقات أكثر من 10.

---

### `POST /api/mail/fetch-analyze`

**يتطلب تسجيل الدخول** (جلسة `user_id`)، وإلا `401` مع رسالة عربية. **نص** JSON يشمل: `consent: true`، `host`، `user`، `password`، واختيارياً: `port` (عدد، افتراضي 993)، `use_ssl` (bool)، `limit` (1–25 داخل `api`؛ الخدمة الداخلية قد تخفض الحد لـ 30 بحد أعلى). الاستجابة الناجحة:

```json
{
  "success": true,
  "count": 3,
  "analyzed": [
    {
      "subject": "…",
      "from_addr": "…",
      "result": {
        "label": "بريد شرعي",
        "is_phishing": false,
        "confidence": 88.0,
        "analyzed_at": "2026-04-20 10:11:12"
      }
    }
  ]
}
```

---

### `GET /api/history`

**يتطلب تسجيل الدخول.** بدون جلسة: `401` مثال:

```json
{
  "success": false,
  "message": "تسجيل الدخول مطلوب لعرض السجل.",
  "analyses": [],
  "total": 0
}
```

**الاستجابة (للمستخدِم المسجّل):**

```json
{
  "success": true,
  "analyses": [
    {
      "id": 1,
      "email_preview": "Thank you for your order...",
      "result": "بريد شرعي",
      "is_phishing": false,
      "confidence": 91.2,
      "analyzed_at": "2026-04-20 10:11:12"
    }
  ],
  "total": 5
}
```

(السجلات **الخاصة بالمستخدم** فقط، حتى 100 سجل، أحدثها أولاً.)

---

### `GET /api/statistics`

- **بدون تسجيل دخول:** يعكس إجمالي جدول `statistics` (كل التحليلات المخزّنة).  
- **مع تسجيل دخول:** يعكس إحصاء **تحليلات هذا المستخدم** فقط (من `analyses` حيث `user_id`).

**مثال استجابة:**

```json
{
  "success": true,
  "stats": {
    "total_analyzed": 45,
    "total_phishing": 23,
    "total_legitimate": 22,
    "phishing_percentage": 51.1,
    "legitimate_percentage": 48.9
  }
}
```

---

### `DELETE /api/history/<int:analysis_id>`

**يتطلب تسجيل دخول.** يحذف فقط إن كان `id` يخص `user_id` الحالي؛ وإلا `404` أو `401`.

**الاستجابة:**

```json
{
  "success": true,
  "message": "تم الحذف."
}
```

---

## قاعدة البيانات

**ملف:** `data/apd_ml_es.db` (SQLite). الاتصال عبر `database/db.get_connection()`.

**جدول `analyses`:**

| العمود | النوع | الوصف |
|--------|--------|--------|
| id | INTEGER PK | مفتاح تلقائي |
| email_text | TEXT | النص الكامل المُدخل/المجموع (بريد + مرفقات أو IMAP) |
| email_preview | TEXT | معاينة قصيرة (في API ~200 حرف + `…`؛ في البذر 120) |
| result | TEXT | تسمية عربية: «تصيد احتيالي» أو «بريد شرعي» |
| is_phishing | INTEGER | 1 أو 0 |
| confidence | REAL | نسبة الثقة (0–100) |
| analyzed_at | TIMESTAMP | وقت التحليل (محلياً في الإدراج عبر API) |
| user_id | INTEGER | اختياري: ربط بالمستخدم لسجلّه ولوحته: NULL للتحليلات قبل تسجيل المستخدم أو العينات |

**جدول `statistics`:** صف مرجعي `id = 1` — إجمالي **عالمي** (كل السجلات في `analyses`) لعرض شريط الصفحة الرئيسية؛ تُحدَّث بـ `recompute_statistics()` بعد إدراج/حذف.

**جدول `users`:**

| العمود | النوع | الوصف |
|--------|--------|--------|
| id | INTEGER PK | معرف المستخدم |
| email | TEXT UNIQUE | البريد (فريد، يُحفظ صغيراً) |
| password_hash | TEXT | `werkzeug` PBKDF2 |
| full_name | TEXT | اختياري |
| phone | TEXT | اختياري (هجرة) |
| bio | TEXT | اختياري (هجرة) |
| created_at | TIMESTAMP | وقت الإنشاء |

**لوحة الإدارة** تعرض/تحذف من `analyses` **لجميع المستخدمين** (لا يفلتر `user_id`).

---

## الخصائص والميزات الكاملة

- واجهة عربية كاملة مع `dir="rtl"` و`lang="ar"`.
- تحليل نص البريد من الصفحة الرئيسية مع عداد أحرف وحد أقصى 5000.
- عرض النتيجة مع لون مناسب وشريط ثقة.
- لوحة تحكم: بطاقات إحصاء، جدول آخر 20 تحليلاً، شريط توزيع، حذف سجل.
- صفحة «عن المشروع» مع الفريق والتقنيات وشرح مبسط للنموذج.
- تدريب تلقائي عند غياب `ml/model.pkl`.
- بذر 30 سجلاً افتراضياً عند أول تشغيل لقاعدة فارغة.
- **حسابات مستخدمين:** تسجيل/دخول/خروج، ملف شخصي، ربط التحليلات والسجل بـ `user_id`.
- **لوحة إدارة:** مسار سري `/<ADMIN_PATH>/` (قيمة `config.Config.ADMIN_PATH`)، دخول بكلمة مرور إدارية `ADMIN_PASSWORD` — منفصلة عن جدول `users`؛ تفريغ/حذف/إعادة حساب **عالمية** للنظام.

---

## المصادقة، لوحة المستخدم، ولوحة الإدارة

- **مستخدِم عادي:** تُعرَّف في جدول `users`، كلمات مرور مُخزّنة `generate_password_hash` / `check_password_hash`. المسارات: `/register`، `/login`، `/logout`، `/profile` (محمي بـ `login_required`). الجلسة تحمل `user_id`، `user_email`، `user_name`. القوالب تتلقى `current_user_*` عبر `auth_bp.app_context_processor`.  
- **لوحة المستخدم** `/dashboard`: تعرض إحصاء **تحليلات المستخدم فقط** (استعلام `analyses` حيث `user_id`). **الواجهة العامة** (شريط إحصاء في الرئيسية) تستخدم `GET /api/statistics` بدون تسجيل → إحصاء **عالمي** من `statistics`.  
- **المشرف (Admin):** ليس سجلاً في `users`؛ تخويل عبر `session['adm']` بعد إدخال `Config.ADMIN_PASSWORD` في `/<ADMIN_PATH>/login`. **لا** تُضَع روابط للإدارة في واجهة الموقع العامة (تعليق في `config.py`).

**بيانات دخول الإدارة (المسار وكلمة المرور الافتراضية):** مذكورة بالتفصيل في قسم [بيانات الإدارة الافتراضية](#بيانات-الإدارة-الافتراضية).

---

## ملفات `templates` و`static` و`assets`

- **`templates/`:** يُمدَّد `base.html` في `index`، `dashboard`، `about`، `auth/*`، `admin/*` (قوالب إدارية تستخدم `admin/base.html` حيث يناسب).  
- **`static/css`:** `style.css` للواجهة، `admin.css` للوحة الأدمن.  
- **`static/js`:** `main.js` مربوط بالصفحات العامة ولوحة المستخدم؛ `admin.js` بصفحة اللوحة فقط.  
- **`assets/`:** `images` للشعار (يُساق من `url_for('main.project_assets_image', filename='Logo.png')`)، `fonts` و`OFL.txt` لرخصة الخط. **`static/fonts`** نسخ للاستدعاء من CSS إن وُجد ربط نسبي.

---

## خدمة IMAP البرمجية (`services/imap_fetch.py`)

تُستدعى فقط من `routes/api.mail_fetch_analyze` بعد تسجيل الدخول. الدالة العامة `fetch_inbox_analyze(host, port, user, password, use_ssl, limit, folder=INBOX)` تستخدم `imaplib` (SSL أو عادي)، `email.policy.default` لتحليل `RFC822`، وتُرجع قائمة قواميس فيها `combined_text` ليُمرَّر لـ `predict_email`. **أمان:** كلمة مرور IMAP لا تُسجّل في DB (انظر فصل [جلب البريد عبر IMAP](#جلب-البريد-عبر-imap-الإعداد-والاستخدام)).

---

## اعتماديات `requirements.txt`

| الحزمة | الاستخدام |
|--------|------------|
| `flask` | تطبيق الويب |
| `scikit-learn` | `TfidfVectorizer`، `RandomForestClassifier` |
| `pandas` | قراءة CSV ودمج بيانات |
| `numpy` | تبعية sklearn |
| `nltk` | `stopwords`، `PorterStemmer` |
| `joblib` | حفظ/تحميل `model.pkl` و`vectorizer.pkl` |
| `beautifulsoup4` | تنظيف HTML (مرفقات + بريد IMAP) |
| `pypdf` | نصوص PDF من المرفقات |
| `Pillow` | فتح صور لـ OCR اختياري |
| (اختياري) `pytesseract` | غير مذكور في `requirements.txt` — إن ثُبّت مع Tesseract يُفعّل OCR في `attachment_extract` |

---

## مسارات الإدارة وواجهات JSON الخاصة بها

جميع المسارات أدناه مسبوقة بـ `/<Config.ADMIN_PATH>/` (بدون نهاية مائلة زائدة — انظر `app.register_blueprint(admin_bp, url_prefix=...)`).

| المسار | الطريقة | الحماية | الوظيفة |
|--------|---------|---------|---------|
| `/` | GET | — | إعادة توجيه لـ `login` أو `panel` |
| `/login` | GET, POST | — | فحص `ADMIN_PASSWORD` |
| `/logout` | GET | — | `session.pop('adm')` |
| `/panel` | GET | `admin_required` | لوحة: إحصاء + جدول + مسارات ملفات |
| `/action/recompute` | POST | `admin_required_json` | `recompute_statistics()` |
| `/action/delete` | POST | `admin_required_json` | JSON `{ "id": <int> }` — حذف سجل من `analyses` |
| `/action/purge` | POST | `admin_required_json` | حذف **كل** `analyses` |
| `/data/refresh` | GET | `admin_required_json` | JSON: `stats` + `analyses` (حتى 500) |

`static/js/admin.js` يبني طلبات `fetch` باستخدام `data-url-delete`، `data-url-refresh`، إلخ من القالب `admin/panel.html`.

---

## الأخطاء الشائعة وحلولها

| المشكلة | الحل |
|---------|------|
| فشل استيراد Flask بعد التثبيت | نفّذ `pip install -r requirements.txt` من نفس مجلد المشروع وتحقق أن `python` يشير لـ Python 3.10+ |
| بطء أو توقف أول تشغيل | التدريب الأولي وتحميل NLTK قد يستغرق وقتاً؛ انتظر حتى رسالة «تم تهيئة التطبيق» |
| خطأ في NLTK | تأكد من الاتصال بالإنترنت مرة واحدة لتحميل `stopwords` و`punkt` |
| المنفذ 5000 مستخدم | غيّر المنفذ في آخر `app.py` أو أغلق التطبيق الذي يشغّل 5000 |
| قاعدة بيانات قديمة تريد إعادة البذر | احذف `data/apd_ml_es.db` (احتفظ بنسخة إن لزم) ثم أعد التشغيل |

---

## معلومات الفريق

| الاسم | الرقم |
|--------|--------|
| Wiam Ali Al-Jari | 461200475 |
| Taif Hussein Al-Enazi | 452217149 |
| Sarah Obaid Al-Rashidi | 452217215 |
| Ghala Suwailam Al-Harbi | 452217090 |
| Abrar Khaled Al-Enazi | 452217153 |
| Bashayer Yahya Mazyadi | 461200381 |
| Renad Suleiman | 461200474 |

**المشرف:** د. شيراز البشير الحق  
**الجامعة:** جامعة القصيم — الكلية التطبيقية — قسم الأمن السيبراني  
**السنة:** 2026م / 1447هـ

---

*نهاية التوثيق — APD-ML-ES*
