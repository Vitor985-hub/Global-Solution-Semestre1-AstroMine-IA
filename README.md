# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# 🚀 AstroMine AI
> *Explorando a riqueza do cosmos com inteligência e precisão.*

---

## 👨‍🚀 Integrantes: 
- <a href="https://github.com/Vitor985-hub">Vitor Eiji</a>
- <a href="https://github.com/BPilecarte">Beatriz Pilecarte</a>
- <a href="https://github.com/yggdrasilGit">Francismar Alves</a>
- <a href="https://github.com/matheusbento04">Matheus Soares</a>
- <a href="https://github.com/AntonioBarros19">Antonio Barros</a>


## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="https://www.linkedin.com/in/caique-nonato/">Caique Nonato</a>
### Coordenador(a)
- <a href="https://www.linkedin.com/in/andregodoichiovato/">André Godoi Chiochiovatto</a>


## 🌌 1. Descrição do Projeto

Com o crescimento populacional e o avanço tecnológico na Terra, a demanda por minerais raros e recursos naturais tem atingido níveis críticos. A **economia espacial** desponta como a próxima fronteira comercial e científica, onde o espaço deixa de ser apenas objeto de estudo e passa a ser uma extensão viável da economia humana. 

A **mineração de asteroides** é uma peça chave nessa nova era, oferecendo acesso a trilhões de dólares em metais preciosos (como platina, ouro e cobalto) e elementos vitais (como água) que podem viabilizar não apenas a indústria terrestre, mas também missões de exploração em espaço profundo.

Neste cenário complexo e com volumes astronômicos de informações, a **Inteligência Artificial e a Automação** são fundamentais. Elas permitem processar imagens, prever composições químicas a bilhões de quilômetros de distância e reduzir drasticamente os custos e os riscos de exploração.

O **AstroMine AI** é uma plataforma inteligente projetada para prospecção e mineração espacial. O sistema atua em todas as frentes da análise exploratória:
- 🛰️ **Coleta dados espaciais** em tempo real através de sensores e agências parceiras;
- 🪨 **Analisa asteroides** com base em características orbitais e físicas;
- 💎 **Classifica minerais** através de modelos preditivos;
- 📈 **Estima a viabilidade econômica** de cada corpo celeste;
- 📑 **Gera relatórios inteligentes** utilizando processamento de linguagem natural;
- 📊 **Exibe tudo em um dashboard interativo** para facilitar a tomada de decisão estratégica.

---

## 🎯 2. Objetivos do Projeto

### Objetivo Geral
Desenvolver uma plataforma de inteligência artificial focada na prospecção espacial, capaz de identificar, analisar e avaliar o potencial econômico de asteroides para mineração.

### Objetivos Específicos
- **Analisar dados espaciais** brutos provenientes de sondas e observatórios.
- **Identificar minerais valiosos** através de modelagem matemática e machine learning.
- **Classificar asteroides** considerando seu risco (ex: tamanho, proximidade) e seu valor comercial.
- **Gerar insights automáticos** e simplificados para stakeholders e pesquisadores por meio de IA generativa.
- **Explorar aplicações futuras da IA na economia espacial**, abrindo portas para processos totalmente autônomos.

---

## 🚀 3. MVP (Produto Mínimo Viável)

O MVP do **AstroMine AI** concentra-se em entregar uma experiência funcional end-to-end, validando a integração entre inteligência artificial, análise de dados e automação de relatórios.

O escopo do MVP contempla:
- 📡 **Integração com APIs da NASA** para extração em tempo real de informações sobre corpos próximos à Terra (NEOs).
- 📥 **Coleta de dados de asteroides** físicos e orbitais de maneira contínua e estruturada.
- 🧠 **Classificação básica de asteroides** utilizando modelos de Machine Learning.
- 🖥️ **Dashboard interativo com visualização de dados** para monitoramento intuitivo.
- 🤖 **IA Generativa para geração de relatórios automáticos**, transformando dados complexos em textos executivos.
- 💾 **Armazenamento em banco de dados** relacional para histórico e consultas.

*Nota: A implementação de funcionalidades envolvendo **computação quântica** será tratada como opcional, sendo desenvolvida apenas caso haja tempo hábil. O foco principal permanece na integração robusta entre IA, dados e automação.*

