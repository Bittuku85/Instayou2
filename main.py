import os
import yt_dlp
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from telegram.ext import CommandHandler

TOKEN = "8236377322:AAHBz9VxoVnS6Pd7kD8RR40Rumd7Ok_vY00"

# Global dict to store user video formats
user_video_data = {}

# ---------- Step 1: When user sends YouTube link ----------
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    chat_id = update.message.chat_id

    if "youtu" not in text:
        await update.message.reply_text("📎 Please send a valid YouTube link only.")
        return

    await update.message.reply_text("🔍 Fetching available qualities...")

    try:
        ydl_opts = {"quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(text, download=False)

        formats = []
        for f in info.get("formats", []):
            if f.get("height") and f.get("ext") == "mp4":
                height = f["height"]
                filesize = f.get("filesize") or f.get("filesize_approx")
                if filesize and filesize < 50 * 1024 * 1024:  # under 50MB
                    formats.append(str(height))

        # Remove duplicates and sort
        qualities = sorted(list(set(formats)))
        if not qualities:
            await update.message.reply_text("❌ No downloadable formats found under 50MB.")
            return

        # Save formats
        user_video_data[chat_id] = {"url": text, "formats": qualities}

        # Send options
        options = "\n".join([f"🎬 {q}p" for q in qualities])
        await update.message.reply_text(
            f"✅ Available qualities:\n\n{options}\n\n📩 Reply with your desired quality (e.g. 720)"
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Failed to fetch qualities: {e}")

# ---------- Step 2: When user replies with quality ----------
async def handle_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    quality = update.message.text.strip().replace("p", "")

    if chat_id not in user_video_data:
        await update.message.reply_text("⚠️ Please send a YouTube link first.")
        return

    url = user_video_data[chat_id]["url"]
    if quality not in user_video_data[chat_id]["formats"]:
        await update.message.reply_text("❌ Invalid quality. Please choose from the listed options.")
        return

    await update.message.reply_text(f"⏳ Downloading video in {quality}p...")

    # Download specific quality
    try:
        ydl_opts = {
            "format": f"bestvideo[height={quality}]+bestaudio/best[height={quality}]",
            "merge_output_format": "mp4",
            "outtmpl": "ytvideo.mp4",
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.exists("ytvideo.mp4"):
            await context.bot.send_video(
                chat_id=chat_id,
                video=open("ytvideo.mp4", "rb"),
                caption=f"✅ Here is your {quality}p video!",
                supports_streaming=True,
            )
            os.remove("ytvideo.mp4")
        else:
            await update.message.reply_text("❌ Failed to download this quality (may exceed 50MB).")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error while downloading: {e}")

# ---------- Start Command ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send a YouTube link to get available qualities!")

# ---------- Start Bot ----------
if __name__ == "__main__":
    print("🚀 Interactive YouTube Bot is running...")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex(r"https?://(www\.)?youtu"), handle_link))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quality))

    app.run_polling()
