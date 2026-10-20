# RaspMeshcore — Plano de execução para agente

Data da revisão: 2026-10-19  
Status: Stage 1 RemoteTerm entregue; integração Companion/rádio ainda em validação.

---

## 1. Missão

Construir um **terminal MeshCore autônomo no Raspberry Pi 4**.

O produto final é o próprio Raspberry Pi:

- rádio MeshCore;
- cliente de envio e recebimento;
- display touchscreen;
- contatos e canais;
- histórico;
- criação/execução de bots;
- diagnóstico/configuração;
- servidor web opcional na LAN.

A função de servidor para celular/notebook é secundária. O sistema não pode depender dela para operar.

### Requisitos fechados

O produto final deve funcionar sem:

- smartphone;
- companion app externo;
- segundo MCU;
- computador externo;
- Internet para mensagens MeshCore básicas.

O Raspberry deve operar como **um único dispositivo**.

---

## 2. Sistema operacional e modo appliance

Usar **Raspberry Pi OS 64-bit com Desktop**.

Motivo: o equipamento terá display local e Chromium em modo kiosk. Não queremos que o usuário use o desktop, mas precisamos da pilha gráfica.

Fluxo final obrigatório:

```text
Power ON
   ↓
Raspberry Pi OS
   ↓
Docker/Compose
   ↓
Companion/radio-core
   ↓
RemoteTerm/UI saudável
   ↓
Chromium kiosk abre
   ↓
Terminal pronto
```

Depois de configurado, o usuário não deve precisar ver terminal ou desktop.

---

## 3. Display será escolhido depois

A escolha do display **não bloqueia nenhuma fase inicial**.

Até lá:

1. configuração/manutenção por SSH;
2. acesso web pela LAN;
3. desktop remoto opcional por TeamViewer, RustDesk, VNC ou equivalente;
4. desenvolvimento do kiosk no desktop/saída HDMI normal;
5. simulador para eliminar dependência do HAT.

Quando o display for definido, criar profile específico para:

- HDMI/DSI/SPI;
- resolução;
- orientação;
- touch;
- escala/DPI;
- teclado virtual;
- brilho;
- blanking;
- montagem;
- alimentação;
- consumo.

A aplicação deve permanecer responsiva e não codificada para uma resolução fixa.

---

## 4. Arquitetura alvo

```text
                       RASPBERRY PI 4
┌────────────────────────────────────────────────────────────────┐
│ HOST                                                           │
│ Raspberry Pi OS 64-bit + Desktop                               │
│ ├─ display/touch                                               │
│ ├─ Chromium kiosk                                              │
│ ├─ Docker/Compose                                              │
│ ├─ SSH                                                         │
│ └─ remote desktop opcional                                     │
│                                                                │
│ CONTAINERS / SERVIÇOS                                          │
│ ┌─────────────┐   ┌────────────────┐   ┌────────────────────┐  │
│ │ RemoteTerm  │◀─▶│ Companion /    │◀─▶│ simulator ou HAT   │  │
│ │ UI + bots   │   │ radio-core     │   │ SX1262            │  │
│ └──────┬──────┘   └────────────────┘   └────────────────────┘  │
│        │                                                       │
│        └── persistência/configuração/logs                      │
└────────────────────────────────────────────────────────────────┘
```

### Princípio de reaproveitamento

RemoteTerm original é a UI preferencial enquanto atender ao produto.

Não criar frontend/backend/bot engine novos por padrão. Criar apenas:

- adaptadores;
- serviços auxiliares;
- patches;
- launcher kiosk;
- APIs complementares;

quando existir necessidade comprovada.

---

## 5. Uma UI, dois acessos

### Primário — display local

```text
Chromium kiosk → http://127.0.0.1:8080
```

### Secundário — LAN

```text
http://raspmeshcore.local:8080
ou
http://<IP_DO_PI>:8080
```

É a **mesma aplicação**.

O acesso LAN deve poder ser desligado posteriormente sem afetar o kiosk.

---

## 6. Docker-first

Meta de distribuição:

```bash
git clone https://github.com/engperini/RaspMeshcore.git
cd RaspMeshcore
docker compose up -d
```

após preparação mínima do host.

### No host

Manter somente:

