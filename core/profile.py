# ============================================================================
# SISTEMA DE XP
# ============================================================================

XP_TABLE = {
    1: 100, 2: 250, 3: 450, 4: 700, 5: 1000,
    6: 1400, 7: 1900, 8: 2500, 9: 3200, 10: 4000,
    11: 5000, 12: 6200, 13: 7600, 14: 9200, 15: 11000,
    16: 13000, 17: 15500, 18: 18500, 19: 22000, 20: 26000
}

def get_xp_reward(rarity: str) -> int:
    """Retorna recompensa de XP por abrir uma carta da raridade especificada."""
    rarity_lower = rarity.lower().strip()
    rewards = {
        "common": 5,
        "uncommon": 10,
        "rare": 25,
        "rare holo": 50,
        "promotional": 30,
        "energy": 2,
    }
    return rewards.get(rarity_lower, 5)


def calculate_level_from_xp(total_xp: int) -> tuple:
    """Retorna (nível, xp_no_nível_atual, xp_necessário_para_próximo)."""
    level = 1
    cumulative = 0
    for lvl in sorted(XP_TABLE.keys()):
        needed = XP_TABLE[lvl]
        if total_xp < cumulative + needed:
            xp_in_level = total_xp - cumulative
            return (level, xp_in_level, needed)
        cumulative += needed
        level = lvl + 1
    max_lvl = max(XP_TABLE.keys())
    return (max_lvl, 0, 0)


# ============================================================================
# SISTEMA DE CONQUISTAS (ACHIEVEMENTS)
# ============================================================================

ACHIEVEMENTS = {
    # Conquistas iniciais
    "first_steps": {
        "name": "First Steps",
        "description": "Welcome to Pymon TCG!",
        "icon": "🎮",
        "unlock": "auto"
    },
    
    # Conquistas de abertura de packs
    "pack_opener": {
        "name": "Pack Opener",
        "description": "Open your first booster pack",
        "icon": "📦",
        "condition": lambda stats: stats.get("packs_opened", 0) >= 1
    },
    "pack_addict": {
        "name": "Pack Addict",
        "description": "Open 10 booster packs",
        "icon": "📦",
        "condition": lambda stats: stats.get("packs_opened", 0) >= 10
    },
    "pack_master": {
        "name": "Pack Master",
        "description": "Open 50 booster packs",
        "icon": "📦",
        "condition": lambda stats: stats.get("packs_opened", 0) >= 50
    },
    "pack_legend": {
        "name": "Pack Legend",
        "description": "Open 100 booster packs",
        "icon": "📦",
        "condition": lambda stats: stats.get("packs_opened", 0) >= 100
    },
    
    # Conquistas de coleção
    "card_collector": {
        "name": "Card Collector",
        "description": "Collect 10 unique cards",
        "icon": "🎴",
        "condition": lambda stats: stats.get("unique_cards", 0) >= 10
    },
    "rare_hunter": {
        "name": "Rare Hunter",
        "description": "Collect 5 rare cards",
        "icon": "💎",
        "condition": lambda stats: stats.get("rare_cards", 0) >= 5
    },
    "holo_master": {
        "name": "Holo Master",
        "description": "Collect 3 rare holo cards",
        "icon": "✨",
        "condition": lambda stats: stats.get("holo_cards", 0) >= 3
    },
    "completionist": {
        "name": "Completionist",
        "description": "Complete any set 100%",
        "icon": "🏆",
        "condition": lambda stats: any(p >= 100 for p in stats.get("set_completion", {}).values())
    },
    "dedicated_collector": {
        "name": "Dedicated Collector",
        "description": "Collect 100 unique cards",
        "icon": "🎴",
        "condition": lambda stats: stats.get("unique_cards", 0) >= 100
    },
    "legendary_collector": {
        "name": "Legendary Collector",
        "description": "Collect 250 unique cards",
        "icon": "🎴",
        "condition": lambda stats: stats.get("unique_cards", 0) >= 250
    },
    
    # Conquistas de riqueza
    "coin_collector": {
        "name": "Coin Collector",
        "description": "Earn 1000 total coins",
        "icon": "💰",
        "condition": lambda stats: stats.get("total_coins_earned", 0) >= 1000
    },
    "rich_trainer": {
        "name": "Rich Trainer",
        "description": "Have 5000 coins at once",
        "icon": "💰",
        "condition": lambda stats: stats.get("coins", 0) >= 5000
    },
    
    # Conquistas de nível
    "novice_trainer": {
        "name": "Novice Trainer",
        "description": "Reach level 5",
        "icon": "⭐",
        "condition": lambda stats: stats.get("level", 1) >= 5
    },
    "experienced_trainer": {
        "name": "Experienced Trainer",
        "description": "Reach level 10",
        "icon": "⭐",
        "condition": lambda stats: stats.get("level", 1) >= 10
    },
    "elite_trainer": {
        "name": "Elite Trainer",
        "description": "Reach level 15",
        "icon": "⭐",
        "condition": lambda stats: stats.get("level", 1) >= 15
    },
    "pokemon_master": {
        "name": "Pokémon Master",
        "description": "Reach level 20",
        "icon": "👑",
        "condition": lambda stats: stats.get("level", 1) >= 20
    },
    
    # Conquistas especiais
    "lucky_streak": {
        "name": "Lucky Streak",
        "description": "Pull 3 rare holos in 10 packs",
        "icon": "🍀",
        "condition": lambda stats: stats.get("recent_holos", 0) >= 3
    },
    "grand_master": {
        "name": "Grand Master",
        "description": "Complete all base game achievements",
        "icon": "👑",
        "condition": lambda stats: len(stats.get("achievements", [])) >= 15
    },
}


