import discord
from discord.ext import commands
import asyncio
from services.gemini import gerar_pergunta_gemini
import database.database as db


class Treino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sessoes = {}  # { user_id: { modo, canal, respondidas, ultima } }


   
    #COMANDO: PRATICAR
    
    @commands.command(name="praticar")
    async def praticar(self, ctx):
        user = ctx.author
        user_id = user.id

        #pegar preferencias do cog estudo
        estudo = self.bot.get_cog("Estudo")
        pref = estudo.get_preferencia(user_id)

        if not pref:
            return await ctx.send("⚠️ Use `!estudar <disciplina> <conteudo>` antes.")

        #verifica se usuário já tem uma sessão
        if user_id in self.sessoes:
            return await ctx.send("⚠️ Você já está em uma sessão ativa! Use `!stop`.")

        #criar thread
        thread = await ctx.channel.create_thread(
            name=f"treino-{user.name}",
            type=discord.ChannelType.public_thread
        )

        await thread.send(f"📘 **{user.mention}, iniciando modo PRÁTICA ilimitada!**\n"
                          "Use `!stop` para encerrar a qualquer momento.")

        #criar sessão
        self.sessoes[user_id] = {
            "modo": "estudo",
            "canal": thread,
            "respondidas": 0,
            "ultima": None,
            "disciplina": pref["disciplina"],
            "conteudo": pref["conteudo"]
        }

        await self.enviar_pergunta(user_id)



    
    #COMANDO: DIARIO
   
    @commands.command(name="diario")
    async def diario(self, ctx):
        user = ctx.author
        user_id = user.id

        estudo = self.bot.get_cog("Estudo")
        pref = estudo.get_preferencia(user_id)

        if not pref:
            return await ctx.send("⚠️ Use `!estudar` antes de iniciar seu diário.")

        # checar se já completou hoje
        feitas = await db.obter_respostas_do_dia(user_id)
        if feitas >= 10:
            return await ctx.send("🔥 Você já completou suas 10 perguntas diárias hoje!")

        if user_id in self.sessoes:
            return await ctx.send("⚠️ Você já está em sessão. Use `!stop` primeiro.")

        # criar thread
        thread = await ctx.channel.create_thread(
            name=f"diario-{user.name}",
            type=discord.ChannelType.public_thread
        )

        await thread.send(
            f"📅 **{user.mention}, iniciando suas PERGUNTAS DIÁRIAS!**\n"
            "Hoje você tem **10 perguntas** valendo XP extra.\n"
            "Escreva `!stop` para encerrar."
        )

        self.sessoes[user_id] = {
            "modo": "diario",
            "canal": thread,
            "respondidas": feitas,
            "ultima": None,
            "disciplina": pref["disciplina"],
            "conteudo": pref["conteudo"]
        }

        await self.enviar_pergunta(user_id)



   
    #ENVIAR PERGUNTA
  
    async def enviar_pergunta(self, user_id):
        if user_id not in self.sessoes:
            return

        sessao = self.sessoes[user_id]
        canal = sessao["canal"]

        disciplina = sessao["disciplina"]
        conteudo = sessao["conteudo"]

        pergunta = await gerar_pergunta_gemini(disciplina, conteudo)
        sessao["ultima"] = pergunta

        #enviar
        await canal.send(f"🧠 **{pergunta['pergunta']}**")

        if pergunta["tipo"] == "multipla":
            alt = pergunta["alternativas"]
            texto = "\n".join([f"{l}) {alt[l]}" for l in "ABCDE"])
            await canal.send(texto)



    
    #RESPOSTAS DO USUÁRIO
   
    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot:
            return

        user_id = msg.author.id

        if user_id not in self.sessoes:
            return  # não está em sessão

        sessao = self.sessoes[user_id]

        # garantir que está respondendo no thread correto
        if msg.channel.id != sessao["canal"].id:
            return

        conteudo = msg.content.lower().strip()

        # comando stop
        if conteudo == "!stop":
            await sessao["canal"].send("🛑 **Sessão encerrada!**")
            await sessao["canal"].edit(archived=True)
            del self.sessoes[user_id]
            return

        pergunta = sessao["ultima"]

        # normalizar resposta
        resposta = conteudo.strip().lower()
        correta = pergunta["correta"].strip().lower()

        if pergunta["tipo"] == "multipla":
            correta = correta[0]  # pega só A/B/C/D/E

        acertou = (resposta == correta)

        # XP
        if sessao["modo"] == "diario":
            # diário é 10 perguntas com XP maior
            feitas = sessao["respondidas"]

            if feitas >= 10:
                await sessao["canal"].send("🔥 Você terminou suas 10 perguntas de hoje!")
                del self.sessoes[user_id]
                return

            xp = 20 if acertou else 0
            await db.incrementar_resposta_diaria(user_id)

        else:
            # modo treino
            xp = 5 if acertou else 0

        if acertou:
            await db.adicionar_xp(user_id, xp)
            await sessao["canal"].send(f"✅ Correto! (+{xp} XP)")
        else:
            await sessao["canal"].send(
                f"❌ Errado! Resposta correta: **{correta.upper()}**"
            )

        sessao["respondidas"] += 1

        # enviar próxima
        await self.enviar_pergunta(user_id)



async def setup(bot):
    await bot.add_cog(Treino(bot))
