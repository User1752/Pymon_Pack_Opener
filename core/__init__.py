"""
Módulo de lógica central do jogo.

Este módulo fornece os componentes principais do jogo incluindo:
- Gestão de Packs e Pokémon
- Sistema de carteira
- Sistema de perfil e conquistas
- Constantes de configuração (cores, paletas, níveis de desbloqueio)
- Sistema de raridade e recompensas
"""

# Entidades do jogo e carregamento de dados
from .game import (
    Pack, Wallet, Pokemon,
    load_packs_from_json, load_pack_info,
    normalize_rarity, reward_for_rarity, rarity_bucket,
    PACKS_FILE, PACKS_INFO_FILE
)

# Constantes de configuração
from .config import COLORS, RARITY_COLORS, PALETTES, PACK_UNLOCK_LEVELS

# Sistema de perfil e progressão
from .profile import ProfileManager, get_xp_reward, calculate_level_from_xp, get_achievement_display_name

__all__ = [
    # Entidades do jogo
    'Pack', 'Wallet', 'Pokemon',
    # Funções de carregamento de dados
    'load_packs_from_json', 'load_pack_info',
    # Sistema de raridade e recompensas
    'normalize_rarity', 'reward_for_rarity', 'rarity_bucket',
    # Caminhos dos ficheiros de dados
    'PACKS_FILE', 'PACKS_INFO_FILE',
    # Configuração
    'COLORS', 'RARITY_COLORS', 'PALETTES', 'PACK_UNLOCK_LEVELS',
    # Gestão de perfil
    'ProfileManager', 'get_xp_reward', 'calculate_level_from_xp', 'get_achievement_display_name'
]
