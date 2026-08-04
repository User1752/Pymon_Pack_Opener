"""
Utilitários para normalizar e comparar nomes de cartas.
Gere casos especiais como Nidoran, Farfetch'd, Mr. Mime, etc.
"""
import unicodedata
import re

def normalize_card_name(name: str) -> str:
    """
    Remove acentos, espaços, pontuação para comparar nomes de cartas.
    Gere casos especiais como Nidoran♀/♂, Farfetch'd, Mr. Mime, etc.
    """
    if not isinstance(name, str):
        return ""
    
    # Normaliza unicode (remove acentos)
    n = unicodedata.normalize("NFKD", name)
    n = "".join(c for c in n if not unicodedata.combining(c))
    
    # Remove todos os caracteres não-alfanuméricos
    n = re.sub(r"[^a-z0-9]+", "", n.lower())
    
    # Casos especiais
    if "nidoranf" in n or "nidoranfemale" in n:
        return "nidoranf"
    if "nidoranm" in n or "nidoranmale" in n:
        return "nidoranm"
    
    # Gere variações comuns
    n = n.replace("imposter", "impostor")  # Normaliza ortografia
    n = n.replace("farfetchd", "farfetchd")  # Remove apóstrofo
    n = n.replace("mrmime", "mrmime")
    
    return n

def extract_card_name_from_slug(slug: str, set_name: str = "") -> str:
    """
    Extrai nome da carta de slug de URL como 'alakazam-base-set-1-102'.
    Args:
        slug: Slug de URL
        set_name: Nome do set opcional para remover do slug (ex: 'fossil', 'base')
    Returns:
        Nome normalizado da carta ou None se extração falhar
    """
    if not slug:
        return None
    
    try:
        parts = slug.split("-")
        
        # Remove segmentos numéricos finais (números de carta)
        while parts and parts[-1].isdigit():
            parts.pop()
        
        # Remove palavras relacionadas com set
        set_keywords = ["set", "fossil", "jungle", "rocket", "gym", "neo", "legendary", "promo", "base"]
        if set_name:
            set_keywords.insert(0, set_name.lower())
        
        # Encontra onde começa o nome do set
        for keyword in set_keywords:
            if keyword in parts:
                idx = parts.index(keyword)
                # Pega tudo antes do nome do set
                parts = parts[:idx]
                break
        
        # Junta partes restantes
        cleaned = " ".join(parts).strip()
        if cleaned:
            name = cleaned.title()
            
            # Gere marcadores de género do Nidoran
            low = name.lower()
            if "nidoran" in low:
                if "female" in low or low.endswith("f"):
                    return "NidoranF"
                elif "male" in low or low.endswith("m"):
                    return "NidoranM"
                else:
                    return "NidoranM"
            
            # Gere caracteres especiais
            if "impostor" in name.lower() or "imposter" in name.lower():
                return "Impostor Professor Oak"
            if "farfetch" in name.lower():
                return "Farfetch'd"
            if "mr" in name.lower() and "mime" in name.lower():
                return "Mr. Mime"
            
            return name
        
    except Exception as e:
        print(f"Error extracting name from slug '{slug}': {e}")
        return None
    
    return None
