"""
Pymon TCG Pack Opener - Main Entry Point
Open booster packs and collect cards with a beautiful interface.
"""
import tkinter as tk
from tkinter import messagebox
import json
import io
import urllib.request
import os
import sys

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

# Adiciona diretório base ao path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Importações da estrutura modular
from core.game import Pack, Wallet, load_packs_from_json, load_pack_info, normalize_rarity, reward_for_rarity, rarity_bucket
from core.config import COLORS, PALETTES, PACK_UNLOCK_LEVELS
from core.profile import ProfileManager, get_xp_reward, get_achievement_display_name
from ui.theme import (
    Colors, Fonts, Spacing, Sizes,
    get_font, create_header, create_button, create_section_title,
    bind_hover_effect, create_card_with_border, create_progress_bar,
    create_stat_row, get_rarity_color, RarityColors
)
from ui.widgets import CardWidget, SlotMachineWidget
from ui.shop import ShopSystem
from ui.collection_viewer import CollectionViewer
from widgets.utils.image_loader import ImageLoader
from widgets.utils.settings_manager import SettingsManager
from widgets.utils.card_images import CardImageSystem

# Diretórios do sistema
SAVE_DIR = os.path.join(BASE_DIR, "saves")
CARD_IMAGES_DIR = os.path.join(BASE_DIR, "assets", "card_images")
SETTINGS_FILE = os.path.join(SAVE_DIR, "settings.json")
PACKS_FILE = os.path.join(BASE_DIR, "data", "packs.json")
PACKS_INFO_FILE = os.path.join(BASE_DIR, "data", "packs_info.json")


