import discord
from discord.ext import commands
import asyncio
from services.gemini import gerar_pergunta_gemini
import database.database as db


class Treino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sessoes = {}  # user_id -> dados da sessão


    # pegar preferencia do cog estudo
    def pegar_pref(self, user_id):
        estudo = self.bot.get_cog("Estudo")
        if estudo:
            return estudo.get_preferencia(user_id)
        return None


    # criar thread privada
    async def criar_thread_privado(self, ctx, nome, usuario):
        thread = await ctx.channel.create_thread(
            name=nome,
            type=discord.ChannelType.public_thread
        )

        overwrite = discord.PermissionOverwrite(send_messages=False)

        for member in ctx.channel.members:
            if member.id not in (usuario.id, ctx.guild.me.id):
                try:
                    await thread.set_permissions(member, overwrite=overwrite)
                except:
                    pass

        return thread


    # enviar pergunta
    async def enviar_pergunta(self, user_id):
        await asyncio.sleep(0)

        if user_id not in self.sessoes:
            return

        sessao = self.sessoes[user_id]
        canal = sessao["canal"]

        await canal.send("⌛ Gerando pergunta...")

        try:
            pergunta = await asyncio.wait_for(
                gerar_pergunta_gemini(sessao["disciplina"], sessao["conteudo"]),
                timeout=25
            )
        except Exception as e:
            print("[ERRO GEMINI]:", e)
            await canal.send("❌ Erro ao gerar pergunta. Sessão encerrada.")
            await self.encerrar_sessao(user_id)
            return

        if not pergunta or "pergunta" not in pergunta:
            await canal.send("❌ A IA enviou uma pergunta inválida.")
            await self.encerrar_sessao(user_id)
            return

        sessao["ultima"] = pergunta

        await canal.send(f"🧠 **{pergunta['pergunta']}**")

        if pergunta["tipo"] == "multipla":
            alt = pergunta["alternativas"]
            opcoes = "\n".join([f"{l}) {alt[l]}" for l in "ABCDE"])
            await canal.send(opcoes)


    # encerrar sessão
    async def encerrar_sessao(self, user_id):
        if user_id not in self.sessoes:
            return

        canal = self.sessoes[user_id]["canal"]

        try:
            await canal.send("🛑 Sessão encerrada.")
            await canal.edit(archived=True)
        except:
            pass

        del self.sessoes[user_id]


    # ======================
    # QUIZ ILIMITADO
    # ======================
    @commands.command(name="quiz")
    async def quiz(self, ctx):
        user = ctx.author
        user_id = user.id

        pref = self.pegar_pref(user_id)
        if not pref:
            return await ctx.send("⚠️ Use `!estudar <disciplina> <conteúdo>` primeiro.")

        if user_id in self.sessoes:
            return await ctx.send("⚠️ Você já tem uma sessão ativa. Use `!stop`.")

        thread = await self.criar_thread_privado(ctx, f"quiz-{user.name}", user)

        await thread.send(
            f"🎮 {user.mention}, seu quiz começou!\nUse **!stop** para encerrar."
        )

        self.sessoes[user_id] = {
            "modo": "estudo",
            "canal": thread,
            "respondidas": 0,
            "ultima": None,
            "disciplina": pref["disciplina"],
            "conteudo": pref["conteudo"]
        }

        await self.enviar_pergunta(user_id)


    # ======================
    # DESAFIO DIÁRIO
    # ======================
    @commands.command(name="diario")
    async def diario(self, ctx):
        user = ctx.author
        user_id = user.id

        pref = self.pegar_pref(user_id)
        if not pref:
            return await ctx.send("⚠️ Use `!estudar <disciplina> <conteúdo>` primeiro.")

        if user_id in self.sessoes:
            return await ctx.send("⚠️ Você já tem uma sessão ativa. Use `!stop`.")

        feitas = await db.obter_respostas_do_dia(user_id)
        if feitas >= 10:
            return await ctx.send("🔥 Você já fez suas **10 perguntas diárias** hoje!")

        thread = await self.criar_thread_privado(ctx, f"diario-{user.name}", user)

        await thread.send(
            f"📅 {user.mention}, iniciando seu **desafio diário**!\n"
            "Serão **10 perguntas**.\nUse **!stop** para encerrar."
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


    # ======================
    # LISTENER DAS RESPOSTAS
    # ======================
    @commands.Cog.listener()
    async def on_message(self, msg):

        try:
            if msg.author.bot:
                return

            user_id = msg.author.id

            if user_id not in self.sessoes:
                return

            sessao = self.sessoes[user_id]

            if msg.channel.id != sessao["canal"].id:
                return

            conteudo = msg.content.lower().strip()

            # parar sessão
            if conteudo == "!stop":
                await sessao["canal"].send("🛑 Sessão encerrada!")
                await sessao["canal"].edit(archived=True)
                del self.sessoes[user_id]
                return

            pergunta = sessao["ultima"]
            if not pergunta:
                return

            correta = pergunta["correta"].strip().lower()
            if pergunta["tipo"] == "multipla":
                correta = correta[0]

            acertou = (conteudo == correta)

            # calcular xp
            if sessao["modo"] == "diario":
                xp = 20 if acertou else 0
            else:
                xp = 5 if acertou else 0

            # feedback
            if acertou:
                await sessao["canal"].send(f"✅ Correto! (+{xp} XP)")
            else:
                await sessao["canal"].send(
                    f"❌ Errado! Resposta correta: **{correta.upper()}**"
                )

            await asyncio.sleep(0)

            # atualizar BD
            if sessao["modo"] == "diario":
                await db.incrementar_resposta_diaria(user_id)

            if acertou:
                await db.adicionar_xp(user_id, xp)

            sessao["respondidas"] += 1

            await self.enviar_pergunta(user_id)

        except Exception as e:
            print("❌ ERRO no on_message:", e)


async def setup(bot):
    await bot.add_cog(Treino(bot))
