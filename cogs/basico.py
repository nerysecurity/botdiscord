import discord
from discord.ext import commands


class Basico(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #ping
    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send("🏓 Pong!")

    #ajuda
    @commands.command(name="ajuda")
    async def help(self, ctx):
        texto = (
            "**📘 Lista de comandos:**\n\n"

            "=== ⚙️ **Geral** ===\n"
            "`!ping` — Interação com usuário\n"
            "`!ajuda` — Mostra esta mensagem de ajuda\n\n"

            "=== 📚 **Estudo** ===\n"
            "`!estudar <disciplina> <conteúdo>` — Define o que você quer estudar\n\n"

            "=== 🎮 **Quiz e Treino** ===\n"
            "`!quiz` — Inicia um quiz infinito em uma thread privada\n"
            "`!diario` — Faz as 10 perguntas diárias com XP alto\n"
            "`!stop` — Encerra a sessão atual de quiz\n\n"

            "=== 👤 **Perfil e XP** ===\n"
            "`!perfil` — Mostra seu perfil completo\n"
            "`!xp` — Mostra seu XP total\n\n"

            "=== 🏆 **Ranking** ===\n"
            "`!rank` — Mostra os usuários com mais XP\n\n"

            "=== 📜 **Histórico** ===\n"
            "`!historico` — Mostra suas últimas respostas\n"
        )

        await ctx.send(texto)


#registra o cog
async def setup(bot):
    await bot.add_cog(Basico(bot))
