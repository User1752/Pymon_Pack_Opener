# 🎴 Pymon TCG Pack Opener

**Simulador profissional de abertura de packs de Pokémon TCG** com sistema completo de coleção, XP, achievements e minigames.

---

## ✨ Funcionalidades

### 🎴 **Sistema de Packs**

* ✅ **Abertura realista** com animações e efeitos visuais
* ✅ **Multi-região**: Sets ingleses (ENG) e japoneses (JP)
* ✅ **Sets disponíveis**: Base Pack Set, Base Set 2, Jungle, Fossil, Expansion Pack (JP), Pokémon Jungle (JP), Mystery of the Fossils (JP)
* ✅ **Sistema de inventário**: guarda packs para abrir depois
* ✅ **Imagens reais** das cartas (modo real/simples)

### 📚 **Coleção & Progresso**

* ✅ **Visualizador de coleção** com filtros por raridade e set
* ✅ **Estatísticas de completude** por pack
* ✅ **Sistema de XP/Level** com progressão visual
* ✅ **25+ Achievements** desbloqueáveis
* ✅ **Perfil do jogador** com estatísticas detalhadas

### 🛒 **Economia & Loja**

* ✅ **Sistema de moedas**: ganha coins abrindo packs
* ✅ **Loja de packs**: compra packs com coins
* ✅ **Packs bloqueados por nível**: desbloqueia novos sets com progresso
* ✅ **Auto-save** após compras (quando configurado)

### 🎰 **Minigames**

* ✅ **Slot Machine**: apostas e multiplicadores
* ✅ **Blackjack**: sistema completo de cartas

### 💾 **Sistema de Save**

* ✅ **3 Slots de Save** independentes
* ✅ **Persistência completa**: coins, coleção, inventário, XP, achievements e definições

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
│   ├── widgets.py                  # Widgets de UI (CardWidget, SlotMachineWidget, ToolTip)
│   ├── shop.py                     # Sistema de loja de packs
│   ├── collection_viewer.py        # Visualizador de coleção com filtros
│   ├── profile_ui.py               # Interface de perfil do jogador
│   └── minigames/
│       ├── __init__.py
│       └── blackjack_gui.py        # Minigame Blackjack completo
│
├── widgets/                        # 🔧 Componentes auxiliares
│   ├── __init__.py
│   ├── card_widget.py              # CardWidget alternativo (compatibilidade)
│   ├── slot_machine.py             # Slot Machine (versão modular, se usada)
│   ├── tooltip.py                  # Tooltip (versão modular, se usada)
│   └── utils/
│       ├── __init__.py
│       ├── image_loader.py         # Loader de imagens por JSON (ATIVO)
│       ├── settings_manager.py     # Sistema de save/load (3 slots)
│       └── card_name_utils.py      # Utilitários de normalização de nomes (se aplicável)
│
├── data/                           # 📊 Dados do jogo
│   ├── packs.json                  # Definições de todos os packs
│   └── packs_info.json             # Informações detalhadas (release, theme decks)
│
├── assets/                         # 🖼️ Recursos gráficos
│   ├── images/                     # Pastas com imagens físicas das cartas
│   │   ├── base_set/
│   │   ├── base_set_2/
│   │   ├── expansion_pack_image/
│   │   ├── fossil/
│   │   ├── jungle/
│   │   ├── jungle_jp/
│   │   └── mystery_of_the_fossils/
│   │
│   ├── base_pack_set.json
│   ├── base_set_2.json
│   ├── expansion_pack.json
│   ├── fossil.json
│   ├── jungle.json
│   ├── mystery_of_the_fossils.json
│   └── pokemon_jungle.json
│
└── saves/                          # 💾 Sistema de saves
    ├── settings.json               # Configurações gerais
    ├── save_slot_1.json            # Slot 1
    ├── save_slot_2.json            # Slot 2
    └── save_slot_3.json            # Slot 3
```

---

## 🖼️ Sistema de Imagens (modo real)

### ✅ Como funciona

* Cada pack tem um ficheiro JSON em `assets/` com o nome do **pack_slug**:

  * Ex.: `assets/base_pack_set.json`, `assets/fossil.json`, etc.
* Cada JSON mapeia:

  * **Nome da carta** → **path da imagem**
  * Ex.: `"Alakazam": "assets/images/base_set/baseset-0.jpeg"`
* O loader (`widgets/utils/image_loader.py`) lê o JSON do pack atual e carrega a imagem certa.
* As imagens são redimensionadas com **fit (contain)** para **caberem dentro do slot**, sem cortar.

### 📌 Requisitos

* As imagens devem existir nos paths referidos pelos JSON (normalmente dentro de `assets/images/...`).
* Recomenda-se ter **Pillow** instalado (PIL) para melhor suporte de imagens:

  * `pip install pillow`

---

## 📦 Sistema de Packs

### **Packs Disponíveis**

| Pack                   | Região | Cartas | Preço    | Nível Mínimo |
| ---------------------- | ------ | ------ | -------- | ------------ |
| Base Pack Set          | ENG    | 102    | 50 coins | 1            |
| Expansion Pack         | JP     | 102    | 50 coins | 1            |
| Jungle                 | ENG    | 32     | 25 coins | 1            |
| Pokémon Jungle         | JP     | 48     | 25 coins | 1            |
| Fossil                 | ENG    | 47     | 25 coins | 1            |
| Mystery of the Fossils | JP     | 48     | 25 coins | 1            |
| Base Set 2             | ENG    | 130    | 50 coins | 5            |

---

## 🟦 Sistema de Raridades

| Raridade  | Recompensa | XP    | Cor          |
| --------- | ---------- | ----- | ------------ |
| Common    | 5 coins    | 5 XP  | Cinza        |
| Uncommon  | 10 coins   | 10 XP | Verde        |
| Rare      | 25 coins   | 25 XP | Azul         |
| Rare Holo | 50 coins   | 50 XP | Roxo/Dourado |
| Energy    | 1 coin     | 2 XP  | Amarelo      |

---

## ▶️ Como executar

1. Instala dependências (recomendado):

* `pip install pillow`

2. Executa:

* `python main.py`

---

## 🧩 Notas rápidas

* O jogo guarda progresso em `saves/` (slots + definições).
* Se uma imagem não existir ou o JSON não tiver a carta, o jogo usa fallback visual (texto/placeholder) sem crash.
