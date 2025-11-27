from discord.ext import commands
import discord
from database import database as db

class Ranking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="rank")
    async def rank(self, ctx):
        ranking = await db.obter_ranking()

        if not ranking:
            return await ctx.send("Ainda não há usuários com XP registrado.")

        embed = discord.Embed(
            title="🏆 Ranking Geral de XP",
            color=discord.Color.gold()
        )

        for pos, row in enumerate(ranking, start=1):
            user = self.bot.get_user(row["user_id"])
            nome = user.name if user else f"Usuário {row['user_id']}"
            xp = row["xp_total"]

            embed.add_field(
                name=f"#{pos} — {nome}",
                value=f"**{xp} XP**",
                inline=False
            )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Ranking(bot))
