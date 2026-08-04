import tkinter as tk
from tkinter import messagebox
import random
import time
from core.config import COLORS
from ui.theme import Colors, Fonts, get_font, create_button, bind_hover_effect


class SlotMachineWidget(tk.Frame):
    """Widget de jogo slot machine."""
    
    def __init__(self, parent, wallet, on_close):
        super().__init__(parent, bg=COLORS["accent"], relief=tk.RAISED, bd=2)
        self.wallet = wallet
        self.on_close = on_close
        self.bet = 100
        self.spinning = False
        self.root = None  # Definido pelo pai
        
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
            font=("Arial", 18, "bold"),
            bg=COLORS["accent"], fg=COLORS["rare"]
        ).pack(pady=10)
        
        # Saldo
        self.balance_lbl = tk.Label(
            self, text=f"Balance: {self.wallet.coins} coins",
            font=("Arial", 12, "bold"),
            bg=COLORS["accent"], fg=COLORS["success"]
        )
        self.balance_lbl.pack()
        
        # Legenda
        tk.Label(
            self,
            text="7-7-7 = 1000  |  🔴🔴🔴 = 500  |  ⭐⭐⭐ = 250  |  🌙🌙🌙 = 200  |  🔔🔔🔔 = 100  |  🔁🔁🔁 = REPLAY",
            font=("Arial", 8),
            bg=COLORS["accent"], fg=COLORS["fg"]
        ).pack(pady=10)
        
        # Rolos
        reels_frame = tk.Frame(self, bg=COLORS["accent"], height=200)
        reels_frame.pack(pady=20, fill=tk.BOTH, expand=True)
        reels_frame.pack_propagate(False)
        
        self.reel_labels = []
        for i in range(3):
            border = tk.Frame(reels_frame, bg=COLORS["rare"], width=180, height=180)
            border.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=20, pady=10)
            border.pack_propagate(False)
            
            reel = tk.Label(
                border, text="?", font=("Arial", 80, "bold"),
                bg=COLORS["button"], fg=COLORS["rare"],
                relief=tk.SUNKEN, bd=3, anchor="center"
            )
            reel.pack(fill=tk.BOTH, expand=True)
            self.reel_labels.append(reel)
        
        # Info & Resultado
        self.info_lbl = tk.Label(
            self, text=f"Bet: {self.bet} coins | Click SPIN to play!",
            font=("Arial", 10), bg=COLORS["accent"], fg=COLORS["fg"]
        ).pack(pady=10)
        
        self.result_lbl = tk.Label(
            self, text="", font=("Arial", 12, "bold"),
            bg=COLORS["accent"], fg=COLORS["success"]
        )
        self.result_lbl.pack(pady=5)
        
        # Botões
        btn_frame = tk.Frame(self, bg=COLORS["accent"])
        btn_frame.pack(pady=15)
        
        self.spin_btn = tk.Button(
            btn_frame, text="🎯 SPIN", font=("Arial", 14, "bold"),
            bg="#FFD700", fg="#000000", padx=30, pady=15,
            command=self.spin, relief=tk.RAISED, bd=3
        )
        self.spin_btn.pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame, text="❌ Close", font=("Arial", 12, "bold"),
            bg=COLORS["button"], fg=COLORS["warning"],
            padx=20, pady=10, command=self.on_close
        ).pack(side=tk.LEFT, padx=10)
    
    def spin(self):
        """Executa rotação."""
        if self.wallet.coins < self.bet:
            self.result_lbl.config(text="❌ Insufficient coins!", fg=COLORS["warning"])
            return
        
        if self.spinning:
            return
        
        self.spinning = True
        self.spin_btn.config(state=tk.DISABLED)
        self.wallet.coins -= self.bet
        self.balance_lbl.config(text=f"Balance: {self.wallet.coins} coins")
        self.result_lbl.config(text="")
        
        self._animate_spin()
    
    def _animate_spin(self):
        """Anima rolos."""
        if not self.root:
            return
        
        for _ in range(20):
            for reel in self.reel_labels:
                reel.config(text=random.choice(self.symbols))
            self.root.update()
            time.sleep(0.08)
        
        # Resultado final
        result = [random.choice(self.symbols) for _ in range(3)]
        for reel, sym in zip(self.reel_labels, result):
            reel.config(text=sym)
        
        if self.root:
            self.root.update()
        time.sleep(0.3)
        
        self._check_result(tuple(result))
    
    def _check_result(self, result):
        """Verifica pagamento."""
        payout = self.payouts.get(result)
        
        if payout == "replay":
            self.result_lbl.config(text="🔁 REPLAY! Spin again for free!", fg=COLORS["success"])
            self.wallet.coins += self.bet
            self.balance_lbl.config(text=f"Balance: {self.wallet.coins} coins")
        elif payout:
            self.wallet.coins += payout
            self.balance_lbl.config(text=f"Balance: {self.wallet.coins} coins")
            self.result_lbl.config(text=f"🎉 WIN! +{payout} coins!", fg=COLORS["success"])
        else:
            self.result_lbl.config(text="❌ No match. Try again!", fg=COLORS["warning"])
        
        self.spinning = False
        self.spin_btn.config(state=tk.NORMAL)
