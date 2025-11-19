import os
import json
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
_pool = None

async def get_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL)
    return _pool

# =====================
# Usuário
# =====================

async def registrar_usuario(user_id):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO usuario (id_usuario)
            VALUES ($1)
            ON CONFLICT DO NOTHING;
        """, user_id)

async def buscar_xp(user_id):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval("""
            SELECT xp_acumulado FROM usuario WHERE id_usuario=$1
        """, user_id)

async def adicionar_xp(user_id, xp):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE usuario SET xp_acumulado = xp_acumulado + $1
            WHERE id_usuario=$2
        """, xp, user_id)

# =====================
# Perguntas do dia
# =====================

async def obter_respostas_do_dia(user_id):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT respostas_do_dia FROM xp_diario
            WHERE id_usuario=$1 AND data_dia=CURRENT_DATE
        """, user_id)

        return row["respostas_do_dia"] if row else 0

async def incrementar_resposta_diaria(user_id):
    pool = await get_pool()
    async with pool.acquire() as conn:
        atual = await obter_respostas_do_dia(user_id)

        if atual == 0:
            await conn.execute("""
                INSERT INTO xp_diario (id_usuario, data_dia, respostas_do_dia)
                VALUES ($1, CURRENT_DATE, 1)
            """, user_id)
            return 1

        novo = atual + 1
        await conn.execute("""
            UPDATE xp_diario SET respostas_do_dia=$1
            WHERE id_usuario=$2 AND data_dia=CURRENT_DATE
        """, novo, user_id)
        return novo

# =====================
# Histórico
# =====================

async def registrar_resposta(
    user_id, pergunta_texto, tipo, alternativas,
    resposta_usuario, resposta_correta, correta, xp_ganho, foi_10
):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO historico_resposta
            (id_usuario, pergunta_texto, tipo, alternativas, resposta_usuario,
             resposta_correta, correta, xp_ganho, foi_10_diarias)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
        """,
            user_id, pergunta_texto, tipo,
            json.dumps(alternativas) if alternativas else None,
            resposta_usuario, resposta_correta, correta, xp_ganho, foi_10
        )
