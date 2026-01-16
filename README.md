# 🎴 Pymon TCG Pack Opener

**Simulador profissional de abertura de packs de Pokémon TCG** com sistema completo de coleção, XP, achievements e minigames.

---

## ✨ Funcionalidades

### 🎴 **Sistema de Packs**
- ✅ **Abertura realista** com animações e efeitos visuais
- ✅ **Multi-região**: Sets ingleses (ENG) e japoneses (JP)
- ✅ **8 Sets disponíveis**: Base Set, Jungle, Fossil, Base Set 2, Expansion Pack (JP), Pokémon Jungle (JP), Mystery of the Fossils (JP)
- ✅ **Sistema de inventário**: Guarde packs para abrir depois
- ✅ **Imagens reais** das cartas (modo real/simples)

### 📚 **Coleção & Progresso**
- ✅ **Visualizador de coleção** com filtros por raridade e set
- ✅ **Estatísticas de completude** por pack
- ✅ **Sistema de XP/Level** com progressão visual
- ✅ **25+ Achievements** desbloqueáveis
- ✅ **Perfil do jogador** com estatísticas detalhadas

### 🛒 **Economia & Loja**
- ✅ **Sistema de moedas** - Ganhe coins abrindo packs
- ✅ **Loja de packs** - Compre com moedas ganhas
- ✅ **Packs bloqueados por nível** - Desbloqueie novos sets
- ✅ **Auto-save** após compras

### 🎰 **Minigames**
- ✅ **Slot Machine** - Apostas e multiplicadores
- ✅ **Blackjack** - Sistema completo de cartas

### 💾 **Sistema de Save**
- ✅ **3 Slots de Save** independentes
- ✅ **Auto-save** no shop
- ✅ **Persistência completa**: coins, coleção, inventário, XP, achievements

---

## 📁 Estrutura do Projeto

```
Pymon_Pack_Opener/
│
├── main.py                         # ⚙️ Ponto de entrada principal
│
├── core/                           # 🎮 Lógica do jogo
│   ├── __init__.py
│   ├── game.py                     # Classes Pack, Wallet, Pokemon, Card
│   ├── config.py                   # Configurações, cores, níveis de unlock
│   └── profile.py                  # Sistema XP/Level/Achievements
│
├── ui/                             # 🎨 Interface gráfica
│   ├── __init__.py
│   ├── theme.py                    # Sistema de temas moderno (helpers centralizados)
│   ├── widgets.py                  # CardWidget, SlotMachineWidget
│   ├── shop.py                     # Sistema de loja de packs
│   ├── collection_viewer.py        # Visualizador de coleção com filtros
│   ├── profile_ui.py               # Interface de perfil do jogador
│   └── minigames/
│       ├── __init__.py
│       └── blackjack_gui.py        # Minigame Blackjack completo
│
├── widgets/                        # 🔧 Componentes auxiliares
│   └── utils/
│       ├── __init__.py
│       ├── image_loader.py         # Sistema de carregamento de imagens (deprecated)
│       ├── card_images.py          # Sistema de URLs de cartas (ATIVO)
│       └── settings_manager.py     # Sistema de save/load (3 slots)
│
├── data/                           # 📊 Dados do jogo
│   ├── packs.json                  # Definições de todos os packs (8 sets)
│   └── packs_info.json             # Informações detalhadas (release, theme decks)
│
├── assets/                         # 🖼️ Recursos gráficos
│   └── card_images/                # Imagens das cartas
│       ├── expansion_pack.json     # 102 cartas (JP)
│       ├── pokemon_jungle.json     # 48 cartas (JP)
│       ├── mystery_of_the_fossils.json # 48 cartas (JP)
│       ├── base_pack_set.json      # 102 cartas (ENG)
│       ├── jungle.json             # 32 cartas (ENG)
│       ├── fossil.json             # 47 cartas (ENG)
│       └── base_set_2.json         # 130 cartas (ENG)
│       └── images/                 # Pastas de imagens físicas
│           ├── expansion_pack_image/   # expansionpack-0.jpeg ... 101.jpeg
│           ├── jungle_jp/              # jungleJP-0.jpeg ... 47.jpeg
│           ├── mystery_of_the_fossils/ # fossilsJP-0.jpeg ... 47.jpeg
│           ├── base_pack_set_images/
│           ├── jungle_images/
│           ├── fossil_images/
│           └── base_set_2_images/
│
└── saves/                          # 💾 Sistema de saves
    ├── settings.json               # Configurações gerais
    ├── save_slot_1.json            # Slot 1
    ├── save_slot_2.json            # Slot 2
    └── save_slot_3.json            # Slot 3

## 📦 Sistema de Packs

### **Packs Disponíveis**

| Pack | Região | Cartas | Preço | Nível Mínimo |
|------|--------|--------|-------|--------------|
| Base Pack Set | ENG | 102 | 50 coins | 1 |
| Expansion Pack | JP | 102 | 50 coins | 1 |
| Jungle | ENG | 32 | 25 coins | 1 |
| Pokémon Jungle | JP | 48 | 25 coins | 1 |
| Fossil | ENG | 47 | 25 coins | 1 |
| Mystery of the Fossils | JP | 48 | 25 coins | 1 |
| Base Set 2 | ENG | 130 | 50 coins | 5 |

### **Sistema de Raridades**

| Raridade | Recompensa | XP | Cor |
|----------|------------|-----|-----|
| Common | 5 coins | 5 XP | Cinza |
| Uncommon | 10 coins | 10 XP | Verde |
| Rare | 25 coins | 25 XP | Azul |
| Rare Holo | 50 coins | 50 XP | Roxo/Dourado |
| Energy | 1 coin | 2 XP | Amarelo |










