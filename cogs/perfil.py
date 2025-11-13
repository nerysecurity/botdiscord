import discord
from discord.ext import commands

class Perfil(commands.Cog):
    """Gerencia perfis e XP dos usuários (simulação sem banco de dados)."""

    def __init__(self, bot):
        self.bot = bot
        # Dicionário para simular um banco de dados
        self.usuarios = {}

    @commands.command()
    async def perfil(self, contexto):
        """Mostra o perfil do usuário e cria um novo caso não exista."""

        usuario = contexto.author
        user_id = usuario.id

        # Se o usuário ainda não existir, cria um perfil novo
        if user_id not in self.usuarios:
            self.usuarios[user_id] = {"xp": 0, "nivel": 1}

        dados = self.usuarios[user_id]
        nome = usuario.display_name
        avatar = usuario.avatar.url if usuario.avatar else None

        embed = discord.Embed(
            title=f"🎮 Perfil de {nome}",
            color=discord.Color.green()
        )
        embed.add_field(name="🏆 XP", value=dados["xp"], inline=True)
        embed.add_field(name="⭐ Nível", value=dados["nivel"], inline=True)
        embed.set_footer(text="Sistema de XP em desenvolvimento 💻")

        if avatar:
            embed.set_thumbnail(url=avatar)

        await contexto.send(embed=embed)

    @commands.command()
    async def ganharxp(self, contexto, quantidade: int = 10):
        """Adiciona XP ao usuário (comando de teste)."""

        usuario = contexto.author
        user_id = usuario.id

        # Se o usuário ainda não existir, cria
        if user_id not in self.usuarios:
            self.usuarios[user_id] = {"xp": 0, "nivel": 1}

        self.usuarios[user_id]["xp"] += quantidade

        if self.usuarios[user_id]["xp"] >= 100:
            self.usuarios[user_id]["nivel"] += 1
            self.usuarios[user_id]["xp"] = 0
            await contexto.send(f"🎉 Parabéns {usuario.mention}, você subiu para o nível {self.usuarios[user_id]['nivel']}!")
        else:
            await contexto.send(f"💪 {usuario.mention}, você ganhou {quantidade} XP!")

async def setup(bot):
    await bot.add_cog(Perfil(bot))