def check_achievements(stats: dict, current_achievements: list) -> list:
    """Verifica quais novas conquistas foram desbloqueadas.
    
    Args:
        stats: Dicionário com estatísticas do jogador
        current_achievements: Lista de IDs de conquistas já desbloqueadas
        
    Returns:
        Lista de IDs de conquistas recém-desbloqueadas
    """
    new_achievements = []
    
    for achievement_id, achievement_data in ACHIEVEMENTS.items():
        # Ignora se já desbloqueada
        if achievement_id in current_achievements:
            continue
        
        # Ignora conquistas de desbloqueio automático (geridas noutro lugar)
        if achievement_data.get("unlock") == "auto":
            continue
        
        # Verifica condição
        condition = achievement_data.get("condition")
        if condition and callable(condition):
            try:
                if condition(stats):
                    new_achievements.append(achievement_id)
            except Exception as e:
                # Falha silenciosa em erros de verificação de condição
                pass
    
    return new_achievements


def get_achievement_display_name(achievement_id: str) -> str:
    """Obtém nome formatado para exibição da conquista.
    
    Args:
        achievement_id: ID interno da conquista
        
    Returns:
        String formatada com ícone e nome (ex: "🏆 Pack Opener")
    """
    achievement = ACHIEVEMENTS.get(achievement_id, {})
    icon = achievement.get("icon", "🏆")
    name = achievement.get("name", achievement_id.replace("_", " ").title())
    return f"{icon} {name}"


def get_achievement_info(achievement_id: str) -> dict:
    """Obtém informação completa da conquista.
    
    Args:
        achievement_id: ID interno da conquista
        
    Returns:
        Dicionário com name, description, icon
    """
    achievement = ACHIEVEMENTS.get(achievement_id, {})
    return {
        "name": achievement.get("name", achievement_id.replace("_", " ").title()),
        "description": achievement.get("description", ""),
        "icon": achievement.get("icon", "🏆"),
    }
# ============================================================================
# CLASSE GESTORA DE PERFIL
# ============================================================================

