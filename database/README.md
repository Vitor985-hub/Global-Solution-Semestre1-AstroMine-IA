# Banco de Dados

O diretorio `database/` concentra a base relacional prevista para o projeto AstroMine AI.

## Objetivo

O arquivo `schema.sql` modela a persistencia de dados orbitais, analises, relatorios e observabilidade do sistema. Embora o fluxo principal atual ainda rode localmente em arquivos e memoria, esse schema prepara a integracao futura com banco relacional.

## Estruturas previstas no schema

O script cria os seguintes componentes:

- extensao `uuid-ossp` para geracao automatica de UUIDs;
- tabela `asteroids` para dados principais de asteroides;
- tabela `mineral_analysis` para resultados dos modelos de IA;
- tabela `reports` para relatorios gerados;
- tabela `space_images` para imagens e resultados de visao computacional;
- tabela `api_logs` para rastreamento e observabilidade.

## Pre-requisitos

- PostgreSQL instalado e em execucao;
- usuario com permissao para criar extensoes;
- acesso por `psql`, pgAdmin ou DBeaver.

## Como executar o schema

### Opcao 1: linha de comando

```bash
psql -U postgres
```

No console do PostgreSQL:

```sql
CREATE DATABASE astromine_db;
\c astromine_db;
```

Depois execute o arquivo:

```bash
psql -U postgres -d astromine_db -f schema.sql
```

### Opcao 2: interface grafica

1. abra o pgAdmin ou DBeaver;
2. conecte no servidor PostgreSQL;
3. crie o banco `astromine_db`;
4. abra uma janela de query;
5. carregue o conteudo de `schema.sql`;
6. execute o script.

## Relacao com o sistema atual

Hoje, o pipeline principal do projeto usa:

- `simulador/trajetoria_capturada.json` para capturas locais;
- calculo quantico em memoria;
- geracao de graficos e GIFs em arquivos locais.

O banco ainda nao esta conectado a `main.py`, mas o schema ja descreve como armazenar a evolucao futura do sistema.

## Proximos usos recomendados

- salvar capturas de trajetoria no banco;
- registrar resultados do QAOA e da aproximacao nao linear;
- persistir os caminhos dos graficos e animacoes gerados;
- salvar logs do pipeline de simulacao.
