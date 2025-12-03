from discord.ext import commands
import database.database as db
import math


class Historico(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="historico")
    async def historico(self, ctx, pagina: int = 1):
        user_id = ctx.author.id

        pool = await db.get_pool()

        #Quantos registros existem
        total = await pool.fetchval("""
            SELECT COUNT(*) FROM historico_resposta
            WHERE id_usuario = $1
        """, user_id)

        if total == 0:
            return await ctx.send("📄 Você ainda não respondeu nenhuma pergunta.")

        por_pagina = 5
        paginas = math.ceil(total / por_pagina)

        if pagina < 1 or pagina > paginas:
            return await ctx.send(f"⚠️ Página inválida! Existem **{paginas}** páginas.")

        offset = (pagina - 1) * por_pagina

        linhas = await pool.fetch("""
            SELECT pergunta_texto, resposta_usuario, resposta_correta, correta, data_resposta
            FROM historico_resposta
            WHERE id_usuario = $1
            ORDER BY data_resposta DESC
            LIMIT $2 OFFSET $3
        """, user_id, por_pagina, offset)

        texto = f"📄 **Seu histórico — Página {pagina}/{paginas}**\n\n"

        for i, row in enumerate(linhas, start=1):
            status = "✔" if row["correta"] else "❌"
            texto += (
                f"**{i}. {row['pergunta_texto']}**\n"
                f" ➤ Sua resposta: **{row['resposta_usuario']}** {status}\n"
                f" ➤ Correta: **{row['resposta_correta']}**\n\n"
            )

        await ctx.send(texto)


async def setup(bot):
    await bot.add_cog(Historico(bot))
