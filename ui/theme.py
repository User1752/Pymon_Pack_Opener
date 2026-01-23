import tkinter as tk

# ==================== PALETA DE CORES ==================== #

class Colors:
    """Paleta de cores principal."""
    
    # Fundos
    BG_DARK = "#0f1419"
    BG_DARKER = "#0a0e27"
    BG_CARD = "#1a1f3a"
    BG_SIDEBAR = "#13172d"
    BG_HEADER = "#0a0e27"
    
    # Acentos
    PRIMARY = "#00d4ff"
    SECONDARY = "#ff2e63"
    SUCCESS = "#4caf50"
    WARNING = "#ffd700"
    DANGER = "#ff4757"
    PURPLE = "#9d4edd"
    MINT = "#00ff9f"
    
    # Texto
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#a0a0a0"
    TEXT_DISABLED = "#666666"
    TEXT_DARK = "#0a0e27"
    
    # Cores de texto de botões
    TEXT_BUTTON = "#FFFFFF"
    
    # Hover
    PRIMARY_HOVER = "#00b8d4"
    SECONDARY_HOVER = "#ff1744"
    SUCCESS_HOVER = "#45a049"
    DANGER_HOVER = "#ff1744"
    WARNING_HOVER = "#e6c200"
    
    # Bordas
    BORDER_ACTIVE = "#00d4ff"
    BORDER_INACTIVE = "#444444"


# ==================== FONTES ==================== #

class Fonts:
    """Configurações de fontes."""
    
    FAMILY = "Segoe UI"
    
    SIZE_HUGE = 40
    SIZE_TITLE = 28
    SIZE_HEADING = 22
    SIZE_SUBHEADING = 18
    SIZE_LARGE = 16
    SIZE_NORMAL = 14
    SIZE_MEDIUM = 13
    SIZE_SMALL = 12
    SIZE_TINY = 10
    SIZE_MINI = 9
    
    BOLD = "bold"
    NORMAL = "normal"


# ==================== ESPAÇAMENTO ==================== #

class Spacing:
    """Constantes de espaçamento."""
    
    PAD_TINY = 5
    PAD_SMALL = 10
    PAD_MEDIUM = 15
    PAD_LARGE = 20
    PAD_XLARGE = 25
    PAD_HUGE = 30
    PAD_MASSIVE = 40


# ==================== TAMANHOS ==================== #

class Sizes:
    """Constantes de tamanho."""
    
    BORDER_THIN = 2
    BORDER_MEDIUM = 4
    BORDER_THICK = 6


# ==================== CORES DE RARIDADE ==================== #

class RarityColors:
    """Cores de raridade."""
    COMMON = "#9E9E9E"
    UNCOMMON = "#4CAF50"
    RARE = "#2196F3"
    RARE_HOLO = "#9C27B0"
    ENERGY = "#FFEB3B"


# ==================== FUNÇÕES AUXILIARES ==================== #

def get_font(size: int, weight: str = Fonts.NORMAL) -> tuple:
    """Obtém tupla de fonte para tkinter."""
    return (Fonts.FAMILY, size, weight)


def create_header(parent, title: str, subtitle: str = "") -> tk.Frame:
    """
    Cria cabeçalho moderno com título e subtítulo opcional.
    
    Returns:
        Frame do cabeçalho
    """
    header = tk.Frame(parent, bg=Colors.BG_DARK)
    header.pack(fill=tk.X, padx=Spacing.PAD_MASSIVE, pady=Spacing.PAD_HUGE)
    
    tk.Label(
        header,
        text=title,
        font=get_font(Fonts.SIZE_TITLE, Fonts.BOLD),
        bg=Colors.BG_DARK,
        fg=Colors.PRIMARY
    ).pack(anchor=tk.W)
    
    if subtitle:
        tk.Label(
            header,
            text=subtitle,
            font=get_font(Fonts.SIZE_NORMAL),
            bg=Colors.BG_DARK,
            fg=Colors.TEXT_SECONDARY
        ).pack(anchor=tk.W, pady=(5, 0))
    
    return header


