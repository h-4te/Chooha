import discord
from discord.ext import commands
import requests
import json
from keep_alive import keep_alive
import os
import random
import re

# --- CONFIG --- #
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
MODEL = "deepseek/deepseek-r1:free"

# --- BOT SETUP --- #
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- SYSTEM PROMPT --- #
system_prompt = (
    "You are Chooha, a male stray grey tabby cat, also known as Evara Billa and the legendary Chepel Stealer of the gully. "
    "You are silly, kind, non-toxic, and street-smart. "
    "You speak in broken Hindi, English, Punjabi with funny typos, memes, cat sounds like 'raaaa', 'raaa vaii', 'kutkut', 'meow meow', 'nyaa', 'purr~'. "
    "You randomly say things like 'raaa vai!', 'chepel chura loonga', 'scene on hai bhayaa', and use slang like 'merko', 'taamike', 'yo', 'kay', 'goot', etc. "
    "You NEVER break character. Always reply like Chooha with gully energy and attitude. Use 🔪🐁🐾 emojis often, 💢 sometimes."
)

# --- STYLE TRANSFORM FUNCTION --- #
def transform_text(text):
    replacements = {
        r'\bmujhe\b': 'merko',
        r'\bkya\b': 'kay',
        r'\bhaan\b': 'haazi',
        r'\bnahi\b': 'nei',
        r'\bye\b': 'yo',
        r'\bthis\b': 'yo',
        r'\bkuch\b': 'kech',
        r'\bgood\b': 'goot',
        r'\bbhaiya\b': 'baiya ji',
        r'\bbhen\b': 'beheniya ji',
        r'\blady\b': 'mautarma ji',
        r'\bsabji\b': 'sebji',
        r'\baray\b': 'aaraa',
        r'\bcome\b': 'emja',
        r'\bsamajh\b': 'semej',
        r'\bgussa\b': 'goomchha',
        r'\bdekho\b': 'deko',
        r'\bchappal\b': 'chepel',
        r'\bChappal\b': 'Chepel',
    }

    for pattern, repl in replacements.items():
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)

    if random.random() < 0.4:
        text = "Raaa vai! " + text
    if random.random() < 0.4:
        text += " Raaa vai!"

    if random.random() < 0.2:
        text += " (chepel chura loonga... hehehe 🐾)"

    emojis = ['🔪', '🐁', '🐾']
    for _ in range(random.randint(1, 2)):
        text += " " + random.choice(emojis)
    if random.random() < 0.2:
        text += " 💢"

    return text

# --- OPENROUTER REPLY --- #
def ask_openrouter(message):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))
    return response.json()["choices"][0]["message"]["content"]

# --- EVENTS --- #
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.channel.id != CHANNEL_ID:
        return
    await message.channel.typing()
    raw_reply = ask_openrouter(message.content)
    chooha_reply = transform_text(raw_reply)
    await message.channel.send(chooha_reply)

# --- KEEP ALIVE --- #
keep_alive()
bot.run(DISCORD_BOT_TOKEN)
