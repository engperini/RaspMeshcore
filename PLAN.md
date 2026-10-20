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
