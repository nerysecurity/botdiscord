import discord
from discord.ext import commands
import asyncio
import datetime
from database import database as db
from services.gemini import gerar_pergunta_gemini

class Perguntas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Cache simples para controlar quem já fez a diária hoje
        # Formato: {user_id: data_de_hoje}
        self.controle_diaria = {} 

    async def _rodar_quiz(self, ctx, disciplina, conteudo, xp_acerto, tipo_modo):
        """
        Função central que gerencia o fluxo da pergunta.
        """
        # 1. Gera a pergunta na IA
        msg_carregando = await ctx.send(f"🤖 Gerando pergunta de **{disciplina}** ({conteudo})...")
        
        try:
            dados_pergunta = await gerar_pergunta_gemini(disciplina, conteudo)
        except Exception as e:
            await msg_carregando.delete()
            return await ctx.send(f"⚠️ Erro ao gerar pergunta: {e}")

        await msg_carregando.delete()

        tipo = dados_pergunta["tipo"]
        texto = dados_pergunta["pergunta"]
        alternativas = dados_pergunta.get("alternativas")
        correta_ia = dados_pergunta["correta"]

        # 2. Monta a visualização (Embed)
        embed = discord.Embed(
            title=f"📚 Quiz: {disciplina}",
            description=f"**Assunto:** {conteudo}\n\n{texto}",
            color=discord.Color.blue()
        )

        if tipo == "multipla" and alternativas:
            texto_alternativas = "\n".join(
                [f"**{letra})** {texto_alt}" for letra, texto_alt in alternativas.items()]
            )
            embed.add_field(name="Alternativas", value=texto_alternativas, inline=False)
            embed.set_footer(text="Responda com A, B, C, D ou E")
        else:
            embed.set_footer(text="Digite sua resposta por extenso.")

        await ctx.send(embed=embed)

        # 3. Aguarda resposta
        def check(m):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        try:
            msg = await self.bot.wait_for("message", timeout=60, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("⏰ Tempo esgotado! Tente novamente.")

        resposta_usuario = msg.content.strip()

        # 4. Validação
        acertou = False
        if tipo == "multipla":
            acertou = resposta_usuario.upper() == correta_ia.upper()
        else:
            # Comparação simples para aberta (pode melhorar depois com IA verificadora)
            acertou = resposta_usuario.lower() == correta_ia.lower()

        # 5. Lógica de XP e Feedback
        xp_ganho = 0
        
        if acertou:
            xp_ganho = xp_acerto
            await ctx.send(f"✅ **Correto!** Você ganhou **{xp_ganho} XP**! 🎉")
            # Se for a diária, marca que o usuário já fez
            if tipo_modo == "diaria":
                self.controle_diaria[ctx.author.id] = datetime.date.today()
                await db.adicionar_xp(ctx.author.id, xp_ganho)
            else:
                # Lógica do limite diário de farming (do seu código original)
                respostas_hoje = await db.obter_respostas_do_dia(ctx.author.id)
                if respostas_hoje < 10:
                    await db.adicionar_xp(ctx.author.id, xp_ganho)
                else:
                    xp_ganho = 5 # XP reduzido após 10 perguntas
                    await db.adicionar_xp(ctx.author.id, xp_ganho)
                    await ctx.send("ℹ️ *Você já respondeu muitas hoje, XP reduzido.*")
        else:
            await ctx.send(f"❌ **Incorreto.** A resposta era: **{correta_ia}**")

        # 6. Salvar histórico e incrementar contador
        await db.incrementar_resposta_diaria(ctx.author.id)
        
        # Adapte os parâmetros conforme sua função db.registrar_resposta espera
        await db.registrar_resposta(
            user_id=ctx.author.id,
            pergunta_texto=texto,
            tipo=tipo,
            alternativas=alternativas, # Pode precisar converter pra JSON/String dependendo do DB
            resposta_usuario=resposta_usuario,
            resposta_correta=str(correta_ia),
            correta=acertou,
            xp_ganho=xp_ganho,
            foi_10=(xp_ganho < 10) # Flag de exemplo
        )

    # --- COMANDO 1: DIÁRIA ---
    @commands.command(name="diaria")
    async def diaria(self, ctx):
        """Responde a pergunta do dia (vale mais XP)."""
        
        # Verifica se já fez hoje
        hoje = datetime.date.today()
        ultimo_uso = self.controle_diaria.get(ctx.author.id)
        
        if ultimo_uso == hoje:
            return await ctx.send("📅 Você já respondeu sua pergunta diária hoje! Use `!praticar` para continuar estudando.")

        # Tópico da diária: Pode ser fixo ou aleatório. 
        # Aqui vou colocar "Conhecimentos Gerais" ou pegar do perfil de Estudo se quiser personalizar.
        disciplina = "Conhecimentos Gerais"
        conteudo = "Curiosidades e Fatos Históricos"
        
        # XP Bônus para diária
        xp_bonus = 100 

        await ctx.send(f"🌞 **Pergunta Diária!** Valendo {xp_bonus} XP.")
        await self._rodar_quiz(ctx, disciplina, conteudo, xp_bonus, "diaria")

    # --- COMANDO 2: PRATICAR ---
    @commands.command(name="praticar", aliases=["responder", "quiz"])
    async def praticar(self, ctx):
        """Pratica com base no que você definiu em !estudar."""
        
        # Pega as preferências do Cog de Estudo
        estudo_cog = self.bot.get_cog("Estudo")
        if not estudo_cog:
            return await ctx.send("⚠️ Erro interno: Módulo de estudo não encontrado.")

        pref = estudo_cog.get_preferencia(ctx.author.id)
        
        if not pref:
            return await ctx.send(
                "⚠️ Você ainda não configurou o que quer estudar!\n"
                "Use: `!estudar <disciplina> <conteudo>` primeiro."
            )

        disciplina = pref["disciplina"]
        conteudo = pref["conteudo"]
        
        # XP padrão
        xp_padrao = 20

        await self._rodar_quiz(ctx, disciplina, conteudo, xp_padrao, "praticar")

async def setup(bot):
    await bot.add_cog(Perguntas(bot))