# Modulo Simulador

O diretorio `simulador/` concentra a captura de movimento pela camera e a preparacao dos dados para o modulo de trajetoria.

## Responsabilidades

- abrir a webcam do computador;
- detectar movimento em tempo real com OpenCV;
- amostrar pontos da trajetoria em intervalos fixos;
- salvar a captura em JSON;
- enviar os dados capturados para o pipeline de calculo orbital.

## Fluxo do simulador

1. o controller abre a camera;
2. o tracker identifica o maior contorno em movimento;
3. os pontos sao amostrados a cada 0,5 segundo por 10 segundos;
4. a captura e salva em `trajetoria_capturada.json`;
5. o modulo de trajetoria recebe a captura e calcula as janelas futuras.

## Estrutura

- `camera_trajetoria.py`: entrypoint direto do simulador.
- `enviar_para_quantico.py`: reaproveita uma captura salva e chama o calculo.
- `domain/`: entidades e regras da captura.
- `application/`: casos de uso de salvar e calcular a partir da captura.
- `infrastructure/`: OpenCV, persistencia JSON e ponte com o modulo quantico.
- `presentation/`: controller que orquestra a execucao.

## Arquivo gerado

- `trajetoria_capturada.json`: contem os pontos capturados, direcao, velocidade e distancia total.

## Como executar diretamente

```bash
source ./instala.sh
python simulador/camera_trajetoria.py
```

Para reprocessar a ultima captura:

```bash
python simulador/enviar_para_quantico.py
```