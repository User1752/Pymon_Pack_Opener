import tkinter as tk
from tkinter import messagebox

# Import relativo dentro da mesma pasta
from .blackjack import BlackjackGame

# Import do tema (caminho relativo)
from ui.theme import Colors, Fonts, Spacing, get_font


class BlackjackGUI:
    """Wrapper de GUI do jogo Blackjack."""
    
    @staticmethod
    def create(content_frame, wallet, colors, root, update_stats_callback, show_welcome_callback, show_notifications_getter=None):
        """
        Cria e configura UI do jogo Blackjack.
        
        Args:
            content_frame: Frame tkinter pai
            wallet: Objeto Wallet com moedas
            colors: Dicionário de esquema de cores
            root: Janela principal tkinter root
            update_stats_callback: Função para atualizar exibição de estatísticas
            show_welcome_callback: Função para voltar ao ecrã inicial
            show_notifications_getter: Função que retorna se notificações estão ativadas
        """
        
        # Getter padrão se não fornecido
        if show_notifications_getter is None:
            show_notifications_getter = lambda: True
        
        # Estado do jogo
        game = BlackjackGame(num_decks=6)
        
        # Cabeçalho moderno
        header = tk.Frame(content_frame, bg="#0f1419")
        header.pack(fill=tk.X, padx=40, pady=30)
        
        tk.Label(
            header,
            text="♠♥ BLACKJACK ♦♣",
            font=("Segoe UI", 28, "bold"),
            bg="#0f1419",
            fg="#ff2e63"
        ).pack(anchor=tk.W)
        
        tk.Label(
            header,
            text="Beat the dealer! Get as close to 21 as possible without going over",
            font=("Segoe UI", 14),
            bg="#0f1419",
            fg="#a0a0a0"
        ).pack(anchor=tk.W, pady=(5, 0))
        
        # Card moderno de Blackjack
        blackjack_card = tk.Frame(content_frame, bg="#1a1f3a")
        blackjack_card.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 20))
        
        # Borda superior
        tk.Frame(blackjack_card, bg="#ff2e63", height=4).pack(fill=tk.X)
        
        # Conteúdo
        game_content = tk.Frame(blackjack_card, bg="#1a1f3a")
        game_content.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Secção de aposta
        bet_frame = tk.Frame(game_content, bg="#1a1f3a")
        bet_frame.pack(pady=(0, 20))
        
        tk.Label(
            bet_frame,
            text="Your Bet:",
            font=("Segoe UI", 14, "bold"),
            bg="#1a1f3a",
            fg="#ffffff"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        bet_entry = tk.Entry(bet_frame, font=("Segoe UI", 14), width=10, bg="#0a0e27", fg="#ffffff", insertbackground="#ffffff")
        bet_entry.pack(side=tk.LEFT, padx=5)
        bet_entry.insert(0, "10")
        
        # Botões de aposta rápida
        quick_bet_frame = tk.Frame(bet_frame, bg="#1a1f3a")
        quick_bet_frame.pack(side=tk.LEFT, padx=15)
        
        def set_bet(amount):
            """Define quantidade de aposta na entrada."""
            bet_entry.delete(0, tk.END)
            if amount == "max":
                bet_entry.insert(0, str(wallet.coins))
            else:
                bet_entry.insert(0, str(amount))
        
        # Botões de aposta rápida (10, 50, 100, MAX)
        for bet_amt in [10, 50, 100]:
            tk.Button(
                quick_bet_frame,
                text=f"{bet_amt}",
                font=("Segoe UI", 10, "bold"),
                bg="#00d4ff",
                fg="#0a0e27",
                activebackground="#00b8d4",
                command=lambda amt=bet_amt: set_bet(amt),
                padx=12,
                pady=6,
                relief=tk.FLAT,
                bd=0,
                cursor="hand2"
            ).pack(side=tk.LEFT, padx=3)
        
        # Botão MAX (all-in)
        tk.Button(
            quick_bet_frame,
            text="MAX",
            font=("Segoe UI", 10, "bold"),
            bg="#ffd700",
            fg="#0a0e27",
            activebackground="#e6c200",
            command=lambda: set_bet("max"),
            padx=12,
            pady=6,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=3)
        
        # Exibição do jogo (área de cartas)
        cards_area = tk.Frame(game_content, bg="#0a0e27", relief=tk.FLAT, bd=0)
        cards_area.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Secção do dealer
        dealer_frame = tk.Frame(cards_area, bg="#0a0e27")
        dealer_frame.pack(fill=tk.X, pady=20, padx=30)
        
        tk.Label(
            dealer_frame,
            text="DEALER'S HAND",
            font=("Segoe UI", 13, "bold"),
            bg="#0a0e27",
            fg="#ff2e63"
        ).pack(anchor=tk.W)
        
        dealer_cards_label = tk.Label(
            dealer_frame,
            text="",
            font=("Segoe UI", 20, "bold"),
            bg="#0a0e27",
            fg="#ffffff"
        )
        dealer_cards_label.pack(anchor=tk.W, pady=(8, 4))
        
        dealer_value_label = tk.Label(
            dealer_frame,
            text="",
            font=("Segoe UI", 12),
            bg="#0a0e27",
            fg="#a0a0a0"
        )
        dealer_value_label.pack(anchor=tk.W)
        
        # Secção do jogador
        player_frame = tk.Frame(cards_area, bg="#0a0e27")
        player_frame.pack(fill=tk.X, pady=20, padx=30)
        
        tk.Label(
            player_frame,
            text="YOUR HAND",
            font=("Segoe UI", 13, "bold"),
            bg="#0a0e27",
            fg="#4caf50"
        ).pack(anchor=tk.W)
        
        player_cards_label = tk.Label(
            player_frame,
            text="",
            font=("Segoe UI", 20, "bold"),
            bg="#0a0e27",
            fg="#ffffff"
        )
        player_cards_label.pack(anchor=tk.W, pady=(8, 4))
        
        player_value_label = tk.Label(
            player_frame,
            text="",
            font=("Segoe UI", 12),
            bg="#0a0e27",
            fg="#a0a0a0"
        )
        player_value_label.pack(anchor=tk.W)
        
        # Label de resultado
        result_label = tk.Label(
            game_content,
            text="",
            font=("Segoe UI", 18, "bold"),
            bg="#1a1f3a",
            fg="#ffd700"
        )
        result_label.pack(pady=15)
        
        # Botões de ação
        action_frame = tk.Frame(game_content, bg="#1a1f3a")
        action_frame.pack(pady=10)
        
        def update_display(hide_dealer_card=False):
            """Atualiza exibição de cartas."""
            # Cartas do dealer
            if hide_dealer_card and len(game.dealer_hand.cards) > 0:
                dealer_text = f"{game.dealer_hand.cards[0]} [?]"
                dealer_value = ""
            else:
                dealer_text = str(game.dealer_hand)
                dealer_value = f"Value: {game.dealer_hand.get_value()}"
            
            dealer_cards_label.config(text=dealer_text)
            dealer_value_label.config(text=dealer_value)
            
            # Cartas do jogador
            player_cards_label.config(text=str(game.player_hand))
            player_value_label.config(text=f"Value: {game.player_hand.get_value()}")
        
        def start_game(event=None):
            """Inicializa novo jogo com aposta do jogador."""
            try:
                bet = int(bet_entry.get())
                if bet <= 0:
                    tk.messagebox.showerror("Invalid Bet", "Bet must be positive!")
                    return
                if bet > wallet.coins:
                    tk.messagebox.showerror("Insufficient Coins", f"You only have {wallet.coins} coins!")
                    return
                
                # Deduz aposta e atualiza imediatamente
                wallet.coins -= bet
                update_stats_callback()
                
                game.bet = bet
                
                # Reinicia e distribui
                game.reset()
                game.bet = bet
                game.deal_initial_cards()
                
                # Atualiza exibição
                update_display(hide_dealer_card=True)
                result_label.config(text="")
                
                # Desativa entrada de aposta durante o jogo
                bet_entry.config(state=tk.DISABLED)
                for child in quick_bet_frame.winfo_children():
                    child.config(state=tk.DISABLED)
                
                # Ativa botões de ação
                hit_btn.config(state=tk.NORMAL)
                stand_btn.config(state=tk.NORMAL)
                start_btn.config(state=tk.DISABLED)
                play_again_btn.config(state=tk.DISABLED)
                
                # Verifica blackjack
                if game.player_hand.is_blackjack():
                    if game.dealer_hand.is_blackjack():
                        result_label.config(text="Push! Both have Blackjack!", fg="#ffd700")
                        wallet.coins += bet
                    else:
                        result_label.config(text="🎉 Blackjack! You win!", fg="#4caf50")
                        wallet.coins += int(bet * 2.5)
                    
                    update_display(hide_dealer_card=False)
                    game.game_over = True
                    hit_btn.config(state=tk.DISABLED)
                    stand_btn.config(state=tk.DISABLED)
                    start_btn.config(state=tk.NORMAL)
                    play_again_btn.config(state=tk.NORMAL)
                    
                    # Reativa entrada de aposta
                    bet_entry.config(state=tk.NORMAL)
                    for child in quick_bet_frame.winfo_children():
                        child.config(state=tk.NORMAL)
                    
                    update_stats_callback()
                
            except ValueError:
                tk.messagebox.showerror("Invalid Bet", "Please enter a valid number!")
        
        def hit():
            """Jogador pede uma carta."""
            if not game.game_over:
                result = game.player_hit()
                update_display(hide_dealer_card=True)
                
                if result == "bust":
                    result_label.config(text="Bust! You lose.", fg="#ff4757")
                    update_display(hide_dealer_card=False)
                    hit_btn.config(state=tk.DISABLED)
                    stand_btn.config(state=tk.DISABLED)
                    start_btn.config(state=tk.NORMAL)
                    play_again_btn.config(state=tk.NORMAL)
                    
                    # Reativa entrada de aposta
                    bet_entry.config(state=tk.NORMAL)
                    for child in quick_bet_frame.winfo_children():
                        child.config(state=tk.NORMAL)
                    
                    update_stats_callback()
        
        def stand():
            """Jogador para, dealer joga."""
            if not game.game_over:
                winner = game.player_stand()
                update_display(hide_dealer_card=False)
                
                if winner == "player":
                    result_label.config(text="You win! 🎉", fg="#4caf50")
                    wallet.coins += game.bet * 2
                elif winner == "dealer":
                    result_label.config(text="Dealer wins.", fg="#ff4757")
                else:
                    result_label.config(text="Push! It's a tie.", fg="#ffd700")
                    wallet.coins += game.bet
                
                hit_btn.config(state=tk.DISABLED)
                stand_btn.config(state=tk.DISABLED)
                start_btn.config(state=tk.NORMAL)
                play_again_btn.config(state=tk.NORMAL)
                
                # Reativa entrada de aposta
                bet_entry.config(state=tk.NORMAL)
                for child in quick_bet_frame.winfo_children():
                    child.config(state=tk.NORMAL)
                
                update_stats_callback()
        
        # Botões
        start_btn = tk.Button(
            action_frame,
            text="Deal Cards",
            font=("Segoe UI", 12, "bold"),
            bg="#4caf50",
            fg="#ffffff",
            activebackground="#45a049",
            command=start_game,
            padx=25,
            pady=12,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2"
        )
        start_btn.pack(side=tk.LEFT, padx=5)
        
        hit_btn = tk.Button(
            action_frame,
            text="Hit",
            font=("Segoe UI", 12, "bold"),
            bg="#00d4ff",
            fg="#0a0e27",
            activebackground="#00b8d4",
            command=hit,
            padx=25,
            pady=12,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            state=tk.DISABLED
        )
        hit_btn.pack(side=tk.LEFT, padx=5)
        
        stand_btn = tk.Button(
            action_frame,
            text="Stand",
            font=("Segoe UI", 12, "bold"),
            bg="#00d4ff",
            fg="#0a0e27",
            activebackground="#00b8d4",
            command=stand,
            padx=25,
            pady=12,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            state=tk.DISABLED
        )
        stand_btn.pack(side=tk.LEFT, padx=5)
        
        # Botão Jogar Novamente
        play_again_btn = tk.Button(
            action_frame,
            text="Play Again",
            font=("Segoe UI", 12, "bold"),
            bg="#ffd700",
            fg="#0a0e27",
            activebackground="#e6c200",
            command=start_game,
            padx=25,
            pady=12,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            state=tk.DISABLED
        )
        play_again_btn.pack(side=tk.LEFT, padx=5)
        
        # Vincula tecla Enter para iniciar jogo
        bet_entry.bind("<Return>", start_game)
        
        # Botão voltar
        tk.Button(
            content_frame,
            text="BACK TO HOME",
            font=("Segoe UI", 13, "bold"),
            bg="#ff4757",
            fg="#ffffff",
            activebackground="#ff1744",
            command=show_welcome_callback,
            padx=35,
            pady=14,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2"
        ).pack(pady=(10, 20))


if __name__ == "__main__":
    print("This module provides Blackjack GUI integration.")
    print("Import BlackjackGUI and use .create() to display the game.")
