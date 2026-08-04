"""
SettingsManager - gere persistência de saves/carregamentos/configurações.
"""
import json
import os
from typing import Optional


class SettingsManager:
    """Gere configurações do jogo, ficheiros de save e dados de perfil."""
    
    def __init__(self, save_dir: str, settings_file: str):
        self.save_dir = save_dir
        self.settings_file = settings_file
        os.makedirs(save_dir, exist_ok=True)
    
    def save_game(self, slot: int, data: dict) -> bool:
        """Guarda estado do jogo no slot."""
        try:
            path = self._slot_path(slot)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving to slot {slot}: {e}")
            return False
    
    def load_game(self, slot: int) -> Optional[dict]:
        """Carrega estado do jogo do slot."""
        path = self._slot_path(slot)
        if not os.path.exists(path):
            return None
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading slot {slot}: {e}")
            return None
    
    def save_settings(self, settings: dict) -> bool:
        """Guarda configurações da aplicação (paleta, modo gráfico, perfil)."""
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def load_settings(self) -> dict:
        """Carrega configurações da aplicação."""
        if not os.path.exists(self.settings_file):
            return {}
        
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {}
    
    def get_slot_info(self, slot: int) -> dict:
        """Obtém metadata sobre um slot de save."""
        path = self._slot_path(slot)
        if not os.path.exists(path):
            return {"exists": False, "slot": slot}
        
        import time
        mtime = os.path.getmtime(path)
        timestamp = time.strftime("%Y-%m-%d %H:%M", time.localtime(mtime))
        
        return {
            "exists": True,
            "slot": slot,
            "timestamp": timestamp,
            "path": path
        }
    
    def _slot_path(self, slot: int) -> str:
        """Obtém caminho do ficheiro para slot de save."""
        return os.path.join(self.save_dir, f"slot{slot}.json")
