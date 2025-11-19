from discord.ext import commands

class Estudo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.preferencias = {}  # { user_id: {disciplina: "...", conteudo: "..."} }

    @commands.command(name="estudar")
    async def estudar(self, ctx, disciplina: str, *, conteudo: str):
        print("DEBUG ESTUDAR — comando foi executado")
        user_id = ctx.author.id

        self.preferencias[user_id] = {
            "disciplina": disciplina,
            "conteudo": conteudo
        }

        await ctx.send(
            f"📚 **Estudo definido!**\n"
            f"Disciplina: **{disciplina}**\n"
            f"Conteúdo: **{conteudo}**\n\n"
            f"Agora use `!quiz` para receber perguntas personalizadas!"
        )

    def get_preferencia(self, user_id):
        return self.preferencias.get(user_id)

async def setup(bot):
    await bot.add_cog(Estudo(bot))
