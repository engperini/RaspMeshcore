# RaspMeshcore

RaspMeshcore transforma um **Raspberry Pi 4 + LoRa HAT/SX1262** em um terminal MeshCore autônomo.

O objetivo principal não é usar o Pi apenas como servidor para um celular. O próprio Raspberry Pi será o equipamento final: **display touch + mensagens + canais + contatos + bots + rádio LoRa**, com acesso remoto/LAN apenas como recurso secundário.

## Produto alvo

```text
Power ON
   ↓
Raspberry Pi OS 64-bit com Desktop
   ↓
Docker Compose sobe os serviços
   ↓
Companion/Radio Core conecta ao SX1262 HAT
   ↓
RemoteTerm / RaspMeshcore UI fica pronta
   ↓
Chromium abre automaticamente em modo KIOSK
   ↓
Terminal MeshCore pronto no próprio display
```

O terminal deve operar sem:

- smartphone;
- companion app externo;
- segundo MCU;
- computador conectado;
- Internet para as funções MeshCore básicas.

A mesma interface poderá continuar disponível na LAN em `http://raspmeshcore.local` ou pelo IP do Pi, mas isso é **secundário**.

## Arquitetura

```text
┌──────────────────────── Raspberry Pi 4 ────────────────────────────┐
│                                                                    │
│ Raspberry Pi OS 64-bit com Desktop                                 │
│ ├─ display/touch                                                   │
│ ├─ Chromium em modo kiosk                                          │
│ ├─ SSH                                                             │
│ ├─ acesso remoto gráfico opcional                                  │
│ └─ Docker + Compose                                                │
│                                                                    │
│ Containers / serviços                                              │
│ ├─ RemoteTerm / UI                                                 │
│ ├─ Companion / radio-core Linux                                    │
│ ├─ simulador sem HAT                                               │
│ ├─ bots                                                            │
│ └─ persistência/configuração                                       │
│                                                                    │
│ Companion/radio-core ── SPI/GPIO ──> SX1262 HAT ──> MeshCore       │
└────────────────────────────────────────────────────────────────────┘
```

### UI local e servidor são a mesma aplicação

No próprio display:

```text
Chromium kiosk → http://127.0.0.1:8080
```

Opcionalmente, na LAN:

```text
outro dispositivo → http://raspmeshcore.local:8080
```

Não haverá uma aplicação separada para o display e outra para a rede.

## Display

O modelo do display será escolhido depois. Isso **não bloqueia o desenvolvimento**.

Primeiro trabalharemos com:

1. SSH para configuração, Docker, logs e diagnóstico;
2. acesso web pela rede para testar a interface;
3. TeamViewer, RustDesk, VNC ou equivalente como acesso gráfico opcional ao desktop;
4. simulador de rádio para desenvolver sem HAT.

Quando o display for escolhido, adicionaremos somente o profile de hardware: resolução, rotação, touch, escala, teclado virtual, brilho e montagem.

## Docker-first

A meta continua sendo manter a aplicação o mais containerizada possível. No host ficam somente os elementos que realmente pertencem ao sistema operacional:

- Raspberry Pi OS;
- kernel/drivers;
- display/touch;
- Docker;
- Chromium/kiosk;
- SSH e acesso remoto opcional.

Radio core, RemoteTerm/UI, simulador, bots e persistência devem ficar em containers sempre que o acesso ao hardware permitir. Para o HAT, preferir `/dev/spidev*`, `/dev/gpiochip*`, grupos e capabilities específicas; evitar `privileged: true` como padrão.

## Estratégia MeshCore

Base técnica pesquisada:

- [Remote-Terminal-for-MeshCore](https://github.com/jkingsman/Remote-Terminal-for-MeshCore) — UI web, mensagens, contatos/canais, bots e transporte Companion.
- [MeshCoreRPI](https://github.com/dabeani/MeshCoreRPI) — candidato para Companion Linux nativo no Raspberry Pi.
- [Guia Seeed Studio / RemoteTerm](https://wiki.seeedstudio.com/get_started_with_meshcore_remote_terminal/) — referência de integração e experiência.

A arquitetura desejada é:

```text
Display touch
    ↓
Chromium kiosk
    ↓
RemoteTerm / UI local
    ↓
Companion Linux no próprio Pi
    ↓
SPI/GPIO
    ↓
SX1262 HAT
    ↓
MeshCore
```

RemoteTerm deve ser reutilizado enquanto atender ao produto. Não vamos recriar frontend/backend/bots sem necessidade. Se alguma função local/touch não for adequada, criaremos apenas a camada/adaptação necessária.

## Bots

Bots são parte central do produto, não apenas um extra.

O usuário deve poder criar/habilitar bots no próprio Raspberry. Prioridade inicial é aproveitar o sistema de bots do RemoteTerm e validar:

- trigger por mensagem;
- resposta automática;
- scripts Python;
- logs;
- habilitar/desabilitar;
- persistência;
- rate limit;
- proteção contra loops/flood.

Integrações posteriores podem incluir MQTT, HTTP, sensores, GPIO/I²C, GPS, Home Assistant e LLM.

## Instalação inicial no Raspberry Pi (simulação sem HAT)

Pré-requisitos: Raspberry Pi OS 64-bit com Desktop e Docker Engine + Compose já instalados. O script não atualiza o OS nem instala pacotes do host.

```bash
git clone https://github.com/engperini/RaspMeshcore.git
cd RaspMeshcore
bash scripts/install.sh
```

Escolha **2** para subir RemoteTerm + Companion simulado. Abra `http://127.0.0.1:8080` no navegador do próprio Pi. Para abrir de outro computador ou smartphone na mesma rede, edite `.env`, configure `RASPMESH_BIND` com o IPv4 local do Pi e execute novamente o instalador. Acesse `http://IP_DO_PI:8080` no outro dispositivo. Sem autenticação configurada, use apenas em uma rede local confiável; não publique a porta na Internet.

Diagnóstico:
```bash
bash scripts/doctor.sh
docker compose -f compose.yaml -f compose.simulator.yaml logs --tail=100
```

**Atenção:** simulador de protocolo parcial com loopback de canal; não representa criptografia, multihop nem RF. A compatibilidade completa com RemoteTerm e os bots ainda depende de teste integrado. Bots ficam desativados por padrão por segurança. O instalador não configura ainda kiosk/autostart.

## Estado atual

### Stage 1 — RemoteTerm container baseline

Já existe baseline Docker do RemoteTerm usando a imagem upstream.

Este estágio **não comprova ainda**:

- Companion Linux ↔ RemoteTerm;
- TX/RX MeshCore;
- criptografia;
- multihop;
- acesso real ao HAT.

O próximo passo é validar toda a pilha possível sem HAT usando Companion/simulador e, depois, substituir o simulador pelo SX1262 real.

## Desenvolvimento atual sem display/HAT

O Raspberry pode ser preparado agora e usado remotamente. O fluxo inicial será:

```text
PC → SSH → Raspberry Pi
PC → navegador → RemoteTerm/RaspMeshcore
                    ↓
             Companion/simulador
```

Depois:

```text
Display touch no Pi
       ↓
Chromium kiosk
       ↓
mesma aplicação
       ↓
Companion Linux
       ↓
SX1262
```

## Documentação

- [PLAN.md](PLAN.md) — plano de execução para o agente.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — arquitetura do appliance, kiosk, rede, containers e hardware.

## Regra principal do projeto

**O Raspberry Pi deve continuar recebendo mensagens, executando bots e operando o rádio mesmo sem celular, sem navegador remoto e com o display apagado.**
