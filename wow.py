from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import subprocess
import datetime

# ===== CONFIG =====
BOT_TOKEN = "8568883176:AAFd-e1XZE0VkRSSO0qRNTkO3pEivvfrRJk"
ADMIN_IDS = 7564665369
ALLOWED_CMDS = ['ls', 'pwd', 'node -v', 'npm -v', 'uptime', 'whoami']
LOG_FILE = "bot_command.log"
# ==================

# ====== Start / Menu ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Status", callback_data="STATUS")],
        [InlineKeyboardButton("⚙️ Commands", callback_data="CMDS")],
    ]
    await update.message.reply_text(
        "🤖 Welcome to Advanced Bot\nChoose an option:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# ====== Button Actions ======
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id not in ADMIN_IDS:
        await query.message.reply_text("❌ Admin only")
        return

    if query.data == "STATUS":
        await query.message.reply_text("✅ Bot running normally")

    elif query.data == "CMDS":
        cmds = "\n".join([f"• {c}" for c in ALLOWED_CMDS])
        await query.message.reply_text(
            f"📌 Allowed commands:\n{cmds}\n\nUse:\n/run <command>"
        )

# ====== Run Command ======
async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMIN_IDS:
        return

    text = update.message.text.strip()
    if not text.startswith("/run "):
        return

    cmd = text.replace("/run ", "", 1)

    if cmd not in ALLOWED_CMDS:
        await update.message.reply_text("⛔ Command not allowed")
        return

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)

        # log command
        with open(LOG_FILE, "a") as f:
            f.write(f"{datetime.datetime.now()} - {update.message.from_user.id} ran: {cmd}\n")

        if result.stdout:
            await update.message.reply_text(f"📤 Output:\n{result.stdout[:3800]}")
        if result.stderr:
            await update.message.reply_text(f"⚠️ Error:\n{result.stderr[:3800]}")

    except Exception as e:
        await update.message.reply_text("❌ Error executing command")

# ====== Main ======
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT, run_command))

    print("✅ Advanced Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()