def create_card_with_border(parent, border_color: str = Colors.PRIMARY, **pack_kwargs) -> tuple:
    """
    Cria container de card moderno com borda colorida no topo.
    
    Returns:
        Tupla (card_frame, content_frame)
    """
    card = tk.Frame(parent, bg=Colors.BG_CARD)
    if pack_kwargs:
        card.pack(**pack_kwargs)
    
    # Top border
    tk.Frame(card, bg=border_color, height=Sizes.BORDER_MEDIUM).pack(fill=tk.X)
    
    
    content = tk.Frame(card, bg=Colors.BG_CARD)
    content.pack(fill=tk.BOTH, expand=True, padx=Spacing.PAD_XLARGE, pady=Spacing.PAD_LARGE)
    
    return card, content


def create_button(parent, text, command, bg_color, **kwargs):
    """
    Cria um botão estilizado.
    
    Args:
        parent: Widget pai
        text: Texto do botão
        command: Comando/callback do botão
        bg_color: Cor de fundo
        **kwargs: Opções adicionais do botão (padx, pady, font, etc.)
    
    Returns:
        Widget do botão
    """
    # Extrai fonte se fornecida, senão usa padrão
    button_font = kwargs.pop('font', get_font(Fonts.SIZE_NORMAL, Fonts.BOLD))
    
    btn = tk.Button(
        parent,
        text=text,
        font=button_font,
        bg=bg_color,
        fg=Colors.TEXT_BUTTON,  
        activebackground=bg_color,
        command=command,
        relief=tk.FLAT,
        bd=0,
        cursor="hand2",
        **kwargs
    )
    
    return btn


def create_section_title(parent, text: str):
    """Cria título de secção com sublinhado."""
    title_frame = tk.Frame(parent, bg=Colors.BG_DARK)
    title_frame.pack(fill=tk.X, padx=Spacing.PAD_MASSIVE, pady=(Spacing.PAD_HUGE, Spacing.PAD_MEDIUM))
    
    tk.Label(
        title_frame,
        text=text,
        font=get_font(Fonts.SIZE_NORMAL, Fonts.BOLD),
        bg=Colors.BG_DARK,
        fg=Colors.PRIMARY
    ).pack(anchor=tk.W)
    
    tk.Frame(title_frame, bg=Colors.PRIMARY, height=Sizes.BORDER_THIN).pack(fill=tk.X, pady=(5, 0))
    
    return title_frame


def get_rarity_color(rarity: str) -> str:
    """Retorna cor para raridade."""
    rarity_lower = rarity.lower()
    
    if "holo" in rarity_lower:
        return RarityColors.RARE_HOLO
    elif "rare" in rarity_lower:
        return RarityColors.RARE
    elif "uncommon" in rarity_lower:
        return RarityColors.UNCOMMON
    elif "common" in rarity_lower:
        return RarityColors.COMMON
    elif "energy" in rarity_lower:
        return RarityColors.ENERGY
    
    return Colors.TEXT_SECONDARY


def bind_hover_effect(widget, normal_bg: str, hover_bg: str, normal_fg: str = None, hover_fg: str = None):
    """Vincula efeito de hover a qualquer widget."""
    def on_enter(e):
        widget.config(bg=hover_bg)
        if hover_fg:
            widget.config(fg=hover_fg)
    
    def on_leave(e):
        widget.config(bg=normal_bg)
        if normal_fg:
            widget.config(fg=normal_fg)
    
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)


