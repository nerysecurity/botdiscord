import discord
from discord.ext import commands
import database.database as db


class Perfil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # ================================
    #   PERFIL COMPLETO DO USUÁRIO
    # ================================
    @commands.command(name="perfil")
    async def perfil(self, ctx, membro: discord.Member = None):

        user = membro or ctx.author
        user_id = user.id

        # garante que está registrado
        await db.registrar_usuario(user_id)

        # pega dados do banco
        dados = await db.obter_dados_perfil(user_id)

        if not dados:
            return await ctx.send("⚠️ Não foi possível carregar seu perfil.")

        xp = dados["xp"]
        acertos = dados["acertos"]
        erros = dados["erros"]
        total = dados["total_respostas"]
        diario = dados["respostas_hoje"]

        # -----------------------------------
        # puxar disciplina e conteúdo atuais
        # -----------------------------------
        estudo = self.bot.get_cog("Estudo")
        pref = estudo.get_preferencia(user_id) if estudo else None

        if pref:
            disciplina = pref["disciplina"]
            conteudo = pref["conteudo"]
            estudo_texto = f"**{disciplina}** — *{conteudo}*"
        else:
            estudo_texto = "Nenhum estudo selecionado."


        # -----------------------------------
        # Cálculo de nível + barra
        # -----------------------------------
        nivel = (xp // 100) + 1
        xp_no_nivel = xp % 100
        xp_necessario = 100

        progresso = int((xp_no_nivel / xp_necessario) * 20)
        progresso = max(0, min(20, progresso))

        barra = "█" * progresso + "░" * (20 - progresso)


        # -----------------------------------
        # MONTAR EMBED
        # -----------------------------------
        embed = discord.Embed(
            title=f"📘 Perfil de {user.name}",
            description=(
                "➡ **+5 XP** por acerto (quiz)\n"
                "➡ **+20 XP** por acerto (diário — 10 perguntas por dia)\n"
            ),
            color=discord.Color.blue()
        )

        embed.set_thumbnail(
            url=user.avatar.url if user.avatar else user.default_avatar.url
        )

        embed.add_field(name="🏅 Nível", value=f"**{nivel}**", inline=True)
        embed.add_field(name="⭐ XP Atual", value=f"**{xp_no_nivel}/{xp_necessario}**", inline=True)
        embed.add_field(name="📊 Progresso", value=f"`{barra}`", inline=False)

        embed.add_field(name="✔ Acertos", value=f"**{acertos}**", inline=True)
        embed.add_field(name="❌ Erros", value=f"**{erros}**", inline=True)
        embed.add_field(name="📚 Total respondido", value=f"**{total}**", inline=True)

        embed.add_field(
            name="📅 Diário",
            value=f"**{diario}/10 respondidas hoje**",
            inline=False
        )

        embed.add_field(
            name="📚 Estudo atual",
            value=estudo_texto,
            inline=False
        )

        await ctx.send(embed=embed)



    # ================================
    #   COMANDO: XP (rápido)
    # ================================
    @commands.command(name="xp")
    async def xp(self, ctx):
        user_id = ctx.author.id
        await db.registrar_usuario(user_id)
        xp = await db.buscar_xp(user_id)
        await ctx.send(f"{ctx.author.mention}, você tem **{xp} XP**!")


async def setup(bot):
    await bot.add_cog(Perfil(bot))
