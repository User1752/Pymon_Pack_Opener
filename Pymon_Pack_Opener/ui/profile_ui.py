"""
==================== ASSISTENTES DE UI DE PERFIL ====================
Componentes de UI para exibição e gestão de perfil.
"""
import tkinter as tk
from ui.theme import (
    Colors, Fonts, Spacing,
    get_font, create_card_with_border, create_progress_bar,
    create_stat_row, create_button
)
from core.profile import get_achievement_display_name


def show_profile_dialog(root, profile, pack_completion_stats_func):
    """
    Mostra diálogo completo de perfil do jogador.
    ÚNICO MÉTODO EXPORTADO - helpers internos foram consolidados.
    
    Args:
        root: Janela principal (Tk)
        profile: Dicionário com dados do perfil
        pack_completion_stats_func: Função que retorna estatísticas de coleção
    """
    dialog = tk.Toplevel(root)
    dialog.title("Player Profile")
    dialog.config(bg=Colors.BG_DARK)
    dialog.geometry("900x900")
    dialog.resizable(False, False)
    
    # Cabeçalho
    header = tk.Frame(dialog, bg=Colors.BG_HEADER, height=80)
    header.pack(fill=tk.X)
    header.pack_propagate(False)
    
    tk.Label(
        header,
        text="PLAYER PROFILE",
        font=get_font(Fonts.SIZE_TITLE, Fonts.BOLD),
        bg=Colors.BG_HEADER,
        fg=Colors.PRIMARY
    ).pack(pady=20)
    
    # Área scrollável para o conteúdo
    canvas = tk.Canvas(dialog, bg=Colors.BG_DARK, highlightthickness=0)
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
    canvas.pack(fill=tk.BOTH, expand=True, padx=Spacing.PAD_MASSIVE, pady=Spacing.PAD_LARGE)
    
    # Nome
    name_card, name_content = create_card_with_border(
        scrollable_frame,
        Colors.PRIMARY,
        fill=tk.X,
        pady=(0, Spacing.PAD_MEDIUM)
    )
    
    tk.Label(
        name_content,
        text="NAME",
        font=get_font(Fonts.SIZE_SMALL, Fonts.BOLD),
        bg=Colors.BG_CARD,
        fg=Colors.TEXT_SECONDARY
    ).pack(anchor=tk.W)
    
    tk.Label(
        name_content,
        text=profile.get("name", "Player"),
        font=get_font(Fonts.SIZE_SUBHEADING, Fonts.BOLD),
        bg=Colors.BG_CARD,
        fg=Colors.TEXT_PRIMARY
    ).pack(anchor=tk.W, pady=(5, 0))
    
    # Level & XP
    level_card, level_content = create_card_with_border(
        scrollable_frame,
        Colors.SUCCESS,
        fill=tk.X,
        pady=(0, Spacing.PAD_MEDIUM)
    )
    
    level = profile.get("level", 1)
    xp_current = profile.get("xp_current", 0)
    xp_max = profile.get("xp_max", 100)
    
    tk.Label(
        level_content,
        text=f"LEVEL {level}",
        font=get_font(Fonts.SIZE_LARGE, Fonts.BOLD),
        bg=Colors.BG_CARD,
        fg=Colors.SUCCESS
    ).pack(anchor=tk.W)
    
    tk.Label(
        level_content,
        text=f"XP: {xp_current} / {xp_max}",
        font=get_font(Fonts.SIZE_SMALL),
        bg=Colors.BG_CARD,
        fg=Colors.TEXT_SECONDARY
    ).pack(anchor=tk.W, pady=(5, 10))
    
    create_progress_bar(level_content, xp_current, xp_max, Colors.SUCCESS)
    
    # Estatísticas
    stats_card, stats_content = create_card_with_border(
        scrollable_frame,
        Colors.WARNING,
        fill=tk.X,
        pady=(0, Spacing.PAD_MEDIUM)
    )
    
    tk.Label(
        stats_content,
        text="STATISTICS",
        font=get_font(Fonts.SIZE_NORMAL, Fonts.BOLD),
        bg=Colors.BG_CARD,
        fg=Colors.WARNING
    ).pack(anchor=tk.W, pady=(0, Spacing.PAD_SMALL))
    
    # Obter contagem de cartas únicas (precisa ser passado como parâmetro)
    unique_cards_count = profile.get("unique_cards_count", 0)
    
    stats_data = [
        ("🎴", f"{profile.get('packs_opened', 0)} Packs Opened", Colors.PRIMARY),
        ("💰", f"{profile.get('total_coins_earned', 0)} Coins Earned", Colors.SUCCESS),
        ("💸", f"{profile.get('total_coins_spent', 0)} Coins Spent", Colors.DANGER),
        ("📚", f"{unique_cards_count} Unique Cards", Colors.PURPLE)
    ]
    
    stats_row = create_stat_row(stats_content, stats_data, bg=Colors.BG_CARD)
    stats_row.pack(fill=tk.X)
    
    # Achievements
    achievements_card, achievements_content = create_card_with_border(
        scrollable_frame,
        Colors.SECONDARY,
        fill=tk.X,
        pady=(0, Spacing.PAD_MEDIUM)
    )
    
    tk.Label(
        achievements_content,
        text="🏆 ACHIEVEMENTS",
        font=get_font(Fonts.SIZE_NORMAL, Fonts.BOLD),
        bg=Colors.BG_CARD,
        fg=Colors.SECONDARY
    ).pack(anchor=tk.W, pady=(0, Spacing.PAD_SMALL))
    
    unlocked_achievements = profile.get("achievements", [])
    
    if unlocked_achievements:
        for achievement_id in unlocked_achievements:
            achievement_name = get_achievement_display_name(achievement_id)
            
            achievement_row = tk.Frame(achievements_content, bg=Colors.BG_CARD)
            achievement_row.pack(fill=tk.X, pady=3)
            
            tk.Label(
                achievement_row,
                text="✓",
                font=get_font(Fonts.SIZE_NORMAL, Fonts.BOLD),
                bg=Colors.BG_CARD,
                fg=Colors.SUCCESS
            ).pack(side=tk.LEFT, padx=(0, 8))
            
            tk.Label(
                achievement_row,
                text=achievement_name,
                font=get_font(Fonts.SIZE_TINY),
                bg=Colors.BG_CARD,
                fg=Colors.TEXT_PRIMARY
            ).pack(side=tk.LEFT)
    else:
        tk.Label(
            achievements_content,
            text="No achievements unlocked yet",
            font=get_font(Fonts.SIZE_TINY),
            bg=Colors.BG_CARD,
            fg=Colors.TEXT_DISABLED
        ).pack(anchor=tk.W)
    
    # Progresso de Coleção
    collection_card, collection_content = create_card_with_border(
        scrollable_frame,
        Colors.MINT,
        fill=tk.X,
        pady=(0, Spacing.PAD_MEDIUM)
    )
    
    tk.Label(
        collection_content,
        text="📦 COLLECTION PROGRESS",
        font=get_font(Fonts.SIZE_NORMAL, Fonts.BOLD),
        bg=Colors.BG_CARD,
        fg=Colors.MINT
    ).pack(anchor=tk.W, pady=(0, Spacing.PAD_SMALL))
    
    # Mostra progresso de cada set
    for pack_name, owned, total, percent in pack_completion_stats_func():
        if total > 0:  # Só mostra sets com cartas
            set_row = tk.Frame(collection_content, bg=Colors.BG_CARD)
            set_row.pack(fill=tk.X, pady=5)
            
            tk.Label(
                set_row,
                text=pack_name,
                font=get_font(Fonts.SIZE_TINY, Fonts.BOLD),
                bg=Colors.BG_CARD,
                fg=Colors.TEXT_PRIMARY,
                width=30,
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            tk.Label(
                set_row,
                text=f"{owned}/{total}",
                font=get_font(Fonts.SIZE_TINY),
                bg=Colors.BG_CARD,
                fg=Colors.TEXT_SECONDARY,
                width=10
            ).pack(side=tk.LEFT, padx=10)
            
            # Mini barra de progresso
            progress_container = tk.Frame(set_row, bg=Colors.BG_DARKER, height=8)
            progress_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            if percent > 0:
                progress_fill = tk.Frame(progress_container, bg=Colors.MINT, height=8)
                progress_fill.place(x=0, y=0, relwidth=percent/100, relheight=1)
    
    # Botão fechar
    create_button(
        dialog,
        "CLOSE",
        lambda: [dialog.unbind_all("<MouseWheel>"), dialog.destroy()],
        Colors.PRIMARY,
        padx=40,
        pady=12
    ).pack(pady=Spacing.PAD_LARGE)


# ==================== INFO DO MÓDULO ==================== #

if __name__ == "__main__":
    print("Profile UI Helpers - Centralized profile display components")