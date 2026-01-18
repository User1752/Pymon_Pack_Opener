"""
Custom Widgets - Pymon TCG
Widgets personalizados para a interface.
"""
import tkinter as tk
import random
import time

# Usa ui.theme em vez de core.config
from ui.theme import Colors, Fonts, Spacing, Sizes, get_font, get_rarity_color

# Importa PIL para redimensionamento
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  PIL not available - images will not be resized")


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
    """Widget para exibir carta individual."""
    
    def __init__(self, parent, card, reward=0, graphics_mode="real", image_loader=None, normalize_rarity_func=None):
        super().__init__(parent, bg=Colors.BG_CARD, width=220, height=360)
        
        self.pack_propagate(False)
        self.card = card
        self.reward = reward
        self.graphics_mode = graphics_mode
        self.image_loader = image_loader
        self.normalize_rarity = normalize_rarity_func or (lambda r: r)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura interface da carta."""
        # Borda superior colorida por raridade
        rarity_color = get_rarity_color(self.card.rarity)
        tk.Frame(self, bg=rarity_color, height=Sizes.BORDER_MEDIUM).pack(fill=tk.X)
        
        content = tk.Frame(self, bg=Colors.BG_CARD)
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Nome da carta
        tk.Label(
            content,
            text=self.card.name.upper(),
            font=get_font(Fonts.SIZE_MINI, Fonts.BOLD),
            bg=Colors.BG_CARD,
            fg=Colors.TEXT_PRIMARY,
            wraplength=180
        ).pack(pady=(0, 6))
        
        # ==================== IMAGEM DA CARTA (SEM RESIZE ADICIONAL) ==================== #
        if self.graphics_mode == "real" and self.image_loader:
            try:
                card_image = self.image_loader(self.card, target_size=(180, 215))
                
                if card_image:
                    # USA DIRETAMENTE - NÃO redimensiona novamente
                    img_label = tk.Label(content, image=card_image, bg=Colors.BG_CARD)
                    img_label.image = card_image  # Mantém referência
                    img_label.pack(pady=(6, 4))
                else:
                    self._display_text_mode(content)
                    
            except Exception as e:
                print(f"❌ Error loading image for {self.card.name}: {e}")
                import traceback
                traceback.print_exc()
                self._display_text_mode(content)
        else:
            self._display_text_mode(content)
        
        # Raridade
        tk.Label(
            content,
            text=self.normalize_rarity(self.card.rarity).upper(),
            font=get_font(Fonts.SIZE_MINI, Fonts.BOLD),
            bg=Colors.BG_CARD,
            fg=rarity_color
        ).pack(pady=(4, 2))
        
        # Recompensa
        if self.reward > 0:
            tk.Label(
                content,
                text=f"+{self.reward} coins",
                font=get_font(Fonts.SIZE_MINI, Fonts.BOLD),
                bg=Colors.BG_CARD,
                fg=Colors.SUCCESS
            ).pack()
    
    def _display_text_mode(self, parent):
        """Exibe modo texto quando imagem não está disponível."""
        text_frame = tk.Frame(parent, bg=Colors.BG_DARKER, width=180, height=200)
        text_frame.pack(pady=6)
        text_frame.pack_propagate(False)
        
        tk.Label(
            text_frame,
            text="🎴",
            font=get_font(Fonts.SIZE_HUGE),
            bg=Colors.BG_DARKER,
            fg=get_rarity_color(self.card.rarity)
        ).pack(expand=True)


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
        ).pack(pady=6)
        
        # Saldo
        self.balance_lbl = tk.Label(
            self, text=f"Balance: {self.wallet.coins} coins",
            font=get_font(Fonts.SIZE_MINI, Fonts.BOLD),
            bg=Colors.BG_CARD, fg=Colors.SUCCESS
        )
        self.balance_lbl.pack()
        
        # Legenda de pagamentos
        tk.Label(
            self,
            text="7-7-7=1000 | 🔴🔴🔴=500 | ⭐⭐⭐=250 | 🌙🌙🌙=200 | 🔔🔔🔔=100 | 🔁🔁🔁=REPLAY",
            font=get_font(Fonts.SIZE_MINI, Fonts.BOLD),
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
            font=get_font(Fonts.SIZE_MINI, Fonts.BOLD),
            bg=Colors.BG_CARD,
            fg=Colors.TEXT_PRIMARY
        )
        self.info_lbl.pack(pady=6)
        
        # Resultado
        self.result_lbl = tk.Label(
            self, text="",
            font=get_font(Fonts.SIZE_MINI, Fonts.BOLD),
            bg=Colors.BG_CARD,
            fg=Colors.SUCCESS
        )
        self.result_lbl.pack(pady=5)
        
        # Botões
        btn_frame = tk.Frame(self, bg=Colors.BG_CARD)
        btn_frame.pack(pady=15)
        
        self.spin_btn = tk.Button(
            btn_frame, text="🎯 SPIN",
            font=get_font(Fonts.SIZE_MINI, Fonts.BOLD),
            bg=Colors.WARNING, fg=Colors.TEXT_DARK,
            padx=30, pady=15, command=self.spin,
            relief=tk.RAISED, bd=3
        )
        self.spin_btn.pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame, text="❌ Close",
            font=get_font(Fonts.SIZE_MINI, Fonts.BOLD),
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
