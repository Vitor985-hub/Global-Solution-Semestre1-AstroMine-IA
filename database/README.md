# Configuração do Banco de Dados (PostgreSQL)

Este diretório contém o arquivo `schema.sql`, responsável por criar as tabelas e extensões necessárias para o banco de dados do projeto AstroMine-IA.

## Pré-requisitos

- **PostgreSQL** instalado e rodando em sua máquina (ou em um servidor).
- Uma ferramenta de linha de comando (`psql`) ou interface gráfica (como **pgAdmin** ou **DBeaver**).

## Como rodar o `schema.sql`

Você pode executar o script SQL de diferentes maneiras:

### Opção 1: Via Linha de Comando (psql)

1. Abra o terminal ou prompt de comando.
2. Conecte-se ao PostgreSQL usando o seu usuário (geralmente `postgres`) e crie um banco de dados para o projeto, caso ainda não exista:
   ```bash
   psql -U postgres
   ```
   Dentro do psql:
   ```sql
   CREATE DATABASE astromine_db;
   \c astromine_db;
   ```
3. Execute o script `schema.sql`:
   ```bash
   psql -U postgres -d astromine_db -f schema.sql
   ```
   *(Substitua `postgres` e `astromine_db` pelo seu usuário e nome do banco de dados, respectivamente).*

### Opção 2: Via Interface Gráfica (pgAdmin ou DBeaver)

1. Abra o **pgAdmin** ou o **DBeaver**.
2. Conecte-se ao seu servidor PostgreSQL.
3. Crie um novo banco de dados (ex: `astromine_db`).
4. Abra uma nova **Query Tool** (janela de consulta) conectada a esse banco de dados.
5. Copie o conteúdo do arquivo `schema.sql` e cole na janela de consulta, **ou** use a opção de carregar o arquivo SQL.
6. Clique no botão de **Executar** (geralmente um ícone de "play" ou `F5`).

## Observações

- O script utiliza a extensão `"uuid-ossp"` para gerar UUIDs automaticamente nas tabelas. O script já inclui o comando `CREATE EXTENSION IF NOT EXISTS "uuid-ossp";` para habilitá-la. Certifique-se de que o usuário utilizado possui permissão para criar extensões.
