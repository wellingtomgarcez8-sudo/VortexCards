# Multiplayer e compatibilidade cruzada

Vortex Cards usa um servidor autoritativo executado no computador do host. O transporte base é TCP, com mensagens JSON UTF-8 precedidas por um tamanho de 32 bits em ordem de rede.

Isso torna o protocolo independente do sistema operacional: Windows e Linux usam exatamente as mesmas mensagens e regras. Não há caminhos, tipos binários nativos ou serialização Python `pickle` no tráfego.

## LAN

O host inicia o servidor em `0.0.0.0:<porta>`. Os convidados conectam ao IPv4/hostname do computador do host e à porta exibida.

## Internet

Conexão direta exige que a porta seja alcançável. Dependendo da rede, isso pode exigir encaminhamento de porta, UPnP/NAT-PMP ou uma futura infraestrutura de NAT traversal/relay. O código da sala é um identificador de convite e não substitui um endereço roteável.

## Segurança

O servidor é a autoridade sobre cartas, turnos, efeitos e pontuação. Clientes enviam somente intenções. Cada resposta `GAME_STATE` inclui a mão privada apenas do destinatário e somente contagens das mãos adversárias.
