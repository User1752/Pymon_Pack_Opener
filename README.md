# Pymon Pack Opener

Interactive booster pack opening simulator for Pokemon and Yu-Gi-Oh! TCG with collection system, progression, and achievements.

## Features

- Pack opening with random card generation
- Collection viewer and card management
- Coin system and shop
- Level progression and XP system
- 25+ unlockable achievements
- Multiple user profiles
- Pokemon and Yu-Gi-Oh! support

## Quick Start

```bash
# Install dependencies
pip install Pillow

# Run the game
python main.py
```

## Project Structure

```
core/           - Game logic and mechanics
ui/             - User interface components
widgets/        - Custom widgets and utilities
data/           - Pack definitions and card data
assets/         - Images and resources
saves/          - User profiles and settings
```

## Technologies

- Python 3.8+
- Tkinter for GUI
- JSON for data storage
- PIL/Pillow for images

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/Pymon_Pack_Opener.git
cd Pymon_Pack_Opener
```

2. Install required dependencies:
```bash
pip install Pillow
```

3. Run the application:
```bash
python main.py
```

## Available Packs

### Pokemon TCG
- Base Pack Set
- Base Set 2
- Expansion Pack
- Jungle
- Fossil
- Mystery of the Fossils

### Yu-Gi-Oh! TCG
- Vol.1 (OCG-JP)
- Booster 1 (OCG-JP)
- Vol.2 (OCG-JP)
- Booster 2 (OCG-JP)
- Starter Boxes

## How to Play

1. Select a TCG game (Pokemon or Yu-Gi-Oh!)
2. Choose a booster pack to open
3. Click to open and reveal random cards
4. Collect cards and earn coins based on rarity
5. Use coins to buy more packs
6. Unlock achievements and level up

## Game Features

**Rarity System**: Common (60%), Uncommon (20%), Rare (15%), Super Rare (3%), Ultra Rare (2%)

**Leveling**: Gain XP from opening packs, unlock new sets at higher levels

**Achievements**: 25+ achievements to unlock with special rewards

**Collections**: View and manage all your collected cards

**Profiles**: Save up to 3 different game profiles

## Debug Mode

To enable infinite packs for testing, set in `main.py`:
```python
self.debug_mode = True
```

## Contributing

Contributions are welcome! Feel free to:
- Report bugs and issues
- Suggest new features
- Add more TCG sets
- Improve the interface

## Acknowledgments

- YGOProDeck for Yu-Gi-Oh! card data
- Pokemon TCG community databases
- Fandom Wiki for card galleries

## License

MIT License