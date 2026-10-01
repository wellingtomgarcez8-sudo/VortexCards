# Vortex Cards

Jogo de cartas estratégico multiplataforma para **Windows e Linux**, escrito em Python/Pygame.

## Estado

Desenvolvimento ativo na branch `dev/vortexcards-complete`. **Nenhuma build de distribuição deve ser disparada antes da conclusão funcional e dos testes.**

## Recursos já implementados na base

- motor de regras modular;
- baralho completo com cartas numéricas e especiais;
- Bloqueio, Inversão, +2, Vórtice Cromático e Colapso Vórtice;
- compra, reciclagem do descarte, vitória e pontuação;
- IA jogável;
- interface Pygame inicial para partida contra bot;
- servidor autoritativo TCP assíncrono;
- protocolo JSON versionado e independente de sistema operacional;
- cliente TCP;
- privacidade das mãos: cada cliente recebe apenas sua própria mão;
- cadastro local em SQLite com senha protegida por Argon2;
- testes unitários iniciais.

## Compatibilidade Windows ↔ Linux

O multiplayer usa TCP + JSON UTF-8 com framing próprio e um protocolo versionado. Não há serialização dependente de plataforma. Assim, uma instância Linux e uma Windows usando a mesma versão de protocolo podem participar da mesma sala, inclusive com o host em qualquer um dos sistemas.

## Desenvolvimento

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Testes:

```bash
pytest -q
```

## Multiplayer pela internet

O servidor autoritativo já aceita conexões TCP reais. Em LAN, conecte ao IP do host. Pela internet, ainda é necessária rota alcançável (port forwarding/UPnP/NAT traversal ou relay). Um código curto de sala, sozinho, não substitui essa infraestrutura.

## Build

Arquivos de empacotamento e workflows de release serão adicionados somente depois da conclusão dos sistemas obrigatórios e dos testes de Windows/Linux, conforme solicitado.
