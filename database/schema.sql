-- Extensão para gerar UUIDs automaticamente
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Tabela Principal: Asteroides
CREATE TABLE asteroids (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nasa_neo_id VARCHAR(50) UNIQUE NOT NULL, -- ID original da NASA (NeoWs)
    name VARCHAR(255) NOT NULL,
    estimated_size_min_km DECIMAL(10, 4),
    estimated_size_max_km DECIMAL(10, 4),
    velocity_kph DECIMAL(15, 2),
    distance_from_earth_km DECIMAL(15, 2),
    orbital_class VARCHAR(100),
    is_potentially_hazardous BOOLEAN, -- Risco
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabela: Análise Mineral (IA)
-- Relação 1:N (Um asteroide pode ter várias análises/revisões)
CREATE TABLE mineral_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asteroid_id UUID REFERENCES asteroids(id) ON DELETE CASCADE,
    predicted_mineral VARCHAR(255),
    confidence_score DECIMAL(5, 4), -- Ex: 0.9850 (98.5%)
    estimated_value_usd DECIMAL(20, 2),
    ai_model_used VARCHAR(100), -- Ex: "RandomForest-v2", "Qiskit-QSVM"
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabela: Relatórios da IA Generativa
-- Relação 1:1 ou 1:N com asteroids
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asteroid_id UUID REFERENCES asteroids(id) ON DELETE CASCADE,
    summary TEXT NOT NULL,
    economic_viability_score INTEGER, -- Escala de 1 a 10 ou 1 a 100
    full_textual_analysis TEXT,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabela: Imagens Espaciais e Visão Computacional
CREATE TABLE space_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asteroid_id UUID REFERENCES asteroids(id) ON DELETE CASCADE,
    image_url VARCHAR(512) NOT NULL,
    cv_results JSONB, -- JSONB é perfeito para guardar os bounding boxes e labels variados da IA
    processing_status VARCHAR(50) DEFAULT 'PENDING', -- PENDING, PROCESSING, COMPLETED, FAILED
    captured_at TIMESTAMP WITH TIME ZONE,
    processed_at TIMESTAMP WITH TIME ZONE
);

-- 5. Tabela: Logs de API (Observabilidade)
CREATE TABLE api_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    endpoint VARCHAR(255) NOT NULL,
    request_method VARCHAR(10), -- GET, POST
    response_time_ms INTEGER,
    status_code INTEGER,
    error_message TEXT, -- Nulo se for sucesso
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);