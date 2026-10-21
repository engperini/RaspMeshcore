# Checklist de release: instalação reproduzível

## Já demonstrado no Raspberry Pi 4 ARM64
- [x] Docker RemoteTerm + simulador ativos após reinicialização
- [x] Roteador TCP encaminha RemoteTerm para simulador
- [x] Companion nativo compilado no Raspberry (PlatformIO)
- [x] Supervisor systemd `active`, `enabled`, `waiting_usb`
- [x] `main` e dados do RemoteTerm preservados durante testes

## Bloqueadores de release plug-and-play
- [ ] Um único instalador idempotente, a partir de clone limpo, configura Docker, UI, Companion e systemd sem passos manuais
- [ ] `install-pi-usb.sh` pode ser reexecutado sem falhar em checkout já modificado pelo overlay
- [ ] Sem necessidade de `sudo` manual para criar `data/radio`
- [ ] Seleção USB/simulador integrada no instalador, persistente após reboot
- [ ] Garantir permissões USB específicas e seleção segura do CH341 correto
- [ ] Companion inicia com parâmetros corretos de SX1262 (DIO2 RF switch, DIO3 TCXO, frequência legal e parâmetros de rede)
- [ ] Testar remoção e reconexão USB, dispositivo ocupado, permissão negada, falha de SPI e reboot
- [ ] Health check distingue processo vivo de rádio realmente operacional
- [ ] Validar RemoteTerm ↔ Companion real, mensagens TX/RX, criptografia e multihop
- [ ] Confirmar CI verde no commit final e teste de instalação limpa
- [ ] Definir instruções para Raspberry Pi OS Lite e Desktop, e kiosk quando display estiver definido
- [ ] Documentar recuperação, rollback, atualização e desinstalação
- [ ] Revisar licença e atribuições de código upstream/terceiros

## Política de release
Não confundir sucesso de compilação com comunicação por rádio. Manter suporte ao simulador e HAT SPI. Não substituir dados existentes e não modificar a `main` antes da revisão final e autorização de merge.
