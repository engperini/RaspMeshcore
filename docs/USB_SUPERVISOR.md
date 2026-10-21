# Raspberry Pi: rádio USB em espera

O serviço de rádio é **independente** da interface web RemoteTerm (Docker). Sem MeshStick, o supervisor permanece ativo e informa `waiting_usb`; não interrompe o painel.

## Estados
- `waiting_usb`: não há dispositivo USB 1a86:5512.
- `missing_binary`: o Companion ainda não foi compilado/instalado no caminho configurado.
- `starting` / `running`: processo iniciado; **running não garante SX1262 saudável ou MeshCore conectado**.
- `retrying` / `start_error`: falha de execução; nova tentativa com espera crescente (máximo 30 s).
- `stopped`: serviço encerrado.

O supervisor verifica a presença pelo sysfs Linux a cada 2 segundos, encerra o processo quando a USB some e tenta reiniciar após falhas. Status JSON em `/run/raspmeshcore/radio.json`. Logs: `journalctl -u raspmeshcore-radio -f`.

**Atenção:** VID/PID 1a86:5512 não identifica exclusivamente um MeshStick; outros CH341 podem compartilhar esse identificador. Ainda é necessária verificação de identidade por USB e validação de rádio real antes de habilitar transmissão automática. Erros de permissão, dispositivo ocupado e falhas de SPI são registrados no log do Companion; o supervisor tenta novamente. Não há reparo automático de firmware ou hardware defeituoso.

## Execução manual (sem instalar serviço)

```bash
cd ~/RaspMeshcore
python3 radio/tools/usb_supervisor.py --binary "$HOME/MeshCoreRPI/.pio/build/RaspberryPiMC_native_companion/program" --status /tmp/raspmeshcore-radio.json
```

O comando aguarda o dispositivo. Se o binário não existir, o estado será `missing_binary`. Não altera o Docker.

## Serviço systemd (somente após ajustar os caminhos)

`radio/systemd/raspmeshcore-radio.service` é um **modelo**, não uma instalação automática. Ajuste `User`, `Group`, `ExecStart` e as permissões de acesso USB antes de copiá-lo para `/etc/systemd/system/`. A regra udev ainda precisa ser verificada para o dispositivo real; não recomendamos abrir permissão global para qualquer CH341.

O Companion é executado com `--spi-dev-prefix usb_ch341`, CS 0, RESET 2, BUSY 4, IRQ 6. **Frequência, potência, parâmetros MeshCore, DIO2 e TCXO precisam ser configurados e verificados no hardware** antes de transmitir. O processo pode encerrar durante a inicialização caso a configuração seja incompatível.

### Limitações atuais
- Ainda não validado com MeshStick físico.
- A inicialização do processo não prova que o rádio esteja recebendo.
- Não há endpoint HTTP de status; o arquivo JSON está disponível para integração futura com a UI.
- O supervisor não substitui validação de hardware, nem permite concluir que a solução está pronta para produção.
