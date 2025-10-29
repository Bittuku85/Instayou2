import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8236377322:AAHBz9VxoVnS6Pd7kD8RR40Rumd7Ok_vY00"  # 👈 अपना token डालो

# ---------- YouTube Downloader ----------
def download_youtube(url):
    try:
        # पहले 1080p ट्राय करेगा, फिर fallback करेगा
        quality_options = [
            "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "bestvideo[height<=480]+bestaudio/best[height<=480]",
        ]
        for quality in quality_options:
            print(f"🔹 Trying quality: {quality}")
            ydl_opts = {
                "format": quality,
                "merge_output_format": "mp4",
                "outtmpl": "ytvideo.mp4",
                "quiet": True,
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                if os.path.exists("ytvideo.mp4"):
                    return "ytvideo.mp4"
            except Exception as e:
                print("YT Error:", e)
                continue
        return None
    except Exception as e:
        print("Download Error:", e)
        return None

# ---------- Handler ----------
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()
    chat_id = update.message.chat_id

    if "youtu" not in msg:
        await update.message.reply_text("📎 Please send a YouTube link only.")
        return

    await update.message.reply_text("⏳ Downloading video (up to 1080p)...")

    path = download_youtube(msg)
    if not path:
        await update.message.reply_text("❌ Couldn't download video. It may be private or too large.")
        return

    try:
        await context.bot.send_video(
            chat_id=chat_id,
            video=open(path, "rb"),
            caption="✅ Here is your YouTube video!",
            supports_streaming=True
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Can't send file: {e}")
    finally:
        if os.path.exists(path):
            os.remove(path)

# ---------- Start Bot ----------
if __name__ == "__main__":
    print("🚀 YouTube Downloader Bot is running...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()
