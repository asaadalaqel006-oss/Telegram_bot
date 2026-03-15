# 🤖 Evolve Books Bot

<div align="center">

بوت تيليجرام لمواد Evolve للإنجليزي مع نظام حماية متكامل ضد الإعلانات

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-20.7-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

</div>

---

## ✨ المميزات

| الميزة | التفاصيل |
|--------|---------|
| 📚 ردود تلقائية | يرد بمواد Evolve 2 و 3 و 4 فوراً |
| 🛡️ حماية ضد الإعلانات | يكتشف ويحذف الإعلانات تلقائياً |
| 🔨 حظر فوري | يحظر مرسلي الإعلانات من المجموعة |
| 🚫 فلترة ذكية | يمنع أرقام الهواتف والروابط والكلمات المحظورة |
| 📊 إحصائيات | أمر `/stats` للأدمن لمراقبة البوت |
| 📝 سجلات | يحفظ كل الأنشطة في `bot.log` |

---

## 📁 هيكل المشروع

```
evolve-bot/
├── bot.py              # الكود الرئيسي للبوت
├── config.py           # الإعدادات والكلمات المحظورة
├── requirements.txt    # المكتبات المطلوبة
├── .gitignore          # ملفات مستثناة من Git
└── README.md           # هذا الملف
```

---

## 🚀 طريقة التشغيل

### 1️⃣ الحصول على التوكن من BotFather

```
1. ابحث في تيليجرام عن: @BotFather
2. أرسل: /newbot
3. اختر اسماً للبوت
4. اختر username (ينتهي بـ bot)
5. احتفظ بالتوكن
```

### 2️⃣ استنساخ المشروع

```bash
git clone https://github.com/YOUR_USERNAME/evolve-bot.git
cd evolve-bot
```

### 3️⃣ تثبيت المكتبات

```bash
pip install -r requirements.txt
```

### 4️⃣ وضع التوكن

افتح `config.py` وعدّل هذا السطر:

```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
# غيّره إلى:
BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
```

### 5️⃣ تشغيل البوت

```bash
python bot.py
```

---

## ⚙️ إعداد البوت كأدمن في المجموعة

> **مهم جداً!** لكي يعمل نظام الحماية، يجب:

1. أضف البوت للمجموعة
2. اجعله **أدمن** مع صلاحيات:
   - ✅ حذف الرسائل
   - ✅ حظر الأعضاء

---

## 💬 أوامر البوت

| الأمر | الوظيفة |
|-------|---------|
| `/start` | رسالة الترحيب |
| `/help` | شرح طريقة الاستخدام |
| `/stats` | إحصائيات (للأدمن فقط) |
| `ايفولف 2` | مواد المستوى الثاني |
| `ايفولف 3` | مواد المستوى الثالث |
| `ايفولف 4` | مواد المستوى الرابع |

---

## 🛡️ نظام الحماية

البوت يكتشف ويحذف الرسائل التي تحتوي على:

- 📵 **كلمات محظورة**: "خدمات طلابية"، "حل واجبات"، "واتساب"، "سكليف"، إلخ
- 📞 **أرقام هواتف**: أي رقم دولي أو محلي
- 🔗 **روابط**: أي رابط خارجي (عدا الروابط المصرح بها)
- 💬 **عبارات إعلانية**: "للتواصل خاص"، "خصم"، إلخ

---

## 🔧 إضافة كلمات محظورة جديدة

افتح `config.py` وأضف الكلمة في قائمة `BANNED_WORDS`:

```python
BANNED_WORDS = [
    "كلمة جديدة",   # ← أضف هنا
    ...
]
```

---

## ☁️ التشغيل على السيرفر (24/7)

### Railway.app (مجاني)

```
1. أنشئ حساباً على railway.app
2. ارفع المشروع من GitHub
3. أضف متغير البيئة: BOT_TOKEN
```

### Linux (systemd)

```bash
sudo nano /etc/systemd/system/evolvebot.service
```

```ini
[Unit]
Description=Evolve Telegram Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/evolve-bot
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable evolvebot
sudo systemctl start evolvebot
```

---

## 📄 الترخيص

MIT License — يمكنك الاستخدام والتعديل بحرية.
