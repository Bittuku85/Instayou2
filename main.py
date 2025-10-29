import os
import re
import requests
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# 🔹 अपना BotFather वाला Token नीचे डालो
TOKEN = "8236377322:AAHBz9VxoVnS6Pd7kD8RR40Rumd7Ok_vY00"

# ---------- YouTube Downloader ----------
def download_youtube(url):
    try:
        ydl_opts = {
            "format": "best[ext=mp4][filesize<45M]",  # 45 MB limit
            "outtmpl": "ytvideo.mp4",
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return "ytvideo.mp4"
    except Exception as e:
        print("YT Error:", e)
        return None

# ---------- Instagram Downloader (public reels only) ----------
def get_instagram_link(url):
    try:
        api = "https://igram.world/api/igdl"
        res = requests.post(api, json={"url": url}, timeout=10).json()
        media = res["result"][0]["url"]
        caption = res["result"][0].get("caption", "")
        return media, caption
    except Exception as e:
        print("IG Error:", e)
        return None, None

# ---------- Handler Function ----------
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()
    chat_id = update.message.chat_id

    if not re.match(r"https?://", msg):
        await update.message.reply_text("📎 Send any *YouTube* or *Instagram* link.", parse_mode="Markdown")
        return

    await update.message.reply_text("⏳ Processing your link...")

    # ---- YouTube ----
    if "youtu" in msg:
        path = download_youtube(msg)
        if not path:
            await update.message.reply_text("❌ Failed to download or video is too large.")
            return
        await context.bot.send_video(chat_id, open(path, "rb"), caption="✅ Downloaded from YouTube!")
        os.remove(path)
        return

    # ---- Instagram ----
    if "instagram.com" in msg:
        link, caption = get_instagram_link(msg)
        if not link:
            await update.message.reply_text("❌ Couldn't fetch Instagram video (public reels only).")
            return
        await update.message.reply_text(f"🎬 Video link:\n{link}\n\n{caption or ''}")
        return

    await update.message.reply_text("⚠️ Only YouTube & Instagram supported for now.")

# ---------- Start Bot ----------
if __name__ == "__main__":
    print("🚀 Bot is running...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()
