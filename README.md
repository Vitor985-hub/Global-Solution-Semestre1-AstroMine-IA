# FIAP - Faculdade de Informatica e Administracao Paulista

<p align="center">
<a href="https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP" border="0" width="40%" height="40%"></a>
</p>

# AstroMine AI

Projeto desenvolvido para o Global Solution 2026.1 da FIAP com foco em mineracao espacial de asteroides. O sistema integra dados reais da NASA, inteligencia artificial (Random Forest + OpenCV), otimizacao quantica (QAOA), uma API REST (FastAPI), banco de dados relacional (PostgreSQL) e um dashboard interativo (Streamlit).

## Integrantes

- <a href="https://github.com/Vitor985-hub">Vitor Eiji</a>
- <a href="https://github.com/BPilecarte">Beatriz Pilecarte</a>
- <a href="https://github.com/yggdrasilGit">Franciscmar Alves</a>
- <a href="https://github.com/matheusbento04">Matheus Soares</a>
- <a href="https://github.com/AntonioBarros19">Antonio Barros</a>

## Professores

### Tutor(a)

- <a href="https://www.linkedin.com/in/caique-nonato/">Caique Nonato</a>

### Coordenador(a)

- <a href="https://www.linkedin.com/in/andregodoichiovato/">Andre Godoi Chiochiovatto</a>

## Visao Geral

O AstroMine AI combina cinco frentes principais:

1. **API REST** (`astromine-api/`) — sincroniza dados reais de asteroides da API SBDB da NASA/JPL e expoe endpoints CRUD via FastAPI;
2. **Pipeline de IA** (`ai/`) — classifica asteroides por tipo geologico (C, S, M) usando Random Forest e extrai features visuais com OpenCV;
3. **Banco de Dados** (`database/`) — PostgreSQL com tabelas para asteroides, analises minerais, relatorios e imagens espaciais;
4. **Dashboard** (`frontend/`) — painel interativo Streamlit com graficos Plotly, filtros avancados e metricas de viabilidade economica;
5. **Simulador Quantico** (`simulador/` + `trajetoria_asteroid/`) — captura de movimento por camera e otimizacao de trajetorias orbitais com QAOA (Qiskit).

## Arquitetura do Sistema

