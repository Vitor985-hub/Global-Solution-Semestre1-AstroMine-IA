import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Query
from typing import List
import hashlib
import logging
import math
import random
import requests
import os
import psycopg2
import re
from datetime import datetime
from dotenv import load_dotenv
from models.asteroid import AsteroideResponse

# Instanciando o FastAPI
app = FastAPI()

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("astromine-api")

# Configuração de acesso à API SBDB da NASA/JPL
SBDB_API_URL = "https://ssd-api.jpl.nasa.gov/sbdb_query.api"

# Configurações de conexão com o banco de dados
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

# Densidade em g/cm³: perfis usados como fallback quando a API não informar o valor real.
ASTEROID_DENSITY_PROFILES = {
    "APOLLO": (1.5, 3.2),
    "AMOR": (1.4, 2.9),
    "ATEN": (1.8, 3.4),
    "ATIRA": (2.0, 3.8),
    "HUNGARIA": (2.8, 4.2),
    "HILDA": (1.0, 2.5),
    "THULE": (2.5, 4.5),
    "C": (1.2, 2.5),
    "B": (1.2, 2.3),
    "S": (2.2, 3.6),
    "M": (4.5, 8.5),
    "D": (0.8, 2.0),
    "P": (0.8, 2.2),
    "T": (1.2, 3.0),
    "V": (2.7, 3.7),
    "E": (3.5, 5.5),
    "X": (3.0, 5.5),
    "ND": (1.8, 4.0),
}

# Diâmetro em km: perfis usados como fallback quando a API não informar o valor real.
ASTEROID_DIAMETER_PROFILES = {
    "APOLLO": (1.0, 90.0),
    "AMOR": (1.0, 120.0),
    "ATEN": (0.5, 60.0),
    "ATIRA": (0.2, 25.0),
    "HUNGARIA": (0.5, 30.0),
    "HILDA": (5.0, 150.0),
    "THULE": (20.0, 250.0),
    "C": (5.0, 120.0),
    "B": (5.0, 110.0),
    "S": (1.0, 80.0),
    "M": (0.5, 60.0),
    "D": (10.0, 150.0),
    "P": (10.0, 150.0),
    "T": (2.0, 80.0),
    "V": (1.0, 60.0),
    "E": (0.5, 20.0),
    "X": (1.0, 70.0),
    "ND": (1.0, 100.0),
}

# Gera um RNG estável baseado em uma combinação de atributos do asteroides
def _stable_rng(*parts: object) -> random.Random:
    seed_source = "|".join("" if part is None else str(part) for part in parts)
    seed = int(hashlib.sha256(seed_source.encode("utf-8")).hexdigest()[:16], 16)
    return random.Random(seed)

# Normaliza a classe para escolher faixas coerentes de densidade e diâmetro
def _normalizar_classe(classe: str | None) -> str:
    if not classe:
        return "ND"
    classe_normalizada = str(classe).strip().upper()
    if classe_normalizada in ASTEROID_DENSITY_PROFILES:
        return classe_normalizada

    primeira_letra = classe_normalizada[:1]
    if primeira_letra in ASTEROID_DENSITY_PROFILES:
        return primeira_letra

    return "ND"

# Estima as dimensões do asteroide usando os perfis de classe e um RNG estável quando os dados reais não estão disponíveis
def _estimar_dimensoes_asteroide(nome: str, classe: str | None, diametro: float | None, densidade: float | None, volume: float | None):
    classe_normalizada = _normalizar_classe(classe)
    rng = _stable_rng(nome, classe_normalizada)

    diametro_estimado = diametro
    if diametro_estimado is None:
        diam_min, diam_max = ASTEROID_DIAMETER_PROFILES.get(classe_normalizada, ASTEROID_DIAMETER_PROFILES["ND"])
        diametro_estimado = round(rng.uniform(diam_min, diam_max), 3)

    densidade_estimado = densidade
    if densidade_estimado is None:
        dens_min, dens_max = ASTEROID_DENSITY_PROFILES.get(classe_normalizada, ASTEROID_DENSITY_PROFILES["ND"])
        densidade_estimado = round(rng.uniform(dens_min, dens_max), 3)

    volume_estimado = volume
    if volume_estimado is None and diametro_estimado is not None:
        raio_km = diametro_estimado / 2.0
        volume_estimado = round((4.0 / 3.0) * math.pi * (raio_km ** 3), 3)

    massa_estimado = None
    if densidade_estimado is not None and volume_estimado is not None:
        massa_estimado = round(densidade_estimado * volume_estimado * 1e12, 3)

    if diametro is None or densidade is None or volume is None:
        logger.info(
            "Estimativa aplicada para %s (classe %s): diametro=%s, densidade=%s, volume=%s, massa=%s",
            nome,
            classe_normalizada,
            diametro_estimado,
            densidade_estimado,
            volume_estimado,
            massa_estimado,
        )
    return classe_normalizada, diametro_estimado, densidade_estimado, volume_estimado, massa_estimado