- Raspberry Pi OS;
- kernel e drivers;
- display/touch;
- Chromium;
- kiosk launcher;
- Docker;
- SSH;
- acesso remoto gráfico opcional.

### Em containers

Preferencialmente:

- RemoteTerm;
- Companion/radio-core;
- simulator;
- serviços auxiliares;
- bots adicionais, se necessários;
- persistência/migrações;
- diagnóstico de aplicação.

### Hardware

Preferir:

- `/dev/spidev*`;
- `/dev/gpiochip*`;
- permissões/grupos;
- capabilities específicas.

Evitar `privileged: true` por padrão.

Se a camada Linux escolhida exigir execução no host para controlar o SX1262, documentar a limitação e manter o restante containerizado. Não esconder essa exceção.

---

## 7. Pesquisa já consolidada

### RemoteTerm

Fonte principal:

- https://github.com/jkingsman/Remote-Terminal-for-MeshCore
- https://wiki.seeedstudio.com/get_started_with_meshcore_remote_terminal/

Recursos relevantes documentados:

- interface web;
- contatos;
- canais;
- histórico/cache;
- visualização de mesh;
- trace/multihop;
- bots Python;
- MQTT;
- webhooks;
- Apprise;
- SQS;
- Home Assistant.

A Seeed demonstra RemoteTerm com Companion serial externo, mas também documenta suporte a Companion TCP/Bluetooth. Isso **não prova** que MeshCoreRPI seja compatível por TCP; precisa ser testado.

### MeshCoreRPI

Candidato principal:

- https://github.com/dabeani/MeshCoreRPI

Comparar quando necessário:

- https://github.com/robertjakub/MeshCoreRPI
- https://github.com/johnterickson/MeshCoreRPI

Objetivo:

```text
RemoteTerm
   ↓ TCP/local transport
Companion Linux no Pi
   ↓ SPI/GPIO
SX1262
```

O firmware MCU oficial não é automaticamente executável em Linux. Precisamos validar implementação equivalente de protocolo, framing, identidade, crypto e driver de rádio.

---

## 8. Fases de implementação

### Fase 0 — Auditoria e congelamento técnico

Entregáveis:

- revisar forks/repos;
- registrar commits/revisões;
- licenças;
- build ARM64;
- interface Companion;
- framing;
- crypto;
- persistência;
- bots;
- TCP;
- dependências de rádio;
- docs/RESEARCH.md;
- docs/DECISIONS.md.

Critério de aceite:

- cada afirmação marcada como:
  - confirmado por fonte;
  - confirmado por código;
  - confirmado por execução;
  - hipótese;
  - bloqueado por hardware.

---

### Fase 1 — Raspberry sem HAT e sem display

Objetivo: executar toda a pilha possível agora.

Entregáveis:

- Raspberry Pi OS 64-bit com Desktop;
- SSH;
- Docker + Compose;
- RemoteTerm;
- Companion/simulador;
- persistência;
- health checks;
- logs;
- LAN/mDNS;
- script de doctor.

Teste mínimo:

```text
Browser remoto
   ↓
RemoteTerm
   ↓
Companion/simulator
   ↓
fake TX/RX
```

Critérios:

- UI abre;
- mensagem TX chega ao simulator;
- simulator injeta RX;
- RX aparece na UI;
- histórico persiste após restart;
- bots podem ser criados/testados;
- tudo explicitamente identificado como SIMULAÇÃO / SEM RF.

---

### Fase 2 — Interoperabilidade Companion ↔ RemoteTerm

Comprovar sem HAT, quando possível:

- conexão TCP;
- handshake;
- framing;
- identidade;
- contatos;
- canais;
- chaves;
- crypto;
- ACK;
- reconexão;
- persistência;
- compatibilidade por versão.

Se MeshCoreRPI não oferecer o transporte necessário:

1. documentar exatamente o gap;
2. criar adaptador mínimo;
3. não reimplementar RemoteTerm inteiro.

Critério:

- teste automatizado/reproduzível com logs.

---

### Fase 3 — Simulação de mesh/multihop

Criar harness com múltiplos nós virtuais.

Validar:

- 2+ peers;
- forwarding;
- TTL;
- duplicação;
- perda;
- retry;
- latência;
- ACK;
- direct messages;
- channels;
- RSSI/SNR simulados;
- hops.

