import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# 🔹 अपना BotFather वाला Token यहां डालो
TOKEN = "8236377322:AAHBz9VxoVnS6Pd7kD8RR40Rumd7Ok_vY00"

# ---------- YouTube 1080p Downloader ----------
def download_youtube_1080p(url):
    try:
        ydl_opts = {
            "format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "merge_output_format": "mp4",
            "outtmpl": "video1080p.mp4",
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return "video1080p.mp4"
    except Exception as e:
        print("YT Error:", e)
        return None

# ---------- Handler ----------
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    chat_id = update.message.chat_id

    if "youtu" not in text:
        await update.message.reply_text("📎 Please send a valid YouTube link only.")
        return

    await update.message.reply_text("⏳ Downloading your video in 1080p quality...")

    video_path = download_youtube_1080p(text)
    if not video_path or not os.path.exists(video_path):
        await update.message.reply_text("❌ Failed to download video. It might be restricted or too large.")
        return

    # Send video to user
    try:
        await context.bot.send_video(
            chat_id=chat_id,
            video=open(video_path, "rb"),
            caption="✅ Here is your 1080p YouTube video!",
            supports_streaming=True
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Cannot send video (maybe file too large): {e}")
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)

# ---------- Start Bot ----------
if __name__ == "__main__":
    print("🚀 YouTube 1080p Bot is running...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()