class PackOpenerGUI:
    """Interface principal para simulador de abertura de packs."""

    def __init__(self, root):
        self.root = root
        self.root.title("Pymon TCG Pack Opener")
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.config(bg=Colors.BG_DARK)
        
        # Gestores de recursos
        self.image_loader = ImageLoader(CARD_IMAGES_DIR)
        self.settings_manager = SettingsManager(SAVE_DIR, SETTINGS_FILE)
        self.card_image_system = CardImageSystem(CARD_IMAGES_DIR)
        
        # Cria diretórios necessários
        os.makedirs(SAVE_DIR, exist_ok=True)
        os.makedirs(CARD_IMAGES_DIR, exist_ok=True)
        
        # Carrega dados do jogo
        self.packs = load_packs_from_json(PACKS_FILE)
        self.pack_info = load_pack_info(PACKS_INFO_FILE)
        self.pack_totals = {p.name: len(p.pokemons) for p in self.packs}
        
        # Carrega imagens
        self.image_loader.load_set_image_maps(self.packs)
        self.card_image_system.load_set_image_maps(self.packs)
        
        # Estado do jogo
        self.wallet = Wallet(coins=0)
        self.collection = {}
        self.collection_by_set = {}
        self.packs_opened = 0
        self.location = "ENG"
        self.opened_cards = []
        self.pack_languages = {p.name: p.language.upper() for p in self.packs}
        # On/OFF Debug Mode
        self.debug_mode = False  
        
        # Sistema de inventário de packs
        self.pack_inventory = {
            "Base Pack Set": 5,
            "Base Set 2": 2,
            # Adiciona packs JP para teste
            "Expansion Pack": 3,
            "Pokémon Jungle": 2,
            "Mystery of the Fossils": 2
        }
        
        # Sistema de perfil
        self.profile_manager = ProfileManager()
        self.profile = self.profile_manager.profile
        
        # Configurações de UI
        self.graphics_mode = "real"
        self.current_palette = "Green"
        self.show_notifications = True
        self.collection_filter_defaults = {
            "common": True, "uncommon": True, "rare": True,
            "rare holo": True,
        }
        self.collection_set_filters = {p.name: True for p in self.packs}
        
        self.collection_preview_win = None
        self.collection_preview_label = None
        
        # Carrega configurações salvas
        self._load_and_apply_settings()
        
        # Inicializa sistema de loja
        self.shop_system = ShopSystem(
            parent=None,
            wallet=self.wallet,
            colors=COLORS,
            profile_manager=self.profile_manager,
            update_stats_callback=self.update_stats_labels,
            save_settings_callback=lambda: self._save_settings(SETTINGS_FILE),
            packs=self.packs,
            pack_unlock_checker=self._is_pack_unlocked,
            pack_inventory=self.pack_inventory,  
            get_location_callback=lambda: self.location
        )
        
        # ADICIONA: Callback para salvar o jogo completo
        self.shop_system.save_game_callback = self.save_game
        
        # ADICIONA: Callback para verificar modo debug
        self.shop_system.is_debug_mode = lambda: self.debug_mode
        
        # Inicializa visualizador de coleção
        self.collection_viewer = CollectionViewer(
            self.root,
            lambda: self.collection,
            lambda: self.collection_by_set,
            lambda: self.pack_languages,
            lambda: self.collection_set_filters,
            self.card_image_system
        )
        
        self.setup_ui()

    def _required_level_for_pack(self, pack) -> int:
        """Retorna nível necessário para desbloquear pack."""
        if not pack or not getattr(pack, "name", None):
            return 0
        key = pack.name.lower()
        return PACK_UNLOCK_LEVELS.get(key, 0)

    def _is_pack_unlocked(self, pack) -> bool:
        """Verifica se pack está desbloqueado."""
        if self.debug_mode:
            return True
        lvl = self.profile.get("level", 1) if isinstance(self.profile, dict) else 1
        return lvl >= self._required_level_for_pack(pack)
    
    def _add_pack_to_inventory(self, pack_name: str, quantity: int = 1):
        """Adiciona packs ao inventário."""
        current = self.pack_inventory.get(pack_name, 0)
        self.pack_inventory[pack_name] = current + quantity
        print(f"INVENTORY: Added {quantity}x {pack_name} (total: {self.pack_inventory[pack_name]})")

    def _load_and_apply_settings(self):
        """Carrega e aplica configurações guardadas."""
        settings = self.settings_manager.load_settings()
        if not settings:
            return
        
        # Aplica paleta de cores
        palette_name = settings.get("palette", "Green")
        if palette_name in PALETTES:
            self.current_palette = palette_name
            for key, value in PALETTES[palette_name].items():
                COLORS[key] = value
        
        self.graphics_mode = settings.get("graphics_mode", "real")
        self.show_notifications = settings.get("show_notifications", True)
        
        # Carrega perfil
        if "profile" in settings:
            self.profile_manager = ProfileManager(settings["profile"])
            self.profile = self.profile_manager.profile

    def save_game(self, slot: int, silent: bool = False):
        """Grava estado do jogo."""
        print(f"\n💾 SAVING GAME TO SLOT {slot}")
        
        # ✅ DEBUG DETALHADO DO INVENTÁRIO
        print(f"📦 Pack inventory BEFORE serialization:")
        for pack_name, count in self.pack_inventory.items():
            print(f"   '{pack_name}': {count}")
        
        print(f"💰 Coins: {self.wallet.coins}")
        print(f"📚 Collection keys: {list(self.collection.keys())}")
        print(f"🎒 Packs opened: {self.packs_opened}")
        
        # Normaliza location para salvar
        location_to_save = self.location
        if self.location.startswith("EN"):
            location_to_save = "ENG"
        elif self.location.startswith("JP"):
            location_to_save = "JPN"
        
        # CORRIGIDO: Serializa collection corretamente (converte para dicts puros)
        serialized_collection = {}
        for rarity, cards in self.collection.items():
            serialized_collection[rarity] = dict(cards)  # Converte para dict puro
        
        serialized_collection_by_set = {}
        for set_name, rarities in self.collection_by_set.items():
            serialized_collection_by_set[set_name] = {}
            for rarity, cards in rarities.items():
                serialized_collection_by_set[set_name][rarity] = dict(cards)
        
        data = {
            "coins": self.wallet.coins,
            "collection": serialized_collection,
            "collection_by_set": serialized_collection_by_set,
            "packs_opened": self.packs_opened,
            "location": location_to_save,
            "graphics_mode": self.graphics_mode,
            "palette": self.current_palette,
            "pack_inventory": dict(self.pack_inventory),  # ✅ Copia ATUAL do inventário
            "profile": self.profile_manager.to_dict(),
            "pack_languages": dict(self.pack_languages),
            "collection_set_filters": dict(self.collection_set_filters)
        }
        
        # ✅ DEBUG: Confirma o que vai ser salvo
        print(f"✅ Data prepared for save:")
        print(f"   - Coins: {data['coins']}")
        print(f"   - Pack inventory TO BE SAVED:")
        for pack_name, count in data['pack_inventory'].items():
            print(f"      '{pack_name}': {count}")
        print()
        
        success = self.settings_manager.save_game(slot, data)
        
        if not silent:
            if success:
                messagebox.showinfo("Success", f"Game saved to slot {slot}")
            else:
                messagebox.showerror("Error", f"Failed to save to slot {slot}")
        
        return success

    def load_game(self, slot: int):
        """Carrega estado do jogo."""
        data = self.settings_manager.load_game(slot)
        if not data:
            messagebox.showerror("Error", f"No save found in slot {slot}")
            return
        
        print(f"\n📁 LOADING SAVE FROM SLOT {slot}")
        print(f"Data keys: {list(data.keys())}")
        
        # ✅ CORRIGIDO: Carrega TUDO
        self.wallet.coins = data.get("coins", 0)
        self.packs_opened = data.get("packs_opened", 0)
        
        # ✅ Carrega collection (converte de volta para defaultdict se necessário)
        loaded_collection = data.get("collection", {})
        self.collection = {}
        for rarity, cards in loaded_collection.items():
            self.collection[rarity] = dict(cards)
        
        # ✅ Carrega collection_by_set
        loaded_collection_by_set = data.get("collection_by_set", {})
        self.collection_by_set = {}
        for set_name, rarities in loaded_collection_by_set.items():
            self.collection_by_set[set_name] = {}
            for rarity, cards in rarities.items():
                self.collection_by_set[set_name][rarity] = dict(cards)
        
        # ✅ Carrega pack_languages
        self.pack_languages = data.get("pack_languages", {p.name: p.language.upper() for p in self.packs})
        
        # ✅ Carrega collection_set_filters
        self.collection_set_filters = data.get("collection_set_filters", {p.name: True for p in self.packs})
        
        # Normaliza location
        loaded_location = data.get("location", "ENG")
        if loaded_location in ["EN", "ENG"]:
            self.location = "ENG"
        elif loaded_location in ["JP", "JPN"]:
            self.location = "JPN"
        else:
            self.location = "ENG"
        
        # ✅ Carrega pack_inventory
        self.pack_inventory = data.get("pack_inventory", {})
        
        # ✅ Carrega perfil
        if "profile" in data:
            self.profile_manager.update_from_dict(data["profile"])
            self.profile = self.profile_manager.profile
        
        # Carrega configurações de UI
        self.graphics_mode = data.get("graphics_mode", "real")
        self.set_graphics_mode(self.graphics_mode)
        
        # DEBUG: Confirma valores carregados
        print(f"✅ LOAD COMPLETE:")
        print(f"   - Wallet.coins: {self.wallet.coins}")
        print(f"   - Packs opened: {self.packs_opened}")
        print(f"   - Location: {self.location}")
        print(f"   - Pack inventory: {self.pack_inventory}")
        print(f"   - Collection rarities: {list(self.collection.keys())}")
        print(f"   - Unique cards in collection: {sum(len(cards) for cards in self.collection.values())}")
        print(f"   - Sets in collection: {list(self.collection_by_set.keys())}")
        print(f"   - Profile level: {self.profile.get('level', 1)}")
        print(f"   - Profile XP: {self.profile.get('xp_current', 0)}/{self.profile.get('xp_max', 100)}\n")
        
        # Atualiza UI
        self.update_stats_labels()
        self.show_welcome()
        
        # Mostra mensagem com estatísticas
        unique_cards = sum(len(cards) for cards in self.collection.values())
        messagebox.showinfo(
            "Game Loaded Successfully", 
            f"Loaded from slot {slot}\n\n"
            f"💰 Coins: {self.wallet.coins}\n"
            f"🎴 Packs opened: {self.packs_opened}\n"
            f"📚 Unique cards: {unique_cards}\n"
            f"⭐ Level: {self.profile.get('level', 1)}"
        )

    def open_pack(self, pack: Pack):
        """Abre pack e mostra cartas obtidas."""
        pack_name = pack.name
        
        # Verifica se tem pack no inventário
        has_pack_in_inventory = self.pack_inventory.get(pack_name, 0) > 0
        
        if not has_pack_in_inventory:
            messagebox.showwarning("No Packs Available",
                f"You don't have any {pack_name} packs!\n\n"
                f"Go to the Shop to buy packs with coins.\n\n"
                f"Price: {pack.price} coins per pack")
            return
        
        # Usa pack do inventário
        self.pack_inventory[pack_name] -= 1
        print(f"PACK: Used 1x {pack_name} (remaining: {self.pack_inventory[pack_name]})")
        
        # Define contexto para carregamento de imagens
        pack_slug = self.image_loader._pack_to_slug(pack.name)
        self.image_loader.set_current_pack(pack_slug)
        self.card_image_system.set_current_pack(pack_slug)
        
        print(f"\nOPENING PACK: {pack_name}")
        print(f"Wallet BEFORE: {self.wallet.coins} coins")
        
        # Abre pack
        self.packs_opened += 1
        self.opened_cards = pack.open()
        
        print(f"Cards pulled: {len(self.opened_cards)}")
        
        # Atribui recompensas e XP
        total_reward = 0
        total_xp = 0
        for idx, card in enumerate(self.opened_cards, 1):
            reward = reward_for_rarity(card.rarity)
            xp = get_xp_reward(card.rarity)
            
            print(f"  {idx}. {card.name} ({card.rarity}) -> +{reward} coins, +{xp} XP")
            
            total_reward += reward
            self.wallet.coins += reward
            self.profile_manager.add_coins_earned(reward)
            total_xp += xp
            
            self._add_card_to_collection(pack, card)
        
        print(f"Total reward: {total_reward} coins")
        print(f"Total XP: {total_xp}")
        print(f"Wallet AFTER: {self.wallet.coins} coins")
        print(f"Total earned (lifetime): {self.profile.get('total_coins_earned', 0)} coins\n")
        
        # Sistema de XP e level up
        old_level = self.profile.get("level", 1)
        level_up = self.profile_manager.add_xp(total_xp)
        new_level = self.profile.get("level", 1)
        
        # Verifica novos achievements
        stats = self._get_achievement_stats()
        new_achievements = self.profile_manager.check_and_unlock_achievements(stats)
        
        if new_achievements:
            self._show_achievement_popup(new_achievements)
        
        self.update_stats_labels()
        self.display_pack_opening(pack.name, total_reward, total_xp, level_up)

    def display_pack_opening(self, pack_name: str, total_reward: int, total_xp: int = 0, level_up: bool = False):
        """Mostra interface de cartas abertas."""
        self.clear_content()
        
        # Cabeçalho
        header = tk.Frame(self.content_frame, bg=Colors.BG_DARK)
        header.pack(fill=tk.X, pady=10)
        
        tk.Label(header, text=f"Pack {pack_name} Opened!",
                font=get_font(Fonts.SIZE_TITLE, Fonts.BOLD), bg=Colors.BG_DARK, fg=Colors.WARNING
        ).pack(side=tk.LEFT)
        
        # Mostra recompensas
        rewards_text = f"Rewards: +{total_reward} coins"
        if total_xp > 0:
            rewards_text += f" | +{total_xp} XP"
        if level_up and self.show_notifications:
            rewards_text += f" LEVEL UP!"
        
        tk.Label(header, text=rewards_text,
                font=get_font(Fonts.SIZE_SUBHEADING, Fonts.BOLD), bg=Colors.BG_DARK, 
                fg=Colors.WARNING if level_up else Colors.SUCCESS
        ).pack(side=tk.RIGHT, padx=20)
        
        # Área de cartas (scrollável)
        cards_canvas = tk.Canvas(self.content_frame, bg=Colors.BG_DARK, highlightthickness=0)
        cards_frame = tk.Frame(cards_canvas, bg=Colors.BG_DARK)
        cards_frame.bind("<Configure>",
            lambda e: cards_canvas.configure(scrollregion=cards_canvas.bbox("all")))
        cards_canvas.create_window((0, 0), window=cards_frame, anchor="nw")
        
        # Mouse wheel scroll
        def _on_wheel(e):
            try:
                if cards_canvas.winfo_exists():
                    cards_canvas.yview_scroll(int(-1 * (e.delta/120)), "units")
            except tk.TclError:
                pass
        
        cards_canvas.bind("<Enter>", lambda e: cards_canvas.bind_all("<MouseWheel>", _on_wheel))
        cards_canvas.bind("<Leave>", lambda e: cards_canvas.unbind_all("<MouseWheel>"))
        
        cards_canvas.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Coloca cartas (4 por linha)
        first_row = min(4, len(self.opened_cards))
        for idx in range(first_row):
            self._place_card(cards_frame, self.opened_cards[idx], 0, idx)
        
        remaining = len(self.opened_cards) - first_row
        for idx in range(remaining):
            self._place_card(cards_frame, self.opened_cards[first_row + idx], 1, idx)
        
        # Configura grid
        max_cols = max(first_row, remaining) if remaining > 0 else first_row
        for c in range(max_cols):
            cards_frame.grid_columnconfigure(c, weight=0, minsize=240)
        
        self._create_pack_buttons(pack_name, cards_canvas)

    def _place_card(self, parent, card, row, col):
        """Coloca widget de carta na grid."""
        reward = reward_for_rarity(card.rarity)
        widget = CardWidget(
            parent, card, reward,
            graphics_mode=self.graphics_mode,
            image_loader=lambda p: self.card_image_system.get_card_image(p),
            normalize_rarity_func=normalize_rarity
        )
        widget.grid(row=row, column=col, padx=10, pady=10, sticky="w")

    def _create_pack_buttons(self, pack_name, canvas):
        """Cria botões de ação após abertura."""
        btn_frame = tk.Frame(self.content_frame, bg=Colors.BG_DARK)
        btn_frame.place(relx=0, rely=1, x=10, y=-10, anchor="sw")
        
        buttons = [
            ("Open Another", lambda: self.open_pack_by_name(pack_name)),
            ("Choose Pack", self.open_pack_menu),
            ("Home", lambda: [self.show_welcome(), canvas.unbind_all("<MouseWheel>")])
        ]
        
        for text, cmd in buttons:
            btn = create_button(btn_frame, text, cmd, Colors.PRIMARY, padx=15, pady=8)
            btn.pack(side=tk.LEFT, padx=5)
            bind_hover_effect(btn, Colors.PRIMARY, Colors.PRIMARY_HOVER)

    def _get_achievement_stats(self) -> dict:
        """Obtém estatísticas para verificação de achievements."""
        unique_cards = set()
        rare_cards = 0
        holo_cards = 0
        
        for rarity, cards in self.collection.items():
            for card_name in cards.keys():
                unique_cards.add(card_name)
                if "rare" in rarity.lower():
                    rare_cards += 1
                if "holo" in rarity.lower():
                    holo_cards += 1
        
        # Calcula completude dos sets
        set_completion = {}
        for pack_name, owned, total, percent in self._pack_completion_stats():
            set_completion[pack_name] = percent
        
        return {
            "packs_opened": self.packs_opened,
            "unique_cards": len(unique_cards),
            "rare_cards": rare_cards,
            "holo_cards": holo_cards,
            "set_completion": set_completion,
            "coins": self.wallet.coins,
            "total_coins_earned": self.profile.get("total_coins_earned", 0),
            "level": self.profile.get("level", 1),
            "achievements": self.profile.get("achievements", []),
        }

    def _show_achievement_popup(self, achievement_ids: list):
        """Mostra popup de achievements desbloqueados."""
        if not self.show_notifications:
            return
        
        achievement_text = "New Achievement(s) Unlocked!\n\n"
        for achievement_id in achievement_ids:
            display_name = get_achievement_display_name(achievement_id)
            achievement_text += f"{display_name}\n"
        
        messagebox.showinfo("Achievement Unlocked!", achievement_text)

    def _add_xp(self, xp: int):
        """Adiciona XP ao perfil (deprecated - usar profile_manager)."""
        self.profile_manager.add_xp(xp)

    def update_stats_labels(self) -> None:
        """Atualiza labels de estatísticas."""
        # Atualiza moedas
        if hasattr(self, 'coins_lbl') and self.coins_lbl and self.coins_lbl.winfo_exists():
            self.coins_lbl.config(text=f"{self.wallet.coins}")
            print(f"💰 Stats updated: {self.wallet.coins} coins")  # DEBUG
        
        # Atualiza packs abertos
        if hasattr(self, 'packs_lbl') and self.packs_lbl and self.packs_lbl.winfo_exists():
            self.packs_lbl.config(text=f"{self.packs_opened}")
        
        # Atualiza região
        if hasattr(self, 'region_canvas') and self.region_canvas:
            try:
                self.region_canvas.itemconfig("text", text=self.location[:2])
            except:
                pass

    def change_region(self):
        """Alterna entre regiões ENG e JPN."""
        if self.location == "ENG":
            self.location = "JPN"
        else:
            self.location = "ENG"
        
        # Atualiza o canvas da região
        if hasattr(self, 'region_canvas') and self.region_canvas:
            try:
                self.region_canvas.itemconfig("text", text=self.location[:2])
            except:
                pass
        
        print(f"🌍 Region changed to: {self.location}")
        
        # Se estiver na página de packs, recarrega automaticamente
        if hasattr(self, 'content_frame') and self.content_frame.winfo_children():
            # Verifica se há canvas (indicativo de página com scroll)
            for widget in self.content_frame.winfo_children():
                if isinstance(widget, tk.Canvas):
                    # Recarrega a página de packs
                    self.open_pack_menu()
                    return
        
        # Mostra mensagem se não estiver na página de packs
        messagebox.showinfo(
            "Region Changed", 
            f"Region set to {self.location}\n\nGo to 'Open Packs' to see available packs."
        )

    def clear_content(self):
        """Limpa frame de conteúdo."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_welcome(self):
        """Mostra ecrã de boas-vindas."""
        self.clear_content()
        
        hero = tk.Frame(self.content_frame, bg=Colors.BG_DARK)
        hero.pack(fill=tk.BOTH, expand=True, padx=60, pady=60)
        
        tk.Label(
            hero,
            text="WELCOME TO PYMON TCG",
            font=get_font(Fonts.SIZE_HUGE, Fonts.BOLD),
            bg=Colors.BG_DARK,
            fg=Colors.PRIMARY
        ).pack(pady=(80, 10))
        
        tk.Label(
            hero,
            text="Open packs. Collect cards. Build your legacy.",
            font=get_font(Fonts.SIZE_SUBHEADING),
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_SECONDARY
        ).pack(pady=(0, 60))
        
        # Grid de funcionalidades
        features_container = tk.Frame(hero, bg=Colors.BG_DARK)
        features_container.pack(pady=40)
        
        features = [
            ("COLLECT", "Build your ultimate collection", Colors.PRIMARY),
            ("EARN", "Get coins for every card", Colors.SUCCESS),
            ("COMPETE", "Win at mini-games", Colors.SECONDARY),
            ("ACHIEVE", "Unlock achievements", Colors.WARNING),
        ]
        
        for idx, (title, desc, color) in enumerate(features):
            feature = tk.Frame(features_container, bg=Colors.BG_CARD, width=250, height=140)
            feature.grid(row=idx//2, column=idx%2, padx=15, pady=15)
            feature.pack_propagate(False)
            
            tk.Frame(feature, bg=color, height=Sizes.BORDER_MEDIUM).pack(fill=tk.X)
            
            content = tk.Frame(feature, bg=Colors.BG_CARD)
            content.pack(fill=tk.BOTH, expand=True, padx=Spacing.PAD_LARGE, pady=Spacing.PAD_LARGE)
            
            tk.Label(
                content,
                text=title,
                font=get_font(Fonts.SIZE_LARGE, Fonts.BOLD),
                bg=Colors.BG_CARD,
                fg=color
            ).pack(anchor=tk.W, pady=(0, Spacing.PAD_SMALL))
            
            tk.Label(
                content,
                text=desc,
                font=get_font(Fonts.SIZE_SMALL),
                bg=Colors.BG_CARD,
                fg=Colors.TEXT_SECONDARY,
                wraplength=200,
                justify=tk.LEFT
            ).pack(anchor=tk.W)
        
        cta_btn = tk.Button(
            hero,
            text="START OPENING PACKS",
            font=get_font(Fonts.SIZE_LARGE, Fonts.BOLD),
            bg=Colors.PRIMARY,
            fg=Colors.TEXT_BUTTON,
            activebackground=Colors.PRIMARY_HOVER,
            command=self.open_pack_menu,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=40,
            pady=18
        )
        cta_btn.pack(pady=30)
        
        bind_hover_effect(cta_btn, Colors.PRIMARY, Colors.PRIMARY_HOVER)
    
    def open_pack_menu(self):
        """Mostra menu de seleção de packs em grid 4x4."""
        self.clear_content()
        
        # DEBUG: Mostra inventário atual
        print(f"\n🎒 CURRENT PACK INVENTORY:")
        for pack_name, count in self.pack_inventory.items():
            print(f"  - {pack_name}: {count}")
        print()
        
        # Exclui packs especiais/promocionais
        excluded_packs = [
            "Special Promos & Exclusives (1999–2000)",
            "Special Promos & Exclusives",
            "Special Promos",
            "Promotional"
        ]
        
        # Obtém packs para localização atual (normaliza para 2 caracteres)
        current_location = self.location.upper()[:2]  # ENG -> EN, JPN -> JP
        
        packs_for_loc = [
            p for p in self.packs 
            if p.language.upper()[:2] == current_location  # Compara só 2 chars
            and p.name not in excluded_packs
            and "promo" not in p.name.lower()
            and "exclusive" not in p.name.lower()
        ]
        locked_packs = [p for p in packs_for_loc if not self._is_pack_unlocked(p)]
        
        if not packs_for_loc:
            messagebox.showerror("No Packs", f"No packs available for {self.location}")
            self.show_welcome()
            return

        create_header(
            self.content_frame,
            "AVAILABLE PACKS",
            f"Region: {self.location} - Choose a pack to open"
        )
        
        # Aviso de packs bloqueados
        if locked_packs:
            warning_card, warning_content = create_card_with_border(
                self.content_frame,
                Colors.WARNING,
                fill=tk.X,
                padx=Spacing.PAD_MASSIVE,
                pady=(0, Spacing.PAD_LARGE)
            )
            
            locked_text = ", ".join([f"{p.name} (Lv {self._required_level_for_pack(p)})" for p in locked_packs])
            tk.Label(
                warning_content,
                text=f"LOCKED: {locked_text}",
                font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
                bg=Colors.BG_CARD,
                fg=Colors.WARNING
            ).pack(anchor=tk.W)
        
        # Área scrollável
        canvas = tk.Canvas(self.content_frame, bg=Colors.BG_DARK, highlightthickness=0)
        scrollable_frame = tk.Frame(canvas, bg=Colors.BG_DARK)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        def _on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass
        
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Container de grid para layout 4 colunas
        grid_container = tk.Frame(scrollable_frame, bg=Colors.BG_DARK)
        grid_container.pack(padx=40, pady=30)
        
        col = 0
        row = 0
        max_cols = 4  # 4 packs por linha
        
        # Cards de packs em grid
        for pack in packs_for_loc:
            unlocked = self._is_pack_unlocked(pack)
            inventory_count = self.pack_inventory.get(pack.name, 0)
            
            # DEBUG: Mostra comparação de nomes
            print(f"🔍 Pack: '{pack.name}' -> Inventory count: {inventory_count}")
            
            # Frame do pack
            pack_card = tk.Frame(grid_container, bg=Colors.BG_CARD, width=220, height=300)
            pack_card.grid(row=row, column=col, padx=15, pady=15)
            pack_card.grid_propagate(False)
            
            # Borda superior
            tk.Frame(pack_card, bg=Colors.PRIMARY if unlocked else Colors.BORDER_INACTIVE, height=Sizes.BORDER_MEDIUM).pack(fill=tk.X)
            
            content_frame = tk.Frame(pack_card, bg=Colors.BG_CARD)
            content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
            
            # Ícone do pack
            tk.Label(
                content_frame,
                text="🎴",
                font=get_font(Fonts.SIZE_HUGE),
                bg=Colors.BG_CARD,
                fg=Colors.PRIMARY if unlocked else Colors.TEXT_DISABLED
            ).pack(pady=(5, 10))
            
            # Nome do pack
            tk.Label(
                content_frame,
                text=pack.name.upper(),
                font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
                bg=Colors.BG_CARD,
                fg=Colors.TEXT_PRIMARY if unlocked else Colors.TEXT_DISABLED,
                wraplength=180,
                justify=tk.CENTER
            ).pack()
            
            # Info
            tk.Label(
                content_frame,
                text=f"{len(pack.pokemons)} cards",
                font=get_font(Fonts.SIZE_TINY),
                bg=Colors.BG_CARD,
                fg=Colors.TEXT_SECONDARY,
                justify=tk.CENTER
            ).pack(pady=(5, 10))
            
            # Estatísticas
            stats_row = tk.Frame(content_frame, bg=Colors.BG_CARD)
            stats_row.pack(pady=(0, 10))
            
            tk.Label(
                stats_row,
                text=f"{pack.price} coins",
                font=get_font(Fonts.SIZE_TINY, Fonts.BOLD),
                bg=Colors.BG_CARD,
                fg=Colors.PRIMARY
            ).pack(side=tk.LEFT, padx=5)
            
            if inventory_count > 0:
                tk.Label(
                    stats_row,
                    text=f"x{inventory_count}",
                    font=get_font(Fonts.SIZE_TINY, Fonts.BOLD),
                    bg=Colors.BG_CARD,
                    fg=Colors.SUCCESS
                ).pack(side=tk.LEFT, padx=5)
            
            # Botão
            if not unlocked:
                tk.Label(
                    content_frame,
                    text=f"LEVEL {self._required_level_for_pack(pack)}",
                    font=get_font(Fonts.SIZE_TINY, Fonts.BOLD),
                    bg=Colors.BG_CARD,
                    fg=Colors.DANGER
                ).pack()
            else:
                has_packs = inventory_count > 0
                
                def make_open_handler(p, has_p):
                    if has_p:
                        return lambda: self.open_pack(p)
                    else:
                        return lambda: self.show_shop()
                
                btn = create_button(
                    content_frame,
                    "OPEN" if has_packs else "SHOP",
                    make_open_handler(pack, has_packs),
                    Colors.PRIMARY if has_packs else Colors.SECONDARY,
                    padx=20,
                    pady=10
                )
                btn.pack(fill=tk.X)
                
                normal_bg = Colors.PRIMARY if has_packs else Colors.SECONDARY
                hover_bg = Colors.PRIMARY_HOVER if has_packs else Colors.SECONDARY_HOVER
                bind_hover_effect(btn, normal_bg, hover_bg)
            
            # Atualiza posição na grid
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        canvas.pack(fill=tk.BOTH, expand=True)

    def show_collection(self):
        """Mostra coleção do jogador."""
        self.collection_viewer.show(
            self.content_frame,
            self.clear_content,
            self._build_scrollable_frame
        )

    def _add_card_to_collection(self, pack, card):
        """Adiciona carta à coleção."""
        bucket = rarity_bucket(card.rarity)
        bucket_dict = self.collection.setdefault(bucket, {})
        bucket_dict[card.name] = bucket_dict.get(card.name, 0) + 1

        set_bucket = self.collection_by_set.setdefault(pack.name, {})
        set_rarity = set_bucket.setdefault(bucket, {})
        set_rarity[card.name] = set_rarity.get(card.name, 0) + 1

        if pack.name not in self.collection_set_filters:
            self.collection_set_filters[pack.name] = True
        if pack.name not in self.pack_languages:
            self.pack_languages[pack.name] = pack.language.upper()

    def show_pack_info(self):
        """Mostra informação detalhada sobre packs com design moderno."""
        self.clear_content()
        
        # Usa helper em vez de criar manualmente
        create_header(
            self.content_frame,
            "PACK INFORMATION",
            "Detailed information about each Pokémon TCG set"
        )

        if not self.pack_info:
            tk.Label(
                self.content_frame,
                text="No information available.",
                font=get_font(Fonts.SIZE_LARGE),  # Usa helper
                bg=Colors.BG_DARK,
                fg=Colors.TEXT_SECONDARY
            ).pack(pady=50)
            return

        # Área scrollável
        canvas, scrollable_frame, _ = self._build_scrollable_frame(
            self.content_frame, orient="vertical", bg=Colors.BG_DARK
        )

        # Dicionário de URLs de imagens dos packs
        pack_image_urls = {
            "Base Pack Set": "https://storage.googleapis.com/images.pricecharting.com/91749045dc974aaeaf9943a17290bb3affadda4fd4e245c1dc58f3de87a9fb10/1600.jpg",
            "Base Set": "https://storage.googleapis.com/images.pricecharting.com/91749045dc974aaeaf9943a17290bb3affadda4fd4e245c1dc58f3de87a9fb10/1600.jpg",
            "Base Set 2": "https://storage.googleapis.com/images.pricecharting.com/2449d486c608ea96843c76889ad9ad33ceb5885026f633a728c089d0bd912925/1600.jpg",
            "Fossil": "https://mlpnk72yciwc.i.optimole.com/cqhiHLc.IIZS~2ef73/w:auto/h:auto/q:75/https://bleedingcool.com/wp-content/uploads/2021/06/box-angle-front-10.jpg",
            "Jungle": "https://storage.googleapis.com/images.pricecharting.com/bc14ac59ce7e7e82d7f225fddb52305a3446cd0e5c6d53afb743da2fcc766d70/1600.jpg",
        }

        # Cards de pack modernos (layout horizontal)
        for pack_name, info in sorted(self.pack_info.items()):
            # USA HELPER em vez de criar manualmente
            pack_card, pack_content = create_card_with_border(
                scrollable_frame,
                Colors.PRIMARY,
                fill=tk.X,
                padx=Spacing.PAD_MASSIVE,
                pady=Spacing.PAD_MEDIUM
            )

            # ==================== ESQUERDA: IMAGEM ==================== #
            image_frame = tk.Frame(pack_content, bg=Colors.BG_DARKER, width=180, height=250)
            image_frame.pack(side=tk.LEFT, padx=(0, 25))
            image_frame.pack_propagate(False)

            # Tenta carregar imagem do pack via URL
            pack_image_url = pack_image_urls.get(pack_name)
            image_loaded = False

            if pack_image_url and Image is not None and ImageTk is not None:
                try:
                    req = urllib.request.Request(
                        pack_image_url,
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    )

                    with urllib.request.urlopen(req, timeout=10) as resp:
                        image_data = resp.read()

                    img = Image.open(io.BytesIO(image_data))
                    img.thumbnail((160, 230), Image.Resampling.LANCZOS)
                    tk_img = ImageTk.PhotoImage(img)

                    img_label = tk.Label(image_frame, image=tk_img, bg=Colors.BG_DARKER)
                    img_label.image = tk_img  # Mantém referência
                    img_label.pack(expand=True)
                    image_loaded = True

                except Exception as e:
                    print(f"❌ Failed to load image for {pack_name}: {e}")
                    image_loaded = False

            # Fallback emoji se imagem não carregar
            if not image_loaded:
                tk.Label(
                    image_frame,
                    text="🎴",
                    font=get_font(Fonts.SIZE_HUGE),
                    bg=Colors.BG_DARKER,
                    fg=Colors.PRIMARY
                ).pack(expand=True)

            # ==================== DIREITA: INFO ==================== #
            info_frame = tk.Frame(pack_content, bg=Colors.BG_CARD)
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Nome do pack
            tk.Label(
                info_frame,
                text=pack_name.upper(),
                font=get_font(Fonts.SIZE_HEADING, Fonts.BOLD),
                bg=Colors.BG_CARD,
                fg=Colors.TEXT_PRIMARY,
                anchor="w"
            ).pack(fill=tk.X, pady=(0, 15))

            if isinstance(info, dict):
                # Linha de estatísticas (lançamento, número do set, cartas)
                stats_data = []
                
                # Data de lançamento
                if info.get("release_date"):
                    release_date = info["release_date"]
                    if isinstance(release_date, dict):
                        date_txt = " | ".join([f"{lang}: {date}" for lang, date in release_date.items()])
                    else:
                        date_txt = str(release_date)
                    stats_data.append(("📅", date_txt, Colors.SUCCESS))

                # Cartas no Set
                if info.get("cards_in_set"):
                    cards_in_set = info["cards_in_set"]
                    if isinstance(cards_in_set, dict):
                        cards_txt = " | ".join([f"{lang}: {num}" for lang, num in cards_in_set.items()])
                    else:
                        cards_txt = str(cards_in_set)
                    stats_data.append(("🃏", f"{cards_txt} cards", Colors.WARNING))

                # Número do Set
                if info.get("set_number"):
                    set_number = info["set_number"]
                    if isinstance(set_number, dict):
                        set_txt = " | ".join([f"{lang}: #{num}" for lang, num in set_number.items()])
                    else:
                        set_txt = f"#{set_number}"
                    stats_data.append(("🔢", set_txt, Colors.PURPLE))
                
                # Criar linha de estatísticas usando helper
                if stats_data:
                    stats_row = create_stat_row(info_frame, stats_data, bg=Colors.BG_CARD)
                    stats_row.pack(fill=tk.X, pady=(0, 15))

                # Descrição/Info
                if info.get("info"):
                    tk.Label(
                        info_frame,
                        text=info["info"],
                        font=get_font(Fonts.SIZE_SMALL),
                        bg=Colors.BG_CARD,
                        fg=Colors.TEXT_SECONDARY,
                        wraplength=700,
                        justify=tk.LEFT,
                        anchor="w"
                    ).pack(fill=tk.X, pady=(0, 15))

                # Características Especiais
                if info.get("special_features"):
                    feature_row = tk.Frame(info_frame, bg=Colors.BG_CARD)
                    feature_row.pack(fill=tk.X, pady=(0, 15))
                    
                    tk.Label(
                        feature_row,
                        text="✨",
                        font=get_font(Fonts.SIZE_NORMAL),
                        bg=Colors.BG_CARD,
                        fg=Colors.WARNING
                    ).pack(side=tk.LEFT, padx=(0, 8))
                    
                    tk.Label(
                        feature_row,
                        text=info["special_features"],
                        font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
                        bg=Colors.BG_CARD,
                        fg=Colors.WARNING
                    ).pack(side=tk.LEFT)

                # Cartas Notáveis
                if info.get("notable_cards") and isinstance(info["notable_cards"], list):
                    tk.Label(
                        info_frame,
                        text="⭐ NOTABLE CARDS",
                        font=get_font(Fonts.SIZE_NORMAL, Fonts.BOLD),
                        bg=Colors.BG_CARD,
                        fg=Colors.SECONDARY
                    ).pack(anchor=tk.W, pady=(10, 8))

                    for card in info["notable_cards"]:
                        card_row = tk.Frame(info_frame, bg=Colors.BG_CARD)
                        card_row.pack(fill=tk.X, pady=2)
                        
                        tk.Label(
                            card_row,
                            text="•",
                            font=get_font(Fonts.SIZE_NORMAL),
                            bg=Colors.BG_CARD,
                            fg=Colors.SECONDARY
                        ).pack(side=tk.LEFT, padx=(0, 8))
                        
                        tk.Label(
                            card_row,
                            text=card,
                            font=get_font(Fonts.SIZE_TINY),
                            bg=Colors.BG_CARD,
                            fg=Colors.TEXT_SECONDARY
                        ).pack(side=tk.LEFT)

                # Theme Decks
                if info.get("theme_decks") and isinstance(info["theme_decks"], list):
                    tk.Label(
                        info_frame,
                        text="🎯 THEME DECKS",
                        font=get_font(Fonts.SIZE_NORMAL, Fonts.BOLD),
                        bg=Colors.BG_CARD,
                        fg=Colors.PRIMARY
                    ).pack(anchor=tk.W, pady=(15, 8))

                    for deck in info["theme_decks"]:
                        deck_row = tk.Frame(info_frame, bg=Colors.BG_CARD)
                        deck_row.pack(fill=tk.X, pady=2)
                        
                        tk.Label(
                            deck_row,
                            text="•",
                            font=get_font(Fonts.SIZE_NORMAL),
                            bg=Colors.BG_CARD,
                            fg=Colors.PRIMARY
                        ).pack(side=tk.LEFT, padx=(0, 8))
                        
                        tk.Label(
                            deck_row,
                            text=deck,
                            font=get_font(Fonts.SIZE_TINY),
                            bg=Colors.BG_CARD,
                            fg=Colors.TEXT_SECONDARY
                        ).pack(side=tk.LEFT)

        canvas.pack(fill=tk.BOTH, expand=True)
    
    def show_settings(self):
        """Mostra interface de configurações."""
        self.clear_content()
        
        # USA HELPER
        create_header(self.content_frame, "SETTINGS", "Customize your experience")
        
        canvas, scrollable_frame, _ = self._build_scrollable_frame(
            self.content_frame, orient="vertical", bg=Colors.BG_DARK
        )
        
        # USA HELPER
        create_section_title(scrollable_frame, "GRAPHICS MODE")
        
        # USA HELPER para card
        graphics_card, graphics_content = create_card_with_border(
            scrollable_frame,
            Colors.PURPLE,
            fill=tk.X,
            padx=Spacing.PAD_MASSIVE,
            pady=Spacing.PAD_SMALL
        )
        
        graphics_var = tk.StringVar(value=self.graphics_mode)
        
        for mode, desc in [("real", "Real Card Images"), ("simple", "Simple Text Display")]:
            radio = tk.Radiobutton(
                graphics_content,
                text=f"{desc.upper()}",
                value=mode,
                variable=graphics_var,
                font=get_font(Fonts.SIZE_NORMAL, Fonts.BOLD),
                bg=Colors.BG_CARD,
                fg=Colors.TEXT_PRIMARY,
                selectcolor=Colors.BG_CARD,
                activebackground=Colors.BG_CARD,
                activeforeground=Colors.PRIMARY,
                command=lambda m=mode: self.set_graphics_mode(m)
            )
            radio.pack(anchor=tk.W, pady=5)
        
        # Secção de Notificações - USA HELPER
        create_section_title(scrollable_frame, "NOTIFICATIONS")
        
        notif_card, notif_content = create_card_with_border(
            scrollable_frame,
            Colors.WARNING,
            fill=tk.X,
            padx=Spacing.PAD_MASSIVE,
            pady=Spacing.PAD_SMALL
        )
        
        notes_var = tk.BooleanVar(value=self.show_notifications)
        
        def toggle_notifications():
            self.show_notifications = notes_var.get()
            self._save_settings(SETTINGS_FILE)
        
        tk.Checkbutton(
            notif_content,
            text="SHOW ACHIEVEMENT AND LEVEL-UP NOTIFICATIONS",
            variable=notes_var,
            font=get_font(Fonts.SIZE_NORMAL, Fonts.BOLD),
            bg=Colors.BG_CARD,
            fg=Colors.TEXT_PRIMARY,
            selectcolor=Colors.BG_CARD,
            activebackground=Colors.BG_CARD,
            activeforeground=Colors.PRIMARY,
            command=toggle_notifications
        ).pack(anchor=tk.W)
        
        # Secção de Debug - USA HELPER
        create_section_title(scrollable_frame, "DEBUG MODE")
        
        debug_card, debug_content = create_card_with_border(
            scrollable_frame,
            Colors.DANGER,
            fill=tk.X,
            padx=Spacing.PAD_MASSIVE,
            pady=Spacing.PAD_SMALL
        )
        
        tk.Label(
            debug_content,
            text="DEBUG MODE" + (" (ACTIVE)" if self.debug_mode else ""),
            font=get_font(Fonts.SIZE_SUBHEADING, Fonts.BOLD),
            bg=Colors.BG_CARD,
            fg=Colors.SUCCESS if self.debug_mode else Colors.TEXT_PRIMARY
        ).pack(anchor=tk.W)
        
        tk.Label(
            debug_content,
            text="Grants 99999 coins and unlocks all packs",
            font=get_font(Fonts.SIZE_SMALL),
            bg=Colors.BG_CARD,
            fg=Colors.TEXT_SECONDARY
        ).pack(anchor=tk.W, pady=(5, 0))
        
        debug_btn = create_button(
            debug_card,
            "DISABLE" if self.debug_mode else "ENABLE",
            self.toggle_debug,
            Colors.DANGER if self.debug_mode else Colors.SUCCESS,
            padx=25,
            pady=12
        )
        debug_btn.pack(side=tk.RIGHT, padx=25, pady=20)
        
        bind_hover_effect(
            debug_btn,
            Colors.DANGER if self.debug_mode else Colors.SUCCESS,
            Colors.DANGER_HOVER if self.debug_mode else Colors.SUCCESS_HOVER
        )
        
        canvas.pack(fill=tk.BOTH, expand=True)

    def show_profile_dialog(self):
        """Mostra diálogo de perfil com design moderno."""
        from ui.profile_ui import show_profile_dialog
        
        # Calcula contagem de cartas únicas
        unique_cards = set()
        for rarity, cards in self.collection.items():
            for card_name in cards.keys():
                unique_cards.add(card_name)
        
        # Atualiza perfil com estatísticas
        profile_with_stats = dict(self.profile)
        profile_with_stats["unique_cards_count"] = len(unique_cards)
        profile_with_stats["packs_opened"] = self.packs_opened
        
        # Chama função do módulo de UI
        show_profile_dialog(
            self.root,
            profile_with_stats,
            self._pack_completion_stats
        )

    def show_save_load_dialog(self):
        """Mostra diálogo de save/load com design moderno."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Save / Load Game")
        dialog.config(bg=Colors.BG_DARK)
        dialog.geometry("600x500")
        dialog.resizable(False, False)
        
        # Cabeçalho - USA HELPER
        header = tk.Frame(dialog, bg=Colors.BG_HEADER, height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="SAVE / LOAD GAME",
            font=get_font(Fonts.SIZE_TITLE, Fonts.BOLD),
            bg=Colors.BG_HEADER,
            fg=Colors.PRIMARY
        ).pack(pady=20)
        
        # Conteúdo
        content = tk.Frame(dialog, bg=Colors.BG_DARK)
        content.pack(fill=tk.BOTH, expand=True, padx=Spacing.PAD_MASSIVE, pady=Spacing.PAD_HUGE)
        
        # Slots
        for slot in range(1, 4):
            slot_info = self.settings_manager.get_slot_info(slot)
            exists = slot_info.get("exists", False)
            timestamp = slot_info.get("timestamp", "Empty")
            
            # USA HELPER
            slot_card, slot_content = create_card_with_border(
                content,
                Colors.SUCCESS if exists else Colors.BORDER_INACTIVE,
                fill=tk.X,
                pady=(0, Spacing.PAD_MEDIUM)
            )
            
            # Info
            info_frame = tk.Frame(slot_content, bg=Colors.BG_CARD)
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20, pady=15)
            
            tk.Label(
                info_frame,
                text=f"SLOT {slot}",
                font=get_font(Fonts.SIZE_NORMAL, Fonts.BOLD),
                bg=Colors.BG_CARD,
                fg=Colors.TEXT_PRIMARY
            ).pack(anchor=tk.W)
            
            status_text = timestamp if exists else "Empty Slot"
            status_color = Colors.SUCCESS if exists else Colors.TEXT_DISABLED
            
            tk.Label(
                info_frame,
                text=status_text,
                font=get_font(Fonts.SIZE_TINY),
                bg=Colors.BG_CARD,
                fg=status_color
            ).pack(anchor=tk.W, pady=(5, 0))
            
            # Botões - USA HELPER
            if exists:
                create_button(
                    slot_content,
                    "LOAD",
                    lambda s=slot: [self.load_game(s), dialog.destroy()],
                    Colors.PRIMARY,
                    padx=15,
                    pady=8
                ).pack(side=tk.LEFT, padx=5)
            
            create_button(
                slot_content,
                "SAVE",
                lambda s=slot: [self.save_game(s), dialog.destroy()],
                Colors.SUCCESS,
                padx=15,
                pady=8
            ).pack(side=tk.LEFT, padx=5)
        
        # Botão fechar - USA HELPER
        create_button(
            dialog,
            "CLOSE",
            dialog.destroy,
            Colors.DANGER,
            padx=40,
            pady=12
        ).pack(pady=Spacing.PAD_LARGE)

    def show_shop(self):
        """Mostra interface da loja."""
        try:
            self.shop_system.show(
                content_frame=self.content_frame,
                show_welcome_callback=self.show_welcome,
                clear_content_callback=self.clear_content
            )
        except Exception as e:
            print(f"Error showing shop: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", "Shop system failed to load!")
            self.show_welcome()

    def exit_game(self):
        """Sai do jogo."""
        self.root.destroy()

    def toggle_debug(self):
        """Alterna modo debug."""
        self.debug_mode = not self.debug_mode
        if self.debug_mode:
            self.wallet.coins = 99999
            self.profile["level"] = 99
            self.update_stats_labels()
            messagebox.showinfo("Debug", 
                "Debug Mode ON\n\n"
                "✅ 99999 coins\n"
                "✅ All packs unlocked\n"
                "✅ All packs are FREE in shop"
            )
        else:
            messagebox.showinfo("Debug", "Debug Mode OFF")
        
        # ADICIONA: Recarrega shop se estiver aberto
        if hasattr(self, 'content_frame') and self.content_frame.winfo_children():
            for widget in self.content_frame.winfo_children():
                if isinstance(widget, tk.Canvas):
                    # Está numa página com scroll - pode ser shop
                    try:
                        self.show_shop()
                    except:
                        pass

    def _save_settings(self, path: str) -> None:
        """Guarda configurações em ficheiro."""
        data = {
            "palette": self.current_palette,
            "graphics_mode": self.graphics_mode,
            "show_notifications": self.show_notifications,
            "profile": self.profile_manager.to_dict(),
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def _pack_completion_stats(self):
        """Retorna estatísticas de completude de packs."""
        stats = []
        for pack in self.packs:
            total = self.pack_totals.get(pack.name, len(getattr(pack, "pokemons", [])))
            set_data = self.collection_by_set.get(pack.name, {})
            owned_names = set()
            for rarity_cards in set_data.values():
                owned_names.update(rarity_cards.keys())
            owned = len(owned_names)
            percent = int((owned / total) * 100) if total else 0
            stats.append((pack.name, owned, total, percent))
        return stats

    def _build_scrollable_frame(self, parent, orient="vertical", bg=None):
        """
        Helper centralizado para criar frames scrolláveis.
        ÚNICO MÉTODO - removidas duplicações.
        """
        bg = bg or Colors.BG_DARK
        canvas = tk.Canvas(parent, bg=bg, highlightthickness=0)
        scrollable_frame = tk.Frame(canvas, bg=bg)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        def _on_mousewheel(event):
            try:
                if not canvas.winfo_exists():
                    return
                delta = int(-1 * (event.delta / 120))
                if orient == "vertical":
                    canvas.yview_scroll(delta, "units")
                else:
                    canvas.xview_scroll(delta, "units")
            except tk.TclError:
                pass
        
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        return canvas, scrollable_frame, None

    def open_pack_by_name(self, pack_name: str):
        """Abre pack específico por nome."""
        pack = next((p for p in self.packs if p.name == pack_name), None)

        if pack:
            self.open_pack(pack)
        else:
            messagebox.showerror("Error", f"Pack '{pack_name}' not found")

    def show_blackjack(self):
        """Mostra interface do jogo Blackjack usando GUI do módulo blackjack."""
        if self.wallet.coins <= 0:
            messagebox.showerror("No Coins", "You need coins to play Blackjack!\nOpen some packs first.")
            return

        self.clear_content()

        try:
            from ui.minigames.blackjack_gui import BlackjackGUI
            
            BlackjackGUI.create(
                self.content_frame,
                self.wallet,
                COLORS,
                self.root,
                self.update_stats_labels,
                self.show_welcome,
                lambda: self.show_notifications
            )
                
        except Exception as e:
            print(f"Blackjack error: {e}")
            import traceback
            traceback.print_exc()
            self._show_blackjack_stub()

    def _show_blackjack_stub(self):
        """Stub mínimo de Blackjack quando módulo não está disponível."""
        tk.Label(
            self.content_frame,
            text="BLACKJACK",
            font=get_font(Fonts.SIZE_TITLE, Fonts.BOLD),
            bg=Colors.BG_DARK,
            fg=Colors.SECONDARY
        ).pack(pady=50)
        
        tk.Label(
            self.content_frame,
            text="Module not available",
            font=get_font(Fonts.SIZE_NORMAL),
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_SECONDARY
        ).pack(pady=20)

    def show_slot_machine(self):
        """Mostra slot machine com design moderno."""
        if self.wallet.coins <= 0:
            messagebox.showerror("No Coins", "You need coins to play Slot Machine!")
            return

        self.clear_content()
        
        # Usa helper para cabeçalho
        create_header(
            self.content_frame,
            "🎰 SLOT MACHINE",
            "Spin to win! Match 3 symbols to multiply your bet"
        )
        
        # Usa helper para card
        slot_card, slot_content = create_card_with_border(
            self.content_frame,
            Colors.PRIMARY,
            fill=tk.BOTH,
            expand=True,
            padx=Spacing.PAD_MASSIVE,
            pady=(0, Spacing.PAD_LARGE)
        )
        
        try:
            slot_widget = SlotMachineWidget(
                slot_content,
                self.wallet,
                self.show_welcome
            )
            slot_widget.root = self.root
            slot_widget.pack(fill=tk.BOTH, expand=True)
            
            self.update_stats_labels()
        except Exception as e:
            print(f"Error initializing SlotMachineWidget: {e}")
            tk.Label(
                slot_content,
                text="❌ SLOT MACHINE UNAVAILABLE",
                font=get_font(Fonts.SIZE_LARGE, Fonts.BOLD),
                bg=Colors.BG_CARD,
                fg=Colors.DANGER
            ).pack(pady=50)
            
            tk.Label(
                slot_content,
                text="The slot machine is currently unavailable",
                font=get_font(Fonts.SIZE_NORMAL),
                bg=Colors.BG_CARD,
                fg=Colors.TEXT_SECONDARY
            ).pack()
        

    def setup_ui(self):
        """Configura UI limpa e profissional."""
        # ==================== BARRA SUPERIOR MODERNA ==================== #
        self.header = tk.Frame(self.root, bg=Colors.BG_HEADER, height=90)
        self.header.pack(fill=tk.X)
        self.header.pack_propagate(False)

        # Branding
        brand_frame = tk.Frame(self.header, bg=Colors.BG_HEADER)
        brand_frame.pack(side=tk.LEFT, padx=40, pady=20)
        
        tk.Label(
            brand_frame,
            text="PYMON",
            font=get_font(Fonts.SIZE_TITLE, Fonts.BOLD),
            bg=Colors.BG_HEADER,
            fg=Colors.PRIMARY
        ).pack(side=tk.LEFT)
        
        tk.Label(
            brand_frame,
            text="TCG",
            font=get_font(Fonts.SIZE_TITLE, Fonts.BOLD),
            bg=Colors.BG_HEADER,
            fg=Colors.SECONDARY
        ).pack(side=tk.LEFT, padx=(5, 0))

        # Barra de estatísticas
        stats_bar = tk.Frame(self.header, bg=Colors.BG_HEADER)
        stats_bar.pack(side=tk.RIGHT, padx=40, pady=15)

        # Botão de perfil
        profile_btn = tk.Canvas(stats_bar, width=50, height=50, bg=Colors.BG_HEADER, highlightthickness=0, cursor="hand2")
        profile_btn.pack(side=tk.LEFT, padx=10)
        profile_btn.create_oval(2, 2, 48, 48, fill=Colors.BG_CARD, outline=Colors.PRIMARY, width=2, tags="circle")
        profile_btn.create_text(25, 25, text="P", font=get_font(Fonts.SIZE_LARGE, Fonts.BOLD), fill=Colors.PRIMARY, tags="text")
        
        def profile_hover(e):
            profile_btn.itemconfig("circle", fill=Colors.PRIMARY)
            profile_btn.itemconfig("text", fill=Colors.TEXT_DARK)
        
        def profile_leave(e):
            profile_btn.itemconfig("circle", fill=Colors.BG_CARD)
            profile_btn.itemconfig("text", fill=Colors.PRIMARY)
        
        profile_btn.bind("<Button-1>", lambda e: self.show_profile_dialog())
        profile_btn.bind("<Enter>", profile_hover)
        profile_btn.bind("<Leave>", profile_leave)

        # Moedas
        coins_container = tk.Frame(stats_bar, bg=Colors.BG_CARD)
        coins_container.pack(side=tk.LEFT, padx=8)
        coins_inner = tk.Frame(coins_container, bg=Colors.BG_CARD)
        coins_inner.pack(padx=15, pady=10)
        
        tk.Label(
            coins_inner,
            text="COINS",
            font=get_font(Fonts.SIZE_MINI, Fonts.BOLD),
            bg=Colors.BG_CARD,
            fg=Colors.PRIMARY
        ).pack(anchor=tk.W)        
        self.coins_lbl = tk.Label(
            coins_inner,
            text=f"{self.wallet.coins}",
            font=get_font(Fonts.SIZE_SUBHEADING, Fonts.BOLD),
            bg=Colors.BG_CARD,
            fg=Colors.TEXT_PRIMARY
        )
        self.coins_lbl.pack(anchor=tk.W)

        # Packs abertos
        packs_container = tk.Frame(stats_bar, bg=Colors.BG_CARD)
        packs_container.pack(side=tk.LEFT, padx=8)
        packs_inner = tk.Frame(packs_container, bg=Colors.BG_CARD)
        packs_inner.pack(padx=15, pady=10)
        
        tk.Label(
            packs_inner,
            text="OPENED",
            font=get_font(Fonts.SIZE_MINI, Fonts.BOLD),
            bg=Colors.BG_CARD,
            fg=Colors.SECONDARY
        ).pack(anchor=tk.W)        
        self.packs_lbl = tk.Label(
            packs_inner,
            text=f"{self.packs_opened}",
            font=get_font(Fonts.SIZE_SUBHEADING, Fonts.BOLD),
            bg=Colors.BG_CARD,
            fg=Colors.TEXT_PRIMARY
        )
        self.packs_lbl.pack(anchor=tk.W)

        # Toggle de região
        self.region_canvas = tk.Canvas(stats_bar, width=50, height=50, bg=Colors.BG_HEADER, highlightthickness=0, cursor="hand2")
        self.region_canvas.pack(side=tk.LEFT, padx=10)
        self.region_canvas.create_oval(2, 2, 48, 48, fill=Colors.BG_CARD, outline=Colors.WARNING, width=2, tags="circle")
        self.region_canvas.create_text(25, 25, text=self.location[:2], font=get_font(Fonts.SIZE_NORMAL, Fonts.BOLD), fill=Colors.WARNING, tags="text")
        
        def region_hover(e):
            self.region_canvas.itemconfig("circle", fill=Colors.WARNING)
            self.region_canvas.itemconfig("text", fill=Colors.TEXT_DARK)
        
        def region_leave(e):
            self.region_canvas.itemconfig("circle", fill=Colors.BG_CARD)
            self.region_canvas.itemconfig("text", fill=Colors.WARNING)        
        self.region_canvas.bind("<Button-1>", lambda e: self.change_region())
        self.region_canvas.bind("<Enter>", region_hover)
        self.region_canvas.bind("<Leave>", region_leave)
        
        # ==================== BARRA LATERAL ==================== #
        sidebar = tk.Frame(self.root, bg=Colors.BG_SIDEBAR, width=220)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="NAVIGATION",
            font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
            bg=Colors.BG_SIDEBAR,
            fg=Colors.PRIMARY,
            anchor=tk.W
        ).pack(fill=tk.X, padx=20, pady=(30, 20))

        nav_items = [
            ("OPEN PACKS", self.open_pack_menu, Colors.PRIMARY),
            ("COLLECTION", self.show_collection, Colors.PURPLE),
            ("PACK INFO", self.show_pack_info, Colors.MINT),
            ("SHOP", self.show_shop, Colors.SUCCESS),
            ("SLOT MACHINE", self.show_slot_machine, Colors.WARNING),
            ("BLACKJACK", self.show_blackjack, Colors.SECONDARY),
            ("SAVE / LOAD", self.show_save_load_dialog, Colors.PRIMARY),
            ("SETTINGS", self.show_settings, Colors.PURPLE),
            ("EXIT", self.exit_game, Colors.DANGER),
        ]
        
        self.menu_buttons = []
        for text, command, color in nav_items:
            btn_container = tk.Frame(sidebar, bg=Colors.BG_SIDEBAR)
            btn_container.pack(fill=tk.X, padx=15, pady=5)
            
            btn = tk.Button(
                btn_container,
                text=text,
                font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
                bg=Colors.BG_CARD,
                fg=Colors.TEXT_PRIMARY,
                activebackground=color,
                activeforeground=Colors.TEXT_PRIMARY,
                command=command,
                relief=tk.FLAT,
                bd=0,
                cursor="hand2",
                anchor=tk.W,
                padx=20,
                pady=12
            )
            btn.pack(fill=tk.X)
            
            accent_line = tk.Canvas(btn_container, width=4, height=0, bg=color, highlightthickness=0)
            accent_line.place(x=0, y=0, relheight=1)
            
            bind_hover_effect(btn, Colors.BG_CARD, color)
            
            self.menu_buttons.append(btn)
        
        # ==================== ÁREA DE CONTEÚDO ==================== #
        self.content_frame = tk.Frame(self.root, bg=Colors.BG_DARK)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.update_stats_labels()
    
    def set_graphics_mode(self, mode: str):
        """Define modo de gráficos."""
        self.graphics_mode = mode
        print(f"INFO: Graphics mode set to '{mode}'")
        
        
        # ==================== PONTO DE ENTRADA PRINCIPAL ==================== #
def main():
    """Ponto de entrada principal."""
    root = tk.Tk()
    app = PackOpenerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()