# RaspMeshcore — Plano de execução para agente

Data: 2026-10-19 | Status: planejamento; integração ainda não validada.

## Missão
Construir terminal MeshCore autônomo em Raspberry Pi 4, sem segundo MCU nem aplicativo companion no celular, com interface web, mensagens, criptografia, multihop e bots configuráveis. Prioridade absoluta: validar todo software possível ANTES de comprar LoRa HAT.

## Resultados da pesquisa e repositórios de partida
- https://github.com/dabeani/MeshCoreRPI — candidato Companion Linux para Raspberry Pi; auditar código, rádio e TCP.
- https://github.com/robertjakub/MeshCoreRPI e https://github.com/johnterickson/MeshCoreRPI — variantes a comparar.
- https://github.com/statico/remoteterm-meshcore — candidato RemoteTerm; conferir interface TCP.
- https://github.com/LA-Seniors/RemoteTerm — implementação alternativa a avaliar.
- Hipótese de arquitetura: MeshCoreRPI Companion no Pi → TCP local (porta 5000 é hipótese a confirmar no código) → RemoteTerm → backend/web/bots.
- Há relato anterior de problemas de multihop com Companion Linux por TCP e RemoteTerm; localizar evidência, reproduzir e documentar.
- Firmware oficial para MCU NÃO é automaticamente executável num HAT que contém somente transceptor LoRa. Avaliar implementação do protocolo no Linux, driver SPI/GPIO e equivalência funcional ao firmware oficial.
- Não confundir LoRaWAN com MeshCore. Compatibilidade mecânica do HAT não comprova compatibilidade de software.

## Fases obrigatórias
### Fase 0 — Auditoria de fontes
Clonar repositórios em revisões fixadas; mapear licenças, commits, README, build, dependências, APIs, protocolo, mensagens e funcionalidades faltantes. Criar docs/RESEARCH.md com evidências e links por commit. Não declarar funcionalidades sem executar ou ler código.

### Fase 1 — Laboratório sem rádio
Instalar dependências no Raspberry Pi 4 (preferir Docker/venv e scripts idempotentes). Compilar e executar MeshCoreRPI e RemoteTerm, com configuração TCP explícita. Criar harness para substituir transporte de rádio e simular dois ou mais nós, preservando framing real. Se a implementação não oferecer injeção de transporte, criar adaptador isolado, sem fingir que houve RF real.

### Fase 2 — Interoperabilidade e protocolo
Comprovar handshake, descoberta, envio e recepção, mensagens diretas/canais, identidade/chaves, criptografia, ACK, reconexão, persistência, compatibilidade de versões e encaminhamento multihop. Capturar logs e traces sanitizados, documentar formatos de frames e limitações. Usar três nós virtuais para testes de encaminhamento, duplicação, TTL e perda; separar testes de protocolo dos testes reais de rádio.

### Fase 3 — Produto web
Criar serviço backend com API local, WebSocket para eventos e interface responsiva para computador/celular: chat, contatos, canais, histórico, estado do nó, diagnóstico, configuração, segurança e backup de chaves. Smartphone deve ser apenas navegador opcional; o Pi opera sem ele. Evitar exposição pública insegura; autenticação obrigatória para ações administrativas.

### Fase 4 — Bots
Criar arquitetura de plugins para bots configuráveis, comandos, gatilhos, respostas automáticas e permissões, inspirada na experiência do aplicativo da Seeed Studio, sem copiar código proprietário. Limitar taxa, impedir loops de retransmissão e registrar auditoria.

### Fase 5 — Decisão sobre HAT
Somente após validação de software, identificar modelo e transceptor efetivos do HAT (por exemplo SX1262), SPI, IRQ, BUSY, RESET, TCXO, RF switch, potência, alimentação, banda homologável e antena. Validar drivers Linux e interface do MeshCoreRPI. Documentar lacunas e recomendação GO/NO-GO antes de comprar. HAT não é segundo MCU.

### Fase 6 — Integração e validação RF
Quando hardware estiver disponível, validar TX/RX reais, configuração regional, RSSI/SNR, alcance, coexistência, consumo, reinicialização e multihop com outros nós MeshCore reais. Não considerar testes virtuais como comprovação de interoperabilidade no ar.

### Fase 7 — Operação
Criar scripts de instalação, systemd, configuração de segredos, logs rotativos, atualização, recuperação, testes automatizados e CI. README com instruções reproduzíveis e matriz de funcionalidades testadas.

