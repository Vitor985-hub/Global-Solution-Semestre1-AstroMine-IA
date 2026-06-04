
-- Tabela de asteroides
CREATE TABLE asteroids (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    classe VARCHAR(10) NOT NULL, -- Ex: C, S, M
    diametro NUMERIC,
    formato VARCHAR(255),
    massa NUMERIC,
    densidade NUMERIC,
    volume NUMERIC,
    distancia_min_terra NUMERIC
);

-- Tabela de análises minerais
CREATE TABLE mineral_analysis (
    id SERIAL PRIMARY KEY,
    asteroid_id INT NOT NULL REFERENCES asteroids(id) ON DELETE CASCADE,
    elemento_principal VARCHAR(100) NOT NULL,
    teor_material NUMERIC, -- concentração (% ou ppm)
    unidade_teor VARCHAR(20), -- ex: '%', 'ppm'
    confianca NUMERIC, -- grau de confiança (0-1 ou %)
    valor_estimado NUMERIC, -- valor em USD ou outra moeda
    modelo_usado VARCHAR(255)
);

-- Tabela de relatórios
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    asteroid_id INT NOT NULL REFERENCES asteroids(id) ON DELETE CASCADE,
    data_analise DATE NOT NULL,
    resumo TEXT
);

-- Tabela de imagens espaciais
CREATE TABLE space_images (
    id SERIAL PRIMARY KEY,
    asteroid_id INT NOT NULL REFERENCES asteroids(id) ON DELETE CASCADE,
    url TEXT NOT NULL
);


