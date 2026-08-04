# Dimensões das cartas
CARD_WIDTH = 220
CARD_HEIGHT = 300

# Dimensões das imagens para carregamento/visualização
IMAGE_WIDTH = 210
IMAGE_HEIGHT = 290

# Esquema de cores (pode ser alterado pela seleção de paleta)
COLORS = {
    "bg": "#1a1a2e",
    "fg": "#eaeaea",
    "accent": "#16213e",
    "rare": "#FFD700",
    "uncommon": "#9370DB",
    "common": "#C0C0C0",
    "energy": "#00CED1",
    "button": "#0f3460",
    "button_hover": "#16213e",
    "success": "#00FF41",
    "warning": "#FF6B6B"
}

RARITY_COLORS = {
    "common": "#9E9E9E",
    "uncommon": "#4CAF50",
    "rare": "#2196F3",
    "rare holo": "#9C27B0",
    "energy": "#FFEB3B"
}

# Paletas de temas
PALETTES = {
    "Green": {
        "bg": "#0c7a4c",
        "fg": "#e7f7ec",
        "accent": "#095c3a",
        "button": "#0f8b55",
        "button_hover": "#0b7045",
        "success": "#2ef27d",
        "warning": "#ffb347",
        "energy": "#00c7c7",
    },
    "Dark": {
        "bg": "#0b0b0b",
        "fg": "#f1f1f1",
        "accent": "#1a1a1a",
        "button": "#2a2a2a",
        "button_hover": "#3a3a3a",
        "success": "#57e389",
        "warning": "#ff6b6b",
        "energy": "#8ecae6",
    },
    "Sapphire": {
        "bg": "#0b234a",
        "fg": "#e7f2ff",
        "accent": "#11386e",
        "button": "#0d2b55",
        "button_hover": "#16427a",
        "success": "#3dd5ff",
        "warning": "#ffb347",
        "energy": "#6be2ff",
    },
    "Ruby": {
        "bg": "#2d0b0b",
        "fg": "#fbe9e9",
        "accent": "#4b0f0f",
        "button": "#6b1313",
        "button_hover": "#8b1b1b",
        "success": "#ffcc66",
        "warning": "#ff6b6b",
        "energy": "#ff8a80",
    },
}

# Níveis de desbloqueio dos packs
PACK_UNLOCK_LEVELS = {
    "base pack set": 1,
    "base set 2": 1,
    "expansion pack": 1,  # Equivalente JP ao Base Pack Set
    "jungle": 3,
    "pokémon jungle": 5,  # Jungle JP requer nível 5
    "fossil": 5,
    "mystery of the fossils": 5,  # Fossil JP
    "special promos & exclusives (1999–2000)": 99,  # Efetivamente desativado
}
