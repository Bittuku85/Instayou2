import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# 🧩 अपना Telegram bot token यहाँ डालो
TOKEN = "8236377322:AAHBz9VxoVnS6Pd7kD8RR40Rumd7Ok_vY00"

# (Optional) अगर private / age-restricted videos हैं तो cookies.txt upload कर सकते हो
COOKIES_FILE = "cookies.txt"

# ---------- Download Highest Quality YouTube Video ----------
def download_highest_quality(url):
    try:
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            "merge_output_format": "mp4",
            "outtmpl": "video.mp4",
            "quiet": True,
            "cookiefile": COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return "video.mp4"
    except Exception as e:
        print("Download error:", e)
        return None

# ---------- Handle YouTube Link ----------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "youtu" not in url:
        await update.message.reply_text("📎 Please send a valid YouTube link only.")
        return

    await update.message.reply_text("⏳ Downloading the highest quality video...")

    video_path = download_highest_quality(url)
    if not video_path or not os.path.exists(video_path):
        await update.message.reply_text("❌ Failed to download video. It might be private or blocked.")
        return

    try:
        await update.message.reply_video(
            video=open(video_path, "rb"),
            caption="✅ Here's your video in the highest available quality!",
            supports_streaming=True
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Can't send video: {e}")
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)

# ---------- Start Bot ----------
if __name__ == "__main__":
    print("🚀 YouTube HD Downloader Bot is running...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
