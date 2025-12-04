# 📘 Bento Bot: Chatbot Gamificado para Discord

O **Bento Bot** é um chatbot gamificado desenvolvido para o **Discord**, criado com o objetivo de incentivar **disciplina**, **motivação** e **constância nos estudos** por meio de quizzes, XP, níveis, ranking e ferramentas de foco.

---

# 🚀 Sobre o Projeto

O Bento Bot transforma a rotina de estudos em uma experiência leve e envolvente utilizando mecânicas de jogo.

Entre os recursos do bot:

* Quizzes diários
* Sistema de XP e níveis
* Ranking geral
* Registro de histórico de respostas
* Limite diário de XP (primeiras 10 respostas corretas)
* Perguntas por categoria
* Salas de foco (Focus Rooms)

---

# 🧩 Tecnologias Utilizadas

* **Node.js** ou **Python**
* **Discord.js** ou **discord.py**
* **PostgreSQL**
* **Docker & Docker Compose** (opcional, recomendado)
* **Git & GitHub**
* **VS Code**

---

# 📌 Pré-requisitos

Antes de começar, instale:

* **Node.js 16+**
* (Opcional) **Python 3.10+**
* **PostgreSQL**
* **Git**
* **VS Code**
* Conta no Discord
* Bot criado no Discord Developer Portal

---

# 🧱 Estrutura do Projeto

* **/db/init.sql** → DDL do banco
* **/db/seed.sql** → perguntas iniciais
* **bot.js / bot.py** → aplicação principal
* **docker-compose.yml** (opcional, recomendado)
* **.env** → variáveis sensíveis

---

# 🛠️ Preparar o Repositório

```bash
git clone https://github.com/nerysecurity/botdiscord
cd botdiscord
```

---

# 🤖 Criar e Configurar o Bot no Discord

