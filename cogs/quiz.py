from discord.ext import commands
import asyncio
import database.database as db
from cogs.gemini import gerar_pergunta_gemini

class Quiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="quiz")
    async def quiz(self, ctx):
        print("DEBUG 1 — entrou no comando !quiz")
        print("DEBUG 2 — estudo_cog =", estudo_cog)
        print("DEBUG 3 — pref =", pref)
        print("DEBUG 4 — chamando IA:", disciplina, conteudo)
        print("DEBUG 5 — retorno da IA:", pergunta)


  
        user_id = ctx.author.id

        # pega disciplina e conteúdo do cog estudio
        estudo_cog = self.bot.get_cog("estudo")
        pref = estudo_cog.get_preferencia(user_id)

        if not pref:
            return await ctx.send(
                "⚠️ Você ainda não escolheu o conteúdo!\n"
                "Use: `!estudar <disciplina> <conteúdo>`"
            )

        disciplina = pref["disciplina"]
        conteudo   = pref["conteudo"]

        # gera pergunta via IA
        pergunta = await gerar_pergunta_gemini(disciplina, conteudo)
        print("DEBUG IA:", pergunta)

        tipo = pergunta["tipo"]
        texto = pergunta["pergunta"]
        alternativas = pergunta["alternativas"]
        correta = pergunta["correta"]

        # envia pergunta
        if tipo == "multipla":
            alt_texto = "\n".join(
                [f"{letra}) {alternativas.get(letra)}" for letra in ["A","B","C","D","E"]]
            )
            await ctx.send(
                f"🧠 **Pergunta de {disciplina}/{conteudo}:**\n"
                f"{texto}\n\n{alt_texto}\n\n"
                "Responda com A, B, C, D ou E"
            )
        else:
            await ctx.send(
                f"🧠 **Pergunta aberta de {disciplina}/{conteudo}:**\n"
                f"{texto}\n\nDigite sua resposta:"
            )

        # aguarda resposta
        def check(m):
            return m.author.id == user_id and m.channel.id == ctx.channel.id

        try:
            msg = await self.bot.wait_for("message", timeout=60, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("⏱ Tempo esgotado!")

        resposta_usuario = msg.content.strip()

        # validação da resposta
        if tipo == "multipla":
            correta_bool = (resposta_usuario.upper() == correta.upper())
        else:
            correta_bool = (resposta_usuario.lower() == correta.lower())

        # XP diário
        respostas_hoje = await db.obter_respostas_do_dia(user_id)
        foid10 = respostas_hoje < 10

        xp = 20 if foid10 else 5
        if correta_bool:
            await db.adicionar_xp(user_id, xp)
        else:
            xp = 0

        await db.incrementar_resposta_diaria(user_id)

        # salvar histórico
        await db.registrar_resposta(
            user_id=user_id,
            pergunta_texto=texto,
            tipo=tipo,
            alternativas=alternativas,
            resposta_usuario=resposta_usuario,
            resposta_correta=correta,
            correta=correta_bool,
            xp_ganho=xp,
            foi_10=foid10
        )

        # resposta final
        if correta_bool:
            await ctx.send(f"✅ Correto! Ganhou **{xp} XP** 🎉")
        else:
            await ctx.send(f"❌ Incorreto. A resposta era: **{correta}**")

async def setup(bot):
    await bot.add_cog(Quiz(bot))
