"""
🎮 Pokémon TCG Battle - Full Game GUI
Complete battle interface using Tkinter with visible hand cards.
"""

import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, simpledialog
import sys
import os

# Add parent directory to path for imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Import the game module
import tcgf

# Colors
BG_COLOR = "#1a1a1a"
SURFACE_COLOR = "#262828"
TEXT_COLOR = "#f5f5f5"
ACCENT_COLOR = "#32b8c6"
PLAYER_COLOR = "#00bfff"
CPU_COLOR = "#ff6b6b"
ENERGY_COLOR = "#ffd700"
HP_GREEN = "#32cd32"
HP_YELLOW = "#ffd700"
HP_RED = "#dc143c"
BUTTON_COLOR = "#333333"
BUTTON_HOVER = "#555555"
CARD_BG = "#2d2d2d"
CARD_SELECTED = "#4a90e2"

class PokemonTCGGame:
    """Main game class with Tkinter interface."""
    
    def __init__(self, root):
        """Initialize the game."""
        self.root = root
        self.root.title("🎮 Pokémon TCG Battle")
        
        # Window setup - maximized but not fullscreen
        self.root.state('zoomed')  # Windows
        try:
            self.root.attributes('-zoomed', True)  # Linux
        except:
            pass
        
        self.root.configure(bg=BG_COLOR)
        
        # Bind ESC to exit
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        
        # Fonts
        self.title_font = tkfont.Font(family="Arial", size=28, weight="bold")
        self.large_font = tkfont.Font(family="Arial", size=20, weight="bold")
        self.normal_font = tkfont.Font(family="Arial", size=14)
        self.small_font = tkfont.Font(family="Arial", size=12)
        self.card_font = tkfont.Font(family="Arial", size=11)
        
        # Game state
        self.state = "DECK_SELECTION"
        self.decks = tcgf.load_decks(tcgf.DECKS_FILE)
        self.selected_decks = {"player": None, "cpu": None}
        self.player = None
        self.cpu = None
        self.current_player = None
        self.turn_count = 0
        self.selected_card = None
        self.first_turn = True
        
        # Main container
        self.main_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Show deck selection
        self.show_deck_selection()
    
    def clear_frame(self):
        """Clear the main frame."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def show_deck_selection(self):
        """Show deck selection screen."""
        self.clear_frame()
        
        # Title
        title = tk.Label(
            self.main_frame,
            text="🎮 POKÉMON TCG BATTLE",
            font=self.title_font,
            bg=BG_COLOR,
            fg=ENERGY_COLOR
        )
        title.pack(pady=30)
        
        # Selection status
        self.status_label = tk.Label(
            self.main_frame,
            text=self.get_selection_status(),
            font=self.normal_font,
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        self.status_label.pack(pady=10)
        
        # Deck selection frame
        decks_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
        decks_frame.pack(pady=20, expand=True)
        
        # Player decks (left)
        player_frame = tk.Frame(decks_frame, bg=BG_COLOR)
        player_frame.pack(side=tk.LEFT, padx=50)
        
        tk.Label(
            player_frame,
            text="Choose YOUR Deck:",
            font=self.large_font,
            bg=BG_COLOR,
            fg=PLAYER_COLOR
        ).pack(pady=10)
        
        for deck in self.decks:
            btn = tk.Button(
                player_frame,
                text=f"🎮 {deck['name']}",
                font=self.normal_font,
                bg=BUTTON_COLOR,
                fg=TEXT_COLOR,
                activebackground=BUTTON_HOVER,
                activeforeground=TEXT_COLOR,
                width=25,
                height=2,
                relief=tk.RAISED,
                bd=2,
                command=lambda d=deck: self.select_deck("player", d)
            )
            btn.pack(pady=8)
        
        # CPU decks (right)
        cpu_frame = tk.Frame(decks_frame, bg=BG_COLOR)
        cpu_frame.pack(side=tk.RIGHT, padx=50)
        
        tk.Label(
            cpu_frame,
            text="Choose OPPONENT'S Deck:",
            font=self.large_font,
            bg=BG_COLOR,
            fg=CPU_COLOR
        ).pack(pady=10)
        
        for deck in self.decks:
            btn = tk.Button(
                cpu_frame,
                text=f"🤖 {deck['name']}",
                font=self.normal_font,
                bg=BUTTON_COLOR,
                fg=TEXT_COLOR,
                activebackground=BUTTON_HOVER,
                activeforeground=TEXT_COLOR,
                width=25,
                height=2,
                relief=tk.RAISED,
                bd=2,
                command=lambda d=deck: self.select_deck("cpu", d)
            )
            btn.pack(pady=8)
        
        # Start button
        start_btn = tk.Button(
            self.main_frame,
            text="▶️ START BATTLE",
            font=self.large_font,
            bg=ACCENT_COLOR,
            fg=BG_COLOR,
            activebackground="#29a3b0",
            activeforeground=BG_COLOR,
            width=20,
            height=2,
            relief=tk.RAISED,
            bd=3,
            command=self.start_battle
        )
        start_btn.pack(pady=30)
    
    def get_selection_status(self):
        """Get selection status text."""
        p_deck = self.selected_decks["player"]
        c_deck = self.selected_decks["cpu"]
        return f"Player: {p_deck['name'] if p_deck else 'Not selected'} | CPU: {c_deck['name'] if c_deck else 'Not selected'}"
    
    def select_deck(self, player_type, deck):
        """Select a deck for player or CPU."""
        self.selected_decks[player_type] = deck
        self.status_label.config(text=self.get_selection_status())
    
    def start_battle(self):
        """Start the battle."""
        if not self.selected_decks["player"] or not self.selected_decks["cpu"]:
            messagebox.showwarning("Warning", "⚠️ Please select both decks!")
            return
        
        # Initialize players
        self.player = tcgf.setup_player("Player", self.selected_decks["player"])
        self.cpu = tcgf.setup_player("CPU", self.selected_decks["cpu"])
        self.current_player = self.player
        self.turn_count = 1
        self.first_turn = True
        self.state = "BATTLE"
        
        # Show battle screen
        self.show_battle_screen()
    
    def show_battle_screen(self):
        """Show the battle screen."""
        self.clear_frame()
        
        # Create scrollable main container
        main_canvas = tk.Canvas(self.main_frame, bg=BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg=BG_COLOR)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # === TOP SECTION (CPU) ===
        top_frame = tk.Frame(scrollable_frame, bg=BG_COLOR)
        top_frame.pack(fill=tk.X, pady=10, padx=20)
        
        tk.Label(
            top_frame,
            text="🤖 CPU POKÉMON",
            font=self.large_font,
            bg=BG_COLOR,
            fg=CPU_COLOR
        ).pack()
        
        self.cpu_card_frame = tk.Frame(top_frame, bg=BG_COLOR)
        self.cpu_card_frame.pack(pady=5)
        
        # CPU bench info
        self.cpu_bench_label = tk.Label(
            top_frame,
            text="",
            font=self.small_font,
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        self.cpu_bench_label.pack()
        
        # === MIDDLE SECTION (Info & Controls) ===
        middle_frame = tk.Frame(scrollable_frame, bg=BG_COLOR)
        middle_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Info bar
        info_bar = tk.Frame(middle_frame, bg=BG_COLOR)
        info_bar.pack(fill=tk.X, pady=5)
        
        self.turn_label = tk.Label(
            info_bar,
            text=f"Turn {self.turn_count}",
            font=self.large_font,
            bg=BG_COLOR,
            fg=ENERGY_COLOR
        )
        self.turn_label.pack()
        
        self.current_player_label = tk.Label(
            info_bar,
            text=self.get_current_player_text(),
            font=self.normal_font,
            bg=BG_COLOR,
            fg=PLAYER_COLOR if self.current_player == self.player else CPU_COLOR
        )
        self.current_player_label.pack()
        
        self.prize_label = tk.Label(
            info_bar,
            text=self.get_prize_text(),
            font=self.normal_font,
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        self.prize_label.pack()
        
        # VS separator
        tk.Label(
            middle_frame,
            text="⚔️ VS ⚔️",
            font=self.large_font,
            bg=BG_COLOR,
            fg=ENERGY_COLOR
        ).pack(pady=5)
        
        # Action buttons
        button_frame = tk.Frame(middle_frame, bg=BG_COLOR)
        button_frame.pack(pady=10)
        
        actions = [
            ("↔️ Retreat", self.retreat),
            ("⚔️ Attack", self.choose_attack),
            ("📦 Switch Bench", self.switch_bench_pokemon),
            ("✓ End Turn", self.end_turn),
        ]
        
        for text, command in actions:
            btn = tk.Button(
                button_frame,
                text=text,
                font=self.normal_font,
                bg=BUTTON_COLOR,
                fg=TEXT_COLOR,
                activebackground=BUTTON_HOVER,
                activeforeground=TEXT_COLOR,
                width=14,
                height=2,
                relief=tk.RAISED,
                bd=2,
                command=command
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Message label
        self.message_label = tk.Label(
            middle_frame,
            text="⚔️ Battle Start! Your turn!",
            font=self.normal_font,
            bg=BG_COLOR,
            fg=ENERGY_COLOR,
            wraplength=800,
            height=3
        )
        self.message_label.pack(pady=10)
        
        # === BOTTOM SECTION (Player) ===
        bottom_frame = tk.Frame(scrollable_frame, bg=BG_COLOR)
        bottom_frame.pack(fill=tk.X, pady=10, padx=20)
        
        tk.Label(
            bottom_frame,
            text="🎮 YOUR POKÉMON",
            font=self.large_font,
            bg=BG_COLOR,
            fg=PLAYER_COLOR
        ).pack()
        
        self.player_card_frame = tk.Frame(bottom_frame, bg=BG_COLOR)
        self.player_card_frame.pack(pady=5)
        
        # Player bench info
        self.player_bench_label = tk.Label(
            bottom_frame,
            text="",
            font=self.small_font,
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        self.player_bench_label.pack()
        
        # === HAND SECTION (FIXED) ===
        hand_section = tk.Frame(scrollable_frame, bg=BG_COLOR)
        hand_section.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)
        
        tk.Label(
            hand_section,
            text="🎴 YOUR HAND (Click cards to play)",
            font=self.large_font,
            bg=BG_COLOR,
            fg=PLAYER_COLOR
        ).pack(pady=(5, 10))
        
        # Hand cards container - DIRECTLY visible, no canvas
        self.hand_frame = tk.Frame(hand_section, bg=BG_COLOR)
        self.hand_frame.pack(fill=tk.BOTH, expand=True)
        
        # Update display
        self.update_battle_display()
    
    def draw_pokemon_card(self, parent_frame, pokemon, energies, show_moves=True):
        """Draw a Pokemon card."""
        if not pokemon:
            tk.Label(
                parent_frame,
                text="No active Pokémon",
                font=self.normal_font,
                bg=SURFACE_COLOR,
                fg=TEXT_COLOR,
                width=35,
                height=10
            ).pack()
            return
        
        # Card frame
        card = tk.Frame(
            parent_frame,
            bg=SURFACE_COLOR,
            relief=tk.RAISED,
            bd=3,
            highlightbackground=ACCENT_COLOR,
            highlightthickness=2
        )
        card.pack(padx=20, pady=5)
        
        # Pokemon name and type
        name_text = f"{pokemon.name} [{pokemon.type}]"
        if hasattr(pokemon, 'stage'):
            name_text += f" - {pokemon.stage.upper()}"
        
        tk.Label(
            card,
            text=name_text,
            font=self.large_font,
            bg=SURFACE_COLOR,
            fg=TEXT_COLOR
        ).pack(pady=3, padx=10)
        
        # HP bar
        hp_frame = tk.Frame(card, bg=SURFACE_COLOR)
        hp_frame.pack(pady=3, padx=10)
        
        hp_percent = pokemon.hp / pokemon.max_hp
        if hp_percent > 0.5:
            hp_color = HP_GREEN
        elif hp_percent > 0.25:
            hp_color = HP_YELLOW
        else:
            hp_color = HP_RED
        
        tk.Label(
            hp_frame,
            text=f"HP: {pokemon.hp}/{pokemon.max_hp}",
            font=self.normal_font,
            bg=hp_color,
            fg=BG_COLOR,
            width=22
        ).pack()
        
        # Energy attached
        if energies:
            energy_text = "⚡ Energy: " + tcgf.format_energy_balls(energies)
            tk.Label(
                card,
                text=energy_text,
                font=self.normal_font,
                bg=SURFACE_COLOR,
                fg=ENERGY_COLOR
            ).pack(pady=2, padx=10)
        
        # Status effects
        if hasattr(pokemon, 'status') and pokemon.status:
            status_icons = {
                "poison": "☠️", "paralyze": "⚡", "sleep": "💤",
                "confuse": "💫", "stiffen": "🛡️"
            }
            status_list = [f"{status_icons.get(eff, '❓')}{eff.upper()}" 
                          for eff, count in pokemon.status.items() if count > 0]
            if status_list:
                status_text = " ".join(status_list)
                tk.Label(
                    card,
                    text=f"Status: {status_text}",
                    font=self.small_font,
                    bg=SURFACE_COLOR,
                    fg="#ffc800"
                ).pack(pady=2, padx=10)
        
        # Weakness and Resistance
        if hasattr(pokemon, 'weakness') and hasattr(pokemon, 'resistance'):
            wr_text = f"Weakness: {pokemon.weakness or 'None'} | Resistance: {pokemon.resistance or 'None'}"
            tk.Label(
                card,
                text=wr_text,
                font=self.small_font,
                bg=SURFACE_COLOR,
                fg=TEXT_COLOR
            ).pack(pady=2, padx=10)
        
        # Moves
        if show_moves and hasattr(pokemon, 'moves') and pokemon.moves:
            moves_frame = tk.Frame(card, bg=SURFACE_COLOR)
            moves_frame.pack(pady=3, padx=10, fill=tk.X)
            
            tk.Label(
                moves_frame,
                text="Attacks:",
                font=self.small_font,
                bg=SURFACE_COLOR,
                fg=ACCENT_COLOR,
                anchor=tk.W
            ).pack(fill=tk.X)
            
            for i, move_data in enumerate(pokemon.moves[:4]):
                mname, cost, base = move_data[0], move_data[1], move_data[2]
                cost_str = tcgf.format_energy_balls(cost)
                move_text = f"  {i+1}. {mname}: {cost_str} → {base} dmg"
                tk.Label(
                    moves_frame,
                    text=move_text,
                    font=self.small_font,
                    bg=SURFACE_COLOR,
                    fg=TEXT_COLOR,
                    anchor=tk.W
                ).pack(fill=tk.X)
        
        # Retreat cost
        if hasattr(pokemon, 'retreat_cost'):
            tk.Label(
                card,
                text=f"Retreat Cost: {pokemon.retreat_cost}⚡",
                font=self.small_font,
                bg=SURFACE_COLOR,
                fg=TEXT_COLOR
            ).pack(pady=3, padx=10)
    
    def draw_hand_card(self, card, index):
        """Draw a card in the hand."""
        # Determine card info
        if isinstance(card, tcgf.PokemonCard):
            card_type = "Pokemon"
            name = card.name
            stage_info = card.stage.upper() if hasattr(card, 'stage') else "BASIC"
            info = f"{stage_info}\nHP:{card.max_hp}"
            color = "#4a7ba7"
        elif isinstance(card, tcgf.EnergyCard):
            card_type = "Energy"
            name = card.type
            info = "⚡"
            color = ENERGY_COLOR
        elif isinstance(card, tcgf.TrainerCard):
            card_type = "Trainer"
            name = card.name
            info = card.subtype if hasattr(card, 'subtype') else "Item"
            color = "#8b4789"
        else:
            card_type = "Card"
            name = str(card)
            info = ""
            color = CARD_BG
        
        # Card frame
        is_selected = (self.selected_card == index)
        card_frame = tk.Frame(
            self.hand_frame,
            bg=CARD_SELECTED if is_selected else CARD_BG,
            relief=tk.RAISED,
            bd=3 if is_selected else 2,
            highlightbackground=ACCENT_COLOR if is_selected else TEXT_COLOR,
            highlightthickness=2,
            width=130,
            height=170
        )
        card_frame.grid(row=0, column=index, padx=5, pady=5, sticky="nsew")
        card_frame.grid_propagate(False)
        
        # Make clickable
        def on_click(event=None):
            self.select_hand_card(index)
        
        card_frame.bind("<Button-1>", on_click)
        
        # Card content
        content_frame = tk.Frame(card_frame, bg=CARD_BG)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        content_frame.bind("<Button-1>", on_click)
        
        # Type label
        type_label = tk.Label(
            content_frame,
            text=card_type,
            font=self.small_font,
            bg=color,
            fg=BG_COLOR
        )
        type_label.pack(fill=tk.X)
        type_label.bind("<Button-1>", on_click)
        
        # Name
        name_label = tk.Label(
            content_frame,
            text=name[:18],
            font=self.card_font,
            bg=CARD_BG,
            fg=TEXT_COLOR,
            wraplength=120,
            height=3
        )
        name_label.pack(pady=5)
        name_label.bind("<Button-1>", on_click)
        
        # Info
        info_label = tk.Label(
            content_frame,
            text=info,
            font=self.card_font,
            bg=CARD_BG,
            fg=TEXT_COLOR
        )
        info_label.pack()
        info_label.bind("<Button-1>", on_click)
    
    def select_hand_card(self, index):
        """Select a card from hand."""
        if self.current_player != self.player:
            self.show_message("❌ Not your turn!")
            return
        
        if index >= len(self.player.hand):
            return
        
        self.selected_card = index
        self.update_hand_display()
        
        # Try to play the card
        card = self.player.hand[index]
        
        if isinstance(card, tcgf.PokemonCard):
            self.play_pokemon(index)
        elif isinstance(card, tcgf.EnergyCard):
            self.attach_energy(index)
        elif isinstance(card, tcgf.TrainerCard):
            self.play_trainer(index)
    
    def play_pokemon(self, index):
        """Play a Pokemon card."""
        if index >= len(self.player.hand):
            return
            
        card = self.player.hand[index]
        
        # Check if evolution
        if hasattr(card, 'stage') and card.stage != "basic":
            # Check first turn rule
            if self.first_turn and self.current_player == self.player:
                self.show_message("❌ Cannot evolve on the first turn!")
                return
            
            # Try to evolve
            evolved = self.try_evolution(card)
            if evolved:
                self.player.hand.pop(index)
                self.selected_card = None
                self.update_battle_display()
            return
        
        # Play basic to bench
        if len(self.player.bench) < 5:
            self.player.bench.append(card)
            self.player.hand.pop(index)
            self.selected_card = None
            self.show_message(f"✓ Played {card.name} to bench!")
            self.update_battle_display()
        else:
            self.show_message("❌ Bench is full (max 5 Pokemon)!")
    
    def try_evolution(self, evolution_card):
        """Try to evolve a Pokemon."""
        if not hasattr(evolution_card, 'evolves_from'):
            self.show_message("❌ This card cannot evolve!")
            return False
            
        # Check active Pokemon
        if self.player.active and hasattr(self.player.active, 'name') and evolution_card.evolves_from == self.player.active.name:
            old_hp = self.player.active.hp
            old_energies = self.player.energies.get(self.player.active.name, {})
            
            # Apply evolution
            self.player.active = evolution_card
            self.player.active.hp = min(evolution_card.max_hp, old_hp)
            
            # Transfer energies
            if old_energies:
                if evolution_card.evolves_from in self.player.energies:
                    del self.player.energies[evolution_card.evolves_from]
                self.player.energies[evolution_card.name] = old_energies
            
            # Remove status effects on evolution
            if hasattr(self.player.active, 'status'):
                self.player.active.status = {}
            
            self.show_message(f"✓ Evolved to {evolution_card.name}!")
            return True
        
        # Check bench
        for i, bench_pkmn in enumerate(self.player.bench):
            if hasattr(bench_pkmn, 'name') and evolution_card.evolves_from == bench_pkmn.name:
                old_hp = bench_pkmn.hp
                old_energies = self.player.energies.get(bench_pkmn.name, {})
                
                # Apply evolution
                self.player.bench[i] = evolution_card
                self.player.bench[i].hp = min(evolution_card.max_hp, old_hp)
                
                # Transfer energies
                if old_energies:
                    if bench_pkmn.name in self.player.energies:
                        del self.player.energies[bench_pkmn.name]
                    self.player.energies[evolution_card.name] = old_energies
                
                self.show_message(f"✓ Evolved bench Pokemon to {evolution_card.name}!")
                return True
        
        self.show_message(f"❌ No {evolution_card.evolves_from} found to evolve!")
        return False
    
    def attach_energy(self, index):
        """Attach an energy card."""
        if self.player.attached_this_turn:
            self.show_message("❌ Already attached energy this turn! (Limit: 1 per turn)")
            return
        
        if not self.player.active:
            self.show_message("❌ No active Pokemon to attach energy to!")
            return
        
        if index >= len(self.player.hand):
            return
            
        card = self.player.hand[index]
        pool = self.player.energies.setdefault(self.player.active.name, {})
        pool[card.type] = pool.get(card.type, 0) + 1
        self.player.hand.pop(index)
        self.player.attached_this_turn = True
        self.selected_card = None
        self.show_message(f"✓ Attached {card.type} energy to {self.player.active.name}!")
        self.update_battle_display()
    
    def play_trainer(self, index):
        """Play a trainer card."""
        if index >= len(self.player.hand):
            return
            
        card = self.player.hand[index]
        self.show_message(f"🎴 Trainer cards not fully implemented: {card.name}")
    
    def switch_bench_pokemon(self):
        """Switch active Pokemon with bench Pokemon."""
        if self.current_player != self.player:
            self.show_message("❌ Not your turn!")
            return
        
        if not self.player.bench:
            self.show_message("❌ No Pokemon on bench to switch with!")
            return
        
        if not self.player.active:
            if self.player.bench:
                self.player.active = self.player.bench.pop(0)
                self.show_message(f"✓ {self.player.active.name} is now active!")
                self.update_battle_display()
            return
        
        # Show selection dialog
        options = [f"{i+1}. {p.name} (HP: {p.hp}/{p.max_hp})" for i, p in enumerate(self.player.bench)]
        choice = simpledialog.askinteger(
            "Switch Pokemon",
            "Choose bench Pokemon to switch with:\n" + "\n".join(options),
            minvalue=1,
            maxvalue=len(self.player.bench)
        )
        
        if choice:
            idx = choice - 1
            old_active = self.player.active
            self.player.active = self.player.bench[idx]
            self.player.bench[idx] = old_active
            self.show_message(f"✓ Switched! {self.player.active.name} is now active!")
            self.update_battle_display()
    
    def choose_attack(self):
        """Let player choose which attack to use."""
        if self.current_player != self.player:
            self.show_message("❌ Not your turn!")
            return
        
        if not self.player.active or not self.cpu.active:
            self.show_message("❌ No active Pokemon!")
            return
        
        # Get available attacks
        pool = self.player.energies.get(self.player.active.name, {})
        playable = [(i, mv) for i, mv in enumerate(self.player.active.moves) if tcgf.can_pay(mv[1], pool)]
        
        if not playable:
            self.show_message("❌ No moves available! Need more energy!")
            return
        
        if len(playable) == 1:
            self.attack(playable[0][0])
        else:
            options = [f"{i+1}. {mv[0]} ({tcgf.format_energy_balls(mv[1])}) - {mv[2]} dmg" 
                      for i, mv in playable]
            
            choice = simpledialog.askinteger(
                "Choose Attack",
                "Select attack:\n" + "\n".join(options),
                minvalue=1,
                maxvalue=len(playable)
            )
            
            if choice:
                attack_idx = playable[choice-1][0]
                self.attack(attack_idx)
    
    def attack(self, move_index=None):
        """Perform attack with specified move."""
        if not self.player.active or not self.cpu.active:
            self.show_message("❌ No active Pokemon!")
            return
        
        if move_index is None:
            pool = self.player.energies.get(self.player.active.name, {})
            playable = [i for i, mv in enumerate(self.player.active.moves) if tcgf.can_pay(mv[1], pool)]
            
            if not playable:
                self.show_message("❌ No moves available!")
                return
            
            move_index = playable[0]
        
        result = self.execute_attack(self.player, self.cpu, move_index)
        if result:
            self.update_battle_display()
            
            if not self.cpu.active and not self.cpu.bench:
                self.end_game("win")
                return
            if not self.player.prizes:
                self.end_game("win")
                return
    
    def execute_attack(self, attacker_player, defender_player, move_index):
        """Execute an attack."""
        atk = attacker_player.active
        tgt = defender_player.active
        
        if not atk or not tgt:
            return False
        
        if hasattr(tgt, 'status') and tgt.status.get("stiffen", 0) > 0:
            self.show_message(f"🛡️ {tgt.name} is protected by Stiffen effect!")
            tgt.status["stiffen"] -= 1
            if tgt.status["stiffen"] <= 0:
                tgt.remove_status("stiffen")
            return False
        
        if hasattr(atk, 'status') and atk.status.get("paralyze", 0) > 0:
            self.show_message(f"⚡ {atk.name} is paralyzed and cannot attack!")
            return False
        
        if hasattr(atk, 'status') and atk.status.get("sleep", 0) > 0:
            self.show_message(f"💤 {atk.name} is asleep and cannot attack!")
            return False
        
        mname, cost, base, eff = atk.moves[move_index]
        
        pool = attacker_player.energies.get(atk.name, {})
        effect_ids = eff if isinstance(eff, list) else tcgf.MOVE_DEFAULT_EFFECTS.get(mname.lower(), [])
        for eid in effect_ids:
            tcgf.apply_effect_id(eid, atk, tgt, pool, attacker_player)
        
        dmg = int(base * tcgf.wmult(atk, tgt)) - tcgf.rsub(atk, tgt)
        dmg = max(0, dmg)
        tgt.hp = max(0, tgt.hp - dmg)
        
        weakness_text = ""
        if tcgf.wmult(atk, tgt) == 2:
            weakness_text = " (2x weakness!)"
        elif tcgf.wmult(atk, tgt) == 0.5:
            weakness_text = " (½ resistance)"
        
        self.show_message(f"⚔️ {atk.name} used {mname}! Dealt {dmg} damage{weakness_text}!")
        
        if tgt.hp <= 0:
            defender_player.discard.append(tgt)
            defender_player.active = None
            
            if defender_player.bench:
                defender_player.active = defender_player.bench.pop(0)
                self.show_message(f"💀 KO! {defender_player.active.name} was promoted from bench!")
            
            if attacker_player.prizes:
                prize = attacker_player.prizes.pop()
                attacker_player.hand.append(prize)
                self.show_message(f"🏆 Prize card taken! {len(attacker_player.prizes)} prizes remaining!")
        
        return True
    
    def retreat(self):
        """Retreat Pokemon."""
        if self.current_player != self.player:
            self.show_message("❌ Not your turn!")
            return
        
        if not self.player.bench:
            self.show_message("❌ No Pokemon on bench to retreat to!")
            return
        
        if not self.player.active:
            self.show_message("❌ No active Pokemon to retreat!")
            return
        
        if tcgf.can_retreat(self.player):
            pool = self.player.energies.get(self.player.active.name, {})
            retreat_cost = self.player.active.retreat_cost
            
            energies_removed = 0
            for etype in list(pool.keys()):
                while pool[etype] > 0 and energies_removed < retreat_cost:
                    pool[etype] -= 1
                    energies_removed += 1
                    if pool[etype] == 0:
                        del pool[etype]
                
                if energies_removed >= retreat_cost:
                    break
            
            if tcgf.perform_retreat(self.player, 0):
                self.show_message(f"↔️ Retreated! {self.player.active.name} is now active!")
                self.update_battle_display()
            else:
                self.show_message("❌ Retreat failed!")
        else:
            self.show_message(f"❌ Not enough energy to retreat! Need {self.player.active.retreat_cost} energy.")
    
    def update_hand_display(self):
        """Update the hand display."""
        for widget in self.hand_frame.winfo_children():
            widget.destroy()
        
        if not self.player or not hasattr(self.player, 'hand'):
            return
        
        # Configure grid columns
        for i in range(len(self.player.hand)):
            self.hand_frame.grid_columnconfigure(i, weight=1)
        
        # Draw each card
        for i, card in enumerate(self.player.hand):
            self.draw_hand_card(card, i)
    
    def update_battle_display(self):
        """Update the battle display."""
        for widget in self.cpu_card_frame.winfo_children():
            widget.destroy()
        for widget in self.player_card_frame.winfo_children():
            widget.destroy()
        
        if self.cpu and self.cpu.active:
            cpu_energies = self.cpu.energies.get(self.cpu.active.name, {})
            self.draw_pokemon_card(self.cpu_card_frame, self.cpu.active, cpu_energies, show_moves=False)
        
        if self.player and self.player.active:
            player_energies = self.player.energies.get(self.player.active.name, {})
            self.draw_pokemon_card(self.player_card_frame, self.player.active, player_energies)
        
        if self.cpu:
            cpu_bench = [f"{b.name}({b.hp}HP)" for b in self.cpu.bench]
            self.cpu_bench_label.config(text=f"📦 CPU Bench ({len(self.cpu.bench)}/5): {', '.join(cpu_bench) if cpu_bench else 'Empty'}")
        
        if self.player:
            player_bench = [f"{b.name}({b.hp}HP)" for b in self.player.bench]
            self.player_bench_label.config(text=f"📦 Your Bench ({len(self.player.bench)}/5): {', '.join(player_bench) if player_bench else 'Empty'}")
        
        self.update_hand_display()
        
        self.turn_label.config(text=f"Turn {self.turn_count}")
        self.current_player_label.config(
            text=self.get_current_player_text(),
            fg=PLAYER_COLOR if self.current_player == self.player else CPU_COLOR
        )
        self.prize_label.config(text=self.get_prize_text())
    
    def get_current_player_text(self):
        return "🎮 YOUR TURN" if self.current_player == self.player else "🤖 CPU TURN"
    
    def get_prize_text(self):
        return f"🏆 Prizes — You: {len(self.player.prizes)} | CPU: {len(self.cpu.prizes)}"
    
    def show_message(self, msg):
        self.message_label.config(text=msg)
    
    def end_turn(self):
        """End the current turn."""
        if self.current_player != self.player:
            self.show_message("❌ Not your turn!")
            return
        
        if self.current_player.active and hasattr(self.current_player.active, 'status') and self.current_player.active.status.get("sleep", 0) > 0:
            import random
            if random.choice([True, False]):
                self.current_player.active.remove_status("sleep")
                self.show_message("💤 Your Pokemon woke up!")
            else:
                self.show_message("💤 Your Pokemon is still asleep...")
        
        tcgf.poison_check(self.current_player)
        
        if self.current_player.active and hasattr(self.current_player.active, 'status') and self.current_player.active.status.get("paralyze", 0) > 0:
            self.current_player.active.remove_status("paralyze")
            self.show_message("⚡ Paralysis wore off!")
        
        self.current_player = self.cpu
        self.first_turn = False
        self.update_battle_display()
        self.show_message("🤖 CPU's turn...")
        
        self.root.after(1500, self.cpu_turn)
    
    def cpu_turn(self):
        """Execute CPU turn."""
        try:
            tcgf.draw(self.cpu, 1)
        except RuntimeError:
            self.end_game("win")
            return
        
        if not self.cpu.attached_this_turn and self.cpu.active:
            for i, card in enumerate(self.cpu.hand):
                if isinstance(card, tcgf.EnergyCard):
                    pool = self.cpu.energies.setdefault(self.cpu.active.name, {})
                    pool[card.type] = pool.get(card.type, 0) + 1
                    self.cpu.hand.pop(i)
                    self.cpu.attached_this_turn = True
                    self.show_message(f"🤖 CPU attached {card.type} energy")
                    self.root.after(500, lambda: None)
                    break
        
        for i, card in enumerate(self.cpu.hand):
            if isinstance(card, tcgf.PokemonCard) and hasattr(card, 'stage') and card.stage == "basic" and len(self.cpu.bench) < 5:
                self.cpu.bench.append(card)
                self.cpu.hand.pop(i)
                self.show_message(f"🤖 CPU played {card.name} to bench")
                self.root.after(500, lambda: None)
                break
        
        if self.cpu.active and self.player.active:
            pool = self.cpu.energies.get(self.cpu.active.name, {})
            playable = [i for i, mv in enumerate(self.cpu.active.moves) if tcgf.can_pay(mv[1], pool)]
            
            if playable and self.cpu.can_attack():
                self.execute_attack(self.cpu, self.player, playable[0])
                self.update_battle_display()
                self.root.after(1000, lambda: None)
        
        if not self.player.active and not self.player.bench:
            self.end_game("lose")
            return
        if not self.cpu.prizes:
            self.end_game("lose")
            return
        
        tcgf.poison_check(self.cpu)
        if self.cpu.active and hasattr(self.cpu.active, 'status') and self.cpu.active.status.get("paralyze", 0) > 0:
            self.cpu.active.remove_status("paralyze")
        
        self.current_player = self.player
        self.turn_count += 1
        self.cpu.attached_this_turn = False
        
        try:
            tcgf.draw(self.player, 1)
            self.player.attached_this_turn = False
        except RuntimeError:
            self.end_game("lose")
            return
        
        self.update_battle_display()
        self.show_message("🎮 Your turn! Drew a card.")
    
    def end_game(self, result):
        """End the game."""
        self.state = "GAME_OVER"
        
        if result == "win":
            msg = "🏆 CONGRATULATIONS! YOU WIN! 🏆"
        else:
            msg = "💀 GAME OVER - YOU LOSE 💀"
        
        response = messagebox.askyesno(
            "Game Over",
            f"{msg}\n\nWould you like to play again?"
        )
        
        if response:
            self.restart_game()
        else:
            self.root.destroy()
    
    def restart_game(self):
        """Restart the game."""
        self.state = "DECK_SELECTION"
        self.selected_decks = {"player": None, "cpu": None}
        self.player = None
        self.cpu = None
        self.current_player = None
        self.turn_count = 0
        self.selected_card = None
        self.first_turn = True
        self.show_deck_selection()

def main():
    """Launch the game."""
    root = tk.Tk()
    game = PokemonTCGGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()