# Simula o formato no padrão "000 x 000 x 000" quando a API não informar o valor real
def _simular_formato_asteroide(nome: str, classe: str | None, diametro: float | None, formato: str | None):
    if formato:
        formato_texto = str(formato).strip()
        if re.search(r"\d\s*x\s*\d\s*x\s*\d", formato_texto, flags=re.IGNORECASE):
            return formato_texto

    classe_normalizada = _normalizar_classe(classe)
    rng = _stable_rng(nome, classe_normalizada, diametro, "formato")

    base = diametro if diametro is not None else rng.uniform(1.0, 100.0)
    eixo_maior = max(1, int(round(base * rng.uniform(0.9, 1.25))))
    eixo_medio = max(1, int(round(eixo_maior * rng.uniform(0.65, 0.95))))
    eixo_menor = max(1, int(round(eixo_medio * rng.uniform(0.55, 0.9))))

    if eixo_menor > eixo_medio:
        eixo_menor, eixo_medio = eixo_medio, eixo_menor
    if eixo_medio > eixo_maior:
        eixo_medio, eixo_maior = eixo_maior, eixo_medio

    formato_simulado = f"{eixo_maior:03d} x {eixo_medio:03d} x {eixo_menor:03d}"
    logger.info(
        "Formato estimado para %s (classe %s): %s",
        nome,
        classe_normalizada,
        formato_simulado,
    )
    return formato_simulado

def get_db():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

def obter_dados_sbdb(limit: int = 50):
    """Faz a chamada HTTP para a API SBDB Query da NASA/JPL e retorna o JSON estruturado."""

    parametros = {
        "fields": "full_name,class,diameter,extent,density,moid",
        "sb-kind": "a",
        "limit": limit, #limite de registros a buscar, pode ser ajustado conforme necessidade
    }

    print(f"🌌 Solicitando dados de asteroides com limite {limit}...")
    response = requests.get(SBDB_API_URL, params=parametros)

    if response.status_code == 200:
        print("✅ Dados recuperados com sucesso!")
        return response.json()
    else:
        print(f"❌ Falha na requisição. Status: {response.status_code}")
        print(response.text)
        return None


# Atualiza a base local com dados da SBDB
@app.post("/sincronizar-asteroides", status_code=200)
def sincronizar_dados_sbdb(limit: int = Query(50, gt=0, le=100, description="Número máximo de registros a buscar")):
    """Consome a API SBDB e salva as informações extraídas no banco de dados."""
    dados_sbdb = obter_dados_sbdb(limit)
    if dados_sbdb is None:
        raise HTTPException(status_code=502, detail="Erro ao chamar a API SBDB.")

    process_and_save_to_db(dados_sbdb)
    return {"status": "sucesso", "mensagens": "Dados sincronizados com o banco de dados."}

# Retorna todos os asteroides salvos no banco de dados
@app.get("/asteroides", response_model=List[AsteroideResponse])
def listar_asteroides_salvos(db_conn=Depends(get_db)):
    """Retorna todos os asteroides salvos no banco de dados."""
    cursor = db_conn.cursor()
    cursor.execute(
        "SELECT id, nome, classe, diametro, formato, massa, densidade, volume, distancia_min_terra FROM asteroids"
    )
    rows = cursor.fetchall()
    cursor.close()

    return [
        {
            "id": row[0],
            "nome": row[1],
            "classe": row[2],
            "diametro": row[3],
            "formato": row[4],
            "massa": row[5],
            "densidade": row[6],
            "volume": row[7],
            "distancia_min_terra": row[8],
        }
        for row in rows
    ]

@app.get("/asteroides/{asteroid_id}", response_model=AsteroideResponse)
def obter_asteroide_por_id(asteroid_id: int, db_conn=Depends(get_db)):

    """Retorna os detalhes de um asteroide específico pelo seu ID."""
    cursor = db_conn.cursor()
    cursor.execute(
        "SELECT id, nome, classe, diametro, formato, massa, densidade, volume, distancia_min_terra FROM asteroids WHERE id = %s",
        (asteroid_id,)
    )
    row = cursor.fetchone()
    cursor.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Asteroide não encontrado.")

    return {
        "id": row[0],
        "nome": row[1],
        "classe": row[2],
        "diametro": row[3],
        "formato": row[4],
        "massa": row[5],
        "densidade": row[6],
        "volume": row[7],
        "distancia_min_terra": row[8],
    }

