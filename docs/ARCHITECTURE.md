# Arquitetura do RaspMeshcore

## 1. Papel do Raspberry Pi

O Raspberry Pi 4 não é apenas um gateway.

Ele é o **terminal MeshCore completo**:

- rádio;
- Companion Linux;
- interface local;
- display touchscreen;
- mensagens;
- canais/contatos;
- bots;
- persistência;
- servidor LAN opcional.

A LAN é um acesso alternativo à mesma aplicação, não o produto principal.

---

## 2. Camadas

```text
┌────────────────────── DISPLAY TOUCH ──────────────────────┐
│ Chromium kiosk                                            │
│ http://127.0.0.1:8080                                     │
└──────────────────────────┬─────────────────────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ RemoteTerm   │
                    │ UI + bots    │
                    └──────┬───────┘
                           │ local transport
                           ▼
                    ┌──────────────┐
                    │ Companion /  │
                    │ radio-core   │
                    └──────┬───────┘
                           │ SPI/GPIO
                           ▼
                    ┌──────────────┐
                    │ SX1262 HAT   │
                    └──────┬───────┘
                           │
                           ▼
                        MeshCore
```

Em modo de desenvolvimento, o HAT é substituído por simulator/provider compatível.

---

## 3. Host

Responsabilidades do host:

- Raspberry Pi OS 64-bit com Desktop;
- kernel;
- drivers;
- display/touch;
- Docker;
- Chromium;
- launcher kiosk;
- SSH;
- mDNS;
- desktop remoto opcional.

O host deve permanecer simples e recuperável.

---

## 4. Containers

Topologia inicial:

```text
compose
├── remoteterm
├── companion / radio-core
├── simulator (profile)
└── serviços auxiliares estritamente necessários
```

Não dividir em muitos serviços sem benefício.

Se o upstream RemoteTerm já possuir bot engine, persistência e backend adequados, reutilizar.

---

## 5. Radio Provider

A camada de rádio deve ter duas implementações conceituais:

```text
RadioProvider
├── SimulatorProvider
└── SX1262Provider
```

A UI não pode depender de detalhes de SPI/GPIO.

Troca por configuração, por exemplo:

```text
RADIO_BACKEND=simulator
RADIO_BACKEND=spi
```

---

## 6. Kiosk

O Chromium não deve abrir antes da aplicação estar saudável.

Launcher:

```text
wait network/local stack
        ↓
wait Docker/Compose
        ↓
poll health endpoint
        ↓
launch Chromium --kiosk
        ↓
watch process
        ↓
restart on failure
```

O browser local deve utilizar loopback sempre que possível.

---

## 7. Mesmo frontend local e remoto

```text
Display local
Chromium → 127.0.0.1:8080 ─────┐
                                │
                                ├── RemoteTerm/RaspMeshcore
                                │
LAN browser → Pi-IP:8080 ───────┘
```

Nada no core pode exigir que exista um navegador remoto conectado.

---

## 8. Funcionamento com tela apagada

A tela é apenas apresentação.

Mesmo com:

- Chromium fechado;
- display desligado;
- nenhum cliente LAN;
- desktop remoto desconectado;

o sistema deve continuar:

- recebendo pacotes;
- processando mensagens;
- executando bots;
- persistindo histórico;
- mantendo Companion/radio-core ativo.

---

## 9. Acesso ao SX1262 em Docker

Ordem de preferência:

1. `/dev/spidev*` explicitamente mapeado;
2. `/dev/gpiochip*` explicitamente mapeado;
3. grupos e permissions;
4. capabilities mínimas;
5. serviço host apenas se tecnicamente necessário.

`privileged: true` não é arquitetura padrão.

---

## 10. RemoteTerm

RemoteTerm é o ponto de partida por já oferecer grande parte da experiência desejada.

Antes de criar UI própria:

- testar a experiência em touchscreen;
- testar teclado virtual;
- testar bot editor;
- testar contatos/canais;
- testar navegação em kiosk;
- medir desempenho no Pi 4.

Somente criar frontend próprio se houver lacuna concreta.

---

## 11. Simulador

O simulador faz parte permanente da arquitetura.

Ele deve permitir:

- RX fake;
- captura TX;
- peers;
- canais;
- RSSI/SNR;
- hops;
- perda;
- latência;
- reconnect;
- falha de rádio.

Usos:

- CI;
- desenvolvimento sem HAT;
- regressão;
- demonstração;
- diagnóstico.

---

## 12. Acesso remoto

### SSH
Canal primário de manutenção.

### Browser LAN
Canal secundário para operar/testar a UI.

### TeamViewer/RustDesk/VNC
Canal opcional para enxergar o desktop/kiosk antes do display físico ou durante suporte.

Nenhum deles é necessário para o funcionamento autônomo.

---

## 13. Falhas e recuperação

### Radio indisponível
UI continua disponível e mostra estado claramente.

### RemoteTerm indisponível
Companion não deve entrar em restart loop destrutivo.

### Browser travou
Kiosk launcher reinicia Chromium.

### Rede LAN caiu
Operação local continua.

### Internet caiu
MeshCore local continua.

### Display apagou
Bots e rádio continuam.

### Reboot
Compose e kiosk voltam automaticamente.

---

## 14. Regra arquitetural principal

**O Raspberry Pi é o dispositivo. O navegador remoto é opcional. O display local é a interface principal. O rádio e os bots continuam funcionando independentemente da UI.**