## Regras de execução para agente
1. Trabalhar em pequenas alterações com testes; registrar decisões em docs/DECISIONS.md.
2. Nunca afirmar que um teste passou sem logs e comandos reproduzíveis.
3. Distinguir: confirmado por código, confirmado por execução, hipótese e bloqueado por hardware.
4. Preservar licença e atribuição de terceiros; não incorporar código sem revisão de licença.
5. Entregar por fase: código, testes, documentação, relatório PASS/FAIL e próximos bloqueios.
6. Não adquirir hardware nem alterar a arquitetura para dois MCUs sem aprovação explícita.
7. Iniciar imediatamente pela Fase 0 e depois Fase 1, sem esperar HAT.

## Critério GO/NO-GO antes de comprar HAT
GO apenas se compilação e serviços funcionarem no Pi 4, interface Companion↔RemoteTerm estiver comprovada ou substituída por integração documentada, mensagens e criptografia tiverem testes reprodutíveis, multihop estiver validado ao nível de protocolo/simulação, e houver caminho plausível e documentado para driver de rádio. Registrar limitações que só podem ser verificadas com hardware.


## Diretriz de produto: referência Seeed Studio
- Usar o modelo de experiência do aplicativo Seeed Studio discutido anteriormente como REFERÊNCIA de UX: onboarding, chats, contatos, canais e criação/configuração de bots pelo usuário. Identificar nome e recursos exatos do aplicativo durante a Fase 0; não alegar paridade antes de comparar telas e funções.
- Implementar interface web responsiva própria, acessível em LAN, sem aplicativo companion no celular. Não copiar marca, código, recursos proprietários ou visual protegido.
- Bots configuráveis via interface (gatilhos, comandos, templates, habilitar/desabilitar, permissões, limites e logs); garantir que bots não provoquem flood na malha.

## Docker-first: requisito obrigatório de distribuição
**Meta de uso:** após preparação mínima do Raspberry Pi OS, `git clone`, `docker compose up -d` e acesso à interface web em `http://<IP-DO-PI>:8080`. O nome `raspberrypi.local` depende de mDNS e não deve ser assumido como garantido.

1. Fornecer `Dockerfile` multi-stage ARM64, `compose.yaml`, `.env.example`, `.dockerignore`, `scripts/setup-host.sh`, `scripts/doctor.sh`, healthchecks e instruções de instalação Docker/Compose.
2. Priorizar distribuição em imagem `linux/arm64` publicada em GHCR com tags versionadas; build local como alternativa. Não exigir compilação no Pi para usuário final.
3. Preferir **um comando Compose** como experiência, mesmo que internamente haja vários serviços. Avaliar container único versus serviços separados (core, API/web, bots) com base em dependências, reinício e isolamento; não forçar monólito se prejudicar estabilidade.
4. Manter identidade, chaves, histórico, configurações e banco SQLite em volumes persistentes, com backup/restore e migrações. Nunca inserir segredos na imagem ou logs.
5. Suportar `RADIO_BACKEND=simulator` como padrão inicial sem hardware e `RADIO_BACKEND=spi` apenas após validação. A interface deve sinalizar claramente **SIMULAÇÃO / SEM RF**.
6. Documentar requisitos reais de host: Docker, arquitetura ARM64, kernel, SPI habilitado, dispositivos `/dev/spidev*` e GPIO acessíveis, permissões, overlays e dependências de driver. Preferir mapeamento de devices e permissões mínimas; **não usar `privileged: true` como padrão**.
7. Não pressupor que firmware MCU oficial rode em container Linux: container compartilha kernel do Pi e não substitui implementação de driver/protocolo compatível.
8. Interface e API expostas somente na LAN por padrão, autenticação inicial, política de senha, TLS por proxy opcional, limites de acesso e atualização segura.
9. Definir healthchecks para core, TCP, web, banco e rádio; reinício automático, logs estruturados, limites de recursos, desligamento limpo e recuperação após reboot/queda de energia.
10. Criar CI que construa imagens ARM64, rode testes unitários e de integração com simulador, publique artefatos versionados e valide `docker compose config`.
11. Entregar documentação `docs/DOCKER.md` com instalação, atualização, downgrade, backup, restauração, troubleshooting, matriz Pi OS 64-bit / Pi 4 e testes de aceitação.
12. Aceitação do modo sem HAT: `docker compose up -d` sobe sem intervenção manual extra (após preparo do host), página responde, simulator opera, bots podem ser configurados, dados sobrevivem a restart e nenhum teste é anunciado como RF real.
13. Aceitação do modo HAT: SPI/GPIO e transceptor efetivamente identificados, TX/RX testados, compatibilidade MeshCore real validada e reinício do container sem perda de configuração.