```text
┌─────────────────────────────────────────────────────────────────────┐
│                        AstroMine AI                                 │
│                                                                     │
│  ┌──────────────┐    ┌───────────────┐    ┌──────────────────────┐  │
│  │  NASA SBDB   │───>│ astromine-api │───>│     PostgreSQL       │  │
│  │  (API JPL)   │    │  (FastAPI)    │    │   (database/)        │  │
│  └──────────────┘    └───────────────┘    └──────────┬───────────┘  │
│                                                      │              │
│                      ┌───────────────┐               │              │
│                      │    ai/        │───────────────>│              │
│                      │ OpenCV + RF   │<──────────────-│              │
│                      └───────────────┘               │              │
│                                                      │              │
│                      ┌───────────────┐               │              │
│                      │  frontend/    │<──────────────-│              │
│                      │  (Streamlit)  │                              │
│                      └───────────────┘                              │
│                                                                     │
│  ┌──────────────┐    ┌───────────────┐                              │
│  │  simulador/  │───>│ trajetoria_   │                              │
│  │  (Camera)    │    │ asteroid/     │                              │
│  │              │    │ (QAOA/Qiskit) │                              │
│  └──────────────┘    └───────────────┘                              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Modulo: `ai/` — Pipeline de Inteligencia Artificial

O arquivo `ai/vision_ml_pipeline.py` implementa o pipeline completo de IA em tres fases:

### Fase 1 — Visao Computacional (OpenCV)

- Busca a URL da imagem do asteroide no banco de dados (`space_images`);
- Faz download em memoria e decodifica com OpenCV;
- Aplica pre-processamento: redimensionamento para 224x224, conversao para escala de cinza, suavizacao gaussiana;
- Executa thresholding binario para detectar regioes de alto brilho (potenciais depositos metalicos);
- Identifica contornos (anomalias) e calcula metricas: percentual de brilho e numero de anomalias;
- Gera dados sinteticos como fallback caso a imagem nao esteja disponivel.

### Fase 2 — Machine Learning (Scikit-Learn)

- Treina um classificador **Random Forest** com 120 estimadores sobre um dataset sintetico de 400 amostras;
- Features de entrada: diametro, massa, percentual de brilho (OpenCV) e numero de anomalias;
- Injeta regras fisicas no treino: asteroides metalicos (M) possuem maior brilho, carbonaceos (C) sao mais escuros;
- Classifica cada asteroide como tipo **C** (carbonaceo), **S** (silicioso) ou **M** (metalico).

### Fase 3 — Persistencia dos Resultados

- Atualiza a classe geologica do asteroide na tabela `asteroids`;
- Deduz elementos minerais e valores economicos em escala real (bilhoes/trilhoes de USD) com base na classe predita;
- Escala o valor estimado pelo diametro real do asteroide e pelo numero de anomalias detectadas;
- Insere os resultados na tabela `mineral_analysis` com confianca, teor e modelo utilizado.

### Execucao automatizada

Ao rodar `python ai/vision_ml_pipeline.py`, o pipeline processa **todos** os asteroides cadastrados no banco de dados em loop.

---

## Modulo: `astromine-api/` — API REST (FastAPI)

A API conecta o sistema aos dados reais da NASA e expoe operacoes CRUD sobre os asteroides.

### Endpoints

| Metodo   | Rota                              | Descricao                                                      |
|----------|-----------------------------------|----------------------------------------------------------------|
| `POST`   | `/sincronizar-asteroides`         | Consome a API SBDB da NASA/JPL e salva/atualiza asteroides no banco (limite configuravel, max 100) |
| `GET`    | `/asteroides`                     | Lista todos os asteroides salvos no banco                      |
| `GET`    | `/asteroides/{id}`                | Retorna detalhes de um asteroide especifico                    |
| `PUT`    | `/asteroides/{id}`                | Atualiza os dados de um asteroide                              |
| `DELETE` | `/asteroides/{id}`                | Exclui um asteroide pelo ID                                    |

### Detalhes tecnicos

- Consome a API `ssd-api.jpl.nasa.gov/sbdb_query.api` com campos: `full_name`, `class`, `diameter`, `extent`, `density`, `moid`;
- Converte MOID (Minimum Orbit Intersection Distance) de unidades astronomicas (AU) para quilometros;
- Usa upsert: atualiza se o asteroide ja existe, insere caso contrario;
- Modelo Pydantic `AsteroideResponse` para validacao de dados;
- Roda com Uvicorn na porta 8000.

### Execucao

```bash
cd astromine-api
uvicorn main:app --reload --port 8000
```

---

## Modulo: `database/` — Banco de Dados (PostgreSQL)

O arquivo `database/schema.sql` define o schema relacional do projeto com as seguintes tabelas:

| Tabela             | Descricao                                                                 |
|--------------------|---------------------------------------------------------------------------|
| `asteroids`        | Dados fisicos dos asteroides: nome, classe, diametro, massa, densidade, volume, MOID |
| `mineral_analysis` | Resultados da IA: elemento principal, teor, unidade, confianca, valor estimado, modelo usado |
| `reports`          | Relatorios gerados por asteroide com data e resumo                        |
| `space_images`     | URLs de imagens espaciais vinculadas a cada asteroide                     |

### Relacionamentos

- `mineral_analysis`, `reports` e `space_images` referenciam `asteroids(id)` com `ON DELETE CASCADE`;
- IDs sequenciais (`SERIAL PRIMARY KEY`) em todas as tabelas.

### Como criar o banco

```bash
psql -U postgres
```

```sql
CREATE DATABASE astromine_db;
\c astromine_db;
```

```bash
psql -U postgres -d astromine_db -f database/schema.sql
```

Consulte `database/README.md` para mais detalhes.

---

## Modulo: `frontend/` — Dashboard (Streamlit)

O arquivo `frontend/astromine_front.py` implementa um painel de controle completo com tema espacial/dark.

### Funcionalidades

- **Conexao direta ao PostgreSQL** via SQLAlchemy + query SQL com JOINs entre `asteroids`, `mineral_analysis` e `reports`;
- **Dados mock** gerados automaticamente quando o banco esta vazio (40 asteroides sinteticos);
- **Filtros avancados na sidebar**: viabilidade economica, nivel de risco, classe geologica, range de diametro, ROI minimo;
- **Metricas de negocio calculadas em tempo real**: custo de extracao (proxy), ROI, viabilidade economica (Alta/Moderada/Baixa/Inviavel), nivel de risco orbital (Critico/Alto/Moderado/Baixo).

### Graficos interativos (Plotly)

1. **Scatter: Valor Estimado vs. Custo de Extracao** — com linha de break-even, escala logaritmica, cor por classe geologica;
2. **Box Plot: ROI por Classe Geologica** — distribuicao de retorno por tipo de asteroide;
3. **Barras empilhadas: Risco x Viabilidade** — cruzamento entre risco orbital e viabilidade economica;
4. **Bubble: Confianca IA x Teor Mineral** — qualidade da predicao por viabilidade;
5. **Scatter: Densidade x Diametro** — perfil fisico por classe;
6. **Donut: Composicao da Carteira** — valor total por classe geologica.

### Catalogo completo

Tabela interativa com todas as colunas: nome, classe, diametro, densidade, MOID, mineral principal, teor, valor estimado, ROI, viabilidade, risco, confianca IA, modelo e data de analise.

### Execucao

```bash
streamlit run frontend/astromine_front.py
```

---

## Modulos Legados: Simulador + Trajetoria Quantica

### Camada de simulacao (`simulador/`)

- `simulador/domain`: entidades e regras de captura.
- `simulador/application`: casos de uso do simulador.
- `simulador/infrastructure`: OpenCV, persistencia JSON e ponte para o modulo quantico.
- `simulador/presentation`: controller de orquestracao da captura.

### Camada de trajetoria (`trajetoria_asteroid/`)

- `trajetoria_asteroid/domain`: entidades orbitais e servicos matematicos.
- `trajetoria_asteroid/application`: caso de uso de otimizacao.
- `trajetoria_asteroid/infrastructure`: adaptador Qiskit e geracao de graficos.
- `trajetoria_asteroid/presentation`: controller para calculo, grafico e animacao.

### Fluxo de captura

1. a camera detecta o maior contorno em movimento em cada frame;
2. os pontos sao amostrados em intervalos fixos de 0,5 segundo;
3. a coleta dura 10 segundos;
4. os pontos capturados sao ajustados por uma curva polinomial de grau 2;
5. a curva ajustada gera janelas futuras de trajetoria para o QAOA.

## Estrutura do Projeto

```text
AstroMine-IA/
├── ai/
│   └── vision_ml_pipeline.py          # Pipeline: OpenCV + Random Forest + Persistencia
├── astromine-api/
│   ├── main.py                        # FastAPI: endpoints CRUD + sincronizacao NASA
│   └── models/
│       └── asteroid.py                # Modelo Pydantic AsteroideResponse
├── database/
│   ├── README.md                      # Documentacao do schema
│   └── schema.sql                     # DDL: asteroids, mineral_analysis, reports, space_images
├── frontend/
│   └── astromine_front.py             # Dashboard Streamlit com Plotly
├── simulador/
│   ├── application/
│   ├── domain/
│   ├── infrastructure/
│   ├── presentation/
│   ├── camera_trajetoria.py
│   ├── enviar_para_quantico.py
│   └── trajetoria_capturada.json
├── trajetoria_asteroid/
│   ├── application/
│   ├── domain/
│   ├── infrastructure/
│   ├── presentation/
│   ├── algoritimo_quantico.py
│   ├── grafico_trajeto.png
│   ├── grafico_trajeto_animado.gif
│   ├── grafico_trajeto_capturado.png
│   └── grafico_trajeto_capturado_animado.gif
├── assets/
│   └── logo-fiap.png
├── .env                               # Variaveis de ambiente (DB_HOST, DB_PORT, etc.)
├── instala.sh
├── main.py
├── requirement.txt
└── README.md
```

## Requisitos

- Python 3.9+ com suporte a `venv`
- PostgreSQL instalado e em execucao
- Variaveis de ambiente configuradas no arquivo `.env`:
  - `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- Permissao de camera (apenas para o modulo simulador)

