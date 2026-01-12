"""
Custom Widgets - Pymon TCG
Widgets personalizados para a interface.
"""
import tkinter as tk
import random
import time

# Usa ui.theme em vez de core.config
from ui.theme import Colors, Fonts, Spacing, get_font, get_rarity_color

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


class ToolTip:
    """Tooltip simples que segue o rato perto de um widget."""

    def __init__(self, widget, text_func, delay=400):
        self.widget = widget
        self.text_func = text_func
        self.delay = delay
        self._after_id = None
        self.tipwindow = None

        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)
        widget.bind("<Motion>", self._on_motion)

    def _on_enter(self, event=None):
        self._schedule()

    def _on_leave(self, event=None):
        self._unschedule()
        self._hidetip()

    def _on_motion(self, event):
        if self.tipwindow:
            x = event.x_root + 20
            y = event.y_root + 10
            self.tipwindow.geometry(f"+{x}+{y}")

    def _schedule(self):
        self._unschedule()
        self._after_id = self.widget.after(self.delay, self._showtip)

    def _unschedule(self):
        if self._after_id is not None:
            self.widget.after_cancel(self._after_id)
            self._after_id = None

    def _showtip(self):
        if self.tipwindow or not self.widget.winfo_viewable():
            return
        text = self.text_func() if callable(self.text_func) else str(self.text_func)
        if not text:
            return
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.overrideredirect(True)
        tw.attributes("-topmost", True)
        label = tk.Label(
            tw, text=text, justify=tk.LEFT,
            bg="#222222", fg="#ffffff",
            relief=tk.SOLID, borderwidth=1, font=("Arial", 9)
        )
        label.pack(ipadx=4, ipady=2)
        try:
            x = self.widget.winfo_pointerx() + 20
            y = self.widget.winfo_pointery() + 10
            tw.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


class CardWidget(tk.Frame):
    """Exibe uma única carta."""
    
    def __init__(self, parent, pokemon, reward: int, 
                 graphics_mode: str = "simple", 
                 image_loader=None,
                 normalize_rarity_func=None):
        super().__init__(parent, bg=Colors.BG_CARD, relief=tk.RAISED, bd=2)
        self.pokemon = pokemon
        self.reward = reward
        self.graphics_mode = graphics_mode
        self.image_loader = image_loader
        
        # Obtém cor da raridade - USA HELPER
        if normalize_rarity_func:
            norm_rarity = normalize_rarity_func(pokemon.rarity)
        else:
            norm_rarity = pokemon.rarity.lower() if hasattr(pokemon, 'rarity') else "common"
        
        # USA HELPER do tema
        rarity_color = get_rarity_color(norm_rarity)
        
        # Tamanho da carta: 220x300
        self.config(bg=rarity_color, width=220, height=300)
        self.pack_propagate(False)

        # Frame interno
        inner = tk.Frame(self, bg=Colors.BG_CARD)
        inner.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tenta carregar imagem
        img = image_loader(pokemon) if image_loader and graphics_mode == "real" else None

        if img:
            # Apenas imagem
            lbl = tk.Label(inner, image=img, bg=Colors.BG_CARD)
            lbl.pack(expand=True)
            lbl._img_ref = img
        else:
            # Apenas texto
            text_frame = tk.Frame(inner, bg=Colors.BG_CARD)
            text_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            if hasattr(pokemon, 'number') and pokemon.number:
                tk.Label(
                    text_frame, text=f"#{pokemon.number}",
                    font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
                    bg=Colors.BG_CARD, fg=rarity_color
                ).pack()
            
            name = str(pokemon.name) if hasattr(pokemon, 'name') else "Unknown"
            tk.Label(
                text_frame, text=name,
                font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
                bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY,
                wraplength=210
            ).pack(pady=3)
            
            if hasattr(pokemon, 'type'):
                tk.Label(
                    text_frame, text=f"Type: {pokemon.type}",
                    font=get_font(Fonts.SIZE_TINY),
                    bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY
                ).pack()
            
            tk.Label(
                text_frame, text=norm_rarity.upper(),
                font=get_font(Fonts.SIZE_TINY, Fonts.BOLD),
                bg=Colors.BG_CARD, fg=rarity_color
            ).pack(pady=3)
            
            tk.Label(
                text_frame, text=f"+{reward} coins",
                font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
                bg=Colors.BG_CARD, fg=Colors.SUCCESS
            ).pack(pady=3)

        # Tooltip
        def tooltip_text():
            return f"{pokemon.name}\nRarity: {norm_rarity.title()}\nReward: +{reward} coins"
        ToolTip(self, tooltip_text)


