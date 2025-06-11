import discord
import os
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import pytz
import re

load_dotenv()
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 123456789012345678  # Заменить на ID канала
MOD_LOG_ID = 987654321098765432  # ID канала для логов модерации
MAX_WARNINGS = 3

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

client = discord.Client(intents=intents)
scheduler = AsyncIOScheduler()

BAD_WORDS = [
    "дурак", "идиот", "тупой", "сволочь", "блин", "чёрт",
    "fuck", "shit", "bitch", "asshole", "сука", "пиздец", "нахуй"
]

warnings = {}
tz = pytz.timezone('Europe/Moscow')

@client.event
async def on_ready():
    print(f"✅ Нэкома запущена как {client.user}")
    scheduler.start()
    scheduler.add_job(send_good_morning, 'cron', hour=8, minute=0, timezone=tz)
    scheduler.add_job(send_good_night, 'cron', hour=23, minute=0, timezone=tz)

async def send_good_morning():
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("🌅 Доброе утро, мяу! Пусть день будет пушистым и солнечным ☀️")

async def send_good_night():
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("🌙 Спокойной ночи, мяу... Сладких снов и тёплого пледа 💤")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content.lower()

    if any(re.search(rf"\\b{word}\\b", content) for word in BAD_WORDS):
        try:
            await message.delete()
            user_id = message.author.id
            warnings[user_id] = warnings.get(user_id, 0) + 1
            count = warnings[user_id]

            if count < MAX_WARNINGS:
                await message.channel.send(f"🚫 {message.author.mention}, это предупреждение №{count}. Будь вежливее, мяу.")
            else:
                await message.guild.ban(message.author, reason="Токсичное поведение")
                await message.channel.send(f"🔨 {message.author.mention} был забанен. Моё терпение — не безгранично, мяу 😼")
                log_channel = client.get_channel(MOD_LOG_ID)
                if log_channel:
                    await log_channel.send(f"🚨 {message.author} забанен за превышение количества предупреждений.")
        except discord.Forbidden:
            print("❌ Недостаточно прав для модерации.")
        return

    if content == "привет":
        await message.channel.send("Мяу! Привет, я Нэкома~ 🐾")

    if "нэкома" in content:
        await message.channel.send("Кто звал Нэкому? Я тут как тут, мяу 💙")

@client.event
async def on_member_join(member):
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(f"✨ Добро пожаловать, {member.mention}! Чувствуй себя как дома, мяу~")

@client.event
async def on_member_remove(member):
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(f"💨 {member.name} покинул сервер... До новых встреч, мяу.")

client.run(TOKEN)

