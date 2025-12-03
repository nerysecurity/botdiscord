from discord.ext import commands
import database.database as db
import asyncpg


class Ranking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

  
    #RANKING GERAL (XP)
    @commands.command(name="rank")
    async def rank(self, ctx):
        pool = await db.get_pool()

        query = """
            SELECT id_usuario, xp_acumulado
            FROM usuario
            ORDER BY xp_acumulado DESC
            LIMIT 20
        """

        linhas = await pool.fetch(query)

        if not linhas:
            return await ctx.send("📄 Ninguém possui XP ainda.")

        texto = "🏆 **RANKING GERAL (TOP 20)**\n\n"

        pos = 1
        for row in linhas:
            user = self.bot.get_user(row["id_usuario"])
            nome = user.name if user else f"Usuário {row['id_usuario']}"
            texto += f"**#{pos}** — {nome}: **{row['xp_acumulado']} XP**\n"
            pos += 1

        await ctx.send(texto)

    #RANKING DIÁRIO
    @commands.command(name="rankdia")
    async def rankdia(self, ctx):
        pool = await db.get_pool()

        query = """
            SELECT id_usuario, respostas_do_dia
            FROM xp_diario
            WHERE data_dia = CURRENT_DATE
            ORDER BY respostas_do_dia DESC
            LIMIT 20
        """

        linhas = await pool.fetch(query)

        if not linhas:
            return await ctx.send("📅 Ninguém respondeu perguntas diárias hoje.")

        texto = "📅 **RANKING DO DIA — 10 perguntas**\n\n"

        pos = 1
        for row in linhas:
            user = self.bot.get_user(row["id_usuario"])
            nome = user.name if user else f"Usuário {row['id_usuario']}"
            texto += f"**#{pos}** — {nome}: **{row['respostas_do_dia']} feitas**\n"
            pos += 1

        await ctx.send(texto)

    
    #TOP 10
    @commands.command(name="top10")
    async def top10(self, ctx):
        pool = await db.get_pool()

        query = """
            SELECT id_usuario, xp_acumulado
            FROM usuario
            ORDER BY xp_acumulado DESC
            LIMIT 10
        """

        linhas = await pool.fetch(query)

        if not linhas:
            return await ctx.send("🏅 Ainda não há jogadores no topo.")

        texto = "🥇 **TOP 10 XP**\n\n"
        pos = 1
        for row in linhas:
            user = self.bot.get_user(row["id_usuario"])
            nome = user.name if user else "Usuário"
            texto += f"**#{pos}** — {nome}: **{row['xp_acumulado']} XP**\n"
            pos += 1

        await ctx.send(texto)


async def setup(bot):
    await bot.add_cog(Ranking(bot))