1. Acesse: [https://discord.com/developers/applications](https://discord.com/developers/applications)
2. Clique em **New Application**
3. Nome: **BentoBot**
4. Vá em **Bot → Add Bot**
5. Copie o **TOKEN**
6. Em **OAuth2 → URL Generator** marque:

   * Scopes: **bot**
   * Permissões: **Send Messages**, **Read Messages**, **Embed Links**, **Manage Messages**
7. Gere o link e adicione o bot ao servidor

⚠️ **Nunca publique o TOKEN no GitHub**

---

# 🗄️ Configurar Banco PostgreSQL

## **Instalação Local**

Entre no psql:

```sql
CREATE DATABASE bentobot;
CREATE USER bentobot_user WITH PASSWORD 'senha_segura';
GRANT ALL PRIVILEGES ON DATABASE bentobot TO bentobot_user;
```

---

# 🧬 Criar Tabelas (DDL)

Crie o arquivo **db/init.sql** com:

```sql
CREATE TABLE usuarios (
  id SERIAL PRIMARY KEY,
  discord_id VARCHAR(50) NOT NULL UNIQUE,
  username VARCHAR(100),
  xp INTEGER DEFAULT 0,
  nivel INTEGER DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE perguntas (
  id SERIAL PRIMARY KEY,
  categoria VARCHAR(100),
  enunciado TEXT NOT NULL,
  opcao_a TEXT NOT NULL,
  opcao_b TEXT NOT NULL,
  opcao_c TEXT,
  opcao_d TEXT,
  alternativa CHAR(1) NOT NULL
);

CREATE TABLE historico_respostas (
  id SERIAL PRIMARY KEY,
  usuario_id INTEGER REFERENCES usuarios(id),
  pergunta_id INTEGER REFERENCES perguntas(id),
  acertou BOOLEAN,
  resposta_escolhida CHAR(1),
  data_resposta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE perguntas_diarias (
  id SERIAL PRIMARY KEY,
  pergunta_id INTEGER REFERENCES perguntas(id),
  data DATE NOT NULL
);

CREATE TABLE contadores_diarios (
  id SERIAL PRIMARY KEY,
  usuario_id INTEGER REFERENCES usuarios(id),
  data DATE NOT NULL,
  respostas_com_xp INTEGER DEFAULT 0,
  UNIQUE (usuario_id, data)
);
```

Executar:

```bash
psql -U postgres -d bentobot -f db/init.sql
```

---

# 🔑 Criar o Arquivo `.env`

Na raiz do projeto:

```
DISCORD_TOKEN=SEU_TOKEN_AQUI

DB_HOST=localhost
DB_PORT=5432
DB_USER=bentobot_user
DB_PASSWORD=senha_segura
DB_NAME=bentobot
```

⚠️ **Não envie esse arquivo para o GitHub**

---

# 📦 Instalar Dependências e Executar

## **Node.js**

```bash
npm install
npm start
```

## **Python**

```bash
pip install -r requirements.txt
python bot.py
```

---

# ▶️ Executar o Bot

## **Node.js**

```bash
npm start
```

## **Python**

```bash
python bot.py
```

---

# 🐳 Docker Compose (Recomendado)

Crie **docker-compose.yml**:

```yaml
version: "3.8"
services:
  db:
    image: postgres:15
    container_name: bentobot_db
    environment:
      POSTGRES_DB: bentobot
      POSTGRES_USER: bentobot_user
      POSTGRES_PASSWORD: senha_segura
    volumes:
      - db_data:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    ports:
      - "5432:5432"

  bot:
    build: .
    container_name: bentobot_app
    depends_on:
      - db
    env_file:
      - .env
    volumes:
      - .:/app
    command: npm start
    restart: unless-stopped

volumes:
  db_data:
```

Rodar:

```bash
docker compose up --build -d
docker compose logs -f bot
```

---

# 📝 Inserir Perguntas Iniciais (Seed)

Arquivo **db/seed.sql**:

```sql
INSERT INTO perguntas (categoria,enunciado,opcao_a,opcao_b,opcao_c,opcao_d,alternativa)
VALUES
('Matemática','Quanto é 2+2?','3','4','5','6','B'),
('Português','Qual é a forma correta?','a','b','c','d','A');
```

Executar:

```bash
psql -U bentobot_user -d bentobot -f db/seed.sql
```

---

# 📘 Lista de Comandos

### ⚙️ Geral

* **!ping**: Testa resposta do bot
* **!ajuda**: Mostra lista de comandos

### 📚 Estudo

* **!estudar `<disciplina>` `<conteúdo>`**: Registra o que o usuário deseja estudar

### 🎮 Quiz e Treino

* **!quiz**: Inicia quiz infinito em thread privada
* **!diario**: Faz as 10 perguntas diárias com XP alto
* **!stop**: Encerra a sessão de quiz

### 👤 Perfil e XP

* **!perfil**: Exibe perfil completo
* **!xp**: Mostra XP acumulado

### 🏆 Ranking

* **!ranking**: Exibe ranking geral de XP

### 📜 Histórico

* **!historico**: Exibe últimas resposta

---

# 🔧 Regras de XP (MVP)

* Apenas **10 primeiras respostas corretas do dia** dão XP
* Demais respostas contam para histórico, mas **não** geram XP
* Controle realizado pela tabela **contadores_diarios**

---

# 💬 Comandos do Bot

| Comando      | Função                       |
| ------------ | ---------------------------- |
| `!quiz`      | Inicia um quiz               |
| `!perfil`    | Mostra XP, nível e progresso |
| `!rank`      | Ranking geral                |
| `!historico` | Histórico do usuário         |
| `!help`      | Lista comandos               |

---

# 🧪 Testes Rápidos Após Instalação

* Bot aparece **online** no Discord
* `!help` funciona
* `!perfil` cria usuário na tabela **usuarios**
* `!quiz` registra respostas
* XP aumenta apenas nas 10 primeiras respostas corretas do dia
* Consultas úteis:

```bash
psql -U bentobot_user -d bentobot -c "SELECT * FROM usuarios LIMIT 10;"
psql -U bentobot_user -d bentobot -c "SELECT * FROM historico_respostas LIMIT 10;"
```

---

# 🎯 Funcionalidades do MVP

* Quizzes diários
* XP limitado por dia
* Níveis
* Ranking
* Histórico de respostas
* Focus Rooms
* Categorias diversas

---

# 🔮 Evoluções Futuras

* Ranking global
* Ligas e temporadas semanais
* Conquistas raras e colecionáveis
* Integração com app mobile

---

# 🧯 Troubleshooting

| Problema                 | Solução                         |
| ------------------------ | ------------------------------- |
| Bot não conecta          | Verificar `DISCORD_TOKEN`       |
| Erro ao conectar no DB   | Revisar usuário/senha/porta     |
| Permissões insuficientes | Regerar URL OAuth2              |
| Porta 5432 ocupada       | Alterar porta no docker-compose |

---

# ✅ Checklist para Avaliação

* Bot sobe com `npm start` / `python bot.py`
* PostgreSQL funcionando
* Tabelas criadas corretamente
* Seed executado
* XP diário funcionando
* Docker Compose funcionando
* Documentação clara

---

Feito com 💙 para ajudar estudantes a evoluir todos os dias.
