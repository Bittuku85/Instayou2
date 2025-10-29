from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import yt_dlp, requests, re, os

TOKEN = "8236377322:AAHBz9VxoVnS6Pd7kD8RR40Rumd7Ok_vY00"  # 🔸 यहां अपना असली BotFather वाला token डालो

# ---------- YouTube ----------
def download_youtube(url):
    try:
        ydl_opts = {
            "format": "best[ext=mp4][filesize<45M]",
            "outtmpl": "ytvideo.mp4",
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return "ytvideo.mp4"
    except Exception as e:
        print("YT Error:", e)
        return None

# ---------- Instagram ----------
def get_instagram_link(url):
    try:
        api = f"https://saveig.app/api/ajaxSearch?query={url}"
        res = requests.get(api, timeout=10).json()
        media = res["data"][0]["url"]
        caption = res["data"][0].get("caption", "")
        return media, caption
    except Exception as e:
        print("IG Error:", e)
        return None, None

# ---------- Handler ----------
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()
    chat_id = update.message.chat_id

    if not re.match(r"https?://", msg):
        await update.message.reply_text("📎 Send me a *YouTube* or *Instagram* link.", parse_mode="Markdown")
        return

    await update.message.reply_text("⏳ Processing...")

    if "youtu" in msg:
        path = download_youtube(msg)
        if not path:
            await update.message.reply_text("❌ Video too large or download failed.")
            return
        await context.bot.send_video(chat_id, open(path, "rb"), caption="✅ Downloaded from YouTube!")
        os.remove(path)
        return

    if "instagram.com" in msg:
        link, caption = get_instagram_link(msg)
        if not link:
            await update.message.reply_text("❌ Couldn't fetch Instagram video.")
            return
        await update.message.reply_text(f"🎬 Video link:\n{link}\n\n{caption or ''}")
        return

    await update.message.reply_text("⚠️ Only YouTube & Instagram supported.")

# ---------- Start Bot ----------
if __name__ == "__main__":
    print("🚀 Bot is running...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()