class ProfileManager:
    """Gere todos os dados do perfil do jogador incluindo XP, conquistas e avatares."""
    
    def __init__(self, profile_data: dict = None):
        """Inicializa gestor de perfil.
        
        Args:
            profile_data: Dicionário de perfil existente para carregar, ou None para novo perfil
        """
        self.profile = profile_data or self._default_profile()
        self._ensure_profile_integrity()
    
    def _default_profile(self) -> dict:
        """Retorna estrutura de perfil padrão para novos jogadores."""
        return {
            "name": "Player",
            "icon": "Trainer",
            "level": 1,
            "xp": 0,
            "xp_current": 0,
            "xp_max": 100,
            "title": "Rookie",
            "achievements": ["first_steps"],
            "unlocked_avatars": ["Trainer"],
            "total_coins_earned": 0,
        }
    
    def _ensure_profile_integrity(self):
        """Garante que o perfil tem todos os campos necessários com valores válidos."""
        defaults = self._default_profile()
        for key, default_value in defaults.items():
            if key not in self.profile:
                self.profile[key] = default_value
        
        # Garante que valores de XP são inteiros
        for key in ["xp", "xp_current", "xp_max"]:
            if isinstance(self.profile.get(key), str):
                try:
                    self.profile[key] = int(self.profile[key].split("/")[0])
                except:
                    self.profile[key] = defaults[key]
    
    def add_xp(self, xp: int) -> bool:
        """Adiciona XP ao perfil e atualiza nível.
        
        Args:
            xp: Quantidade de XP a adicionar
            
        Returns:
            True se o jogador subiu de nível, False caso contrário
        """
        if xp <= 0:
            return False
        
        current_xp = self.profile.get("xp", 0)
        if isinstance(current_xp, str):
            current_xp = int(current_xp.split("/")[0]) if "/" in current_xp else 0
        
        old_level = self.profile.get("level", 1)
        new_total_xp = current_xp + xp
        level, xp_in_level, xp_needed = calculate_level_from_xp(new_total_xp)
        
        self.profile["level"] = level
        self.profile["xp"] = new_total_xp
        self.profile["xp_current"] = xp_in_level
        self.profile["xp_max"] = xp_needed
        
        return level > old_level
    
    def check_and_unlock_achievements(self, stats: dict) -> list:
        """Verifica novas conquistas e desbloqueia-as.
        
        Args:
            stats: Dicionário com estatísticas atuais do jogador
            
        Returns:
            Lista de IDs de conquistas recém-desbloqueadas
        """
        current = self.profile.get("achievements", [])
        new_achievements = check_achievements(stats, current)
        
        if new_achievements:
            self.profile["achievements"] = current + new_achievements
        
        return new_achievements
    
    def unlock_avatar(self, avatar_name: str):
        """Desbloqueia um avatar para utilização.
        
        Args:
            avatar_name: Nome do avatar a desbloquear
        """
        unlocked = self.profile.get("unlocked_avatars", ["Trainer"])
        if avatar_name not in unlocked:
            unlocked.append(avatar_name)
            self.profile["unlocked_avatars"] = unlocked
    
    def is_avatar_unlocked(self, avatar_name: str) -> bool:
        """Verifica se um avatar está desbloqueado.
        
        Args:
            avatar_name: Nome do avatar a verificar
            
        Returns:
            True se desbloqueado, False caso contrário
        """
        return avatar_name in self.profile.get("unlocked_avatars", ["Trainer"])
    
    def get_unlocked_avatars(self) -> list:
        """Obtém lista de todos os avatares desbloqueados.
        
        Returns:
            Lista de nomes de avatares desbloqueados
        """
        return self.profile.get("unlocked_avatars", ["Trainer"])
    
    def set_avatar(self, avatar_name: str) -> bool:
        """Define o avatar ativo (se desbloqueado).
        
        Args:
            avatar_name: Nome do avatar a definir como ativo
            
        Returns:
            True se bem-sucedido, False se não desbloqueado
        """
        if self.is_avatar_unlocked(avatar_name):
            self.profile["icon"] = avatar_name
            return True
        return False
    
    def add_coins_earned(self, amount: int):
        """Regista total de moedas ganhas para conquistas.
        
        Args:
            amount: Moedas ganhas a adicionar ao total
        """
        if amount <= 0:
            return
        
        current = self.profile.get("total_coins_earned", 0)
        self.profile["total_coins_earned"] = current + amount
        
        # DEBUG: Regista rastreamento de moedas
        print(f"💰 Tracked coins: +{amount} (total earned: {self.profile['total_coins_earned']})")
    
    def to_dict(self) -> dict:
        """Exporta perfil como dicionário.
        
        Returns:
            Cópia do dicionário de perfil
        """
        return self.profile.copy()
    
    def update_from_dict(self, data: dict):
        """Atualiza perfil a partir de dicionário.
        
        Args:
            data: Dicionário com dados de perfil
        """
        self.profile.update(data)
        self._ensure_profile_integrity()
