import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
import database.database as db

# Carregar variáveis de ambiente
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.messages = True

# Criar instância do bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Evento: quando o bot iniciar
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

    try:
        await db.get_pool()
        print("🌐 Banco de dados conectado com sucesso!")
    except Exception as e:
        print("❌ ERRO ao conectar ao banco:", e)

# Carregar os módulos Cogs
async def carregar_cogs():
    cogs = [
        "cogs.basico",
        "cogs.estudo",
        "cogs.perfil",
        "cogs.treino",
        "cogs.ranking",
        "cogs.historico"
    ]

    for cog in cogs:
        cog_name = cog.split(".")[-1].capitalize()
        if not bot.get_cog(cog_name):
            try:
                await bot.load_extension(cog)
                print(f"[OK] {cog} carregado")
            except Exception as e:
                print(f"[ERRO] {cog}", e)

# Iniciar o bot
async def main():
    await carregar_cogs()
    await bot.start(token)  # start apenas uma vez

if __name__ == "__main__":
    asyncio.run(main())
