"""
Image Loader System - Pymon TCG
Carrega imagens de cartas LOCAIS APENAS.
"""
import os
import json
try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


class ImageLoader:
    """Gere carregamento de imagens de cartas (apenas local)."""
    
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.image_maps = {}
        self.current_pack = None
        # CORRIGIDO: base_dir JÁ É assets/card_images
        # Sobe 2 níveis: assets/card_images -> assets -> Pymon_Pack_Opener
        self.project_root = os.path.dirname(os.path.dirname(base_dir))
        print(f"📂 ImageLoader initialized with base_dir: {base_dir}")
        print(f"📂 Project root: {self.project_root}")
    
    def set_current_pack(self, pack_slug: str):
        """Define pack atual para contexto de carregamento."""
        self.current_pack = pack_slug
    
    def _pack_to_slug(self, pack_name: str) -> str:
        """Converte nome de pack para slug de ficheiro."""
        slug = pack_name.lower()
        slug = slug.replace("é", "e").replace("ó", "o").replace("ã", "a")
        slug = slug.replace(" ", "_").replace("'", "").replace(".", "")
        slug = slug.replace("(", "").replace(")", "").replace("–", "").replace("—", "")
        return slug
    
    def load_set_image_maps(self, packs):
        """Carrega mapeamentos de imagens para todos os sets."""
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
    
    def get_image(self, card_name: str):
        """Carrega imagem de carta LOCAL."""
        if not self.current_pack or self.current_pack not in self.image_maps:
            return None
        
        path = self.image_maps[self.current_pack].get(card_name)
        if not path:
            return None
        
        try:
            # CORRIGIDO: Usa project_root corretamente
            abs_path = os.path.join(self.project_root, path.replace("/", os.sep))
            
            print(f"🖼️  Loading: {card_name}")
            print(f"   Path: {abs_path}")
            print(f"   Exists: {os.path.exists(abs_path)}")
            
            if not os.path.exists(abs_path):
                print(f"❌ File not found: {abs_path}")
                return None
            
            # Carrega imagem LOCAL
            img = Image.open(abs_path)
            img.thumbnail((200, 280), Image.Resampling.LANCZOS)
            print(f"✅ Loaded successfully!")
            return ImageTk.PhotoImage(img)
        
        except Exception as e:
            print(f"❌ Failed to load {card_name}: {e}")
            import traceback
            traceback.print_exc()
            return None