---

## 🛠️ 4. Stack Tecnológica

| Categoria | Tecnologias Utilizadas |
|-----------|------------------------|
| **Backend** | Python, FastAPI |
| **IA e Machine Learning** | scikit-learn, pandas, numpy |
| **Visão Computacional** | OpenCV |
| **Banco de Dados** | PostgreSQL ou SQLite |
| **Frontend / Dashboard** | Streamlit ou React |
| **IA Generativa** | OpenAI API ou Ollama |
| **APIs Espaciais** | NASA APIs, NeoWs API |
| **Computação Quântica** *(Opcional)* | Qiskit, Aer Simulator |

---

## ⚙️ 5. Arquitetura da Solução

O AstroMine AI opera sob uma arquitetura de microsserviços e processamento em pipeline, garantindo escalabilidade e modularidade.

```text
  [NASA APIs / NeoWs]
           │
           ▼ (Extração de Dados)
  [Backend FastAPI] ───────────┐
           │                   │
           ▼                   ▼ (Persistência)
 [Pipeline de IA & ML]     [Banco de Dados]
           │                   │
           ▼                   │
 [Processamento/Classif.]      │
           │                   │
           ▼ (Insights)        │
 [Dashboard Frontend] ◄────────┘
           │
           ▼ (Análise Textual)
    [IA Generativa]
```

### Componentes:
- **Coleta de Dados:** Interfaces de comunicação com agências espaciais e web scraping responsável.
- **Processamento:** Limpeza, normalização e feature engineering dos dados astronômicos.
- **Classificação:** Modelos de Machine Learning (como Random Forest ou SVM) para prever composição e periculosidade.
- **Armazenamento:** Persistência segura dos perfis de asteroides, logs de execução e relatórios.
- **Visualização:** Front-end reativo para navegação de dados espaciais e estatísticas de forma fluida.
- **Geração de Relatórios:** LLMs integrados para traduzir números e classificações em relatórios executivos.

---

## 📂 6. Estrutura Recomendada do Projeto

Abaixo apresentamos a estrutura de diretórios adotada para manter o projeto escalável e limpo:

```text
📦 AstroMine-IA
 ┣ 📂 backend/       # Código fonte da API (FastAPI, rotas, schemas)
 ┣ 📂 frontend/      # Dashboard (Streamlit/React) e interface de usuário
 ┣ 📂 ai/            # Notebooks de treinamento, modelos salvos (scikit-learn, OpenCV)
 ┣ 📂 database/      # Scripts de migração, modelos ORM e seed de banco
 ┣ 📂 docs/          # Documentações complementares, diagramas e referências
 ┣ 📂 assets/        # Elementos não-estruturados, como logos, ícones e imagens 
 ┣ 📂 quantum/       # (Opcional) Experimentos e circuitos utilizando Qiskit
 ┣ 📜 .gitignore     # Ignorar arquivos temporários/ambientes virtuais
 ┗ 📜 README.md      # Documentação central do projeto (este arquivo)
```

---

## 🔮 7. Funcionalidades Futuras (Roadmap)

Visando a expansão do AstroMine AI para missões de maior complexidade, listamos nosso roadmap tecnológico:

- ⚛️ **Otimização Quântica:** Utilização de algoritmos quânticos (VQE, QAOA) para simular moléculas e otimizar trajetórias orbitais.
- ⏱️ **Processamento em Tempo Real:** Streaming de dados via WebSockets ou Kafka para atualização simultânea do dashboard.
- 🌍 **Visualização Orbital 3D:** Implementação de mapas tridimensionais (Three.js/WebGL) mostrando trajetórias de asteroides.
- 🔬 **Análise Avançada de Imagens Espaciais:** Segmentação avançada utilizando redes neurais convolucionais (CNNs).
- 🤖 **Automação de Missões Mineradoras:** Módulo de simulação logística para envio e retorno de sondas extrativas autônomas.
- 🔌 **Integração com ESP32:** Testes de hardware in the loop simulando sensores IoT de sondas em ambiente de solo.

---
<p align="center">
Desenvolvido para o <b>Global Solution 2026.1 - FIAP</b>. O cosmos é apenas o começo. ✨
</p>

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>