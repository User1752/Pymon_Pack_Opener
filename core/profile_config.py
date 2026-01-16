ACHIEVEMENTS = [
    {"id": "first_pack", "name": "First Pack", "desc": "Open your first pack."},
    {"id": "ten_packs", "name": "Pack Collector", "desc": "Open 10 packs."},
    {"id": "rare_holo", "name": "Shiny!", "desc": "Pull a rare holo card."},
]

def _build_levels(max_level: int = 100) -> dict:
    """Gera tabela de XP até max_level com custo de escala suave."""
    levels = {}
    for lvl in range(1, max_level + 1):
        if lvl == 1:
            xp_needed = 0
        else:
            # Crescimento exponencial suave: base 120 por nível com aumento de 4%
            xp_needed = int(120 * (1.04 ** (lvl - 2)) * (lvl - 1))
        levels[lvl] = {"xp_needed": xp_needed}
    # Recompensa especial no nível 5
    if 5 in levels:
        levels[5]["reward"] = "unlock_set_jungle"
    return levels

XP_LEVELS = _build_levels()

AVATARS = [
    "Trainer",
    "Pikachu",
    "Charizard",
    "Squirtle",
    "Eevee",
]

REWARDS = {
    "unlock_set_jungle": {
        "name": "Unlock Jungle Set",
        "description": "Gain access to Jungle packs at level 5.",
    }
   
}

def next_level_info(level: int) -> dict:
    """Retorna informação do próximo nível ou dicionário vazio se no máximo."""
    if level >= max(XP_LEVELS.keys()):
        return {}
    return XP_LEVELS.get(level + 1, {})