from discord.ext import commands
import database.database as db

class Perfil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="xp")
    async def xp(self, ctx):
        user_id = ctx.author.id

        # Garante que existe no banco
        await db.registrar_usuario(user_id)

        # Busca o XP
        xp = await db.buscar_xp(user_id)

        await ctx.send(f"{ctx.author.mention}, você tem **{xp} XP**!")

async def setup(bot):
    await bot.add_cog(Perfil(bot))