## Ordem de implementação revisada
Na Fase 0 verificar especificamente viabilidade de containerizar MeshCoreRPI e RemoteTerm e descobrir dependências de kernel/radio. Na Fase 1 criar o esqueleto Docker Compose com simulador, healthchecks e UI mínima; em seguida executar testes de integração antes de avançar em UX/bots. Não aguardar aquisição de HAT.


## Requisito adicional: aplicativo oficial utilizado pela Seeed Studio
O usuário pode optar por usar o aplicativo da Seeed Studio **em vez da interface web própria**. Tratar esse caminho como objetivo de primeira classe, mas ainda NÃO validado.
- Fase 0: identificar nome, versão, fabricante, documentação e compatibilidade MeshCore do aplicativo concreto citado; diferenciar app da Seeed, MeshCore oficial e apps de terceiros.
- Auditar quais transportes o app aceita (BLE, USB, TCP, Wi-Fi, gateway), descoberta, pairing, identidade, framing, autenticação e recursos de bots.
- Prototipar conexão app ↔ Companion no Raspberry Pi via transporte oficialmente suportado. Se TCP não for aceito, estudar ponte BLE/Wi-Fi ou gateway com limitações explícitas; não afirmar suporte inexistente.
- Validar envio, recebimento, canais, contatos, bots e multihop a partir do app; documentar matriz por versão e plataforma Android/iOS.
- Manter a interface web como alternativa e painel de administração, não como substituto obrigatório do app.
- Critério de aprovação: vídeo/logs e roteiro reproduzível de conexão real entre app e Pi, com distinção entre testes simulados e RF.


## Descoberta confirmada: referência Seeed Studio (fonte primária)
Fonte: https://wiki.seeedstudio.com/get_started_with_meshcore_remote_terminal/
- A Seeed documenta **RemoteTerm**, projeto aberto de **jkingsman/Remote-Terminal-for-MeshCore**: https://github.com/jkingsman/Remote-Terminal-for-MeshCore . Não se trata de app proprietário da Seeed. Esta é a implementação **preferencial**; as outras variantes são referências secundárias.
- A documentação Seeed instala RemoteTerm no Raspberry Pi OS Lite 64-bit com script `./scripts/setup/install_docker.sh` e `docker compose up -d`. **Reutilizar Compose/instalador upstream sempre que possível**, sem recriar desnecessariamente a UI.
- Funcionalidades documentadas: interface web mobile, cache de pacotes, contatos/canais, mapas e visualizador mesh, trace multihop, busca, bots Python editáveis na UI, MQTT, webhooks, Apprise, SQS e Home Assistant.
- Transporte: a Seeed demonstra Serial Companion via USB em XIAO ESP32-S3 + SX1262; declara que RemoteTerm também suporta companions TCP e Bluetooth. Isso **não comprova** que MeshCoreRPI ofereça TCP compatível: verificar na implementação e testar.
- **Arquitetura-alvo:** Raspberry Pi 4 + LoRa HAT SPI/GPIO + Companion Linux compatível + RemoteTerm original em Docker; sem ESP32 adicional e sem app celular obrigatório. A UI original do RemoteTerm é o cliente principal.
- Rever decisões anteriores: não criar frontend/backend/bots substitutos se o RemoteTerm já atende; criar apenas adaptadores e painel auxiliar estritamente necessários. Evitar bifurcação do upstream sem necessidade.
- Verificar preservação de contatos/chaves quando RemoteTerm assume gerenciamento do Companion; o guia alerta que RemoteTerm passa a governar a sincronização de contatos/canais.
- Validar modos: Docker RemoteTerm com Companion TCP simulado primeiro; depois Companion Linux real sem rádio, por fim HAT. Documentar limitações do simulador.
- Ajustar critérios de aceitação: interface original abre no navegador, bots Python podem ser criados e acionados com mensagens de teste, TCP Companion↔RemoteTerm funciona, persistência em volumes e recuperação após reboot.
- Não alegar que o aplicativo móvel nativo da Seeed é suportado: o produto documentado é uma aplicação **web**.
