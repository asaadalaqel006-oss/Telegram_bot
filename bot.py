#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 بوت تيليجرام - Evolve Books Bot (نسخة محمية)
=================================================
✅ يرد على كلمات مفتاحية بروابط الكتب
🛡️ يحذف الإعلانات والمحتوى المسيء تلقائياً
🔨 يحظر المستخدمين المخالفين فوراً
"""

import logging
import asyncio
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.error import TelegramError
from telegram.constants import ChatMemberStatus

from config import (
    BOT_TOKEN,
    RESPONSES,
    BANNED_WORDS,
    COMPILED_PHONE_PATTERNS,
    COMPILED_URL_PATTERNS,
)

# ===================================================
# ⚙️ إعداد السجلات
# ===================================================
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


# ===================================================
# 🛡️ دالة فحص الرسالة
# ===================================================
def is_spam(text: str) -> tuple[bool, str]:
    """
    يفحص النص ويعيد (True, السبب) إذا كان محتوى محظوراً
    أو (False, '') إذا كان نظيفاً
    """
    text_lower = text.lower()

    # 1️⃣ فحص الكلمات المحظورة
    for word in BANNED_WORDS:
        if word.lower() in text_lower:
            return True, f"كلمة محظورة: {word}"

    # 2️⃣ فحص أرقام الهواتف
    for pattern in COMPILED_PHONE_PATTERNS:
        match = pattern.search(text)
        if match:
            return True, f"رقم هاتف: {match.group()}"

    # 3️⃣ فحص الروابط
    for pattern in COMPILED_URL_PATTERNS:
        match = pattern.search(text)
        if match:
            return True, f"رابط محظور: {match.group()}"

    return False, ""


# ===================================================
# 🔨 دالة الحذف والحظر
# ===================================================
async def delete_and_ban(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    reason: str,
) -> None:
    """يحذف الرسالة ويحظر المستخدم من المجموعة"""
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    # حذف الرسالة
    try:
        await message.delete()
        logger.info(f"🗑️ حُذفت رسالة من {user.full_name} (ID:{user.id}) | {reason}")
    except TelegramError as e:
        logger.warning(f"⚠️ فشل الحذف: {e}")

    # حظر المستخدم
    try:
        await context.bot.ban_chat_member(chat_id=chat.id, user_id=user.id)
        logger.info(f"🔨 حُظر: {user.full_name} (ID:{user.id})")

        # إشعار المجموعة
        ban_msg = await context.bot.send_message(
            chat_id=chat.id,
            text=(
                f"⛔️ تم حظر المستخدم تلقائياً\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 المستخدم: {user.full_name}\n"
                f"🆔 الآيدي: {user.id}\n"
                f"📌 السبب: {reason}\n"
                f"🕐 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🛡️ البوت يحمي المجموعة من الإعلانات"
            ),
        )

        # حذف إشعار الحظر بعد 30 ثانية
        await asyncio.sleep(30)
        try:
            await ban_msg.delete()
        except TelegramError:
            pass

    except TelegramError as e:
        logger.warning(f"⚠️ فشل الحظر: {e}")


# ===================================================
# 💬 معالج رسائل المجموعات (حماية + ردود)
# ===================================================
async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """يعالج رسائل المجموعة: يفحص الإعلانات ثم يرد على الكلمات المفتاحية"""
    message = update.effective_message
    user    = update.effective_user
    chat    = update.effective_chat

    if not user or user.is_bot:
        return

    user_text = (message.text or "").strip()
    if not user_text:
        return

    # ── 1️⃣ فحص الحماية ──
    spam_detected, reason = is_spam(user_text)
    if spam_detected:
        try:
            bot_member = await chat.get_member(context.bot.id)
            if bot_member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                member = await chat.get_member(user.id)
                if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                    logger.warning(f"🚨 إعلان من {user.full_name} في {chat.title}: {reason}")
                    await delete_and_ban(update, context, reason)
                    return
        except TelegramError as e:
            logger.warning(f"⚠️ خطأ في فحص الصلاحيات: {e}")

    # ── 2️⃣ الرد على الكلمات المفتاحية ──
    if user_text in RESPONSES:
        data = RESPONSES[user_text]
        reply_text = f"{data['title']}\n\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for name, url in data["links"]:
            reply_text += f"{name}\n{url}\n\n"
        reply_text += "━━━━━━━━━━━━━━━━━━━━━━━━\n✅ استمتع بالتعلم! 🎓"
        await message.reply_text(reply_text)
        logger.info(f"✅ رد على '{user_text}' في {chat.title}")


# ===================================================
# 💬 معالج الرسائل الخاصة (Private)
# ===================================================
async def handle_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """يرد على الرسائل الخاصة بالروابط"""
    user      = update.effective_user
    user_text = update.message.text.strip()

    logger.info(f"📨 خاص من {user.full_name} (ID:{user.id}): {user_text}")

    if user_text in RESPONSES:
        data = RESPONSES[user_text]
        reply_text = f"{data['title']}\n\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for name, url in data["links"]:
            reply_text += f"{name}\n{url}\n\n"
        reply_text += "━━━━━━━━━━━━━━━━━━━━━━━━\n✅ استمتع بالتعلم! 🎓"
        await update.message.reply_text(reply_text)
        logger.info(f"✅ تم الرد على: {user_text}")


# ===================================================
# 🚀 أمر /start
# ===================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    text = (
        f"👋 أهلاً {user.first_name}!\n\n"
        "📚 بوت مواد Evolve للإنجليزي\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "اكتب إحدى الكلمات التالية:\n\n"
        "🔹 ايفولف 2\n"
        "🔹 ايفولف 3\n"
        "🔹 ايفولف 4\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "✨ وسيصلك كل شيء فوراً!\n"
        "🛡️ البوت يحمي المجموعة من الإعلانات تلقائياً"
    )
    await update.message.reply_text(text)
    logger.info(f"/start من: {user.full_name} (ID:{user.id})")


# ===================================================
# 🆘 أمر /help
# ===================================================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "📖 كيفية الاستخدام:\n\n"
        "▫️ ايفولف 2  ← مواد المستوى الثاني\n"
        "▫️ ايفولف 3  ← مواد المستوى الثالث\n"
        "▫️ ايفولف 4  ← مواد المستوى الرابع\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🛡️ نظام الحماية:\n"
        "⛔ يحذف الإعلانات تلقائياً\n"
        "🔨 يحظر مرسلي الإعلانات فوراً\n"
        "🚫 يمنع روابط واتساب وأرقام الهواتف"
    )
    await update.message.reply_text(text)


# ===================================================
# 📊 أمر /stats (للأدمن فقط)
# ===================================================
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    user = update.effective_user
    try:
        member = await chat.get_member(user.id)
        if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            await update.message.reply_text("⛔ هذا الأمر للأدمن فقط!")
            return
    except TelegramError:
        return

    text = (
        "📊 إحصائيات البوت\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 اسم البوت: {context.bot.first_name}\n"
        f"🆔 آيدي البوت: {context.bot.id}\n"
        f"🏠 المجموعة: {chat.title}\n"
        f"🔑 آيدي المجموعة: {chat.id}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🚫 الكلمات المحظورة: {len(BANNED_WORDS)}\n"
        "✅ النظام يعمل بشكل طبيعي"
    )
    await update.message.reply_text(text)


# ===================================================
# 🏁 الدالة الرئيسية
# ===================================================
def main() -> None:
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ خطأ: لم تضع التوكن في config.py!")
        print("💡 افتح config.py وعدّل السطر: BOT_TOKEN = '...'")
        return

    logger.info("🚀 جاري تشغيل البوت...")

    app = Application.builder().token(BOT_TOKEN).build()

    # أوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help",  help_command))
    app.add_handler(CommandHandler("stats", stats))

    # رسائل خاصة
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        handle_private_message,
    ))

    # رسائل المجموعات
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & (filters.ChatType.GROUP | filters.ChatType.SUPERGROUP),
        handle_group_message,
    ))

    logger.info("✅ البوت يعمل الآن! اضغط Ctrl+C للإيقاف")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
