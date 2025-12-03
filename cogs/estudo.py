from discord.ext import commands

class Estudo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.preferencias = {}  # salva disciplina e conteúdo

    @commands.command(name="estudar")
    async def estudar(self, ctx, disciplina: str, *, conteudo: str):
        user_id = ctx.author.id

        # salva preferências
        self.preferencias[user_id] = {
            "disciplina": disciplina,
            "conteudo": conteudo
        }

        await ctx.send(
            "📚 Estudo definido!\n"
            f"Disciplina: **{disciplina}**\n"
            f"Conteúdo: **{conteudo}**\n\n"
            "Agora escolha um modo de treino:\n"
            "➡️ **!quiz** — perguntas ilimitadas\n"
            "➡️ **!diario** — 10 perguntas por dia"
        )

        # debug
        print("DEBUG ESTUDAR — salvou preferências")
        print("ID:", user_id)
        print("PREFERENCIA:", self.preferencias[user_id])

    def get_preferencia(self, user_id):
        return self.preferencias.get(user_id)


async def setup(bot):
    await bot.add_cog(Estudo(bot))
