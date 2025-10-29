import os
import re
import requests
import yt_dlp
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ============= BOT TOKEN =============
TOKEN = os.environ.get("TELEGRAM_TOKEN") or "8236377322:AAHBz9VxoVnS6Pd7kD8RR40Rumd7Ok_vY00"

# ============= INSTAGRAM DOWNLOADER =============
def get_instagram_video(url: str):
    try:
        api = f"https://snapinsta.app/action.php?url={url}&action=post"
        res = requests.get(api, timeout=15)
        if res.status_code != 200:
            print("❌ Instagram API Error:", res.text[:100])
            return None, None
        media_links = re.findall(r'https://[^"]+\.mp4', res.text)
        if not media_links:
            return None, None
        return media_links[0], "✅ Downloaded from Instagram!"
    except Exception as e:
        print("Instagram Error:", e)
        return None, None

# ============= YOUTUBE DOWNLOADER =============
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

# ============= MAIN HANDLER =============
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    text = message.text.strip() if message.text else ""

    if not text or not re.match(r"https?://", text):
        await message.reply_text("📎 Send a valid Instagram or YouTube link!")
        return

    await message.reply_text("⏳ Processing... Please wait...")

    try:
        if "instagram.com" in text:
            media, caption = get_instagram_video(text)
            if media:
                await message.reply_video(video=media, caption=caption)
            else:
                await message.reply_text("❌ Couldn't fetch Instagram video (try a public post).")
            return

        elif "youtube.com" in text or "youtu.be" in text:
            filepath = get_youtube_video(text)
            if filepath:
                await message.reply_video(video=open(filepath, "rb"), caption="✅ Downloaded from YouTube!")
                os.remove(filepath)
            else:
                await message.reply_text("❌ YouTube download failed. Try a different link.")
            return

        else:
            await message.reply_text("⚠️ Only Instagram or YouTube links are supported.")

    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)[:200]}")

# ============= RUN BOT =============
async def main():
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
        raise SystemExit("❌ TELEGRAM_TOKEN missing. Add it in Railway/Render/Replit variables.")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🚀 Bot is running and waiting for messages...")
    await app.initialize()
    await app.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
