import os
import json
import datetime
import asyncio
import logging
from aiogram import Bot
from aiogram.types import InputFile
from config import BOT_TOKEN, ADMIN_ID, MEDIA_FOLDER, BROADCAST_HOURS
from database import get_all_user_ids

bot = Bot(token=BOT_TOKEN)

# Logging
logging.basicConfig(filename="broadcast.log", level=logging.INFO, format='[%(asctime)s] %(message)s')
def log(msg): print(msg); logging.info(msg)

async def send_broadcast_to_all():
    try:
        with open("captions.json", "r", encoding="utf-8") as f:
            captions = json.load(f)
    except Exception as e:
        log(f"❌ Gagal baca captions.json: {e}")
        return

    if not captions:
        log("⚠️ captions.json kosong.")
        return

    user_ids = get_all_user_ids()
    total_users = len(user_ids)

    for filename, caption in captions.items():
        media_path = os.path.join(MEDIA_FOLDER, filename)
        success, failed = 0, 0

        log(f"🚀 Kirim: {filename} - ke {total_users} user")

        for uid in user_ids:
            try:
                if os.path.isfile(media_path):
                    if filename.endswith(('.jpg', '.jpeg', '.png')):
                        await bot.send_photo(uid, photo=InputFile(media_path), caption=caption)
                    elif filename.endswith('.mp4'):
                        await bot.send_video(uid, video=InputFile(media_path), caption=caption)
                    else:
                        await bot.send_message(uid, text=caption)
                else:
                    await bot.send_message(uid, text=caption)  # fallback caption only
                success += 1
            except Exception as e:
                failed += 1
                with open("failed_users.txt", "a") as f:
                    f.write(f"{uid}\n")
                log(f"❌ {uid} gagal: {e}")

        summary = f"📦 Broadcast [{filename}]:\n✅ {success} sukses\n❌ {failed} gagal"
        log(summary)
        await bot.send_message(ADMIN_ID, summary)

async def scheduler():
    sudah_dikirim = set()
    while True:
        now = datetime.datetime.now()
        jam = now.hour

        if jam in BROADCAST_HOURS and jam not in sudah_dikirim:
            await send_broadcast_to_all()
            sudah_dikirim.add(jam)

        if jam == 0:
            sudah_dikirim.clear()

        await asyncio.sleep(60)

async def main():
    log("✅ Bot auto-broadcast aktif.")
    await scheduler()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log("🛑 Bot dihentikan.")