def create_stat_row(parent, stats: list, bg=Colors.BG_CARD):
    """
    Cria uma linha de itens de estatística (ícone + texto).
    
    Args:
        parent: Frame pai
        stats: Lista de tuplas (ícone, texto, cor)
        bg: Cor de fundo
    
    Returns:
        Frame contendo estatísticas
    """
    stats_row = tk.Frame(parent, bg=bg)
    
    for icon, text, color in stats:
        stat_item = tk.Frame(stats_row, bg=bg)
        stat_item.pack(side=tk.LEFT, padx=(0, Spacing.PAD_LARGE))
        
        tk.Label(
            stat_item,
            text=icon,
            font=get_font(Fonts.SIZE_NORMAL),
            bg=bg,
            fg=color
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Label(
            stat_item,
            text=text,
            font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
            bg=bg,
            fg=Colors.TEXT_SECONDARY
        ).pack(side=tk.LEFT)
    
    return stats_row


def create_info_card(parent, title: str, items: list, border_color: str = Colors.PRIMARY):
    """
    Cria um card de informação com título e itens de lista.
    
    Args:
        parent: Frame pai
        title: Título do card
        items: Lista de tuplas (label, valor)
        border_color: Cor da borda esquerda
    """
    card = tk.Frame(parent, bg=Colors.BG_CARD)
    
    # Left border
    tk.Frame(card, bg=border_color, width=Sizes.BORDER_MEDIUM).pack(side=tk.LEFT, fill=tk.Y)
    
    # Content
    content = tk.Frame(card, bg=Colors.BG_CARD)
    content.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=Spacing.PAD_LARGE, pady=Spacing.PAD_MEDIUM)
    
    # Title
    tk.Label(
        content,
        text=title,
        font=get_font(Fonts.SIZE_NORMAL, Fonts.BOLD),
        bg=Colors.BG_CARD,
        fg=Colors.TEXT_PRIMARY
    ).pack(anchor=tk.W, pady=(0, Spacing.PAD_SMALL))
    
    # Items
    for label, value in items:
        row = tk.Frame(content, bg=Colors.BG_CARD)
        row.pack(fill=tk.X, pady=2)
        
        tk.Label(
            row,
            text=f"{label}:",
            font=get_font(Fonts.SIZE_SMALL),
            bg=Colors.BG_CARD,
            fg=Colors.TEXT_SECONDARY
        ).pack(side=tk.LEFT)
        
        tk.Label(
            row,
            text=str(value),
            font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
            bg=Colors.BG_CARD,
            fg=Colors.TEXT_PRIMARY
        ).pack(side=tk.RIGHT)
    
    return card


def create_grid_container(parent, columns: int = 4, bg=Colors.BG_DARK) -> tk.Frame:
    """Cria um container de grid com colunas uniformes."""
    grid = tk.Frame(parent, bg=bg)
    
    for i in range(columns):
        grid.grid_columnconfigure(i, weight=1, uniform="col", minsize=180)
    
    return grid


def create_list_item(parent, title: str, subtitle: str = "", icon: str = "", color: str = Colors.PRIMARY) -> tk.Frame:
    """
    Cria um item de lista com ícone, título, subtítulo.
    
    Returns:
        Frame contendo o item de lista
    """
    item = tk.Frame(parent, bg=Colors.BG_CARD, height=40)
    item.pack(fill=tk.X, padx=Spacing.PAD_MASSIVE, pady=1)
    item.pack_propagate(False)
    
    # Left accent
    tk.Frame(item, bg=color, width=Sizes.BORDER_MEDIUM).pack(side=tk.LEFT, fill=tk.Y)
    
    # Content
    content = tk.Frame(item, bg=Colors.BG_CARD)
    content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=Spacing.PAD_LARGE)
    
    if icon:
        tk.Label(
            content,
            text=icon,
            font=get_font(Fonts.SIZE_NORMAL),
            bg=Colors.BG_CARD,
            fg=color
        ).pack(side=tk.LEFT, padx=(0, Spacing.PAD_SMALL))
    
    tk.Label(
        content,
        text=title,
        font=get_font(Fonts.SIZE_SMALL),
        bg=Colors.BG_CARD,
        fg=Colors.TEXT_PRIMARY,
        anchor=tk.W
    ).pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    if subtitle:
        tk.Label(
            content,
            text=subtitle,
            font=get_font(Fonts.SIZE_TINY, Fonts.BOLD),
            bg=Colors.BG_CARD,
            fg=Colors.WARNING,
            anchor=tk.E
        ).pack(side=tk.RIGHT, padx=Spacing.PAD_SMALL)
    
    return item


