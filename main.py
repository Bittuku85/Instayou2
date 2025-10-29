import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)

TOKEN = "8236377322:AAHBz9VxoVnS6Pd7kD8RR40Rumd7Ok_vY00"  # 👈 अपना BotFather token डालो
COOKIES_FILE = "cookies.txt"   # 👈 optional (browser से cookies export करके डाल सकते हो)

# ---------- Get Available Qualities ----------
def get_yt_qualities(url):
    try:
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "cookiefile": COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get("formats", [])
            quality_dict = {}
            for f in formats:
                height = f.get("height")
                ext = f.get("ext")
                if height and ext == "mp4":
                    quality_dict[f"{height}p"] = f["format_id"]
            return sorted(set(quality_dict.keys()), key=lambda x: int(x.replace("p", "")))
    except Exception as e:
        print("Fetch qualities error:", e)
        return None

# ---------- Download Specific Quality ----------
def download_yt_video(url, format_id):
    try:
        ydl_opts = {
            "format": format_id,
            "outtmpl": "ytvideo.mp4",
            "quiet": True,
            "merge_output_format": "mp4",
            "cookiefile": COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return "ytvideo.mp4"
    except Exception as e:
        print("Download error:", e)
        return None

# ---------- Step 1: Handle YouTube link ----------
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "youtu" not in url:
        await update.message.reply_text("📎 Please send a valid YouTube link only.")
        return

    await update.message.reply_text("🔍 Fetching available qualities...")
    qualities = get_yt_qualities(url)
    if not qualities:
        await update.message.reply_text("⚠️ Failed to fetch qualities. Maybe login is required or the video is private.")
        return

    # Save URL in user data for later
    context.user_data["url"] = url

    # Create buttons for each quality
