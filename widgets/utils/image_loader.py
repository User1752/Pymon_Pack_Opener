"""
Utilitários de carregamento de imagens.
"""
import os
import json

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


class ImageLoader:
    """Sistema de carregamento de imagens de cartas."""
    
    def __init__(self, base_dir: str):
        self.base_dir = os.path.abspath(base_dir)
        self.image_cache = {}
        self.url_maps = {}
        self.current_pack = None
        print(f"📂 ImageLoader initialized with base_dir: {self.base_dir}")
    
    def set_current_pack(self, pack_slug: str):
        """Define pack atual."""
        self.current_pack = pack_slug
        self._load_url_map(pack_slug)
    
    def _load_url_map(self, pack_slug: str):
        """Carrega mapa de URLs do JSON do pack."""
        if pack_slug in self.url_maps:
            return
        
        json_filename = f"{pack_slug}.json"
        json_path = os.path.join(self.base_dir, json_filename)
        
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.url_maps[pack_slug] = data
                print(f"✅ Loaded {len(data)} card URLs from {json_filename}")
                return
            except Exception as e:
                print(f"❌ Failed to load {json_path}: {e}")
                self.url_maps[pack_slug] = {}
        else:
            print(f"⚠️  File not found: {json_path}")
            self.url_maps[pack_slug] = {}
    
    def load_set_image_maps(self, packs):
        """Carrega mapas de URLs para todos os packs."""
        # Packs a ignorar (não têm JSON files)
        skip_packs = [
            "special_promos_and_exclusives",
            "special_promos",
            "promotional",
            "pokemon_jungle"
        ]
        
        for pack in packs:
            slug = self._pack_to_slug(pack.name)
            
            # Ignora packs problemáticos
            if slug in skip_packs:
                print(f"⏭️  Skipping pack without images: {pack.name}")
                continue
            
            self._load_url_map(slug)
    
    def _pack_to_slug(self, pack_name: str) -> str:
        """Converte nome para slug."""
        import re
        
        slug = pack_name.lower()
        
        # Remove acentos
        replacements = {
            'é': 'e', 'è': 'e', 'ê': 'e',
            'á': 'a', 'à': 'a', 'â': 'a',
            'í': 'i', 'ì': 'i', 'î': 'i',
            'ó': 'o', 'ò': 'o', 'ô': 'o',
            'ú': 'u', 'ù': 'u', 'û': 'u'
        }
        for old, new in replacements.items():
            slug = slug.replace(old, new)
        
        # Remove parênteses e conteúdo
        slug = re.sub(r'\([^)]*\)', '', slug)
        
        # Remove anos
        slug = re.sub(r'\d{4}', '', slug)
        
        # Substitui separadores por underscore
        slug = re.sub(r'[ \-–]+', '_', slug)
        
        # Substitui & por and
        slug = slug.replace('&', 'and')
        
        # Remove caracteres especiais
        slug = re.sub(r'[^a-z0-9_]', '', slug)
        
        # Remove underscores duplicados
        slug = re.sub(r'_+', '_', slug)
        
        # Remove underscores no início/fim
        slug = slug.strip('_')
        
        print(f"🔧 SLUG: '{pack_name}' → '{slug}'")
        return slug

    def _get_card_key(self, pokemon) -> str:
        """Gera chave única para carta."""
        name = pokemon.name.lower().replace(" ", "_")
        number = getattr(pokemon, 'number', 0)
        return f"{name}_{number}" if number else name
    
    def get_card_image(self, pokemon):
        """Obtém imagem de carta (do cache ou carrega)."""
        if Image is None or ImageTk is None:
            return None
        
        card_key = self._get_card_key(pokemon)
        
        if card_key in self.image_cache:
            return self.image_cache[card_key]
        
        image = self._load_image_from_disk(card_key)
        
        if image:
            self.image_cache[card_key] = image
            return image
        
        return None
    
    def _load_image_from_disk(self, card_key: str):
        """Carrega imagem do disco."""
        if not self.current_pack:
            return None
        
        for ext in ['.png', '.jpg', '.jpeg']:
            filepath = os.path.join(self.base_dir, self.current_pack, f"{card_key}{ext}")
            
            if os.path.exists(filepath):
                try:
                    img = Image.open(filepath)
                    img.thumbnail((200, 280), Image.Resampling.LANCZOS)
                    return ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"ERROR: Failed to load image {filepath} - {e}")
        
        return None
    
    def clear_cache(self):
        """Limpa cache de imagens."""
        self.image_cache.clear()