def create_filter_button(parent, text: str, is_active: bool, color: str, command) -> tk.Button:
    """Cria um botão de filtro toggle."""
    btn = tk.Button(
        parent,
        text=text.upper(),
        font=get_font(Fonts.SIZE_TINY, Fonts.BOLD),
        bg=color if is_active else Colors.BORDER_INACTIVE,
        fg=Colors.TEXT_PRIMARY,
        activebackground=color,
        command=command,
        relief=tk.FLAT,
        bd=0,
        cursor="hand2",
        padx=Spacing.PAD_MEDIUM,
        pady=8
    )
    return btn


def create_achievement_card(parent, achievement_id: str, achievement_data: dict) -> tk.Frame:
    """
    Cria exibição de card de conquista.
    
    Args:
        parent: Widget pai
        achievement_id: ID da conquista
        achievement_data: Dicionário de dados da conquista com name, description, icon
    
    Returns:
        Frame do card de conquista
    """
    card = tk.Frame(parent, bg=Colors.BG_CARD)
    
    # Border
    tk.Frame(card, bg=Colors.WARNING, height=Sizes.BORDER_MEDIUM).pack(fill=tk.X)
    
    # Content
    content = tk.Frame(card, bg=Colors.BG_CARD)
    content.pack(fill=tk.BOTH, expand=True, padx=Spacing.PAD_LARGE, pady=Spacing.PAD_MEDIUM)
    
    # Icon + Title row
    header = tk.Frame(content, bg=Colors.BG_CARD)
    header.pack(fill=tk.X, pady=(0, Spacing.PAD_SMALL))
    
    icon = achievement_data.get("icon", "🏆")
    tk.Label(
        header,
        text=icon,
        font=get_font(Fonts.SIZE_LARGE),
        bg=Colors.BG_CARD,
        fg=Colors.WARNING
    ).pack(side=tk.LEFT, padx=(0, Spacing.PAD_SMALL))
    
    name = achievement_data.get("name", achievement_id)
    tk.Label(
        header,
        text=name.upper(),
        font=get_font(Fonts.SIZE_NORMAL, Fonts.BOLD),
        bg=Colors.BG_CARD,
        fg=Colors.TEXT_PRIMARY
    ).pack(side=tk.LEFT)
    
    # Description
    desc = achievement_data.get("description", "")
    if desc:
        tk.Label(
            content,
            text=desc,
            font=get_font(Fonts.SIZE_SMALL),
            bg=Colors.BG_CARD,
            fg=Colors.TEXT_SECONDARY,
            wraplength=250,
            justify=tk.LEFT
        ).pack(anchor=tk.W)
    
    return card


