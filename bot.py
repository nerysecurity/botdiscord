import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
import database.database as db


#Carregar variáveis de ambiente 
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

#Configurar intents
intents = discord.Intents.default()
intents.message_content = True

#Criar instância do bot
bot = commands.Bot(command_prefix="!", intents=intents)


#Evento: quando o bot iniciar
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    await db.get_pool()
    print("conectado ao banco de dados:D")


#Carregar os módulos Cogs
async def carregar_cogs():
    
    await bot.load_extension("cogs.basico")
    await bot.load_extension("cogs.estudo     ")
    await bot.load_extension("cogs.perguntas")
    await bot.load_extension("cogs.ranking")
    await bot.load_extension("cogs.perfil")
    print("Cogs carregados")
    




#Iniciar o bot
async def main():
    async with bot:
        await carregar_cogs()
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())

