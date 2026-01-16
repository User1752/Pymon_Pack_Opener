"""
Collection Viewer - Pymon TCG
Visualizador de coleção de cartas.
"""
import tkinter as tk

# Imports completos do tema
from ui.theme import (
    Colors, Fonts, Spacing, Sizes, RarityColors,
    get_font, create_header, create_button, get_rarity_color,
    create_card_with_border
)


class CollectionViewer:
    """Visualizador de coleção com formato de lista e pré-visualização ao passar rato."""
    
    def __init__(self, root, collection_getter, collection_by_set_getter, pack_languages_getter, set_filters_getter, card_image_system):
        """Inicializa visualizador de coleção."""
        self.root = root
        self.get_collection = collection_getter
        self.get_collection_by_set = collection_by_set_getter
        self.get_pack_languages = pack_languages_getter
        self.get_set_filters = set_filters_getter
        self.card_image_system = card_image_system
        
        # Janela de pré-visualização ao passar rato
        self.preview_window = None
        self.preview_label = None
        
        # Rastreia set atual para contexto de pack
        self.current_set_slug = None
        
        # Filtros de raridade (todos ativados por padrão)
        self.rarity_filters = {
            "common": True,
            "uncommon": True,
            "rare": True,
            "rare holo": True
        }
    
    def _get_rarity_color(self, rarity):
        """Usa helper centralizado do tema."""
        return get_rarity_color(rarity)
    
    def show(self, content_frame, clear_content_callback, build_scrollable_callback):
        """Mostra visualizador de coleção."""
        clear_content_callback()
        
        collection = self.get_collection()
        collection_by_set = self.get_collection_by_set()
        
        # Calcula estatísticas de coleção
        total_unique = sum(len(cards) for cards in collection.values())
        total_cards_all_sets = self._calculate_total_possible_cards()
        
        # Cabeçalho ÚNICO com contador total - USA HELPER
        from ui.theme import create_header, Spacing, Colors, Fonts, get_font
        
        create_header(
            content_frame,
            "MY COLLECTION",
            f"{total_unique}/{total_cards_all_sets} Cards Total"
        )
        
        # Obtém dados atualizados
        set_filters = self.get_set_filters()
        
        # Verifica se coleção está vazia
        if not collection or sum(len(cards) for cards in collection.values()) == 0:
            # Mostra estado vazio
            empty_frame = tk.Frame(content_frame, bg=Colors.BG_DARK)
            empty_frame.pack(fill=tk.BOTH, expand=True)
            
            tk.Label(
                empty_frame,
                text="NO CARDS YET",
                font=get_font(Fonts.SIZE_TITLE, Fonts.BOLD),
                bg=Colors.BG_DARK,
                fg=Colors.PRIMARY
            ).pack(pady=(100, 20))
            
            tk.Label(
                empty_frame,
                text="Open some packs to start your collection!",
                font=get_font(Fonts.SIZE_NORMAL),
                bg=Colors.BG_DARK,
                fg=Colors.TEXT_SECONDARY
            ).pack()
            
            return
        
        # Preview label fixo no canto direito
        preview_frame = tk.Frame(content_frame, bg=Colors.BG_CARD, width=250)
        preview_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=Spacing.PAD_LARGE, pady=Spacing.PAD_LARGE)
        preview_frame.pack_propagate(False)
        
        tk.Label(
            preview_frame,
            text="CARD PREVIEW",
            font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
            bg=Colors.BG_CARD,
            fg=Colors.PRIMARY
        ).pack(pady=Spacing.PAD_MEDIUM)
        
        self.card_preview_label = tk.Label(
            preview_frame,
            text="Hover over a card\nto see preview",
            font=get_font(Fonts.SIZE_SMALL),
            bg=Colors.BG_CARD,
            fg=Colors.TEXT_SECONDARY,
            compound=tk.TOP
        )
        self.card_preview_label.pack(expand=True)
        
        # Secção de filtros - usa cores do tema
        filter_container = tk.Frame(content_frame, bg=Colors.BG_DARK)
        filter_container.pack(fill=tk.X, padx=Spacing.PAD_MASSIVE, pady=(0, Spacing.PAD_LARGE))
        
        # Card de filtros de raridade com helper
        rarity_card, rarity_content = create_card_with_border(
            filter_container,
            Colors.PURPLE,
            fill=tk.X,
            pady=(0, Spacing.PAD_SMALL)
        )
        
        tk.Label(
            rarity_content,
            text="FILTER BY RARITY",
            font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
            bg=Colors.BG_CARD,
            fg=Colors.PURPLE
        ).pack(anchor=tk.W, pady=(0, Spacing.PAD_SMALL))
        
        rarity_buttons = tk.Frame(rarity_content, bg=Colors.BG_CARD)
        rarity_buttons.pack(fill=tk.X)
        
        for rarity in ["common", "uncommon", "rare", "rare holo"]:
            is_active = self.rarity_filters.get(rarity, True)
            
            # Usa cores do tema
            btn = tk.Button(
                rarity_buttons,
                text=rarity.upper(),
                font=get_font(Fonts.SIZE_TINY, Fonts.BOLD),
                bg=self._get_rarity_color(rarity) if is_active else Colors.BORDER_INACTIVE,
                fg=Colors.TEXT_PRIMARY,
                activebackground=self._get_rarity_color(rarity),
                command=lambda r=rarity: self._toggle_rarity_filter(r, content_frame, clear_content_callback, build_scrollable_callback),
                relief=tk.FLAT,
                bd=0,
                cursor="hand2",
                padx=Spacing.PAD_MEDIUM,
                pady=8
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Filtros de set com tema
        if len(set_filters) > 1:
            set_card, set_content = create_card_with_border(
                filter_container,
                Colors.PRIMARY,
                fill=tk.X
            )
            
            tk.Label(
                set_content,
                text="FILTER BY SET",
                font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
                bg=Colors.BG_CARD,
                fg=Colors.PRIMARY
            ).pack(anchor=tk.W, pady=(0, Spacing.PAD_SMALL))
            
            set_buttons = tk.Frame(set_content, bg=Colors.BG_CARD)
            set_buttons.pack(fill=tk.X)
            
            for set_name in sorted(set_filters.keys()):
                is_active = set_filters[set_name]
                
                btn = tk.Button(
                    set_buttons,
                    text=set_name.upper(),  # ✅ FIX: era .UPPER() (maiúsculo)
                    font=get_font(Fonts.SIZE_MINI, Fonts.BOLD),
                    bg=Colors.PRIMARY if is_active else Colors.BORDER_INACTIVE,
                    fg=Colors.TEXT_PRIMARY if is_active else Colors.TEXT_DISABLED,
                    activebackground=Colors.PRIMARY_HOVER,
                    command=lambda s=set_name: self._toggle_set_filter(s, content_frame, clear_content_callback, build_scrollable_callback),
                    relief=tk.FLAT,
                    bd=0,
                    cursor="hand2",
                    padx=12,
                    pady=6
                )
                btn.pack(side=tk.LEFT, padx=3, pady=2)
        
        # Área scrollável de LISTA - FIX: usar nome correto do parâmetro
        canvas, scrollable_frame, _ = build_scrollable_callback(
            content_frame, orient="vertical", bg=Colors.BG_DARK
        )
        
        # Exibe cartas em formato de LISTA
        self._display_cards_as_list(scrollable_frame, collection_by_set, set_filters)
        
        canvas.pack(fill=tk.BOTH, expand=True)
    
    def _display_cards_as_list(self, parent, collection_by_set, set_filters):
        """Exibe cartas em FORMATO DE LISTA com 4 colunas de largura aumentada."""
        pack_languages = self.get_pack_languages()
        
        # Ordem de raridade (descendente: rara → comum)
        rarity_order = ["rare holo", "rare", "uncommon", "common"]
        
        # Filtra sets visíveis
        visible_sets = [
            set_name for set_name in sorted(collection_by_set.keys())
            if set_filters.get(set_name, True)
        ]
        
        if not visible_sets:
            tk.Label(
                parent,
                text="No sets to display",
                font=get_font(Fonts.SIZE_NORMAL),
                bg=Colors.BG_DARK,
                fg=Colors.TEXT_SECONDARY
            ).pack(pady=50)
            return
        
        # Container principal com grid de 4 colunas fixas - LARGURA AUMENTADA
        grid_container = tk.Frame(parent, bg=Colors.BG_DARK)
        grid_container.pack(fill=tk.BOTH, expand=True, padx=Spacing.PAD_MEDIUM, pady=Spacing.PAD_MEDIUM)
        
        # Configura 4 colunas de largura igual
        for col in range(4):
            grid_container.grid_columnconfigure(col, weight=1, uniform="column", minsize=320)
        
        # Distribui sets pelas 4 colunas
        for idx, set_name in enumerate(visible_sets):
            row = idx // 4
            col = idx % 4
            
            # Define contexto de pack para imagens
            try:
                pack_slug = set_name.lower().replace(" ", "-").replace("_", "-")
                self.card_image_system.set_current_pack(pack_slug)
                self.current_set_slug = pack_slug
                print(f"DEBUG: Set pack context to '{pack_slug}' for set '{set_name}'")
            except Exception as e:
                print(f"WARNING: Failed to set pack context for '{set_name}': {e}")
            
            set_data = collection_by_set[set_name]
            
            # Conta cartas visíveis e totais
            visible_count = 0
            for rarity, cards in set_data.items():
                if self.rarity_filters.get(rarity, True):
                    visible_count += len(cards)
            
            # Obtém total de cartas no set
            total_in_set = self._get_total_cards_in_set(set_name)
            
            if visible_count == 0:
                continue
            
            # Coluna do set (LARGURA AUMENTADA)
            set_column = tk.Frame(grid_container, bg=Colors.BG_DARK)
            set_column.grid(row=row, column=col, sticky="nsew", padx=3, pady=3)
            
            # Cabeçalho do set com tema
            set_header = tk.Frame(set_column, bg=Colors.BG_CARD)
            set_header.pack(fill=tk.X)
            
            tk.Frame(set_header, bg=Colors.PRIMARY, height=Sizes.BORDER_MEDIUM).pack(fill=tk.X)
            
            header_content = tk.Frame(set_header, bg=Colors.BG_CARD)
            header_content.pack(fill=tk.X, padx=Spacing.PAD_LARGE, pady=Spacing.PAD_SMALL)
            
            # Nome do set (MAIOR)
            set_display_name = set_name.upper()
            if len(set_display_name) > 25:
                set_display_name = set_display_name[:22] + "..."
            
            tk.Label(
                header_content,
                text=set_display_name,
                font=get_font(Fonts.SIZE_NORMAL, Fonts.BOLD),
                bg=Colors.BG_CARD,
                fg=Colors.TEXT_PRIMARY
            ).pack(anchor=tk.W)
            
            # Contador individual X/Y cards
            completion_percent = int((visible_count / total_in_set) * 100) if total_in_set > 0 else 0
            counter_color = Colors.SUCCESS if completion_percent == 100 else Colors.WARNING
            
            tk.Label(
                header_content,
                text=f"{visible_count}/{total_in_set} cards",
                font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
                bg=Colors.BG_CARD,
                fg=counter_color
            ).pack(anchor=tk.W)
            
            # CABEÇALHO DA TABELA (LARGURAS AUMENTADAS)
            table_header = tk.Frame(set_column, bg=Colors.BG_DARKER)
            table_header.pack(fill=tk.X)
            
            header_row = tk.Frame(table_header, bg=Colors.BG_DARKER)
            header_row.pack(fill=tk.X, padx=Spacing.PAD_MEDIUM, pady=4)
            
            tk.Label(
                header_row,
                text="CARD NAME",
                font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
                bg=Colors.BG_DARKER,
                fg=Colors.PRIMARY,
                anchor=tk.W,
                width=22
            ).pack(side=tk.LEFT)
            
            tk.Label(
                header_row,
                text="R",
                font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
                bg=Colors.BG_DARKER,
                fg=Colors.PRIMARY,
                anchor=tk.CENTER,
                width=4
            ).pack(side=tk.LEFT)
            
            tk.Label(
                header_row,
                text="QTY",
                font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
                bg=Colors.BG_DARKER,
                fg=Colors.PRIMARY,
                anchor=tk.CENTER,
                width=4
            ).pack(side=tk.LEFT)
            
            # ITENS DA LISTA (scrollável dentro da coluna)
            cards_container = tk.Frame(set_column, bg=Colors.BG_CARD)
            cards_container.pack(fill=tk.BOTH, expand=True)
            
            for rarity in rarity_order:
                if rarity not in set_data:
                    continue
                if not self.rarity_filters.get(rarity, True):
                    continue
                
                cards = set_data[rarity]
                
                for card_name, count in sorted(cards.items()):
                    # Linha da carta (ALTURA AUMENTADA)
                    card_row = tk.Frame(cards_container, bg=Colors.BG_CARD, height=38)
                    card_row.pack(fill=tk.X, pady=1)
                    card_row.pack_propagate(False)
                    
                    # Left accent
                    tk.Frame(card_row, bg=self._get_rarity_color(rarity), width=4).pack(side=tk.LEFT, fill=tk.Y)
                    
                    inner_row = tk.Frame(card_row, bg=Colors.BG_CARD)
                    inner_row.pack(fill=tk.BOTH, expand=True, padx=Spacing.PAD_MEDIUM)
                    
                    # Card name (LARGURA AUMENTADA)
                    card_display_name = card_name[:20] + "..." if len(card_name) > 20 else card_name
                    
                    tk.Label(
                        inner_row,
                        text=card_display_name,
                        font=get_font(Fonts.SIZE_SMALL),
                        bg=Colors.BG_CARD,
                        fg=Colors.TEXT_PRIMARY,
                        anchor=tk.W,
                        width=22
                    ).pack(side=tk.LEFT)
                    
                    # Rarity symbol
                    rarity_symbol = {
                        "rare holo": "✨",
                        "rare": "⭐",
                        "uncommon": "◆",
                        "common": "●"
                    }.get(rarity, "•")
                    
                    tk.Label(
                        inner_row,
                        text=rarity_symbol,
                        font=get_font(Fonts.SIZE_NORMAL),
                        bg=Colors.BG_CARD,
                        fg=self._get_rarity_color(rarity),
                        anchor=tk.CENTER,
                        width=4
                    ).pack(side=tk.LEFT)
                    
                    # Count
                    tk.Label(
                        inner_row,
                        text=f"{count}",
                        font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
                        bg=Colors.BG_CARD,
                        fg=Colors.WARNING,
                        anchor=tk.CENTER,
                        width=4
                    ).pack(side=tk.LEFT)
                    
                    # Bind hover para preview
                    card_row.bind("<Enter>", lambda e, n=card_name, s=pack_slug: self._show_card_preview(n, s))
                    card_row.bind("<Leave>", lambda e: self._hide_card_preview())
    
    def _show_card_preview(self, card_name, pack_name):
        """Mostra pré-visualização da carta."""
        # Substitui hífens por underscores
        pack_slug = self._pack_to_slug(pack_name)
        
        self.card_image_system.set_current_pack(pack_slug)
        card_img = self.card_image_system.get_card_image(card_name)
        
        if card_img:
            self.card_preview_label.config(image=card_img)
            self.card_preview_label.image = card_img
        else:
            self.card_preview_label.config(
                image="",
                text=f"Preview not available\n\n{card_name}",
                compound=tk.TOP
            )
    
    def _hide_card_preview(self):
        """Esconde pré-visualização da carta."""
        self.card_preview_label.config(image="", text="Hover over a card\nto see preview")
    
    def _toggle_rarity_filter(self, rarity, content_frame, clear_callback, build_callback):
        """Alterna filtro de raridade e atualiza."""
        self.rarity_filters[rarity] = not self.rarity_filters.get(rarity, True)
        self.show(content_frame, clear_callback, build_callback)
    
    def _toggle_set_filter(self, set_name, content_frame, clear_callback, build_callback):
        """Alterna filtro de set e atualiza."""
        set_filters = self.get_set_filters()
        set_filters[set_name] = not set_filters[set_name]
        self.show(content_frame, clear_callback, build_callback)
    
    def _pack_to_slug(self, pack_name: str) -> str:
        """Converte nome para slug (COM UNDERSCORES)."""
        import re
        
        slug = pack_name.lower()
        slug = slug.replace('é', 'e').replace('ô', 'o')
        slug = re.sub(r'\([^)]*\)', '', slug)
        slug = re.sub(r'\d{4}', '', slug)
        slug = re.sub(r'[ \-–]+', '_', slug)  # HÍFENS → UNDERSCORES
        slug = slug.replace('&', 'and')
        slug = re.sub(r'[^a-z0-9_]', '', slug)
        slug = re.sub(r'_+', '_', slug).strip('_')
        
        return slug
    
    def _calculate_total_possible_cards(self) -> int:
        """Calcula total de cartas únicas possíveis em todos os sets."""
        # Importa packs para contar cartas totais
        try:
            from core.game import load_packs_from_json
            import os
            
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            packs_file = os.path.join(base_dir, "data", "packs.json")
            packs = load_packs_from_json(packs_file)
            
            # Conta cartas únicas por nome (evita duplicatas)
            all_card_names = set()
            for pack in packs:
                for pokemon in getattr(pack, "pokemons", []):
                    all_card_names.add(pokemon.name)
            
            return len(all_card_names)
        except Exception as e:
            print(f"Warning: Could not calculate total cards: {e}")
            return 0
        
    def _show_set_view(self, content_frame, build_scrollable_callback, set_name: str):
        """Mostra cartas de um set específico com contador."""
        from ui.theme import (
            create_header, create_card_with_border, create_button,
            bind_hover_effect, Colors, Fonts, Spacing, get_font
        )
        
        collection_by_set = self.get_collection_by_set()
        set_data = collection_by_set.get(set_name, {})
        set_filters = self.get_set_filters()  # FIX: adicionar esta linha
        
        # Calcula cartas únicas no set
        unique_cards_in_set = set()
        for rarity_cards in set_data.values():
            unique_cards_in_set.update(rarity_cards.keys())
        
        owned_count = len(unique_cards_in_set)
        total_count = self._get_total_cards_in_set(set_name)
        completion_percent = int((owned_count / total_count) * 100) if total_count > 0 else 0
        
        # Cabeçalho com progresso
        header_frame = tk.Frame(content_frame, bg=Colors.BG_DARK)
        header_frame.pack(fill=tk.X, padx=Spacing.PAD_MASSIVE, pady=(Spacing.PAD_LARGE, 0))
        
        tk.Label(
            header_frame,
            text=set_name.upper(),
            font=get_font(Fonts.SIZE_TITLE, Fonts.BOLD),
            bg=Colors.BG_DARK,
            fg=Colors.PRIMARY
        ).pack(side=tk.LEFT)
        
        # Contador de cartas
        progress_text = f"{owned_count}/{total_count} Cards ({completion_percent}%)"
        progress_color = Colors.SUCCESS if completion_percent == 100 else Colors.WARNING
        
        tk.Label(
            header_frame,
            text=progress_text,
            font=get_font(Fonts.SIZE_SUBHEADING, Fonts.BOLD),
            bg=Colors.BG_DARK,
            fg=progress_color
        ).pack(side=tk.RIGHT)
        
        # Área scrollável de LISTA - FIX: usar nome correto do parâmetro
        canvas, scrollable_frame, _ = build_scrollable_callback(
            content_frame, orient="vertical", bg=Colors.BG_DARK
        )
        
        # Exibe cartas em formato de LISTA
        self._display_cards_as_list(scrollable_frame, collection_by_set, set_filters)
        
        canvas.pack(fill=tk.BOTH, expand=True)
    
    def _get_total_cards_in_set(self, set_name: str) -> int:
        """Obtém total de cartas num set específico."""
        try:
            from core.game import load_packs_from_json
            import os
            
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            packs_file = os.path.join(base_dir, "data", "packs.json")
            packs = load_packs_from_json(packs_file)
            
            for pack in packs:
                if pack.name == set_name:
                    return len(getattr(pack, "pokemons", []))
            
            return 0
        except Exception as e:
            print(f"Warning: Could not get total for {set_name}: {e}")
            return 0


# ==================== INFO DO MÓDULO ==================== #

if __name__ == "__main__":
    print("This module provides collection viewer functionality.")
    print("Import CollectionViewer and use .show() to display the collection.")
