import os, re, asyncio, requests, yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TELEGRAM_TOKEN") or "8236377322:AAHBz9VxoVnS6Pd7kD8RR40Rumd7Ok_vY00"

# ---------- YouTube ----------
def fetch_youtube(url):
    try:
        ydl_opts = {
            "format": "best[ext=mp4][filesize<45M]",  # 45 MB cap (Telegram free limit)
            "outtmpl": "ytvideo.mp4",
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return "ytvideo.mp4"
    except Exception as e:
        print("YT-Error:", e)
        return None

# ---------- Instagram ----------
def fetch_instagram(url):
    try:
        api = f"https://saveig.app/api/ajaxSearch?query={url}"
        res = requests.get(api, timeout=10).json()
        media = res["data"][0]["url"]
        caption = res["data"][0].get("caption", "")
        return media, caption
    except Exception as e:
        print("IG-Error:", e)
        return None, None

# ---------- Handler ----------
async def handle(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    text = (msg.text or "").strip()

    if not re.match(r"https?://", text):
        await msg.reply_text("📎 Send any *YouTube* or *Instagram* link.", parse_mode="Markdown")
        return

    await msg.reply_text("⏳ Processing your link…")

    # ---- YouTube ----
    if "youtu" in text:
        path = fetch_youtube(text)
        if not path:
            await msg.reply_text("❌ Failed to fetch or too large (>45 MB).")
            return
        try:
            await msg.reply_video(open(path, "rb"), caption="✅ Downloaded from YouTube!")
        except Exception as e:
            await msg.reply_text(f"⚠️ Can't send: {e}")
        finally:
            if os.path.exists(path):
                os.remove(path)
        return

    # ---- Instagram ----
    if "instagram.com" in text:
        link, caption = fetch_instagram(text)
        if not link:
            await msg.reply_text("❌ Couldn't fetch Instagram video (public posts only).")
            return
        await msg.reply_text(f"✅ Video link:\n{link}\n\n{caption or ''}")
        return

    await msg.reply_text("⚠️ Only Instagram & YouTube supported.")

# ---------- Start ----------
async def main():
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
        raise SystemExit("❌ TELEGRAM_TOKEN not set.")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("🚀 Bot running…")
    await app.initialize()
    await app.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
