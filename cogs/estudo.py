import discord
from discord.ext import commands
import google.generativeai as genai 
import os
import asyncio
from dotenv import load_dotenv
import random

load_dotenv()
genai.configure(api_key=os.getenv("TOKEN_IA"))



class Estudo(commands.Cog):
    """Permite estudo ilimitado com IA e XP reduzido."""

    def __init__(self, bot):
        self.bot = bot
        self.xp_usuarios = {}  #temporário até conectar o banco

    @commands.command()
    async def estudo(self, contexto):
        usuario = contexto.author

        await contexto.send(f"📚 {usuario.mention}, qual **categoria** você quer estudar? (ex: História, Matemática, Ciências...)")

        def check(msg):
            return msg.author == usuario and msg.channel == contexto.channel

        #categoria
        try:
            msg_categoria = await self.bot.wait_for("message", check=check, timeout=60)
            categoria = msg_categoria.content.strip().capitalize()
        except asyncio.TimeoutError:
            await contexto.send("⏰ Tempo esgotado! Tente novamente com `!estudo`.")
            return

        #subtema
        await contexto.send(f"🔍 Ok! Dentro de **{categoria}**, qual **assunto** você quer estudar?")

        try:
            msg_assunto = await self.bot.wait_for("message", check=check, timeout=60)
            assunto = msg_assunto.content.strip().capitalize()
        except asyncio.TimeoutError:
            await contexto.send("⏰ Tempo esgotado! Tente novamente com `!estudo`.")
            return

        await contexto.send(f"🧠 Vamos estudar **{categoria} / {assunto}**!\nDigite `sair` para encerrar a sessão.")

        #loop de perguntas
        while True:
            pergunta, resposta_correta = self.gerar_pergunta_ia(categoria, assunto)
            await contexto.send(f"❓ {pergunta}")

            try:
                resposta = await self.bot.wait_for("message", check=check, timeout=90)
                conteudo = resposta.content.lower().strip()

                if conteudo == "sair":
                    await contexto.send("✅ Sessão de estudo encerrada. Bom trabalho! 👏")
                    break

                #Comparação simples de resposta
                if resposta_correta.lower() in conteudo:
                    self.adicionar_xp(usuario.id, 10)
                    await contexto.send(f"✅ Correto, {usuario.mention}! Você ganhou **10 XP** 🧩")
                else:
                    await contexto.send(f"❌ Errado! A resposta correta era: **{resposta_correta}**")

                await asyncio.sleep(2)

            except asyncio.TimeoutError:
                await contexto.send("⏰ Tempo esgotado! Encerrando a sessão de estudo.")
                break

    #perguntaia
    def gerar_pergunta_ia(self, categoria, assunto):
        resposta = genai.configure.chat.completions.create(
            model= genai.GenerativeModel("gemini-1.5-flash"),
            messages=[
                {"role": "system", "content": "Você é um gerador de perguntas educativas com respostas curtas"},
                {"role": "user", "content": f"Crie uma pergunta e a resposta sobre o tema '{categoria} - {assunto}'. Responda no formato 'pergunta | resposta'."}
            ]
        )

        conteudo = resposta.choices[0].message.content
        if "|" in conteudo:
            pergunta, resposta_correta = conteudo.split("|", 1)
        else:
            pergunta, resposta_correta = conteudo, "sem resposta definida"
        return pergunta.strip(), resposta_correta.strip()


    def adicionar_xp(self, user_id, quantidade):
        self.xp_usuarios[user_id] = self.xp_usuarios.get(user_id, 0) + quantidade


async def setup(bot):
    await bot.add_cog(Estudo(bot))
