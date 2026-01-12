"""
Sistema de Loja - Pymon TCG
Gestão de compra de packs com moedas.
"""
import sys
import os

# Adiciona diretório pai ao path ANTES dos imports (para quando executado diretamente)
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

import tkinter as tk
from tkinter import messagebox

# Imports relativos à estrutura modular
from ui.theme import (
    Colors, Fonts, Spacing, Sizes,
    get_font, create_header, create_button, create_grid_container, create_card_with_border
)


class ShopSystem:
    """Gere a interface e lógica da loja de packs."""
    
    def __init__(self, parent, wallet, colors, profile_manager, 
                 update_stats_callback, save_settings_callback, packs, 
                 pack_unlock_checker, pack_inventory, get_location_callback):
        # Armazena referências
        self.parent = parent
        self.wallet = wallet
        self.colors = colors
        self.profile_manager = profile_manager
        self.update_stats = update_stats_callback
        self.save_settings = save_settings_callback
        self.packs = packs
        self.is_pack_unlocked = pack_unlock_checker
        self.pack_unlock_checker = pack_unlock_checker
        self.pack_inventory = pack_inventory
        self.get_location = get_location_callback
        
        # ADICIONA: Callback para salvar jogo
        self.save_game_callback = None
        
        self.coins_label = None
    
    def show(self, content_frame, show_welcome_callback, clear_content_callback):
        """Mostra interface da loja."""
        clear_content_callback()
        
        # Cabeçalho sem estatísticas de moedas (já está no header principal)
        create_header(
            content_frame,
            "🛒 SHOP",
            "Purchase packs with your coins"
        )
        
        # Frame de tabs (removido - apenas packs)
        tabs_frame = tk.Frame(content_frame, bg="#13172d", height=60)
        tabs_frame.pack(fill=tk.X)
        tabs_frame.pack_propagate(False)
        
        # Área de conteúdo
        shop_content = tk.Frame(content_frame, bg="#0f1419")
        shop_content.pack(fill=tk.BOTH, expand=True)
        
        self._show_booster_packs_tab(shop_content)
        
        # Botão voltar
        create_button(
            content_frame,
            "BACK TO HOME",
            show_welcome_callback,
            Colors.DANGER,
            padx=35,
            pady=14
        ).pack(pady=(Spacing.PAD_SMALL, Spacing.PAD_MEDIUM))
    
    def _update_coins_display(self):
        """Atualiza exibição de moedas."""
        if self.coins_label and self.coins_label.winfo_exists():
            self.coins_label.config(text=f"{self.wallet.coins} coins")
    
    def _show_booster_packs_tab(self, parent):
        """Mostra tab de booster packs."""
        # Limpa widgets anteriores
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Área scrollável
        canvas = tk.Canvas(parent, bg="#0f1419", highlightthickness=0)
        scrollable_frame = tk.Frame(canvas, bg="#0f1419")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Mouse wheel scroll
        def _on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass
        
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Obtém localização atual (normaliza para 2 caracteres)
        current_location = self.get_location().upper()[:2]
        
        # Packs excluídos (apenas promocionais)
        excluded_packs = [
            "Special Promos & Exclusives (1999–2000)",
            "Special Promos & Exclusives",
            "Special Promos",
            "Promotional"
        ]
        
        # Filtra packs por região e exclusões
        available_packs = []
        for p in self.packs:
            pack_lang = getattr(p, 'language', 'ENG').upper()[:2]
            is_excluded = (
                p.name in excluded_packs or 
                "promo" in p.name.lower() or 
                "exclusive" in p.name.lower()
            )
            
            if pack_lang == current_location and not is_excluded:
                available_packs.append(p)
        
        # Mensagem se não houver packs
        if not available_packs:
            tk.Label(
                scrollable_frame,
                text=f"No packs available for {current_location} region",
                font=get_font(Fonts.SIZE_LARGE, Fonts.BOLD),
                bg="#0f1419",
                fg=Colors.TEXT_SECONDARY
            ).pack(pady=100)
            canvas.pack(fill=tk.BOTH, expand=True)
            return
        
        # Container de grid para layout horizontal
        grid_container = tk.Frame(scrollable_frame, bg="#0f1419")
        grid_container.pack(padx=40, pady=30)
        
        col = 0
        row = 0
        max_cols = 4  # 4 packs por linha
        
        # Cria card para cada pack
        for pack in available_packs:
            unlocked = self.pack_unlock_checker(pack)
            
            # Frame do pack
            pack_card = tk.Frame(grid_container, bg=Colors.BG_CARD, width=220, height=280)
            pack_card.grid(row=row, column=col, padx=15, pady=15)
            pack_card.grid_propagate(False)
            
            # Borda superior
            tk.Frame(pack_card, bg=Colors.PRIMARY if unlocked else Colors.BORDER_INACTIVE, height=Sizes.BORDER_MEDIUM).pack(fill=tk.X)
            
            content_frame = tk.Frame(pack_card, bg=Colors.BG_CARD)
            content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
            
            # Ícone do pack
            tk.Label(
                content_frame,
                text="[PACK]",
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
            
            # Descrição
            description = getattr(pack, 'description', f'{len(pack.pokemons)} cards')
            tk.Label(
                content_frame,
                text=description,
                font=get_font(Fonts.SIZE_TINY),
                bg=Colors.BG_CARD,
                fg=Colors.TEXT_SECONDARY,
                wraplength=180,
                justify=tk.CENTER
            ).pack(pady=(5, 10))
            
            # Linha de estatísticas
            stats_row = tk.Frame(content_frame, bg=Colors.BG_CARD)
            stats_row.pack(pady=(0, 10))
            
            tk.Label(
                stats_row,
                text=f"{pack.price} coins",
                font=get_font(Fonts.SIZE_TINY, Fonts.BOLD),
                bg=Colors.BG_CARD,
                fg=Colors.SUCCESS if unlocked else Colors.TEXT_DISABLED
            ).pack(side=tk.LEFT, padx=8)
            
            # Mostra quantidade no inventário
            owned = self.pack_inventory.get(pack.name, 0)
            if owned > 0:
                tk.Label(
                    stats_row,
                    text=f"Owned: {owned}",
                    font=get_font(Fonts.SIZE_TINY, Fonts.BOLD),
                    bg=Colors.BG_CARD,
                    fg=Colors.WARNING
                ).pack(side=tk.LEFT, padx=8)
            
            # Botão de compra ou mensagem de bloqueio
            if not unlocked:
                tk.Label(
                    content_frame,
                    text="LOCKED",
                    font=get_font(Fonts.SIZE_TINY, Fonts.BOLD),
                    bg=Colors.BG_CARD,
                    fg=Colors.DANGER
                ).pack()
            else:
                # Função de compra com closure adequado
                def make_buy_handler(name=pack.name, cost=pack.price):
                    def buy():
                        if self.wallet.coins >= cost:
                            self.wallet.coins -= cost
                            current = self.pack_inventory.get(name, 0)
                            self.pack_inventory[name] = current + 1
                            
                            # DEBUG: Confirma compra
                            print(f"\n🛒 SHOP PURCHASE:")
                            print(f"  Pack name: '{name}'")
                            print(f"  New count: {self.pack_inventory[name]}")
                            print(f"  Full inventory: {self.pack_inventory}\n")
                            
                            self.update_stats()
                            
                            # SALVA CONFIGURAÇÕES (settings.json)
                            if self.save_settings:
                                self.save_settings()
                            
                            # SALVA O JOGO COMPLETO (silenciosamente) - CORRIGIDO
                            if hasattr(self, 'save_game_callback') and self.save_game_callback:
                                print("💾 Auto-saving game after purchase...")
                                self.save_game_callback(1, silent=True)
                            else:
                                print("⚠️  WARNING: save_game_callback not set!")
                            
                            self._update_coins_display()
                            self._show_booster_packs_tab(parent)
                        else:
                            messagebox.showerror("Insufficient Coins", 
                                f"You need {cost} coins but only have {self.wallet.coins}")
                    return buy
                
                create_button(
                    content_frame,
                    "BUY PACK",
                    make_buy_handler(),
                    Colors.PRIMARY,
                    padx=20,
                    pady=10
                ).pack(fill=tk.X)
            
            # Atualiza posição na grid
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        canvas.pack(fill=tk.BOTH, expand=True)

    def _build_scrollable_frame(self, parent, orient="vertical", bg=None, bind_scroll=True):
        """Constrói frame scrollável com canvas."""
        bg = bg or self.colors["accent"]
        canvas = tk.Canvas(parent, bg=bg, highlightthickness=0)
        scrollable_frame = tk.Frame(canvas, bg=bg)
        scrollbar = tk.Scrollbar(
            parent,
            orient=tk.VERTICAL if orient == "vertical" else tk.HORIZONTAL,
            command=canvas.yview if orient == "vertical" else canvas.xview
        )

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        if bind_scroll:
            def _on_mousewheel(event):
                if event.widget == canvas or canvas.winfo_containing(event.x_root, event.y_root) == canvas:
                    delta = int(-1 * (event.delta / 120))
                    if orient == "vertical":
                        canvas.yview_scroll(delta, "units")
                    else:
                        canvas.xview_scroll(delta, "units")

            canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
            canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        if orient == "vertical":
            canvas.configure(yscrollcommand=scrollbar.set)
        else:
            canvas.configure(xscrollcommand=scrollbar.set)

        return canvas, scrollable_frame, scrollbar

    def _buy_pack(self, pack):
        """Compra pack e adiciona ao inventário."""
        if self.wallet.coins < pack.price:
            messagebox.showwarning(
                "Insufficient Coins",
                f"You need {pack.price} coins to buy this pack.\n"
                f"You have {self.wallet.coins} coins."
            )
            return
        
        # Deduz moedas
        self.wallet.coins -= pack.price
        print(f"SHOP: Bought 1x {pack.name} for {pack.price} coins (balance: {self.wallet.coins})")
        
        # Adiciona pack ao inventário
        if hasattr(self, 'pack_inventory') and self.pack_inventory is not None:
            current = self.pack_inventory.get(pack.name, 0)
            self.pack_inventory[pack.name] = current + 1
            print(f"SHOP: Added to inventory - {pack.name}: {self.pack_inventory[pack.name]}")
        else:
            print("ERROR: pack_inventory not available in ShopSystem")
        
        # Atualiza UI
        if self.update_stats:
            self.update_stats()
        
        # Atualiza perfil
        if self.profile_manager:
            self.profile_manager.add_coins_spent(pack.price)
        
        # Salva configurações
        if self.save_settings:
            self.save_settings()
        
        # Mostra confirmação
        messagebox.showinfo(
            "Pack Purchased!",
            f"You bought 1x {pack.name}\n\n"
            f"Remaining coins: {self.wallet.coins}\n"
            f"Packs in inventory: {self.pack_inventory.get(pack.name, 0)}"
        )


if __name__ == "__main__":
    print("Shop System Module - Pymon TCG")
    print("This module should be imported, not run directly.")
    print("Run main.py instead:")
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"  python {os.path.join(parent_dir, 'main.py')}")
