"""
Card Image System - Pymon TCG
Sistema de carregamento de imagens LOCAIS APENAS.
"""
import os
import json
import tkinter as tk

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class CardImageSystem:
    """Sistema de gestão de imagens de cartas."""
    
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.image_maps = {}
        self.current_pack = None
        # CORRIGIDO: Calcula root corretamente (base_dir JÁ É assets/card_images)
        # Precisa subir 2 níveis: assets/card_images -> assets -> Pymon_Pack_Opener
        self.project_root = os.path.dirname(os.path.dirname(base_dir))
        print(f"📂 CardImageSystem initialized with base_dir: {base_dir}")
        print(f"📂 Project root: {self.project_root}")
    
    def set_current_pack(self, pack_slug: str):
        """Define pack atual para contexto."""
        self.current_pack = pack_slug
    
    def _pack_to_slug(self, pack_name: str) -> str:
        """Converte nome de pack para slug."""
        slug = pack_name.lower()
        slug = slug.replace("é", "e").replace("ó", "o").replace("ã", "a")
        slug = slug.replace(" ", "_").replace("'", "").replace(".", "")
        slug = slug.replace("(", "").replace(")", "").replace("–", "").replace("—", "")
        return slug
    
    def load_set_image_maps(self, packs):
        """Carrega mapeamentos de imagens."""
        for pack in packs:
            slug = self._pack_to_slug(pack.name)
            json_path = os.path.join(self.base_dir, f"{slug}.json")
            
            print(f"🔧 SLUG: '{pack.name}' → '{slug}'")
            
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        self.image_maps[slug] = json.load(f)
                    print(f"✅ Loaded {len(self.image_maps[slug])} card URLs from {slug}.json")
                except Exception as e:
                    print(f"❌ Failed to load {slug}.json: {e}")
            else:
                print(f"⏭️  Skipping pack without images: {pack.name}")
    
    def get_card_image(self, card_name: str):
        """
        Obtém imagem da carta redimensionada para 160x220px.
        
        Args:
            card_name: Nome da carta
        
        Returns:
            PhotoImage redimensionada ou None
        """
        if not self.current_pack:
            print(f"⚠️  No pack set for CardImageSystem")
            return None
        
        card_map = self.image_maps.get(self.current_pack, {})
        
        if not card_map:
            print(f"⚠️  No image map for pack '{self.current_pack}'")
            return None
        
        image_path = card_map.get(card_name)
        
        if not image_path:
            print(f"⚠️  No path found for card '{card_name}' in pack '{self.current_pack}'")
            return None
        
        full_path = os.path.join(self.project_root, image_path)
        
        # DEBUG: Mostra path completo e verifica existência
        print(f"🔍 DEBUG - Card: {card_name}")
        print(f"   Pack: {self.current_pack}")
        print(f"   Path from JSON: {image_path}")
        print(f"   Full path: {full_path}")
        print(f"   File exists: {os.path.exists(full_path)}")
        
        if not os.path.exists(full_path):
            # Tenta listar ficheiros na pasta para debug
            folder = os.path.dirname(full_path)
            if os.path.exists(folder):
                print(f"   📁 Files in folder:")
                for f in os.listdir(folder)[:5]:  # Mostra primeiros 5
                    print(f"      - {f}")
            else:
                print(f"   ❌ Folder doesn't exist: {folder}")
            
            print(f"❌ Image file not found: {full_path}")
            return None
        
        try:
            # Carrega e redimensiona com PIL
            if PIL_AVAILABLE:
                pil_image = Image.open(full_path)
                original_size = pil_image.size
                
                # DIMENSÕES FIXAS para área de carta
                TARGET_WIDTH = 160
                TARGET_HEIGHT = 220
                
                # Calcula aspect ratio mantendo proporções
                width_ratio = TARGET_WIDTH / original_size[0]
                height_ratio = TARGET_HEIGHT / original_size[1]
                scale_ratio = min(width_ratio, height_ratio)
                
                # Calcula novas dimensões
                new_width = int(original_size[0] * scale_ratio)
                new_height = int(original_size[1] * scale_ratio)
                
                # Redimensiona com ALTA QUALIDADE
                pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Converte para PhotoImage
                photo_image = ImageTk.PhotoImage(pil_image)
                
                print(f"✅ Loaded {card_name}: {original_size} → {new_width}x{new_height}px")
                return photo_image
            else:
                # Fallback: Tkinter PhotoImage nativo (SEM resize)
                photo_image = tk.PhotoImage(file=full_path)
                print(f"⚠️  Loaded {card_name} without resize (PIL not available)")
                return photo_image
                
        except Exception as e:
            print(f"❌ Failed to load image for {card_name}: {e}")
            import traceback
            traceback.print_exc()
            return None