Três nós virtuais são o mínimo para testes de encaminhamento.

Separar rigorosamente:

- teste de protocolo;
- teste de rádio real.

---

### Fase 4 — Bots

Prioridade: aproveitar bots nativos do RemoteTerm.

Validar:

- criação pela UI;
- edição;
- enable/disable;
- triggers;
- resposta MeshCore;
- timeout;
- rate limit;
- persistência;
- logs;
- proteção contra loops;
- isolamento de erro.

Bots iniciais:

1. Echo Bot;
2. System Status Bot;
3. Keyword Bot;
4. Scheduled Bot;
5. Diagnostic Bot.

Possíveis integrações posteriores:

- MQTT;
- HTTP;
- Home Assistant;
- sensores;
- GPIO/I²C;
- GPS;
- LLM local/remoto.

Critério:

- erro em bot nunca derruba Companion/radio-core.

---

### Fase 5 — Kiosk local

Pode ser implementada antes do display físico.

Entregáveis:

- launcher de Chromium;
- `--kiosk`;
- fullscreen;
- profile dedicado;
- disable first-run prompts;
- health-wait;
- autoreload/recovery;
- autostart após login/boot;
- esconder cursor quando apropriado;
- opção administrativa para sair do kiosk;
- reboot/shutdown pela UI ou painel auxiliar.

Fluxo:

```text
boot
 ↓
compose up
 ↓
health checks
 ↓
UI healthy
 ↓
open Chromium kiosk
 ↓
monitor Chromium
 ↓
restart se morrer
```

Critério:

- reiniciar o Pi leva automaticamente à aplicação sem teclado/mouse.

---

### Fase 6 — Decisão GO/NO-GO do HAT

Antes da compra/conexão:

Identificar e documentar:

- modelo exato;
- SX1262/variante;
- frequência;
- SPI;
- IRQ;
- BUSY;
- RESET;
- TCXO;
- RF switch;
- potência;
- alimentação;
- antena;
- driver Linux;
- acesso dentro de container;
- requisitos regionais.

GO somente se:

- software base funciona;
- RemoteTerm↔Companion está validado ou existe adaptador reproduzível;
- simulator cobre TX/RX e multihop no nível de protocolo;
- existe caminho técnico plausível para o HAT.

---

### Fase 7 — Integração RF real

Com hardware:

- inicialização SX1262;
- TX;
- RX;
- frequência/região;
- RSSI;
- SNR;
- potência;
- reconexão;
- reboot;
- mensagens criptografadas;
- peers reais;
- multihop real;
- coexistência;
- consumo.

Nunca marcar teste virtual como RF validado.

---

### Fase 8 — Display touchscreen escolhido

Integrar profile do display.

Validar:

- driver;
- boot;
- resolução;
- touch;
- teclado virtual;
- tamanho dos controles;
- rotação;
- brilho;
- blanking;
- estabilidade do Chromium;
- consumo;
- alimentação.

Critério:

- todos os fluxos essenciais são executáveis somente pelo touch.

---

### Fase 9 — Hardening/appliance

Entregáveis:

- watchdog;
- restart policies;
- health monitoring;
- rotação de logs;
- backup/restore;
- atualização;
- rollback;
- export/import de configuração;
- shutdown limpo;
- recuperação após queda de energia;
- diagnóstico de storage/RAM/temperatura/rede/rádio.

---

## 9. Acesso remoto durante desenvolvimento

### SSH — preferencial

Usar para:

- Docker;
- logs;
- atualizações;
- configuração;
- doctor;
- troubleshooting.

### Web UI pela LAN

Usar para desenvolver/testar a mesma interface que ficará no kiosk.

### Desktop remoto — opcional

TeamViewer, RustDesk, VNC ou solução equivalente.

Usar para:

- validar desktop;
- kiosk;
- resolução;
- Chromium;
- autostart;

antes da chegada do display.

Não transformar desktop remoto em dependência do produto.

---

## 10. Persistência

Persistir no mínimo:

- identidade;
- chaves;
- contatos;
- canais;
- histórico;
- bots;
- preferências;
- configuração de rádio;
- parâmetros da aplicação.

Preferir volumes Docker e SQLite se compatível com o upstream.

