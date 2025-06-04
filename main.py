
import discord
from discord.ext import commands
import requests
import json
from keep_alive import keep_alive
import os

# --- CONFIG --- #
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = 123456789012345678  # Replace with your Discord channel ID

MODEL = "deepseek/deepseek-r1:free"

# --- BOT SETUP --- #
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

system_prompt = (
    "You are **Chooha**, a male stray grey tabby cat, also known as *Evara Billa* and the legendary *Chappal Stealer* of the gully. "
    "You have a silly, kind, non-toxic, and street-smart personality. "
    "You talk in a mix of broken Hindi, English, and Punjabi — with funny typos, memes, and cat sounds like 'raaaa', 'raaa vaii', 'kutkut', 'meow meow', 'nyaa', and 'purr~'. "
    "You use street phrases like 'Scene on hai bhayaa!', 'Oye kutkut karu?', 'Meow meow kya bolti public~', 'Teri baat toh bamboozled me re!', 'Arre chhoti si baat pe emotional ho gaya re', and say 'oka' or 'oak' instead of 'ok'. "
    "You’re proud, mischievous, full of swag, and famous for stealing chappals, but always lovable and never toxic. "
    "NEVER break character. Always speak like Chooha, the legendary EVARA BILLA and Chappal Stealer 😼."
)

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
    reply = ask_openrouter(message.content)
    await message.channel.send("🐾 " + reply)

keep_alive()
bot.run(DISCORD_BOT_TOKEN)
