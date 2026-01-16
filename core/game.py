"""
Módulo de Lógica do Jogo - Pymon TCG Pack Opener
Mecânicas centrais do jogo: Pokemon, Packs, Carteira, sistema de raridade.
"""
import json
import random
import os
from typing import List, Dict, Optional

# Caminhos dos ficheiros de dados (relativos à pasta Pymon_Pack_Opener)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKS_FILE = os.path.join(BASE_DIR, "data", "packs.json")
PACKS_INFO_FILE = os.path.join(BASE_DIR, "data", "packs_info.json")


class Pokemon:
    """Representa uma carta Pokemon."""
    
    def __init__(self, name: str, rarity: str, card_type: str = "Pokemon", number: int = 0):
        self.name = name
        self.rarity = rarity
        self.type = card_type
        self.number = number
    
    def __repr__(self):
        return f"Pokemon({self.name}, {self.rarity})"


class Pack:
    """Representa um booster pack com cartas."""
    
    def __init__(self, name: str, price: int, language: str, pokemons: List[Pokemon]):
        self.name = name
        self.price = price
        self.language = language
        self.pokemons = pokemons
    
    def open(self) -> List[Pokemon]:
        """Abre pack e retorna cartas aleatórias baseadas em distribuição de raridade."""
        cards = []
        
        # Separa cartas por raridade
        common = [p for p in self.pokemons if "common" in p.rarity.lower()]
        uncommon = [p for p in self.pokemons if "uncommon" in p.rarity.lower()]
        rare = [p for p in self.pokemons if "rare" in p.rarity.lower()]
        energy = [p for p in self.pokemons if "energy" in p.rarity.lower()]
        
        # Distribuição padrão (6 common, 3 uncommon, 1 rare, 1 energy)
        if common:
            cards.extend(random.choices(common, k=min(6, len(common))))
        if uncommon:
            cards.extend(random.choices(uncommon, k=min(3, len(uncommon))))
        if rare:
            cards.append(random.choice(rare))
        if energy:
            cards.append(random.choice(energy))
        
        return cards
    
    def __repr__(self):
        return f"Pack({self.name}, {self.price} coins, {len(self.pokemons)} cards)"


class Wallet:
    """Gere moedas do jogador."""
    
    def __init__(self, coins: int = 0):
        self.coins = coins
    
    def add_coins(self, amount: int):
        """Adiciona moedas à carteira."""
        self.coins += amount
    
    def spend_coins(self, amount: int) -> bool:
        """Gasta moedas se disponível."""
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False
    
    def __repr__(self):
        return f"Wallet({self.coins} coins)"


# Ordem de raridades
RARITY_ORDER = ["common", "uncommon", "rare", "rare holo", "energy", "t", "other"]

RARITY_LABEL = {
    "common": "Common",
    "uncommon": "Uncommon",
    "rare": "Rare",
    "rare holo": "Rare Holo",
    "energy": "Energy",
    "t": "Trainer",
    "other": "Other",
}


def normalize_rarity(r: Optional[str]) -> Optional[str]:
    """Normaliza string de raridade."""
    if not r: 
        return None
    r = r.strip().lower()
    
    if "energy" in r: 
        return "energy"
    if "holo" in r: 
        return "rare holo"
    if r in ("t","trainer","trainers"): 
        return "t"
    if r in ("common","uncommon","rare","rare holo"): 
        return r
    
    return r


def reward_for_rarity(rarity: str) -> int:
    """Retorna recompensa de moedas baseada na raridade da carta."""
    norm = normalize_rarity(rarity)
    
    if "promotional" in norm or "promo" in norm:
        return 100
    elif "rare holo" in norm or "holo" in norm:
        return 50
    elif "rare" in norm:
        return 30
    elif "uncommon" in norm:
        return 10
    elif "common" in norm:
        return 5
    elif "energy" in norm:
        return 1
    else:
        return 5


def rarity_bucket(rarity: str) -> str:
    """Agrupa raridades em categorias para organização de coleção."""
    norm = normalize_rarity(rarity)
    
    if "promotional" in norm or "promo" in norm:
        return "promotional"
    elif "rare holo" in norm or "holo" in norm:
        return "rare holo"
    elif "rare" in norm:
        return "rare"
    elif "uncommon" in norm:
        return "uncommon"
    elif "energy" in norm:
        return "energy"
    else:
        return "common"


def load_packs_from_json(filepath: str) -> List[Pack]:
    """Carrega dados de packs do ficheiro JSON."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        packs = []
        for pack_data in data.get("packs", []):
            pokemons = []
            for card in pack_data.get("cards", []):
                pokemon = Pokemon(
                    name=card.get("name", "Unknown"),
                    rarity=card.get("rarity", "Common"),
                    card_type=card.get("type", "Pokemon"),
                    number=card.get("no", 0)
                )
                pokemons.append(pokemon)
            
            pack = Pack(
                name=pack_data.get("name", "Unknown Pack"),
                price=pack_data.get("price", 50),
                language=pack_data.get("language", "ENG"),
                pokemons=pokemons
            )
            packs.append(pack)
        
        print(f"LOADER: Loaded {len(packs)} packs from {filepath}")
        return packs
    
    except FileNotFoundError:
        print(f"ERROR: File not found - {filepath}")
        return []
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {filepath} - {e}")
        return []
    except Exception as e:
        print(f"ERROR: Failed to load packs - {e}")
        return []


def load_pack_info(filepath: str) -> Dict:
    """Carrega informação de metadata dos packs do ficheiro JSON."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"LOADER: Loaded pack info from {filepath}")
        return data
    except FileNotFoundError:
        print(f"WARNING: Pack info file not found - {filepath}")
        return {}
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in pack info - {e}")
        return {}
    except Exception as e:
        print(f"ERROR: Failed to load pack info - {e}")
        return {}
