import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Query
from typing import List
import requests
import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from models.asteroid import AsteroideResponse

# Instanciando o FastAPI
app = FastAPI()

load_dotenv()

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

def get_db():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
    finally:
        conn.close()


# # Simulação de banco de dados em memória
# asteroids_db = [
#     {"id":1, "name": "Asteroid 1", "estimated_size_min": 10, "estimated_size_max": 20, "velocity_kph": 50000, "distance_from_earth_km": 7500000, "orbital_class": "Apollo", "is_potentially_hazardous": True, "created_at": "2024-06-01T12:00:00Z"},
#     {"id":2, "name": "Asteroid 2", "estimated_size_min": 5, "estimated_size_max": 15, "velocity_kph": 30000, "distance_from_earth_km": 15000000, "orbital_class": "Amor", "is_potentially_hazardous": False, "created_at": "2024-06-02T12:00:00Z"},
# ]


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
def sincronizar_dados_sbdb(
    limit: int = Query(50, gt=0, le=100, description="Número máximo de registros a buscar"),
):
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
            formato = row[field_indices.get("extent")]
            densidade = safe_float(row[field_indices.get("density")])
            moid = safe_float(row[field_indices.get("moid")])
            distancia_min_terra = moid * 149597870.7 if moid is not None else None # converte o moid retornado pela API de unidades de AU para km

            if not name:
                continue

            cur.execute("SELECT id FROM asteroids WHERE nome = %s LIMIT 1", (name,))
            row_exists = cur.fetchone()

            classe_padrao = classe or "ND"
            if row_exists:
                asteroid_id = row_exists[0]
                cur.execute(
                    "UPDATE asteroids SET classe = %s, diametro = %s, formato = %s, densidade = %s, distancia_min_terra = %s WHERE id = %s",
                    (classe_padrao, diam, formato, densidade, distancia_min_terra, asteroid_id),
                )
            else:
                cur.execute(
                    "INSERT INTO asteroids (nome, classe, diametro, formato, densidade, distancia_min_terra) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                    (name, classe_padrao, diam, formato, densidade, distancia_min_terra),
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
