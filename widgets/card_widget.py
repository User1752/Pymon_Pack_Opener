import tkinter as tk
from core.config import COLORS, RARITY_COLORS, CARD_WIDTH, CARD_HEIGHT
from ui.theme import Colors, Fonts, get_font, get_rarity_color
from .tooltip import ToolTip


class CardWidget(tk.Frame):
    """Exibe uma única carta com imagem ou texto alternativo."""

    def __init__(self, parent, pokemon, reward: int, graphics_mode: str = "simple",
                 image_loader=None, normalize_rarity_func=None):
        super().__init__(parent, bg=COLORS["accent"], relief=tk.RAISED, bd=2)
        self.pokemon = pokemon
        self.reward = reward
        self.graphics_mode = graphics_mode
        self.image_loader = image_loader
        self.normalize_rarity = normalize_rarity_func or (lambda r: r)

        # Cor da borda da carta baseada na raridade
        rarity_color = RARITY_COLORS.get(
            self.normalize_rarity(pokemon.rarity),
            COLORS["common"]
        )

        self.config(bg=rarity_color, width=CARD_WIDTH, height=CARD_HEIGHT)
        self.pack_propagate(False)

        self._build_ui(rarity_color)
        self._attach_tooltip()

    def _build_ui(self, rarity_color):
        """Constrói UI da carta (imagem ou texto)."""
        inner = tk.Frame(self, bg=COLORS["accent"])
        inner.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        img = None
        if self.image_loader and self.graphics_mode == "real":
            # Espaço útil dentro do widget (tira padding e uma margem extra)
            target_w = max(int(CARD_WIDTH) - 20, 50)
            target_h = max(int(CARD_HEIGHT) - 20, 50)

            # Tenta chamar com target_size; se o loader antigo não aceitar, faz fallback
            try:
                img = self.image_loader(self.pokemon, target_size=(target_w, target_h))
            except TypeError:
                img = self.image_loader(self.pokemon)

        if img:
            self._display_image(inner, img)
        else:
            self._display_text(inner, rarity_color)

    def _display_image(self, parent, img):
        """Exibe imagem da carta."""
        lbl = tk.Label(parent, image=img, bg=COLORS["accent"])
        lbl.pack(fill=tk.BOTH, expand=True)
        lbl._img_ref = img  

    def _display_text(self, parent, rarity_color):
        """Exibe informação da carta como texto."""
        frame = tk.Frame(parent, bg=COLORS["accent"])
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        if self.pokemon.number:
            tk.Label(
                frame, text=f"#{self.pokemon.number}",
                font=("Arial", 10, "bold"),
                bg=COLORS["accent"], fg=rarity_color
            ).pack()

        tk.Label(
            frame,
            text=str(self.pokemon.name) if hasattr(self.pokemon, "name") else "Unknown",
            font=("Arial", 11, "bold"),
            bg=COLORS["accent"], fg=COLORS["fg"],
            wraplength=210
        ).pack(pady=3)

        tk.Label(
            frame, text=f"Type: {self.pokemon.type}",
            font=("Arial", 9),
            bg=COLORS["accent"], fg=COLORS["fg"]
        ).pack()

        rarity_txt = self.normalize_rarity(self.pokemon.rarity) or "Unknown"
        tk.Label(
            frame, text=rarity_txt.upper(),
            font=("Arial", 8, "bold"),
            bg=COLORS["accent"], fg=rarity_color
        ).pack(pady=3)

        tk.Label(
            frame, text=f"+{self.reward} coins",
            font=("Arial", 10, "bold"),
            bg=COLORS["accent"], fg=COLORS["success"]
        ).pack(pady=3)

    def _attach_tooltip(self):
        """Adiciona tooltip ao passar rato."""
        def tooltip_text():
            rarity_txt = self.normalize_rarity(self.pokemon.rarity) or "Unknown"
            return f"{self.pokemon.name}\nRarity: {rarity_txt.title()}\nReward: +{self.reward} coins"

        ToolTip(self, tooltip_text)
