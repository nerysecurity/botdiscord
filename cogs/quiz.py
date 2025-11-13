import discord
from discord.ext import commands
import random
import asyncio
from datetime import datetime, timedelta


class Quiz(commands.Cog):
    """Sistema de quiz com pontuação e limite diário."""

    def __init__(self, bot):
        self.bot = bot
        self.perguntas = [
            {"pergunta": "Quem descobriu o Brasil?", "resposta": "pedro alvares cabral"},
            {"pergunta": "Qual é a capital da França?", "resposta": "paris"},
            {"pergunta": "Quanto é 7 x 8?", "resposta": "56"},
            {"pergunta": "Quem escreveu Dom Casmurro?", "resposta": "machado de assis"},
        ]
        # Controla tentativas diárias por usuário
        self.tentativas_diarias = {}

    @commands.command()
    async def quiz(self, contexto):
        """Inicia um quiz e concede XP se acertar, com avisos de tempo."""

        usuario = contexto.author
        user_id = usuario.id
        agora = datetime.now()

        # Verifica limite diário de tentativas (10 por dia)
        if user_id in self.tentativas_diarias:
            ultimo, tentativas = self.tentativas_diarias[user_id]
            if agora.date() == ultimo.date() and tentativas >= 10:
                await contexto.send(f"⚠️ {usuario.mention}, você já fez 10 tentativas hoje! Volte amanhã 😉")
                return
            elif agora.date() != ultimo.date():
                self.tentativas_diarias[user_id] = (agora, 0)
        else:
            self.tentativas_diarias[user_id] = (agora, 0)

        # Escolhe uma pergunta aleatória
        pergunta = random.choice(self.perguntas)
        await contexto.send(f"🧠 {usuario.mention}, aqui vai sua pergunta:\n**{pergunta['pergunta']}**")
        await contexto.send("⏳ Você tem **1 minuto (60 segundos)** para responder!")

        def check(msg):
            return msg.author == usuario and msg.channel == contexto.channel

        try:
            # Mensagens de aviso
            async def avisos_tempo():
                await asyncio.sleep(30)
                await contexto.send("⌛ Restam **30 segundos!**")
                await asyncio.sleep(15)
                await contexto.send("⏰ Restam **15 segundos!**")
                await asyncio.sleep(10)
                await contexto.send("⚡ Restam **5 segundos!**")

            # Roda os avisos em paralelo
            aviso_task = asyncio.create_task(avisos_tempo())

            # Espera a resposta do usuário
            resposta = await self.bot.wait_for("message", check=check, timeout=60.0)
            aviso_task.cancel()  # cancela os avisos se o usuário responder antes

        except asyncio.TimeoutError:
            await contexto.send("⏰ Tempo esgotado! Tente novamente.")
            return

        # Atualiza tentativas do dia
        _, tentativas = self.tentativas_diarias[user_id]
        self.tentativas_diarias[user_id] = (agora, tentativas + 1)

        # Verifica resposta
        if resposta.content.lower().strip() == pergunta["resposta"]:
            await contexto.send(f"✅ Correto, {usuario.mention}! Você ganhou **20 XP!** 🎉")
        else:
            await contexto.send(f"❌ Errado, {usuario.mention}! A resposta certa era **{pergunta['resposta']}**.")


# 👇 Fora da classe — precisa estar alinhado à esquerda
async def setup(bot):
    await bot.add_cog(Quiz(bot))
