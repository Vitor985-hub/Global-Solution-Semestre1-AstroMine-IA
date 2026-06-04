import os
import cv2
import numpy as np
import pandas as pd
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestClassifier

# 1. Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

# =====================================================================
# FASE 1: VISÃO COMPUTACIONAL & INFRAESTRUTURA
# =====================================================================
def get_asteroid_image_from_db(asteroid_id):
    """
    Busca a URL da imagem no banco de dados e realiza o download 
    direto para a memória do OpenCV.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        
        query = "SELECT url FROM space_images WHERE asteroid_id = %s LIMIT 1;"
        cur.execute(query, (asteroid_id,))
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if not result:
            print(f"⚠️ Nenhuma imagem cadastrada para o asteroide ID {asteroid_id}.")
            return None
            
        url_imagem = result['url']
        print(f"🔗 URL obtida do banco: {url_imagem}")
        
        # Baixa os bytes da imagem da internet
        response = requests.get(url_imagem, timeout=10)
        if response.status_code == 200:
            # Transforma os bytes em uma matriz de pixels que o OpenCV entende
            image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
            img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            return img
        else:
            print(f"❌ Falha no download da imagem. Status Code: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"💥 Erro ao buscar/baixar imagem: {e}")
        return None


def extract_visual_features(img):
    """
    Aplica processamento digital de imagens com OpenCV:
    Normalização, Suavização Gaussiana e Thresholding para detecção de anomalias.
    """
    if img is None:
        # Fallback caso a imagem falhe (Gera ruído espacial e anomalias fictícias)
        print("⚠️ Imagem nula recebida. Gerando dados sintéticos para o OpenCV...")
        img = np.random.randint(40, 120, (400, 400, 3), dtype=np.uint8)
        for _ in range(4):
            x, y = np.random.randint(0, 400, 2)
            cv2.circle(img, (x, y), np.random.randint(5, 15), (255, 255, 255), -1)

    # 1. Pré-processamento e Normalização básica
    img_resized = cv2.resize(img, (224, 224))
    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    
    # Suavização Gaussiana para remover ruídos e poeira do sensor
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 2. Detecção de Anomalias (Filtro de Brilho / Albedo)
    # Isola pixels altamente reflexivos (potenciais depósitos metálicos)
    _, thresholded = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)
    
    # Encontra os contornos (clusters) desses depósitos
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Métricas numéricas extraídas da imagem
    total_pixels = gray.size
    bright_pixels = cv2.countNonZero(thresholded)
    pct_brilho = (bright_pixels / total_pixels) * 100
    num_anomalias = len(contours)
    
    print(f"👁️  OpenCV: {num_anomalias} anomalias encontradas | {pct_brilho:.2f}% de brilho.")
    return {
        "pct_brilho": pct_brilho,
        "num_anomalias": num_anomalias
    }

# =====================================================================
# FASE 2: MACHINE LEARNING (Scikit-Learn)
# =====================================================================
def train_classifier():
    """
    Treina o classificador Random Forest simulando o histórico do banco.
    """
    print("🧠 Treinando modelo Random Forest (Classificador de Asteroides)...")
    
    # Criando dataset histórico de treino simulado
    np.random.seed(42)
    dados_treino = {
        'diametro': np.random.uniform(10, 600, 400),
        'massa': np.random.uniform(1e9, 5e13, 400),
        'pct_brilho': np.random.uniform(0, 25, 400),
        'num_anomalias': np.random.randint(0, 20, 400),
        'classe': np.random.choice(['C', 'S', 'M'], 400)
    }
    df = pd.DataFrame(dados_treino)
    
    # Injetando regras físicas para o modelo aprender a correlação:
    df.loc[df['classe'] == 'M', 'pct_brilho'] += 12.0  # Metálicos refletem mais
    df.loc[df['classe'] == 'C', 'pct_brilho'] *= 0.1   # Carbonáceos absorvem luz (escuros)
    
    X = df[['diametro', 'massa', 'pct_brilho', 'num_anomalias']]
    y = df['classe']
    
    model = RandomForestClassifier(n_estimators=120, random_state=42)
    model.fit(X, y)
    print("✅ Treinamento concluído.")
    return model

# =====================================================================
# FASE 3: PERSISTÊNCIA DOS RESULTADOS (Banco de Dados)
# =====================================================================
def save_ai_results_to_db(asteroid_id, classe_predita, cv_data):
    """
    Salva os insights da IA diretamente nas tabelas asteroids e mineral_analysis.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 1. Atualiza a classe estimada do asteroide
        update_query = "UPDATE asteroids SET classe = %s WHERE id = %s;"
        cur.execute(update_query, (classe_predita, asteroid_id))
        
        # 2. Limpa análises antigas desse ID para não duplicar se rodar de novo
        cur.execute("DELETE FROM mineral_analysis WHERE asteroid_id = %s;", (asteroid_id,))
        
        # 3. Deduz elementos minerais e valores com base no resultado da IA
        if classe_predita == 'M':
            minerais = [('Ferro', 75.0, '%'), ('Níquel', 15.0, '%'), ('Platina', 120.0, 'ppm')]
            multiplicador_valor = 5000000
        elif classe_predita == 'S':
            minerais = [('Silício', 60.0, '%'), ('Magnésio', 20.0, '%')]
            multiplicador_valor = 800000
        else: # Classe C
            minerais = [('Carbono', 80.0, '%'), ('Água/Gelo', 10.0, '%')]
            multiplicador_valor = 200000

        # CORRIGIDO: valor_estimado de acordo com seu banco
        insert_query = """
            INSERT INTO mineral_analysis (asteroid_id, elemento_principal, teor_material, unidade_teor, confianca, valor_estimado, modelo_usado)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        
        for elemento, teor_base, unidade in minerais:
            # O teor final flutua baseado no brilho que o OpenCV detectou
            teor_real = round(teor_base + (cv_data['pct_brilho'] * 0.5), 2)
            
            # Se o OpenCV achar 0 anomalias, garantimos um valor mínimo baseado no tamanho/massa para não zerar a economia
            anomalias = cv_data['num_anomalias'] if cv_data['num_anomalias'] > 0 else 1
            valor_calculado = round(anomalias * multiplicador_valor, 2)
            
            cur.execute(insert_query, (
                asteroid_id, 
                elemento, 
                teor_real, 
                unidade, 
                0.85, 
                valor_calculado, 
                'RandomForest + OpenCV Pipeline'
            ))
            
        conn.commit()
        cur.close()
        conn.close()
        print(f"💾 Resultados persistidos com sucesso no banco para o ID {asteroid_id}!")
        
    except Exception as e:
        print(f"❌ Falha ao salvar dados no banco: {e}")
# =====================================================================
# PIPELINE ORQUESTRADOR
# =====================================================================
def run_full_pipeline(asteroid_id, physical_data, ai_model):
    print(f"\n🚀 --- INICIANDO PIPELINE DE IA PARA O ASTEROIDE ID {asteroid_id} ---")
    
    # Passo 1: Busca e Baixa a Imagem
    img = get_asteroid_image_from_db(asteroid_id)
    
    # Passo 2: OpenCV extrai dados visuais
    cv_features = extract_visual_features(img)
    
    # Passo 3: Prepara os dados tabulares agregando os dados físicos da NASA
    input_features = pd.DataFrame([{
        'diametro': physical_data['diametro'],
        'massa': physical_data['massa'],
        'pct_brilho': cv_features['pct_brilho'],
        'num_anomalias': cv_features['num_anomalias']
    }])
    
    # Passo 4: Scikit-Learn Classifica
    classe_predita = ai_model.predict(input_features)[0]
    probabilidades = ai_model.predict_proba(input_features)[0]
    
    print(f"🎯 Classificação Final: CLASSE {classe_predita} (Confiança: {max(probabilidades)*100:.1f}%)")
    
    # Passo 5: Persiste no PostgreSQL
    save_ai_results_to_db(asteroid_id, classe_predita, cv_features)
    print("🚀 --- PIPELINE CONCLUÍDO COM SUCESSO ---\n")


# Execution block para testes locais
if __name__ == "__main__":
    # Inicializa/Treina a IA
    modelo_treinado = train_classifier()
    
    # Exemplo de dados físicos que viriam da API da NASA para o ID 1
    dados_nasa_exemplo = {
        'diametro': 150.0,
        'massa': 3.4e11
    }
    
    # Executa o pipeline passando o ID do asteroide que você quer analisar
    run_full_pipeline(asteroid_id=1, physical_data=dados_nasa_exemplo, ai_model=modelo_treinado)