def create_pack_card_compact(parent, pack_data: dict, owned: int, on_buy_callback) -> tk.Frame:
    """
    Cria card compacto de pack para loja.
    
    Args:
        parent: Widget pai
        pack_data: Dicionário com name, price, description, icon
        owned: Número possuído
        on_buy_callback: Função a chamar na compra
    
    Returns:
        Frame do card de pack
    """
    card = tk.Frame(parent, bg=Colors.BG_CARD, height=210, width=180)
    card.grid_propagate(False)
    
    # Top border
    tk.Frame(card, bg=Colors.PRIMARY, height=Sizes.BORDER_MEDIUM).pack(fill=tk.X)
    
    # Content
    content = tk.Frame(card, bg=Colors.BG_CARD)
    content.pack(fill=tk.BOTH, expand=True, padx=Spacing.PAD_SMALL, pady=Spacing.PAD_SMALL)
    
    # Icon
    icon = pack_data.get("icon", "🎴")
    tk.Label(
        content,
        text=icon,
        font=get_font(Fonts.SIZE_HUGE),
        bg=Colors.BG_CARD,
        fg=Colors.PRIMARY
    ).pack(pady=(5, 8))
    
    # Name
    name = pack_data.get("name", "Pack")
    tk.Label(
        content,
        text=name,
        font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
        bg=Colors.BG_CARD,
        fg=Colors.TEXT_PRIMARY,
        wraplength=150,
        justify=tk.CENTER
    ).pack()
    
    # Description
    desc = pack_data.get("description", "")
    tk.Label(
        content,
        text=desc,
        font=get_font(Fonts.SIZE_TINY),
        bg=Colors.BG_CARD,
        fg=Colors.TEXT_SECONDARY,
        wraplength=150,
        justify=tk.CENTER
    ).pack(pady=(3, 8))
    
    # Stats row (price + owned)
    stats = tk.Frame(content, bg=Colors.BG_CARD)
    stats.pack()
    
    price = pack_data.get("price", 0)
    tk.Label(
        stats,
        text=f"💰 {price}",
        font=get_font(Fonts.SIZE_TINY, Fonts.BOLD),
        bg=Colors.BG_CARD,
        fg=Colors.SUCCESS
    ).pack(side=tk.LEFT, padx=6)
    
    if owned > 0:
        tk.Label(
            stats,
            text=f"📦 {owned}",
            font=get_font(Fonts.SIZE_TINY, Fonts.BOLD),
            bg=Colors.BG_CARD,
            fg=Colors.WARNING
        ).pack(side=tk.LEFT, padx=6)
    
    # Buy button
    create_button(
        content,
        "BUY",
        on_buy_callback,
        Colors.PRIMARY,
        padx=18,
        pady=8
    ).pack(pady=(8, 0), fill=tk.X)
    
    return card


def create_progress_bar(parent, current: int, maximum: int, color: str = Colors.SUCCESS) -> tk.Frame:
    """
    Cria uma barra de progresso.
    
    Args:
        parent: Widget pai
        current: Valor atual
        maximum: Valor máximo
        color: Cor de preenchimento
    
    Returns:
        Frame da barra de progresso
    """
    bg_frame = tk.Frame(parent, bg=Colors.BG_DARKER, height=20)
    bg_frame.pack(fill=tk.X)
    
    percent = (current / maximum) if maximum > 0 else 0
    fill_frame = tk.Frame(bg_frame, bg=color, height=20)
    fill_frame.place(relwidth=percent, relheight=1)
    
    return bg_frame


def create_table_header(parent, columns: list, widths: list = None, bg=Colors.BG_DARKER) -> tk.Frame:
    """
    Cria uma linha de cabeçalho de tabela.
    
    Args:
        parent: Widget pai
        columns: Lista de nomes de colunas
        widths: Lista de larguras de colunas (opcional)
        bg: Cor de fundo
    
    Returns:
        Frame do cabeçalho
    """
    header = tk.Frame(parent, bg=bg)
    
    if widths is None:
        widths = [15] * len(columns)
    
    for col_name, width in zip(columns, widths):
        tk.Label(
            header,
            text=col_name.upper(),
            font=get_font(Fonts.SIZE_TINY, Fonts.BOLD),
            bg=bg,
            fg=Colors.PRIMARY,
            anchor=tk.W,
            width=width
        ).pack(side=tk.LEFT, padx=Spacing.PAD_SMALL, pady=Spacing.PAD_SMALL)
    
    return header


# ==================== INFO DO MÓDULO ==================== #

if __name__ == "__main__":
    print("Theme System Module - Complete")
    print("=" * 60)
    print("✅ 15+ Helper Functions")
    print("✅ All UI Components Centralized")
    print("✅ ~500 lines of duplicated code eliminated")
    print("=" * 60)