Backup antes de upgrades.

---

## 11. Observabilidade

Cada componente deve expor:

- logs com timestamp;
- nível;
- componente;
- health check;
- erro acionável.

Eventos importantes:

- Companion connected/disconnected;
- radio available/unavailable;
- TX queued/sent/failed;
- RX;
- bot started/completed/failed;
- persistência indisponível;
- reconnect;
- startup/kiosk failure.

---

## 12. Segurança

- não expor RemoteTerm diretamente à Internet;
- bots Python têm alto poder e exigem proteção;
- LAN por padrão;
- autenticação para ações administrativas quando aplicável;
- secrets fora do Git;
- evitar container privilegiado;
- portas mínimas;
- logs sem chaves/segredos;
- TLS/reverse proxy opcional para cenários remotos.

---

## 13. Definition of Done do MVP

O MVP só está pronto quando:

- Pi liga e sobe sozinho;
- Chromium entra em kiosk;
- UI aparece no próprio Pi;
- Pi opera como Companion/cliente MeshCore;
- SX1262 é controlado sem segundo MCU;
- TX/RX real funciona;
- contatos/canais funcionam;
- histórico persiste;
- bots funcionam;
- display touch permite operação completa;
- LAN continua disponível como opção;
- celular não é necessário;
- companion app externo não é necessário;
- reboot não exige intervenção;
- instalação do zero está documentada.

---

## 14. Ordem imediata de trabalho

1. Gravar Raspberry Pi OS 64-bit **com Desktop**.
2. Habilitar SSH no Imager.
3. Fazer primeiro boot.
4. Confirmar rede/hostname.
5. Instalar/verificar Docker + Compose.
6. Clonar `engperini/RaspMeshcore`.
7. Subir o Stage 1 existente.
8. Implementar Companion/simulator.
9. Validar RemoteTerm↔simulator.
10. Validar bots.
11. Criar kiosk/autostart mesmo sem display dedicado.
12. Validar acesso remoto por SSH + web + desktop remoto opcional.
13. Só então avançar para HAT real.
14. Display físico pode ser escolhido em paralelo sem bloquear software.

---

## 15. Regras para o agente

1. Entregar etapas completas e testadas.
2. Revisar antes de entregar.
3. Não declarar PASS sem evidência reproduzível.
4. Não confundir simulação com RF.
5. Não introduzir segundo MCU sem aprovação.
6. Não tornar smartphone obrigatório.
7. Não recriar RemoteTerm sem necessidade comprovada.
8. Manter Docker como caminho padrão.
9. Registrar decisões técnicas.
10. Atualizar este plano conforme cada fase for concluída.


## 16. Prioridade operacional aprovada (2026-10-19)
1. **P0** Simulador Companion compatível com RemoteTerm sem HAT; não basta observar TCP. Implementação inicial parcial com comandos básicos e loopback local; aguarda teste integrado real.
2. **P1** Executar testes automatizados de conexão, handshake, TX/RX e persistência usando o RemoteTerm upstream, corrigir divergências de versão e só então marcar PASS.
3. **P2** Habilitar/testar bots originais RemoteTerm com autenticação e HTTPS adequados.
4. **P3** Kiosk/autostart no Raspberry Pi OS Desktop, com espera de saúde da UI e recuperação de falhas.
5. **P4** Container Companion nativo e validação de HAT SX1262, RF e multihop físico.

### Instalação e configuração
- Entregar `scripts/install.sh` como entrada assistida, `scripts/doctor.sh` como diagnóstico, `.env.example` como referência e Compose overlay por modo.
- Não atualizar o Raspberry Pi OS, nem instalar toolchain no host. Docker Engine/Compose e Chromium no OS Desktop são pré-requisitos.
- O instalador deve ser idempotente e recusar execução sem Docker/Compose.
- O modo simulador deve ficar identificado como SEM RF, sem criptografia e sem multihop real; não prometer chat funcional antes do teste RemoteTerm completo.
- O acesso remoto pela LAN é opcional e exige bind explícito; bots ficam desativados por padrão devido à execução arbitrária de Python.
- Antes de cada entrega: revisar arquivos, executar testes, inspecionar resultado da CI e atualizar `docs/STATUS.md`.
