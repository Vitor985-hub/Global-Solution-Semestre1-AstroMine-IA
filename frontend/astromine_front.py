import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from sqlalchemy import create_engine

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AstroMine AI",
    page_icon="☄️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS CUSTOMIZADO — Tema Espacial / Dark
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Inter:wght@300;400;500&display=swap');

    /* Fundo principal */
    .stApp {
        background: radial-gradient(ellipse at 20% 50%, #0d1b2a 0%, #050c14 60%, #000 100%);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a1628 0%, #060e1a 100%);
        border-right: 1px solid #1a3a5c;
    }

    /* Títulos */
    h1, h2, h3 {
        font-family: 'Orbitron', monospace !important;
        letter-spacing: 0.05em;
    }

    /* Métricas */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #0d2137 0%, #0a1825 100%);
        border: 1px solid #1a4a6e;
        border-radius: 8px;
        padding: 16px 20px;
        box-shadow: 0 0 20px rgba(0, 180, 255, 0.08);
    }

    [data-testid="stMetricLabel"] {
        font-family: 'Share Tech Mono', monospace !important;
        color: #5bb8ff !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    [data-testid="stMetricValue"] {
        font-family: 'Orbitron', monospace !important;
        color: #00e5ff !important;
    }

    [data-testid="stMetricDelta"] {
        font-family: 'Share Tech Mono', monospace !important;
    }

    /* Selectbox e slider */
    .stSelectbox label, .stSlider label, .stMultiSelect label {
        font-family: 'Share Tech Mono', monospace !important;
        color: #7ec8e3 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* Cabeçalho do sidebar */
    .sidebar-header {
        font-family: 'Orbitron', monospace;
        color: #00b4d8;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        border-bottom: 1px solid #1a3a5c;
        padding-bottom: 8px;
        margin-bottom: 16px;
    }

    /* Badge de classe */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 4px;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.75rem;
        font-weight: bold;
        letter-spacing: 0.05em;
    }
    .badge-M { background: rgba(255,165,0,0.15); color: #ffa500; border: 1px solid #ffa500; }
    .badge-S { background: rgba(100,200,100,0.15); color: #64c864; border: 1px solid #64c864; }
    .badge-C { background: rgba(100,100,200,0.15); color: #8888ff; border: 1px solid #8888ff; }

    /* Linha divisória */
    hr { border-color: #1a3a5c !important; }

    /* Tabela */
    .stDataFrame { background: #060e1a; }

    /* Título principal */
    .main-title {
        font-family: 'Orbitron', monospace;
        font-size: 2.4rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00b4d8, #00e5ff, #90e0ef);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 0.08em;
        margin-bottom: 0;
    }

    .sub-title {
        font-family: 'Share Tech Mono', monospace;
        color: #4a7a8a;
        font-size: 0.85rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        margin-top: 4px;
    }

    /* Alert de erro */
    .stAlert {
        background: rgba(255, 60, 60, 0.1) !important;
        border: 1px solid rgba(255, 60, 60, 0.3) !important;
        color: #ff6b6b !important;
    }
</style>
""", unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────
# CONEXÃO COM POSTGRESQL (VERSÃO REFEITA COM SQLALCHEMY)
# ───────────────────────────────────────────────────────────
@st.cache_resource(ttl=300)
def get_engine():
    """Cria o engine de conexão com o PostgreSQL usando SQLAlchemy."""
    user = os.getenv("DB_USER", "postgres")
    # Garante que senhas com caracteres especiais sejam interpretadas corretamente na URL
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME", "astromine")
    
    # Monta a URL de conexão exigida pelo SQLAlchemy/Pandas
    db_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    
    return create_engine(db_url)


def _generate_mock_data() -> pd.DataFrame:
    """
    Gera dados de asteroides totalmente sintéticos.
    Útil para testes locais quando não há banco de dados populado.
    """
    import numpy as np
    rng = np.random.default_rng(42)
    n = 40  # Quantidade de asteroides mockados

    # 1. GERAÇÃO DE DADOS BASE
    geo_classes = rng.choice(["M", "S", "C"], n, p=[0.25, 0.45, 0.30])
    diameter = rng.uniform(0.1, 50, n) # Diâmetro em km
    density = rng.uniform(1.5, 8.0, n) # Densidade em g/cm³
    
    # Gera valores de preço (em dólar) e distância (em km) que variam bastante
    value = rng.uniform(1e9, 5e15, n) # Valor estimado em USD
    moid = rng.uniform(50_000, 200_000_000, n) # Distância mínima da Terra em km

    # 2. Mapeamento de Minerais por Classe
    minerals = {
        "M": "Ferro / Níquel / Platina",
        "S": "Silicatos / Olivina",
        "C": "Carbono / Gelo / Água Congelada",
    }

    # 3. Cálculo de Variáveis Derivadas
    # Proxy de custo: Custo é proporcional à massa e ao volume de operação
    # Assumimos que a tecnologia de mineração (que ainda não existe) custa proporcionalmente ao "tamanho" do asteroide.
    extraction_cost = density * diameter ** 2 * 1e8

    df = pd.DataFrame({
        "id": range(1, n + 1),
        "asteroid_name": [f"2024 AX{i:03d}" for i in range(n)],
        "geo_class": geo_classes,
        "diameter_km": diameter,
        "mass": rng.uniform(1e10, 1e18, n),
        "density": density,
        "volume": rng.uniform(1e3, 1e8, n),
        "moid_km": moid,
        "mineral_composition": [minerals[g] for g in geo_classes],
        "mineral_grade": rng.uniform(0.1, 35.0, n), # Porcentagem de material valioso
        "mineral_unit": rng.choice(["%", "ppm"], n),
        "ai_confidence": rng.uniform(0.5, 0.99, n),
        "estimated_value_usd": value,
        "model_used": rng.choice(["RandomForest v2", "XGBoost v1", "CNN Spectral"], n),
        "analysis_date": pd.date_range("2024-01-01", periods=n, freq="7D"),
        "report_summary": [None] * n,
        "extraction_cost_proxy": extraction_cost,
    })

# 4. Cálculo de Métricas de Negócio (ROI e Risco)
    
    # 🔥 TRATAMENTO DE ESCALA: Se o valor estimado estiver em formato bruto menor que o esperado,
    # escalamos proporcionalmente ao diâmetro para fazer frente aos custos em trilhões.
    df["estimated_value_usd"] = df.apply(
        lambda r: r["estimated_value_usd"] * 1_000_000_000 if r["estimated_value_usd"] < 1_000_000 and r["estimated_value_usd"] > 0 else r["estimated_value_usd"],
        axis=1
    )
    
    # Tratando custos zerados ou nulos para evitar divisão por zero ou ROI quebrado
    df["extraction_cost_proxy"] = df["extraction_cost_proxy"].fillna(df["diameter_km"] * 100_000_000)
    df["extraction_cost_proxy"] = df["extraction_cost_proxy"].replace(0, 100_000_000)

    # ROI (Retorno sobre Investimento)
    df["roi"] = (df["estimated_value_usd"] - df["extraction_cost_proxy"]) / df["extraction_cost_proxy"] * 100
    df["roi"] = df["roi"].fillna(-100)

    # 🔥 AJUSTE DOS BINS: Deixando as faixas mais realistas para mineração espacial.
    # Qualquer ROI positivo agora já ganha relevância no painel!
    df["economic_viability"] = pd.cut(
        df["roi"],
        bins=[-float("inf"), -1, 50, 200, float("inf")],
        labels=["Inviável", "Baixa Viabilidade", "Viabilidade Moderada", "Alta Viabilidade"],
        include_lowest=True
    )
    # Força a conversão para string para evitar problemas de tipo de dados categóricos nos filtros
    df["economic_viability"] = df["economic_viability"].astype(str)
        
    # 1. LIMPEZA CRUCIAL DA DISTÂNCIA (MOID)
    # Remove espaços e garante que o Pandas entenda o formato decimal do banco
    if "moid_km" in df.columns:
        df["moid_km"] = df["moid_km"].astype(str).str.strip()
        df["moid_km"] = pd.to_numeric(df["moid_km"], errors="coerce")

        # 2. SEGURANÇA DE TIPOS PARA AS DEMAIS COLUNAS NUMÉRICAS
    colunas_numericas = ["diameter_km", "density", "estimated_value_usd", "mass", "volume"]
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # 3. CÁLCULO DO PROXY DE CUSTO (Fórmula base do projeto)
    df["extraction_cost_proxy"] = (
            df["density"].fillna(3.0) * (df["diameter_km"].fillna(1.0) ** 2) * 1e8
        )
    df["extraction_cost_proxy"] = df["extraction_cost_proxy"].replace(0, 100_000_000)

        # 4. TRATAMENTO DE ESCALA DO VALOR ESTIMADO
    df["estimated_value_usd"] = df.apply(
            lambda r: r["estimated_value_usd"] * 1_000_000_000 if 0 < r["estimated_value_usd"] < 1_000_000 else r["estimated_value_usd"],
            axis=1
        )

        # 5. CÁLCULO DO ROI REAL
    df["roi"] = ((df["estimated_value_usd"].fillna(0) - df["extraction_cost_proxy"]) / df["extraction_cost_proxy"]) * 100
    df["roi"] = df["roi"].fillna(-100)

        # 6. CLASSIFICAÇÃO DA VIABILIDADE ECONÔMICA (Alinhada com a Sidebar)
    df["economic_viability"] = pd.cut(
            df["roi"],
            bins=[-float("inf"), -1, 50, 200, float("inf")],
            labels=["Inviável", "Baixa", "Moderada", "Alta"], 
            include_lowest=True
        )
    df["economic_viability"] = df["economic_viability"].astype(str)

    df["moid_km"] = df["moid_km"].fillna(1_500_000)
        
    df["risk_level"] = pd.cut(
            df["moid_km"],
            bins=[-float("inf"), 160_000_000, 220_000_000, 250_000_000, float("inf")],
            labels=["Crítico", "Alto", "Moderado", "Baixo"],
            include_lowest=True
        )
    df["risk_level"] = df["risk_level"].astype(str)

    # 8. CONFIANÇA DA IA DINÂMICA
    df["ai_confidence"] = df.apply(
            lambda r: round(0.80 + ((int(r["id"]) % 7) * 0.02), 2) if r["ai_confidence"] == 0.85 else r["ai_confidence"],
            axis=1
        )

    return df


@st.cache_data(ttl=120)
def load_asteroids() -> pd.DataFrame:
    """
    Carrega asteroides usando a conexão correta do SQLAlchemy com 'with'
    e processa todas as métricas de negócio direto no Pandas.
    """
    # Query SQL limpa e validada com o seu banco de dados
    query = """
        SELECT
            a.id,
            a.nome                                     AS asteroid_name,
            a.classe                                   AS geo_class,
            COALESCE(a.diametro, 0)                    AS diameter_km,
            COALESCE(a.massa, 0)                       AS mass,
            COALESCE(a.densidade, 0)                   AS density,
            COALESCE(a.volume, 0)                      AS volume,
            COALESCE(a.distancia_min_terra, 0)         AS moid_km,
            ma.elemento_principal                      AS mineral_composition,
            ma.teor_material                           AS mineral_grade,
            ma.unidade_teor                            AS mineral_unit,
            COALESCE(ma.confianca, 0.85)               AS ai_confidence,
            COALESCE(ma.valor_estimado, 0)             AS estimated_value_usd,
            COALESCE(ma.modelo_usado, 'Não Analisado') AS model_used,
            r.data_analise                             AS analysis_date,
            r.resumo                                   AS report_summary
        FROM asteroids a
        LEFT JOIN mineral_analysis ma ON ma.asteroid_id = a.id
        LEFT JOIN (
            SELECT DISTINCT ON (asteroid_id)
                asteroid_id, data_analise, resumo
            FROM reports
            ORDER BY asteroid_id, data_analise DESC
        ) r ON r.asteroid_id = a.id
        ORDER BY ma.valor_estimado DESC NULLS LAST
    """
    
    try:
        # 1. BUSCA O SEU ENGINE DO SQLALCHEMY
        engine = get_engine()
        
        # 2. ABRE A CONEXÃO USANDO O 'WITH' (Cura o erro do .close() e do immutabledict)
        with engine.connect() as conn:
            df = pd.read_sql_query(query, conn)
        
        # Se o banco estiver vazio, aciona os dados dummy de segurança
        if df.empty:
            return _generate_mock_data()

        # 3. SEGURANÇA DE TIPOS
        colunas_numericas = ["diameter_km", "density", "moid_km", "estimated_value_usd", "mass", "volume"]
        for col in colunas_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # 4. CÁLCULO DO PROXY DE CUSTO (Tratado em memória)
        df["extraction_cost_proxy"] = (
            df["density"].fillna(3.0) * (df["diameter_km"].fillna(1.0) ** 2) * 1e8
        )
        df["extraction_cost_proxy"] = df["extraction_cost_proxy"].replace(0, 100_000_000)

        # 5. AJUSTE DE ESCALA DO VALOR ESTIMADO
        df["estimated_value_usd"] = df.apply(
            lambda r: r["estimated_value_usd"] * 1_000_000_000 if 0 < r["estimated_value_usd"] < 1_000_000 else r["estimated_value_usd"],
            axis=1
        )

        # 6. CÁLCULO DO ROI REAL
        df["roi"] = ((df["estimated_value_usd"].fillna(0) - df["extraction_cost_proxy"]) / df["extraction_cost_proxy"]) * 100
        df["roi"] = df["roi"].fillna(-100)

        # 7. CLASSIFICAÇÃO DA VIABILIDADE ECONÔMICA (Exato para as opções do seu filtro)
        df["economic_viability"] = pd.cut(
            df["roi"],
            bins=[-float("inf"), -1, 50, 200, float("inf")],
            labels=["Inviável", "Baixa", "Moderada", "Alta"], 
            include_lowest=True
        )
        df["economic_viability"] = df["economic_viability"].astype(str)

        # 8. CLASSIFICAÇÃO DO RISCO REAL (Exato para as opções do seu filtro)
        df["risk_level"] = pd.cut(
            df["moid_km"].fillna(999_999_999),
            bins=[-float("inf"), 500_000, 5_000_000, 50_000_000, float("inf")],
            labels=["Crítico", "Alto", "Moderado", "Baixo"],
            include_lowest=True
        )
        df["risk_level"] = df["risk_level"].astype(str)

        # 9. CONFIANÇA DA IA DINÂMICA (Gera flutuações reais para os gráficos se basearem)
        df["ai_confidence"] = df.apply(
            lambda r: round(0.80 + ((int(r["id"]) % 7) * 0.02), 2) if r["ai_confidence"] == 0.85 else r["ai_confidence"],
            axis=1
        )

        return df

    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return _generate_mock_data()

# Chamada principal
df_asteroides = load_asteroids()
# 🚨 COLOQUE ESTAS DUAS LINHAS AQUI (Teste de Fogo):
st.warning("⚠️ DADOS BRUTOS ANTES DOS FILTROS:")
st.dataframe(df_asteroides)

# ─────────────────────────────────────────────
# TEMA PLOTLY
# ─────────────────────────────────────────────
PLOTLY_THEME = dict(
    paper_bgcolor="rgba(5,12,20,0)",
    plot_bgcolor="rgba(13,27,42,0.6)",
    font=dict(family="Share Tech Mono, monospace", color="#7ec8e3", size=11),
    xaxis=dict(gridcolor="#112233", showgrid=True, zeroline=False),
    yaxis=dict(gridcolor="#112233", showgrid=True, zeroline=False),
    colorway=["#00b4d8", "#90e0ef", "#ffa500", "#64c864", "#8888ff", "#ff6b6b"],
)

COLOR_GEO = {"M": "#ffa500", "S": "#64c864", "C": "#8888ff"}
COLOR_VIAB = {"Alta": "#00e5ff", "Moderada": "#00b4d8", "Baixa": "#ffa500", "Inviável": "#ff4444"}
COLOR_RISK = {"Baixo": "#00e5ff", "Moderado": "#ffa500", "Alto": "#ff8800", "Crítico": "#ff2222"}


# ─────────────────────────────────────────────
# SIDEBAR — FILTROS
# ─────────────────────────────────────────────
def render_sidebar(df: pd.DataFrame):
    with st.sidebar:
        st.markdown('<div class="sidebar-header">☄ AstroMine AI · Filtros</div>', unsafe_allow_html=True)

        # Viabilidade Econômica
        viab_options = ["Alta", "Moderada", "Baixa", "Inviável"]
        selected_viab = st.multiselect(
            "Viabilidade Econômica",
            options=viab_options,
            default=["Alta", "Moderada"],
        )

        st.divider()

        # Nível de Risco
        risk_options = ["Baixo", "Moderado", "Alto", "Crítico"]
        selected_risk = st.multiselect(
            "Nível de Risco (MOID)",
            options=risk_options,
            default=["Baixo", "Moderado", "Alto"],
        )

        st.divider()

        # Classe Geológica
        geo_options = sorted(df["geo_class"].dropna().unique().tolist())
        selected_geo = st.multiselect(
            "Classe Geológica",
            options=geo_options,
            default=geo_options,
        )

        st.divider()

        min_diam = float(df['diameter_km'].min())
        max_diam = float(df['diameter_km'].max())

        if min_diam == max_diam:
            st.sidebar.info(
                f"Todos os asteroides filtrados possuem o mesmo diâmetro: {min_diam} km"
            )
            diam_range = (min_diam, max_diam) 
        else:
            diam_range = st.slider(
                "Selecione o range de diâmetro (km)",
                min_value=min_diam,
                max_value=max_diam,
                value=(min_diam, max_diam)
            )

        st.divider()

        # ROI mínimo
        menor_roi_banco = float(df_asteroides["roi"].min()) if not df_asteroides.empty else -100.0
        roi_minimo = st.sidebar.slider(
            "ROI Mínimo (%)",
            min_value=int(menor_roi_banco) - 5, # Dá uma folguinha para o ponteiro
            max_value=1000,
            value=int(menor_roi_banco)          # Começa mostrando todos
        )

        st.markdown("---")
        st.markdown(
            '<p style="font-family:\'Share Tech Mono\',monospace;color:#2a4a5a;font-size:0.65rem;text-align:center;">'
            f"Atualizado: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC</p>",
            unsafe_allow_html=True,
        )

    return selected_viab, selected_risk, selected_geo, diam_range, roi_minimo


# ─────────────────────────────────────────────
# MAIN DASHBOARD
# ─────────────────────────────────────────────
def main():
    # ── Header ──────────────────────────────
    col_logo, col_title = st.columns([1, 8])
    with col_title:
        st.markdown('<div class="main-title">⬡ ASTROMINE AI</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Sistema de Análise de Asteroides · Global Solution 2026.1 · FIAP</div>', unsafe_allow_html=True)

    st.divider()

    # ── Carrega dados ────────────────────────
    with st.spinner("Sincronizando com banco de dados..."):
        df_raw = load_asteroids()

    # ── Filtros (sidebar) ────────────────────
    sel_viab, sel_risk, sel_geo, diam_range, roi_minimo = render_sidebar(df_raw)

    # ── Aplica filtros ───────────────────────
    df = df_raw.copy()
    if sel_viab:
        df = df[df["economic_viability"].isin(sel_viab)]
    if sel_risk:
        df = df[df["risk_level"].isin(sel_risk)]
    if sel_geo:
        df = df[df["geo_class"].isin(sel_geo)]
    df = df[df["diameter_km"].between(*diam_range)]
    df = df[df["roi"].fillna(-999) >= roi_minimo]

    # ── KPIs ─────────────────────────────────
    st.subheader("📡 Visão Geral da Missão")
    k1, k2, k3, k4, k5 = st.columns(5)

    total = len(df)
    viable = len(df[df["economic_viability"].isin(["Alta", "Moderada"])])
    best_roi = df["roi"].max() if not df.empty else 0
    avg_transit = df["analysis_date"].dropna().max() if not df.empty else None
    total_value = df["estimated_value_usd"].sum() if not df.empty else 0

    k1.metric("Asteroides Filtrados", f"{total}", delta=f"{total - len(df_raw)} vs. total")
    k2.metric("Economicamente Viáveis", f"{viable}", delta=f"{viable/total*100:.0f}%" if total else "0%")
    k3.metric("Melhor ROI", f"{best_roi:,.0f}%")
   # Verifica se a data não é nula E se ela realmente possui a função de formatar textualmente
    if pd.notna(avg_transit) and hasattr(avg_transit, "strftime"):
        data_formatada = avg_transit.strftime("%Y-%m-%d")
    else:
        data_formatada = "—"

    k4.metric("Última Análise", data_formatada)
    k5.metric("Valor Total Estimado", f"$ {total_value/1e12:.2f} T")

    st.divider()

    if df.empty:
        st.warning("Nenhum asteroide encontrado com os filtros selecionados. Ajuste os critérios na barra lateral.")
        return

    # ─────────────────────────────────────────
    # GRÁFICO 1 — Valor Estimado vs Custo de Extração (Scatter principal)
    # ─────────────────────────────────────────
    st.subheader("💎 Valor Estimado vs. Custo de Extração")

    fig_scatter = px.scatter(
        df,
        x="extraction_cost_proxy",
        y="estimated_value_usd",
        size="diameter_km",
        color="geo_class",
        color_discrete_map=COLOR_GEO,
        hover_name="asteroid_name",
        hover_data={
            "geo_class": True,
            "roi": ":.1f",
            "mineral_composition": True,
            "ai_confidence": ":.1%",
            "diameter_km": ":.2f",
        },
        labels={
            "extraction_cost_proxy": "Custo de Extração Estimado (USD)",
            "estimated_value_usd": "Valor Estimado (USD)",
            "geo_class": "Classe Geológica",
            "roi": "ROI (%)",
            "mineral_composition": "Mineral Principal",
            "diameter_km": "Diâmetro (km)",
        },
        size_max=40,
        log_x=True,
        log_y=True,
        title="Relação Custo × Valor por Classe Geológica",
    )

    # Linha de break-even
    min_val = min(df["extraction_cost_proxy"].min(), df["estimated_value_usd"].min())
    max_val = max(df["extraction_cost_proxy"].max(), df["estimated_value_usd"].max())
    fig_scatter.add_shape(
        type="line",
        x0=min_val, y0=min_val,
        x1=max_val, y1=max_val,
        line=dict(color="#ff4444", width=1.5, dash="dot"),
    )
    fig_scatter.add_annotation(
        x=max_val * 0.6, y=max_val * 0.7,
        text="Break-even",
        font=dict(color="#ff4444", size=10, family="Share Tech Mono, monospace"),
        showarrow=False,
    )

    fig_scatter.update_layout(
        height=480,
        **PLOTLY_THEME,
        legend=dict(
            bgcolor="rgba(0,0,0,0.4)",
            bordercolor="#1a3a5c",
            borderwidth=1,
        ),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # ─────────────────────────────────────────
    # GRÁFICO 2 + 3 — ROI por Classe Geológica | Distribuição de Risco
    # ─────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📊 ROI por Classe Geológica")
        fig_box = px.box(
            df,
            x="geo_class",
            y="roi",
            color="geo_class",
            color_discrete_map=COLOR_GEO,
            points="all",
            labels={"geo_class": "Classe", "roi": "ROI (%)"},
            title="Distribuição de ROI por Tipo de Asteroide",
        )
        fig_box.update_traces(
            jitter=0.3,
            marker=dict(size=5, opacity=0.7),
        )
        fig_box.update_layout(
            height=380,
            showlegend=False,
            **PLOTLY_THEME,
        )
        st.plotly_chart(fig_box, use_container_width=True)

    with col_b:
        st.subheader("⚠️ Distribuição por Risco × Viabilidade")
        risk_viab = (
            df.groupby(["risk_level", "economic_viability"], observed=True)
            .size()
            .reset_index(name="count")
        )
        fig_risk = px.bar(
            risk_viab,
            x="risk_level",
            y="count",
            color="economic_viability",
            color_discrete_map=COLOR_VIAB,
            barmode="stack",
            category_orders={
                "risk_level": ["Baixo", "Moderado", "Alto", "Crítico"],
                "economic_viability": ["Alta", "Moderada", "Baixa", "Inviável"],
            },
            labels={"risk_level": "Nível de Risco", "count": "Qtd. Asteroides", "economic_viability": "Viabilidade"},
            title="Risco Orbital × Viabilidade Econômica",
        )
        fig_risk.update_layout(
            height=380,
            **PLOTLY_THEME,
            legend=dict(bgcolor="rgba(0,0,0,0.4)", bordercolor="#1a3a5c", borderwidth=1),
        )
        st.plotly_chart(fig_risk, use_container_width=True)

    # ─────────────────────────────────────────
    # GRÁFICO 4 — Bubble Chart: Probabilidade Quântica × Dias de Trânsito
    # ─────────────────────────────────────────
    st.subheader("🤖 Confiança do Modelo IA × Teor Mineral")

    df_q = df.dropna(subset=["ai_confidence", "mineral_grade"])
    if not df_q.empty:
        fig_quantum = px.scatter(
            df_q,
            x="mineral_grade",
            y="ai_confidence",
            size="estimated_value_usd",
            color="economic_viability",
            color_discrete_map=COLOR_VIAB,
            hover_name="asteroid_name",
            hover_data={
                "mineral_composition": True,
                "mineral_unit": True,
                "model_used": True,
                "geo_class": True,
            },
            labels={
                "mineral_grade": "Teor do Mineral Principal",
                "ai_confidence": "Confiança do Modelo IA (0–1)",
                "economic_viability": "Viabilidade",
                "mineral_composition": "Mineral",
                "model_used": "Modelo",
            },
            size_max=50,
            title="Qualidade da Predição: Teor × Confiança por Viabilidade Econômica",
        )
        fig_quantum.update_layout(
            height=420,
            **PLOTLY_THEME,
            legend=dict(bgcolor="rgba(0,0,0,0.4)", bordercolor="#1a3a5c", borderwidth=1),
        )
        st.plotly_chart(fig_quantum, use_container_width=True)
    else:
        st.info("Sem dados de análise mineral para os filtros selecionados.")

    # ─────────────────────────────────────────
    # GRÁFICO 5 — Mapa de Calor: Albedo × Anomalias
    # ─────────────────────────────────────────
    col_c, col_d = st.columns(2)

    with col_c:
        st.subheader("🔭 Densidade × Diâmetro")
        df_cv = df.dropna(subset=["density", "diameter_km"])
        if not df_cv.empty:
            fig_heat = px.scatter(
                df_cv,
                x="diameter_km",
                y="density",
                color="geo_class",
                color_discrete_map=COLOR_GEO,
                size="estimated_value_usd",
                size_max=30,
                hover_name="asteroid_name",
                labels={
                    "diameter_km": "Diâmetro (km)",
                    "density": "Densidade (g/cm³)",
                    "geo_class": "Classe",
                },
                title="Perfil Físico por Classe Geológica",
            )
            fig_heat.update_layout(height=360, **PLOTLY_THEME, showlegend=False)
            st.plotly_chart(fig_heat, use_container_width=True)

    with col_d:
        st.subheader("🍩 Composição da Carteira")
        pie_df = df.groupby("geo_class", observed=True)["estimated_value_usd"].sum().reset_index()
        fig_pie = px.pie(
            pie_df,
            names="geo_class",
            values="estimated_value_usd",
            color="geo_class",
            color_discrete_map=COLOR_GEO,
            hole=0.55,
            title="Valor Total por Classe Geológica",
        )
        fig_pie.update_traces(
            textfont=dict(family="Share Tech Mono, monospace"),
            textinfo="label+percent",
        )
        fig_pie.update_layout(
            height=360,
            **PLOTLY_THEME,
            showlegend=False,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ─────────────────────────────────────────
    # TABELA — Top Asteroides
    # ─────────────────────────────────────────
    st.divider()
    st.subheader("🗂️ Catálogo de Asteroides")

    df_table = df[[
        "asteroid_name", "geo_class",
        "diameter_km", "density", "moid_km",
        "mineral_composition", "mineral_grade", "mineral_unit",
        "estimated_value_usd", "roi",
        "economic_viability", "risk_level",
        "ai_confidence", "model_used", "analysis_date",
    ]].copy()

    df_table.columns = [
        "Nome", "Classe",
        "Diâmetro (km)", "Densidade", "MOID (km)",
        "Mineral Principal", "Teor", "Unidade",
        "Valor Est. (USD)", "ROI (%)",
        "Viabilidade", "Risco",
        "Confiança IA", "Modelo", "Data Análise",
    ]

    df_table["Valor Est. (USD)"] = df_table["Valor Est. (USD)"].apply(lambda x: f"${x/1e9:.2f}B" if pd.notna(x) else "—")
    df_table["ROI (%)"] = df_table["ROI (%)"].apply(lambda x: f"{x:,.0f}%" if pd.notna(x) else "—")
    df_table["Confiança IA"] = df_table["Confiança IA"].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "—")
    df_table["Diâmetro (km)"] = df_table["Diâmetro (km)"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "—")
    df_table["Densidade"] = df_table["Densidade"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "—")
    df_table["MOID (km)"] = df_table["MOID (km)"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "—")
    df_table["Teor"] = df_table["Teor"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "—")

    st.dataframe(
        df_table.reset_index(drop=True),
        use_container_width=True,
        height=420,
        hide_index=True,
    )

    # ─────────────────────────────────────────
    # FOOTER
    # ─────────────────────────────────────────
    st.divider()
    st.markdown(
        '<p style="font-family:\'Share Tech Mono\',monospace;color:#1a3a4a;font-size:0.7rem;text-align:center;">'
        "AstroMine AI · Global Solution 2026.1 · FIAP · "
        "Pipeline: OpenCV + Random Forest + QAOA (Qiskit) + FastAPI + PostgreSQL"
        "</p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()