class SlotMachineWidget(tk.Frame):
    """Widget de jogo slot machine."""
    
    def __init__(self, parent, wallet, on_close):
        super().__init__(parent, bg=Colors.BG_CARD, relief=tk.RAISED, bd=2)
        self.wallet = wallet
        self.on_close = on_close
        self.bet = 100
        self.reels = [[], [], []]
        self.spinning = False
        self.root = None
        
        self.symbols = ["7", "🔴", "⭐", "🌙", "🔔", "🔁"]
        self.payouts = {
            ("7", "7", "7"): 1000,
            ("🔴", "🔴", "🔴"): 500,
            ("⭐", "⭐", "⭐"): 250,
            ("🌙", "🌙", "🌙"): 200,
            ("🔔", "🔔", "🔔"): 100,
            ("🔁", "🔁", "🔁"): "replay",
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """Cria UI da slot machine."""
        # Título
        tk.Label(
            self, text="🎰 SLOT MACHINE 🎰",
            font=get_font(Fonts.SIZE_SUBHEADING, Fonts.BOLD),
            bg=Colors.BG_CARD, fg=Colors.WARNING
        ).pack(pady=10)
        
        # Saldo
        self.balance_lbl = tk.Label(
            self, text=f"Balance: {self.wallet.coins} coins",
            font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
            bg=Colors.BG_CARD, fg=Colors.SUCCESS
        )
        self.balance_lbl.pack()
        
        # Legenda de pagamentos
        tk.Label(
            self,
            text="7-7-7=1000 | 🔴🔴🔴=500 | ⭐⭐⭐=250 | 🌙🌙🌙=200 | 🔔🔔🔔=100 | 🔁🔁🔁=REPLAY",
            font=get_font(Fonts.SIZE_TINY),
            bg=Colors.BG_CARD,
            fg=Colors.TEXT_SECONDARY
        ).pack(pady=5)
        
        # Rolos
        reels_frame = tk.Frame(self, bg=Colors.BG_CARD)
        reels_frame.pack(pady=20)
        
        self.reel_labels = []
        for _ in range(3):
            reel = tk.Label(
                reels_frame, text="?",
                font=("Arial", 80, "bold"),
                bg=Colors.BG_DARKER, fg=Colors.WARNING,
                relief=tk.SUNKEN, bd=3,
                width=2, height=1
            )
            reel.pack(side=tk.LEFT, padx=10)
            self.reel_labels.append(reel)
        
        # Info
        self.info_lbl = tk.Label(
            self, text=f"Bet: {self.bet} coins | Click SPIN to play!",
            font=get_font(Fonts.SIZE_SMALL),
            bg=Colors.BG_CARD,
            fg=Colors.TEXT_PRIMARY
        )
        self.info_lbl.pack(pady=10)
        
        # Resultado
        self.result_lbl = tk.Label(
            self, text="",
            font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
            bg=Colors.BG_CARD,
            fg=Colors.SUCCESS
        )
        self.result_lbl.pack(pady=5)
        
        # Botões
        btn_frame = tk.Frame(self, bg=Colors.BG_CARD)
        btn_frame.pack(pady=15)
        
        self.spin_btn = tk.Button(
            btn_frame, text="🎯 SPIN",
            font=get_font(Fonts.SIZE_NORMAL, Fonts.BOLD),
            bg=Colors.WARNING, fg=Colors.TEXT_DARK,
            padx=30, pady=15, command=self.spin,
            relief=tk.RAISED, bd=3
        )
        self.spin_btn.pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame, text="❌ Close",
            font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
            bg=Colors.DANGER, fg=Colors.TEXT_BUTTON,
            padx=20, pady=10, command=self.on_close
        ).pack(side=tk.LEFT, padx=10)
    
    def spin(self):
        """Executa rotação."""
        if self.wallet.coins < self.bet:
            self.result_lbl.config(text="❌ Insufficient coins!", fg=Colors.DANGER)
            return
        
        if self.spinning:
            return
        
        self.spinning = True
        self.spin_btn.config(state=tk.DISABLED)
        self.wallet.coins -= self.bet
        self.balance_lbl.config(text=f"Balance: {self.wallet.coins} coins")
        self.result_lbl.config(text="")
        
        self.animate_spin()
    
    def animate_spin(self):
        """Anima rotação."""
        if not self.root:
            return
        
        for _ in range(20):
            for reel_idx in range(3):
                self.reel_labels[reel_idx].config(text=random.choice(self.symbols))
            self.root.update()
            time.sleep(0.08)
        
        # Resultado final
        self.reels = [random.choice(self.symbols) for _ in range(3)]
        for i, sym in enumerate(self.reels):
            self.reel_labels[i].config(text=sym)
        
        if self.root:
            self.root.update()
        time.sleep(0.3)
        
        self.check_result()
    
    def check_result(self):
        """Verifica resultado e atribui prémios."""
        result_key = tuple(self.reels)
        payout = self.payouts.get(result_key)
        
        if payout == "replay":
            self.result_lbl.config(text="🔁 REPLAY! Spin again for free!", fg=Colors.SUCCESS)
            self.wallet.coins += self.bet
            self.balance_lbl.config(text=f"Balance: {self.wallet.coins} coins")
        elif payout:
            self.wallet.coins += payout
            self.balance_lbl.config(text=f"Balance: {self.wallet.coins} coins")
            self.result_lbl.config(text=f"🎉 WIN! +{payout} coins!", fg=Colors.SUCCESS)
        else:
            self.result_lbl.config(text="❌ No match. Try again!", fg=Colors.DANGER)
        
        self.spinning = False
        self.spin_btn.config(state=tk.NORMAL)
