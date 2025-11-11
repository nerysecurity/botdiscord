import discord
from discord.ext import commands

class Basico(commands.Cog):
    """Comandos básicos do bot (ping, help, etc)."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, contexto):
        """Testa se o bot está online."""
        await contexto.send("🏓 Pong!")

    @commands.command(name="help")
    async def ajuda(self, contexto):
        """Mostra a lista de comandos disponíveis."""
        texto = (
            "**Comandos disponíveis:**\n"
            "`!ping` — Testa se o bot está online\n"
            "`!help` — Mostra esta mensagem de ajuda\n"
            "`!perfil` — Mostra seu perfil (em breve: XP e nível)\n"
        )
        await contexto.send(texto)


# Função obrigatória para registrar o Cog
async def setup(bot):
    await bot.add_cog(Basico(bot))
