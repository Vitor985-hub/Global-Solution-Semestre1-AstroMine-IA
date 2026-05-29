# FIAP - Faculdade de Informatica e Administracao Paulista

<p align="center">
<a href="https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP" border="0" width="40%" height="40%"></a>
</p>

# AstroMine AI

Projeto desenvolvido para o Global Solution 2026.1 da FIAP com foco em simulacao de trajetorias de asteroides, captura de movimento via camera e avaliacao orbital com apoio de algoritmos quanticos.

## Integrantes

- <a href="https://github.com/Vitor985-hub">Vitor Eiji</a>
- <a href="https://github.com/BPilecarte">Beatriz Pilecarte</a>
- <a href="https://github.com/yggdrasilGit">Francismar Alves</a>
- <a href="https://github.com/matheusbento04">Matheus Soares</a>
- <a href="https://github.com/AntonioBarros19">Antonio Barros</a>

## Professores

### Tutor(a)

- <a href="https://www.linkedin.com/in/caique-nonato/">Caique Nonato</a>

### Coordenador(a)

- <a href="https://www.linkedin.com/in/andregodoichiovato/">Andre Godoi Chiochiovatto</a>

## Visao Geral

O AstroMine AI combina tres frentes principais:

1. captura de movimento em tempo real por camera para simular o deslocamento de um asteroide;
2. conversao da captura em janelas orbitais com aproximacao nao linear;
3. avaliacao da melhor janela usando QAOA e geracao de graficos e animacoes.

O projeto atual esta orientado a prova de conceito local, com foco em demonstrar o pipeline completo de visao computacional, modelagem nao linear e otimizacao quantica.

## Fluxo Principal do Sistema

O fluxo padrao do projeto acontece em quatro etapas:

1. o simulador abre a camera do computador;
2. o sistema captura pontos de movimento durante 10 segundos em intervalos de 0,5 segundo;
3. os pontos capturados sao convertidos em janelas de trajetoria com ajuste nao linear;
4. o modulo quantico seleciona a melhor janela e gera grafico estatico e animacao.

## Arquitetura Atual

O projeto foi organizado em camadas inspiradas em MVC e Clean Architecture para os modulos principais.

### Camada de simulacao

- `simulador/domain`: entidades e regras de captura.
- `simulador/application`: casos de uso do simulador.
- `simulador/infrastructure`: OpenCV, persistencia JSON e ponte para o modulo quantico.
- `simulador/presentation`: controller de orquestracao da captura.

### Camada de trajetoria

- `trajetoria_asteroid/domain`: entidades orbitais e servicos matematicos.
- `trajetoria_asteroid/application`: caso de uso de otimizacao.
- `trajetoria_asteroid/infrastructure`: adaptador Qiskit e geracao de graficos.
- `trajetoria_asteroid/presentation`: controller para calculo, grafico e animacao.

## Estrutura do Projeto

```text
AstroMine-IA
├── assets/
│   └── logo-fiap.png
├── database/
│   ├── README.md
│   └── schema.sql
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
├── instala.sh
├── main.py
├── requirement.txt
└── README.md
```

## Requisitos

- Python 3 com suporte a `venv`
- permissao de camera no macOS para Terminal e, se necessario, para o VS Code
- ambiente local com interface grafica para abrir a webcam

## Dependencias

As dependencias atualmente utilizadas pelo projeto sao:

- `qiskit`
- `qiskit-aer`
- `qiskit-algorithms`
- `numpy`
- `opencv-python`
- `matplotlib`
- `pillow`

Elas sao instaladas a partir de `requirement.txt` pelo script `instala.sh`.

## Instalacao

Na raiz do projeto:

```bash
source ./instala.sh
```

Esse script:

1. cria a pasta `.venv`;
2. ativa o ambiente virtual no terminal atual;
3. instala ou atualiza as dependencias do projeto.

## Como Executar

### Fluxo completo com camera

```bash
source ./instala.sh
python main.py
```

Esse comando:

1. abre a camera;
2. captura a trajetoria do movimento;
3. salva a captura em `simulador/trajetoria_capturada.json`;
4. calcula a melhor janela de trajetoria;
5. gera o grafico e a animacao da captura.

### Reprocessar uma captura salva

```bash
python main.py captura
```

### Rodar apenas o exemplo quantico do modulo de trajetoria

```bash
python main.py grafico
```

## Arquivos de Saida

O sistema gera os seguintes artefatos durante a execucao:

- `simulador/trajetoria_capturada.json`: pontos capturados pela camera.
- `trajetoria_asteroid/grafico_trajeto.png`: grafico do exemplo quantico padrao.
- `trajetoria_asteroid/grafico_trajeto_animado.gif`: animacao do exemplo quantico padrao.
- `trajetoria_asteroid/grafico_trajeto_capturado.png`: grafico da trajetoria capturada.
- `trajetoria_asteroid/grafico_trajeto_capturado_animado.gif`: animacao da trajetoria capturada.

## Modelo de Captura e Trajetoria Nao Linear

O fluxo atual de captura e projecao funciona assim:

1. a camera detecta o maior contorno em movimento em cada frame;
2. os pontos sao amostrados em intervalos fixos de 0,5 segundo;
3. a coleta dura 10 segundos;
4. os pontos capturados sao ajustados por uma curva polinomial de grau 2;
5. a curva ajustada gera janelas futuras de trajetoria para o QAOA.

Esse modelo nao representa uma dinamica orbital fisicamente completa, mas fornece uma aproximacao nao linear mais realista do que uma simples ligacao reta entre pontos.

## Modos do `main.py`

O arquivo `main.py` e o ponto unico de entrada do sistema.

- `python main.py`: executa o fluxo completo com camera.
- `python main.py captura`: reutiliza a ultima captura salva.
- `python main.py grafico`: executa apenas o exemplo quantico de referencia.

## Banco de Dados

O diretorio `database/` contem o esquema SQL do projeto. Ele ainda nao esta integrado diretamente ao fluxo principal em `main.py`, mas documenta a persistencia planejada para asteroides, analises minerais, relatorios, imagens e logs.

Consulte `database/README.md` para detalhes de uso.

## Roadmap Tecnico

Possiveis evolucoes para o projeto:

- integrar dados reais da NASA ao pipeline quantico;
- substituir a aproximacao polinomial por modelos dinamicos orbitais mais completos;
- persistir capturas, janelas e resultados no banco relacional;
- expor o pipeline como API ou dashboard;
- adicionar filtros e calibracao espacial para converter pixels em unidades fisicas.

## Limitacoes Atuais

- o modelo nao linear atual usa ajuste polinomial, nao simulacao astrodinamica completa;
- o acesso a camera depende das permissoes do sistema operacional;
- o QAOA gera warnings do SciPy relacionados a performance, mas eles nao interrompem a execucao;
- os graficos sao gerados localmente e nao existe interface web neste estado do projeto.

## Licenca

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> esta licenciado sob <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>