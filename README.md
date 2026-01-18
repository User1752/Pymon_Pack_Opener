# Pymon TCG Pack Opener

A polished Pokémon TCG pack-opening simulator with a complete system for collection tracking, XP/levels, achievements, and minigames.

---

## Features

### Pack System

* Realistic pack opening with animations and visual effects
* Multi-region support: English (ENG) and Japanese (JP) sets
* Available sets: Base Pack Set, Base Set 2, Jungle, Fossil, Expansion Pack (JP), Pokémon Jungle (JP), Mystery of the Fossils (JP)
* Inventory system: keep packs to open later
* Real card images (real/simple display modes)

### Collection & Progress

* Collection viewer with filters by rarity and set
* Pack completion statistics
* XP/Level progression with visual feedback
* 25+ unlockable achievements
* Player profile with detailed stats

### Economy & Shop

* Coin system: earn coins by opening packs
* Pack shop: buy packs with coins
* Packs locked by level: unlock new sets as you progress
* Auto-save after purchases (when enabled)

### Minigames

* Slot Machine: bets and multipliers
* Blackjack: full card system

### Save System

* 3 independent save slots
* Full persistence: coins, collection, inventory, XP, achievements, and settings

---

## Project Structure

```
Pymon_Pack_Opener/
│
├── main.py                         # Main entry point
│
├── core/                           # Game logic
│   ├── __init__.py
│   ├── game.py                     # Pack, Wallet, Pokemon, Card classes
│   ├── config.py                   # Settings, colors, unlock levels
│   └── profile.py                  # XP/Level/Achievements system
│
├── ui/                             # User interface
│   ├── __init__.py
│   ├── theme.py                    # Theme system (centralized helpers)
│   ├── widgets.py                  # UI widgets (CardWidget, SlotMachineWidget, ToolTip)
│   ├── shop.py                     # Pack shop
│   ├── collection_viewer.py        # Collection viewer with filters
│   ├── profile_ui.py               # Player profile UI
│   └── minigames/
│       ├── __init__.py
│       └── blackjack_gui.py        # Blackjack minigame
│
├── widgets/                        # Auxiliary components
│   ├── __init__.py
│   ├── card_widget.py              # Alternative CardWidget (compatibility)
│   ├── slot_machine.py             # Slot Machine (modular version, if used)
│   ├── tooltip.py                  # Tooltip (modular version, if used)
│   └── utils/
│       ├── __init__.py
│       ├── image_loader.py         # JSON-based image loader (ACTIVE)
│       ├── settings_manager.py     # Save/load system (3 slots)
│       └── card_name_utils.py      # Card name normalization utilities (if applicable)
│
├── data/                           # Game data
│   ├── packs.json                  # Pack definitions
│   └── packs_info.json             # Detailed pack info (release, theme decks)
│
├── assets/                         # Assets
│   ├── images/                     # Physical card image folders
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
└── saves/                          # Saves
    ├── settings.json               # General settings
    ├── save_slot_1.json            # Slot 1
    ├── save_slot_2.json            # Slot 2
    └── save_slot_3.json            # Slot 3
```

---

## Real Images System

### How it works

* Each set has a JSON file in `assets/` named with its **pack_slug** (e.g., `assets/base_pack_set.json`, `assets/fossil.json`).
* Each JSON maps:

  * **Card name** → **image path**
  * Example: `"Alakazam": "assets/images/base_set/baseset-0.jpeg"`
* The loader (`widgets/utils/image_loader.py`) reads the JSON for the current pack and loads the correct image.
* Images are resized using **fit (contain)** so they **always fit inside the card slot** without cropping.

### Requirements

* Image files must exist at the paths referenced in the JSON (usually under `assets/images/...`).
* Recommended: install Pillow for best image support:

  * `pip install pillow`

---

## Packs

### Available Packs

| Pack                   | Region | Cards | Price    | Minimum Level |
| ---------------------- | ------ | ----- | -------- | ------------- |
| Base Pack Set          | ENG    | 102   | 50 coins | 1             |
| Expansion Pack         | JP     | 102   | 50 coins | 1             |
| Jungle                 | ENG    | 32    | 25 coins | 1             |
| Pokémon Jungle         | JP     | 48    | 25 coins | 1             |
| Fossil                 | ENG    | 47    | 25 coins | 1             |
| Mystery of the Fossils | JP     | 48    | 25 coins | 1             |
| Base Set 2             | ENG    | 130   | 50 coins | 5             |

---

## Rarities

| Rarity    | Reward   | XP    | Color       |
| --------- | -------- | ----- | ----------- |
| Common    | 5 coins  | 5 XP  | Gray        |
| Uncommon  | 10 coins | 10 XP | Green       |
| Rare      | 25 coins | 25 XP | Blue        |
| Rare Holo | 50 coins | 50 XP | Purple/Gold |
| Energy    | 1 coin   | 2 XP  | Yellow      |

---

## How to Run

1. Install dependencies (recommended):

* `pip install pillow`

2. Run:

* `python main.py`

---

## Notes

* Progress is saved in `saves/` (slots + settings).
* If an image is missing or the JSON does not include a card, the UI falls back to a placeholder/text display without crashing.