@app.delete("/asteroides/{asteroid_id}")
def excluir_asteroide(asteroid_id: int, db_conn=Depends(get_db)):

    """Exclui um asteroide específico pelo seu ID."""
    cursor = db_conn.cursor()
    cursor.execute("DELETE FROM asteroids WHERE id = %s", (asteroid_id,))
    db_conn.commit()
    cursor.close()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Asteroide não encontrado.")

    return {"status": "sucesso", "mensagens": "Asteroide excluído com sucesso."}

@app.put("/asteroides/{asteroid_id}", response_model=AsteroideResponse)
def atualizar_asteroide(asteroid_id: int, asteroid_data: AsteroideResponse, db_conn=Depends(get_db)):   
    """Atualiza os detalhes de um asteroide específico pelo seu ID."""
    cursor = db_conn.cursor()
    cursor.execute(
        "UPDATE asteroids SET nome = %s, classe = %s, diametro = %s, formato = %s, massa = %s, densidade = %s, volume = %s, distancia_min_terra = %s WHERE id = %s RETURNING id",
        (
            asteroid_data.nome,
            asteroid_data.classe,
            asteroid_data.diametro,
            asteroid_data.formato,
            asteroid_data.massa,
            asteroid_data.densidade,
            asteroid_data.volume,
            asteroid_data.distancia_min_terra,
            asteroid_id
        )
    )
    updated_id = cursor.fetchone()
    db_conn.commit()
    cursor.close()

    if updated_id is None:
        raise HTTPException(status_code=404, detail="Asteroide não encontrado.")

    return {
        "id": updated_id[0],
        "nome": asteroid_data.nome,
        "classe": asteroid_data.classe,
        "diametro": asteroid_data.diametro,
        "formato": asteroid_data.formato,
        "massa": asteroid_data.massa,
        "densidade": asteroid_data.densidade,
        "volume": asteroid_data.volume,
        "distancia_min_terra": asteroid_data.distancia_min_terra,
    }

def process_and_save_to_db(raw_data: dict):
    """Interpreta a resposta da API SBDB e persiste na tabela `asteroids` do projeto"""
    if not raw_data:
        print("❗ Nenhum dado para processar.")
        return

    fields = raw_data.get("fields", [])
    data_rows = raw_data.get("data", [])
    if not fields or not data_rows:
        print("❌ Resposta SBDB não contém campos ou dados.")
        return

    field_indices = {field: idx for idx, field in enumerate(fields)}

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    processed_asteroids = 0

    def safe_float(value):
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    try:
        for row in data_rows:
            raw_name = row[field_indices.get("full_name")]
            name = raw_name.strip() if raw_name is not None else None
            classe = row[field_indices.get("class")]
            diam = safe_float(row[field_indices.get("diameter")])
            # extent vira uma string no padrão 000 x 000 x 000; se vier vazio, é simulado.
            formato = _simular_formato_asteroide(name or "ND", classe, diam, row[field_indices.get("extent")])
            densidade = safe_float(row[field_indices.get("density")])
            moid = safe_float(row[field_indices.get("moid")])
            # MOID vem em AU; aqui convertemos para km.
            distancia_min_terra = moid * 149597870.7 if moid is not None else None

            if not name:
                continue

            # Volume sai em km³ e a massa é calculada em kg a partir da densidade e do volume.
            classe_padrao, diam, densidade, volume, massa = _estimar_dimensoes_asteroide(
                name,
                classe,
                diam,
                densidade,
                None,
            )

            cur.execute("SELECT id FROM asteroids WHERE nome = %s LIMIT 1", (name,))
            row_exists = cur.fetchone()
            if row_exists:
                asteroid_id = row_exists[0]
                cur.execute(
                    "UPDATE asteroids SET classe = %s, diametro = %s, formato = %s, massa = %s, densidade = %s, volume = %s, distancia_min_terra = %s WHERE id = %s",
                    (classe_padrao, diam, formato, massa, densidade, volume, distancia_min_terra, asteroid_id),
                )
            else:
                cur.execute(
                    "INSERT INTO asteroids (nome, classe, diametro, formato, massa, densidade, volume, distancia_min_terra) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
                    (name, classe_padrao, diam, formato, massa, densidade, volume, distancia_min_terra),
                )
                asteroid_id = cur.fetchone()[0]

            processed_asteroids += 1

        conn.commit()
        print(f"✅ {processed_asteroids} asteroides processados.")

    except Exception as e:
        conn.rollback()
        print(f"❌ Falha ao salvar lote no banco de dados: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
