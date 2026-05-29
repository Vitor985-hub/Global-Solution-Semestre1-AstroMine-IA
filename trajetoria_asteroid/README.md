# Modulo de Trajetoria

O diretorio `trajetoria_asteroid/` concentra o calculo orbital, a avaliacao quantica e a visualizacao das trajetorias.

## Responsabilidades

- representar janelas de trajetoria e vetores de estado;
- calcular custos orbitais considerando Terra e Sol;
- executar a otimizacao com QAOA;
- gerar graficos e animacoes das trajetorias;
- processar tanto o exemplo padrao quanto trajetorias vindas da camera.

## Componentes principais

- `algoritimo_quantico.py`: entrypoint do exemplo padrao do modulo.
- `domain/`: entidades e servicos orbitais.
- `application/`: caso de uso de otimizacao.
- `infrastructure/qiskit_optimizer.py`: adaptador quantico com QAOA.
- `infrastructure/trajectory_plotter.py`: geracao de PNG e GIF.
- `presentation/controller.py`: controller que integra calculo, grafico e animacao.

## Saidas geradas

- `grafico_trajeto.png`: exemplo quantico padrao.
- `grafico_trajeto_animado.gif`: animacao do exemplo quantico padrao.
- `grafico_trajeto_capturado.png`: grafico da captura real.
- `grafico_trajeto_capturado_animado.gif`: animacao da captura real.

## Modelo nao linear

Quando a entrada vem do simulador, o sistema nao trabalha apenas com ligacoes retas entre pontos. O pipeline ajusta uma curva polinomial sobre as amostras capturadas e usa essa curva para gerar janelas futuras mais suaves.

## Como executar diretamente

```bash
source ./instala.sh
python trajetoria_asteroid/algoritimo_quantico.py
```

Para o fluxo principal integrado, prefira:

```bash
python main.py
```