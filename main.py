import os
import re
import requests
import yt_dlp
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# --- Telegram Token ---
TOKEN = os.environ.get("TELEGRAM_TOKEN") or "8236377322:AAHBz9VxoVnS6Pd7kD8RR40Rumd7Ok_vY00"

# --- Instagram Downloader ---
def get_instagram_video(url: str):
    try:
        api_url = f"https://saveig.app/api/ajaxSearch?query={url}"
        res = requests.get(api_url).json()
        media = res["data"][0]["url"]
        caption = res["data"][0].get("caption", "")
        return media, caption
    except Exception as e:
        print("Instagram Error:", e)
        return None, None

# --- YouTube Downloader ---
def get_youtube_video(url: str):
    try:
        ydl_opts = {
            "outtmpl": "video.mp4",
            "format": "best[ext=mp4]",
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return "video.mp4"
    except Exception as e:
        print("YouTube Error:", e)
        return None

# --- Main Handler ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    text = message.text.strip() if message.text else ""

    if not re.match(r"https?://", text):
        await message.reply_text("📎 Please send a valid YouTube or Instagram link!")
        return

    await message.reply_text("⏳ Processing your link... Please wait...")

    if "instagram.com" in text:
        media, caption = get_instagram_video(text)
        if media:
            await message.reply_video(video=media, caption=caption or "✅ Downloaded from Instagram!")
        else:
            await message.reply_text("❌ Failed to download Instagram video.")
        return

    elif "youtube.com" in text or "youtu.be" in text:
        filepath = get_youtube_video(text)
        if filepath:
            try:
                await message.reply_video(video=open(filepath, "rb"), caption="✅ Downloaded from YouTube!")
            finally:
                os.remove(filepath)
        else:
            await message.reply_text("❌ Failed to download YouTube video.")
        return

    else:
        await message.reply_text("⚠️ Only Instagram and YouTube links are supported.")

# --- Start Bot (Async) ---
async def main():
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
        raise SystemExit("❌ TELEGRAM_TOKEN missing in environment variables.")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 Bot is running... Waiting for messages...")
    await app.initialize()
    await app.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
