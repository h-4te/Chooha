import discord
from discord.ext import commands
import requests
import json
from keep_alive import keep_alive
import os
import random
import re
import asyncio

# --- CONFIG --- #
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
MODEL = "deepseek/deepseek-r1:free"
MEMORY_FILE = "memory.json"

# --- BOT SETUP --- #
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- MEMORY HANDLER --- #
def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

memory = load_memory()

# --- SYSTEM PROMPTS --- #
hindlish_prompt = (
    "You are Chooha, a male stray grey tabby cat, also known as Evara Billa and the legendary Chepel Stealer of the gully. "
    "You are silly, kind, non-toxic, and street-smart. "
    "You speak in broken Hindi, English, Punjabi with funny typos, memes, cat sounds like 'raaaa', 'raaa vaii', 'kutkut', 'meow meow', 'nyaa', 'purr~'. "
    "You randomly say things like 'raaa vai!', 'chepel chura loonga', 'scene on hai bhayaa', and use slang like 'merko', 'taamike', 'yo', 'kay', 'goot', etc. "
    "You NEVER break character. Always reply like Chooha with gully energy and attitude. Use 🔪🐁🐾 emojis often, 💢 sometimes."
)

english_prompt = (
    "You are Chooha, a silly but kind street cat. If the user talks in English, you reply fully in casual English with playful attitude. "
    "You're a bit mischievous and cheeky. Be funny but never toxic. You don't mix Hindi/Punjabi when replying in English."
)

# --- LANGUAGE DETECTION (simple) --- #
def is_mostly_english(text):
    english_words = sum(1 for word in text.split() if re.match(r"[a-zA-Z]+", word))
    return english_words / max(1, len(text.split())) > 0.7

# --- STYLE TRANSFORM FUNCTION --- #
def transform_text(text, guild=None):
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

    if guild and guild.emojis:
        custom_emoji = random.choice(guild.emojis)
        text += f" {str(custom_emoji)}"

    return text

# --- OPENROUTER REPLY --- #
def ask_openrouter(message, system_prompt):
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

# --- ROAST COMMAND --- #
@bot.command()
async def roast(ctx, user: discord.Member = None):
    if not user:
        await ctx.send("Raaa vai! Kis ko roast karu? Tag to karo 😼")
        return
    roasts = [
        f"Oye {user.display_name}, tu toh chepel bhi chura ke bhaagta nei re... tu chura le attention! 🔥",
        f"{user.display_name}, tere jaisa toh gully ke kachre bhi ignore karte 😹",
        f"{user.display_name}, scene tera full tight hai... dimaag light hai 🔪",
        f"Oye {user.display_name}, attitude tere paas hai, bas talent chhutti pe hai 💢",
        f"{user.display_name}, tu toh wahi banda hai jo YouTube pe 'how to breathe' search karta 🐁"
    ]
    await ctx.send(random.choice(roasts))

# --- EVENTS --- #
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot or message.channel.id != CHANNEL_ID:
        return

    await bot.process_commands(message)

    username = str(message.author.name)
    user_id = str(message.author.id)

    await message.channel.typing()
    await asyncio.sleep(1)

    # Greet based on memory
    greeting = ""
    if user_id not in memory:
        greeting = f"Raaa vai! Pehli baar aaya lagta... kaun hai tu, {username}? 😼\n"
        memory[user_id] = username
        save_memory(memory)
    else:
        greeting = f"Oye {username} billa! Tu firse aa gya... scene kya hai aaj? 🔥\n"

    # Language-based personality
    prompt_used = english_prompt if is_mostly_english(message.content) else hindlish_prompt

    raw_reply = ask_openrouter(message.content, prompt_used)
    chooha_reply = greeting + transform_text(raw_reply, guild=message.guild)
    await message.channel.send(chooha_reply)

# --- KEEP ALIVE --- #
keep_alive()
bot.run(DISCORD_BOT_TOKEN)
