import asyncio
import requests
import random
from rubika_bot_api.api import Robot
from rubika_bot_api import filters

# ========= تنظیمات =========
RUBIKA_TOKEN = "FGGCF0ZCZKMWPBMJKTNIBMUONOFASGPZOWOUDJWMSXJVWYTGBCDEDHFCRTKPWJCG"
GROQ_API_KEY = "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"

bot = Robot(token=RUBIKA_TOKEN)

# ========= پاسخ‌های کوتاه =========
SHORT_REPLIES = [
    "جانم",
    "هستم",
    "بگو",
    "چی شده",
    "گوش می‌دم",
    "بله",
    "هوم؟"
]

# ========= شخصیت =========
SYSTEM_PROMPT = """
اسم تو حشمت است.
خیلی کوتاه و محاوره‌ای جواب بده.
حداکثر ۳ تا ۶ کلمه.
غیررسمی، غیرکتابی.
مثل شوهر خودمونی حرف بزن.
"""

# ========= حافظه =========
memory = {}
MAX_MEMORY = 6

def ask_ai(chat_id, user_id, user_text):
    if chat_id not in memory:
        memory[chat_id] = {}
    if user_id not in memory[chat_id]:
        memory[chat_id][user_id] = []

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(memory[chat_id][user_id])
    messages.append({"role": "user", "content": user_text})

    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-8b-8192",
            "messages": messages,
            "temperature": 0.6
        },
        timeout=20
    )

    reply = r.json()["choices"][0]["message"]["content"]

    memory[chat_id][user_id].append({"role": "user", "content": user_text})
    memory[chat_id][user_id].append({"role": "assistant", "content": reply})

    if len(memory[chat_id][user_id]) > MAX_MEMORY * 2:
        memory[chat_id][user_id] = memory[chat_id][user_id][-MAX_MEMORY * 2:]

    return reply

# ========= هندل پیام =========
@bot.on_message(filters.text)
async def handle_message(bot_instance, message):
    if message.chat_type != "Group":
        return

    text = (message.text or "").strip()
    if not text:
        return

    triggers = ["حشمت", "ربات"]

    # فقط اسم
    if text in triggers:
        await bot_instance.send_message(
            message.chat_id,
            random.choice(SHORT_REPLIES)
        )
        return

    # اسم + حرف
    if any(t in text for t in triggers):
        cleaned = text
        for t in triggers:
            cleaned = cleaned.replace(t, "")
        cleaned = cleaned.strip()

        if not cleaned:
            await bot_instance.send_message(
                message.chat_id,
                random.choice(SHORT_REPLIES)
            )
            return

        reply = ask_ai(
            message.chat_id,
            message.author_object_guid,
            cleaned
        )

        await bot_instance.send_message(message.chat_id, reply)

# ========= اجرا =========
if __name__ == "__main__":
    print("🤖 حشمت آنلاین شد")
    asyncio.run(bot.run())