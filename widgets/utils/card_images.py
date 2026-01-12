"""
Card Image System - Pymon TCG
Sistema de carregamento de imagens de cartas.
"""
import os
import json
import urllib.request
import io

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

class CardImageSystem:
    """Sistema de carregamento de imagens de cartas via URLs."""
    
    def __init__(self, base_dir: str):
        # Garante path absoluto e correto
        self.base_dir = os.path.abspath(base_dir)
        self.image_cache = {}
        self.url_maps = {}
        self.current_pack = None
        
        print(f"📂 CardImageSystem initialized with base_dir: {self.base_dir}")
    
    def set_current_pack(self, pack_slug: str):
        """Define pack atual."""
        self.current_pack = pack_slug
        self._load_url_map(pack_slug)
    
    def _load_url_map(self, pack_slug: str):
        """Carrega mapa de URLs do JSON do pack."""
        if pack_slug in self.url_maps:
            return
        
        # Path absoluto garantido
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
        """Converte nome para slug (limpo, sem duplicações)."""
        import re
        
        # Passo 1: Lowercase
        slug = pack_name.lower()
        
        # Passo 2: Remove acentos
        replacements = {
            'é': 'e', 'è': 'e', 'ê': 'e',
            'á': 'a', 'à': 'a', 'â': 'a',
            'í': 'i', 'ì': 'i', 'î': 'i',
            'ó': 'o', 'ò': 'o', 'ô': 'o',
            'ú': 'u', 'ù': 'u', 'û': 'u'
        }
        for old, new in replacements.items():
            slug = slug.replace(old, new)
        
        # Passo 3: Remove parênteses e conteúdo
        slug = re.sub(r'\([^)]*\)', '', slug)
        
        # Passo 4: Remove anos (4 dígitos consecutivos)
        slug = re.sub(r'\d{4}', '', slug)
        
        # Passo 5: Substitui separadores por underscore
        slug = re.sub(r'[ \-–]+', '_', slug)
        
        # Passo 6: Substitui & por and
        slug = slug.replace('&', 'and')
        
        # Passo 7: Remove caracteres especiais (mantém apenas letras, números, _)
        slug = re.sub(r'[^a-z0-9_]', '', slug)
        
        # Passo 8: Remove underscores duplicados
        slug = re.sub(r'_+', '_', slug)
        
        # Passo 9: Remove underscores no início/fim
        slug = slug.strip('_')
        
        print(f"🔧 SLUG: '{pack_name}' → '{slug}'")
        return slug
    
    def _get_card_key(self, pokemon_or_name):
        """Gera chave da carta."""
        if isinstance(pokemon_or_name, str):
            return pokemon_or_name.strip()
        else:
            return pokemon_or_name.name.strip()
    
    def get_card_image(self, pokemon_or_name):
        """Obtém imagem de carta via URL."""
        if Image is None or ImageTk is None:
            return None
        
        if not self.current_pack:
            return None
        
        card_name = self._get_card_key(pokemon_or_name)
        
        # Verifica cache
        cache_key = f"{self.current_pack}_{card_name}"
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
        
        # Tenta carregar imagem do URL
        image = self._download_image_from_url(card_name)
        
        if image:
            self.image_cache[cache_key] = image
            return image
        
        return None
    
    def _download_image_from_url(self, card_name: str):
        """Faz download da imagem do URL no JSON."""
        if self.current_pack not in self.url_maps:
            return None
        
        url_map = self.url_maps[self.current_pack]
        
        if not url_map:
            return None
        
        # Procura URL exato
        image_url = url_map.get(card_name)
        
        # Fallback: case-insensitive
        if not image_url:
            for key, url in url_map.items():
                if key.lower() == card_name.lower():
                    image_url = url
                    break
        
        if not image_url:
            return None
        
        # Download da imagem
        try:
            req = urllib.request.Request(
                image_url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                image_data = response.read()
            
            img = Image.open(io.BytesIO(image_data))
            img.thumbnail((200, 280), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
            
        except Exception as e:
            print(f"❌ Failed to download {card_name}: {e}")
            return None