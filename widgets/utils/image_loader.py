"""Utilitários de carregamento de imagens.

Objetivo: devolver imagens que CABEM no slot (sem cortar), respeitando o tamanho
pedido pelo CardWidget via target_size.

Os JSON de cada set devem estar em: <assets>/<pack_slug>.json
e mapear: {"Card Name": "assets/images/.../file.jpg", ...}
"""
from __future__ import annotations

import os
import json

try:
    from PIL import Image, ImageTk, ImageOps
except ImportError:
    Image = None
    ImageTk = None
    ImageOps = None


class ImageLoader:
    """Sistema de carregamento de imagens de cartas."""

    DEFAULT_SIZE = (200, 280)

    def __init__(self, base_dir: str):
        # base_dir deve apontar para a pasta 'assets'
        self.base_dir = os.path.abspath(base_dir)

        # Cache por (full_path, size_tuple)
        self.image_cache = {}

        # Mapas por pack_slug: { "Card Name": "assets/images/..." }
        self.path_maps = {}

        self.current_pack = None
        print(f"📂 ImageLoader initialized with base_dir: {self.base_dir}")

    def set_current_pack(self, pack_slug: str):
        """Define pack atual e carrega o respetivo JSON."""
        self.current_pack = pack_slug
        self._load_pack_map(pack_slug)

    def _load_pack_map(self, pack_slug: str):
        """Carrega o mapa (nome -> path) do JSON do pack."""
        if pack_slug in self.path_maps:
            return

        json_path = os.path.join(self.base_dir, f"{pack_slug}.json")
        if not os.path.exists(json_path):
            print(f"⚠️  File not found: {json_path}")
            self.path_maps[pack_slug] = {}
            return

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                print(f"⚠️  Invalid JSON format in {pack_slug}.json (expected dict)")
                data = {}

            self.path_maps[pack_slug] = data
            print(f"✅ Loaded {len(data)} card paths from {pack_slug}.json")

        except Exception as e:
            print(f"❌ Failed to load {json_path}: {e}")
            self.path_maps[pack_slug] = {}

    def load_set_image_maps(self, packs):
        """Carrega mapas de imagem para todos os packs (desde que tenham JSON)."""
        for pack in packs:
            slug = self._pack_to_slug(getattr(pack, "name", ""))
            if slug:
                self._load_pack_map(slug)

    def _pack_to_slug(self, pack_name: str) -> str:
        """Converte nome para slug."""
        import re

        slug = (pack_name or "").lower()

        replacements = {
            "é": "e", "è": "e", "ê": "e",
            "á": "a", "à": "a", "â": "a",
            "í": "i", "ì": "i", "î": "i",
            "ó": "o", "ò": "o", "ô": "o",
            "ú": "u", "ù": "u", "û": "u",
        }
        for old, new in replacements.items():
            slug = slug.replace(old, new)

        slug = re.sub(r"\([^)]*\)", "", slug)
        slug = re.sub(r"\d{4}", "", slug)
        slug = re.sub(r"[ \-–]+", "_", slug)
        slug = slug.replace("&", "and")
        slug = re.sub(r"[^a-z0-9_]", "", slug)
        slug = re.sub(r"_+", "_", slug).strip("_")

        print(f"🔧 SLUG: '{pack_name}' → '{slug}'")
        return slug

    def _find_image_path_in_map(self, card_name: str):
        """Encontra o path no JSON do pack atual (com fallback case-insensitive)."""
        if not self.current_pack:
            return None

        path_map = self.path_maps.get(self.current_pack) or {}
        if not path_map:
            return None

        if card_name in path_map:
            return path_map[card_name]

        low = card_name.lower()
        for k, v in path_map.items():
            if isinstance(k, str) and k.lower() == low:
                return v

        return None

    def _resolve_full_path(self, image_path_from_json: str) -> str:
        """Converte 'assets/images/...' para caminho absoluto."""
        p = (image_path_from_json or "").strip()
        if p.startswith("assets/"):
            p = p[len("assets/"):]
        return os.path.normpath(os.path.join(self.base_dir, p))

    def get_card_image(self, pokemon, target_size=None):
        """Devolve PhotoImage redimensionada para CABER (sem cortar) no target_size."""
        if Image is None or ImageTk is None or ImageOps is None:
            return None

        if not self.current_pack:
            return None

        card_name = pokemon if isinstance(pokemon, str) else getattr(pokemon, "name", None)
        if not card_name:
            return None

        image_path = self._find_image_path_in_map(card_name)
        if not image_path:
            return None

        full_path = self._resolve_full_path(image_path)
        size = target_size or self.DEFAULT_SIZE

        cache_key = (full_path, size)
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]

        if not os.path.exists(full_path):
            return None

        try:
            img = Image.open(full_path).convert("RGBA")
            img = ImageOps.contain(img, size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.image_cache[cache_key] = photo
            return photo
        except Exception:
            return None

    def clear_cache(self):
        self.image_cache.clear()
