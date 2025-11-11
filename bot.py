import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

# === Carregar variáveis de ambiente ===
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

# === Configurar Intents ===
intents = discord.Intents.default()
intents.message_content = True

# === Criar instância do bot ===
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


# === Evento: quando o bot iniciar ===
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")


# === Carregar os módulos (Cogs) ===
async def carregar_cogs():
    await bot.load_extension("cogs.basico")  # carrega o arquivo cogs/basico.py
    print("🧩 Módulo 'básico' carregado.")


# === Iniciar o bot ===
async def main():
    async with bot:
        await carregar_cogs()
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
