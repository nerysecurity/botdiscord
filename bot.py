import discord
from discord.ext import commands
import asyncpg
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv() 
token = os.getenv("DISCORD_TOKEN")
print(token)  

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def ping(contexto):
    print(contexto.author)
    print(contexto.channel)
    await contexto.send("Pong!")
    
bot.run(token)