## Dependencias

As dependencias utilizadas pelo projeto incluem:

**Pipeline de IA e API:**
- `fastapi`
- `uvicorn`
- `psycopg2` (ou `psycopg2-binary`)
- `scikit-learn`
- `pandas`
- `requests`
- `python-dotenv`
- `pydantic`

**Dashboard:**
- `streamlit`
- `plotly`
- `sqlalchemy`

**Simulador e Quantico:**
- `qiskit`
- `qiskit-aer`
- `qiskit-algorithms`
- `numpy`
- `opencv-python`
- `matplotlib`
- `pillow`

Instale via `requirement.txt`:

```bash
pip install -r requirement.txt
```

## Como Executar

### 1. Configurar o banco de dados

```bash
psql -U postgres -d astromine_db -f database/schema.sql
```

### 2. Configurar variaveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=astromine_db
DB_USER=postgres
DB_PASSWORD=sua_senha
```

### 3. Iniciar a API

```bash
cd astromine-api
uvicorn main:app --reload --port 8000
```

### 4. Sincronizar dados da NASA

Faca um POST para sincronizar asteroides reais:

```bash
curl -X POST "http://localhost:8000/sincronizar-asteroides?limit=50"
```

### 5. Rodar o pipeline de IA

```bash
python ai/vision_ml_pipeline.py
```

### 6. Abrir o dashboard

```bash
streamlit run frontend/astromine_front.py
```

### 7. Fluxo do simulador quantico (opcional)

```bash
source ./instala.sh
python main.py          # Fluxo completo com camera
python main.py captura  # Reutiliza ultima captura
python main.py grafico  # Apenas exemplo quantico
```

## Arquivos de Saida

- `simulador/trajetoria_capturada.json`: pontos capturados pela camera.
- `trajetoria_asteroid/grafico_trajeto.png`: grafico do exemplo quantico padrao.
- `trajetoria_asteroid/grafico_trajeto_animado.gif`: animacao do exemplo quantico padrao.
- `trajetoria_asteroid/grafico_trajeto_capturado.png`: grafico da trajetoria capturada.
- `trajetoria_asteroid/grafico_trajeto_capturado_animado.gif`: animacao da trajetoria capturada.

## Roadmap Tecnico

Possiveis evolucoes futuras para o projeto:

- substituir a aproximacao polinomial por modelos dinamicos orbitais mais completos;
- adicionar filtros e calibracao espacial para converter pixels em unidades fisicas;
- treinar o modelo de IA com datasets reais de espectroscopia de asteroides;
- integrar o modulo quantico (QAOA) ao fluxo principal da API;
- adicionar autenticacao e controle de acesso a API;
- deploy em nuvem com Docker Compose.

## Limitacoes Atuais

- o modelo Random Forest e treinado com dados sinteticos (nao ha dataset espectral real disponivel);
- o modelo nao linear do simulador usa ajuste polinomial, nao simulacao astrodinamica completa;
- o acesso a camera depende das permissoes do sistema operacional;
- o QAOA gera warnings do SciPy relacionados a performance, mas eles nao interrompem a execucao;
- o dashboard exibe dados mock quando o banco de dados esta vazio.

## Licenca

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> esta licenciado sob <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>