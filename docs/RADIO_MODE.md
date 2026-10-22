# Seleção de rádio: simulador ou MeshStick USB

Este recurso foi desenvolvido na branch `feature/meshstick-usb-ch341`. **Não está implantado no Pi até você atualizar o worktree e subir o Compose.**

## Sem alterar a instalação principal

No Pi, mantenha `~/RaspMeshcore` (main) intacto. Execute a integração a partir do worktree `~/RaspMeshcore-USB`, mas **não suba uma segunda instância RemoteTerm na porta 8080** enquanto a instância principal estiver rodando.

Para migrar a instância atual, recomendamos uma janela de manutenção: copiar os arquivos novos (`compose.radio-router.yaml`, `radio/tools/tcp_router.py`, `scripts/radio-mode.sh`) para a instalação principal após revisão, sem trocar de branch, e preservar `data/remoteterm`. Isso exige recriação apenas do contêiner RemoteTerm, com uma breve interrupção da interface. Não execute dois Compose em paralelo com a mesma porta.

## Modo explícito, sem falsa conectividade

O proxy TCP encaminha novas conexões do RemoteTerm para:
- `simulator:5000` quando `data/radio/radio-mode` contém `simulator` (padrão).
- `host.docker.internal:5000` quando contém `usb`.

Não há fallback silencioso para o simulador em modo USB. Se o rádio estiver ausente, a interface deve indicar desconexão, não simular mensagens reais. A mudança de modo só vale para novas conexões TCP; reinicie o RemoteTerm para forçar reconexão.

Compose no diretório principal, após adicionar os arquivos e preservar `.env`:

```bash
mkdir -p data/radio
printf 'simulator\n' > data/radio/radio-mode
sudo docker compose -f compose.yaml -f compose.simulator.yaml -f compose.radio-router.yaml up -d
```

Para alternar, quando o hardware estiver validado:

```bash
bash scripts/radio-mode.sh usb
sudo docker compose -f compose.yaml -f compose.simulator.yaml -f compose.radio-router.yaml restart remoteterm
```

Para voltar à simulação:

```bash
bash scripts/radio-mode.sh simulator
sudo docker compose -f compose.yaml -f compose.simulator.yaml -f compose.radio-router.yaml restart remoteterm
```

## Portas e limites

O Companion nativo escuta TCP 5000 em todas as interfaces do host, conforme implementação upstream; **não exponha esta porta na Internet**. O roteador TCP é interno à rede Docker. O simulador pode continuar rodando sem afetar a comunicação USB.

A presença de um dispositivo VID/PID CH341 não comprova ser MeshStick. O supervisor registra `running` quando o processo existe, não quando o SX1262 está saudável. Antes da primeira transmissão, validar identificação física, permissões USB, configuração de região, frequência e potência, inicialização do rádio, TCP, TX/RX e MeshCore multihop.

O proxy TCP é um componente de desenvolvimento, não substitui autenticação, health check de rádio, confirmação de entrega ou uma UI de estado integrada. Sem o stick, **não há validação ponta a ponta possível**.
