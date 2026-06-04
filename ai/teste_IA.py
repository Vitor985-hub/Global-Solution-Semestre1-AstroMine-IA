import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

def popular_banco_inicial():
    print("🌱 Populando banco de dados com asteroide de teste...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 1. Garante que o banco está limpo para o teste não duplicar
        cur.execute("TRUNCATE TABLE space_images, reports, mineral_analysis, asteroids RESTART IDENTITY CASCADE;")
        
        # 2. Insere o asteroide base (ID 1) - Deixamos a classe vazia porque a IA vai preencher
        insert_asteroid = """
            INSERT INTO asteroids (id, nome, classe, diametro, formato, massa, densidade, volume, distancia_min_terra)
            VALUES (1, 'Vesta-77', '?', 525.4, 'Esferoidal', 2.59e20, 3.42, 7.4e7, 1.2e8);
        """
        cur.execute(insert_asteroid)
        
        # 3. Insere a URL de uma imagem espacial real na tabela space_images linked ao ID 1
        # Usando uma foto pública da própria NASA (Asteroide Vesta)
        url_nasa_real = "https://images-assets.nasa.gov/image/PIA14313/PIA14313~orig.jpg"
        
        insert_image = """
            INSERT INTO space_images (asteroid_id, url)
            VALUES (1, %s);
        """
        cur.execute(insert_image, (url_nasa_real,))
        
        conn.commit()
        cur.close()
        conn.close()
        print("🚀 Banco populado! Asteroide ID 1 criado com imagem real vinculada.")
        
    except Exception as e:
        print(f"❌ Erro ao popular banco: {repr(e)}")

if __name__ == "__main__":
    popular_banco_inicial()

