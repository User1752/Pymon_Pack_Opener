# 🎴 Pymon TCG Pack Opener

## ✨ Funcionalidades

- 🎴 **Abertura de Packs** - Sistema realista com animações
- 📚 **Coleção Completa** - Visualize e organize cartas
- 🌍 **Multi-Região** - Sets ingleses (ENG) e japoneses (JP)
- 📦 **Sistema de Inventário** - Guarde packs para abrir depois
- 🏆 **XP/Level System** - Ganhe experiência e suba de nível
- 🎖️ **25+ Achievements** - Conquistas desbloqueáveis
- 🛒 **Loja de Packs** - Compre com moedas ganhas
- 🎰 **Minigames** - Blackjack e Slot Machine
- 💾 **3 Slots de Save** - Múltiplos perfis

## 📁 Estrutura

Pymon_Pack_Opener/
├── main.py                    # Ponto de entrada principal
├── core/                      # Lógica do jogo
│   ├── game.py               # Classes Pack, Wallet, Pokemon
│   ├── config.py             # Configurações e constantes
│   └── profile.py            # Sistema de perfil/XP/achievements
├── ui/                        # Interface gráfica
│   ├── theme.py              # Sistema de temas
│   ├── widgets.py            # Widgets reutilizáveis
│   ├── shop.py               # Sistema de loja
│   ├── collection_viewer.py  # Visualizador de coleção
│   ├── profile_ui.py         # Interface de perfil
│   └── minigames/            # Minigames
│       └── blackjack_gui.py  # Blackjack
├── widgets/                   # Componentes auxiliares
│   └── utils/                # Utilitários
│       ├── image_loader.py   # Carregamento de imagens
│       ├── settings_manager.py # Sistema de save/load
│       └── card_images.py    # Sistema de URLs de cartas
├── data/                      # Dados do jogo
│   ├── packs.json            # Definições de packs
│   └── packs_info.json       # Informações detalhadas
├── assets/                    # Recursos gráficos
│   └── card_images/          # JSONs com URLs das cartas
│       ├── expansion_pack.json
│       ├── pokemon_jungle.json
│       ├── mystery_of_the_fossils.json
│       ├── base_pack_set.json
│       ├── jungle.json
│       └── fossil.json
└── saves/                     # Saves do jogador
    ├── settings.json
    ├── save_slot_1.json
    ├── save_slot_2.json
    └── save_slot_3.json