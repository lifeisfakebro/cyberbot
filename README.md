# بوت الأخبار السيبرانية 🛡️

بوت بايثون يسحب أخبار الأمن السيبراني من مواقع RSS (وبشكل تجريبي من X)
ويرسلها تلقائياً لبوت تيليجرام، صورة + نص، عن طريق GitHub Actions المجاني.

---

## 1) خطوات الإعداد بالترتيب

### أ) إنشاء بوت تيليجرام والحصول على التوكن
1. افتح تيليجرام وابحث عن `@BotFather`.
2. أرسل له `/newbot` واتبع التعليمات (اسم البوت، ثم username ينتهي بـ `bot`).
3. راح يعطيك **توكن** شكله تقريباً: `123456789:ABCdefGhIJKlmNoPQRstuVwxYZ`.

### ب) الحصول على Chat ID
- لو بترسل لنفسك أو لمحادثة خاصة: أرسل أي رسالة للبوت، بعدين افتح بالمتصفح:
  `https://api.telegram.org/bot<التوكن>/getUpdates`
  وبتلقى `chat.id` بالرد.
- لو بترسل لقناة: أضف البوت كـ Admin بالقناة، وChat ID القناة يكون بصيغة `-100xxxxxxxxxx`.

### ج) رفع المشروع على GitHub
```bash
git init
git add .
git commit -m "أول نسخة من بوت الأخبار السيبرانية"
git branch -M main
git remote add origin https://github.com/<اسم_المستخدم>/<اسم_الريبو>.git
git push -u origin main
```

### د) إضافة الأسرار (Secrets) بالريبو
داخل الريبو على GitHub:
`Settings > Secrets and variables > Actions > New repository secret`

أضف السرّين التاليين:
| الاسم | القيمة |
|---|---|
| `TELEGRAM_BOT_TOKEN` | توكن البوت اللي أخذته من BotFather |
| `TELEGRAM_CHAT_ID` | آيدي الشات أو القناة |

### هـ) تفعيل GitHub Actions
اذهب لتبويب **Actions** بالريبو ووافق على تفعيله (يظهر تلقائياً أول مرة).
البوت بعدها بيشتغل تلقائياً كل 30 دقيقة حسب الجدولة بملف
`.github/workflows/run-bot.yml`.

تقدر أيضاً تجربه يدوياً فوراً من تبويب Actions باختيار
"Cyber News Bot" ثم "Run workflow".

---

## 2) تعديل مصادر الأخبار

كل شي بملف `config.json`:

```json
{
  "rss_sources": ["ضيف روابط RSS اللي تبيها هنا"],
  "twitter_accounts": ["اسم_المستخدم بدون @"],
  "nitter_instances": ["https://nitter.net"],
  "max_items_per_run": 10
}
```

- **rss_sources**: حطيت لك 5 مصادر سيبرانية معروفة كبداية، عدّلها زي ما تبي.
- **twitter_accounts**: فاضية افتراضياً، ضيف أسماء المستخدمين اللي تبيها.
- **max_items_per_run**: أقصى عدد أخبار يرسلها بكل تشغيلة (عشان ما يغرق الشات بأول تشغيلة).

---

## 3) ملاحظة مهمة جداً عن جزء X (تويتر) ⚠️

منصة X ألغت أي وصول مجاني رسمي للـ API بفبراير 2026 (صار كل شي pay-per-use).
عشان كذا الجزء الخاص بـ X بالبوت يعتمد على **Nitter** — واجهة بديلة غير رسمية
تقرأ تويتر بدون API. المشكلة إن أغلب الـ instances العامة لـ Nitter صارت
غير مستقرة بشكل كبير، وممكن تتوقف فجأة.

**البوت مصمم يتعامل مع هذا بذكاء:**
- يجرب أكثر من instance بالتناوب (`nitter_instances` بملف الإعدادات).
- لو كل الـ instances فشلت، يتجاوز جزء X فقط ويكمل إرسال أخبار RSS بشكل طبيعي.
- لن يوقف البوت بالكامل بسبب فشل جزء X.

**لو تبي حل مستقر على المدى الطويل لاحقاً:**
- استخدام X API الرسمي (pay-per-use، حوالي $5 لكل 1000 قراءة تغريدة).
- أو استضافة RSS Bridge بنفسك (حل بديل، لكنه أيضاً غير مضمون 100%).

---

## 4) هيكل المشروع

```
cybernews-bot/
├── main.py                      # نقطة التشغيل الرئيسية
├── config.json                  # الإعدادات (مصادر RSS وحسابات X)
├── requirements.txt             # المكتبات المطلوبة
├── modules/
│   ├── rss_fetcher.py           # سحب من مواقع RSS
│   ├── twitter_fetcher.py       # سحب من X عبر Nitter (best-effort)
│   ├── image_extractor.py       # استخراج صورة الخبر
│   ├── telegram_sender.py       # الإرسال لتيليجرام
│   └── state_manager.py         # منع تكرار إرسال نفس الخبر
├── state/
│   └── seen_items.json          # سجل الأخبار المرسلة (يتحدث تلقائياً)
└── .github/workflows/
    └── run-bot.yml              # جدولة GitHub Actions
```

---

## 5) اختبار محلي قبل الرفع (اختياري)

```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN="التوكن_هنا"
export TELEGRAM_CHAT_ID="الآيدي_هنا"
python main.py
```

---

## 6) أشياء تقدر تضيفها لاحقاً

- تصنيف الأخبار حسب الخطورة أو الكلمات المفتاحية (CVE، ransomware...).
- ترجمة تلقائية للعربي قبل الإرسال.
- تجميع عدة أخبار برسالة واحدة بدل رسالة لكل خبر.
- استخدام Telegram Channel بدل Chat خاص للنشر العام.
