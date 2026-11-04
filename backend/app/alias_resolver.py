import re
from typing import Tuple, Dict, Any, List

# Common Westeros spelling corrections & phonetic normalizations
COMMON_SPELLING_CORRECTIONS = {
    # Characters
    r"\bdaen(e)?rys\b": "Daenerys",
    r"\bdaenerys targarian\b": "Daenerys Targaryen",
    r"\btyrian\b": "Tyrion",
    r"\btyrion lanister\b": "Tyrion Lannister",
    r"\bcerci\b": "Cersei",
    r"\bcersei lanister\b": "Cersei Lannister",
    r"\bjoffery\b": "Joffrey",
    r"\bjoffery barathean\b": "Joffrey Baratheon",
    r"\bjon sno\b": "Jon Snow",
    r"\bcaitlyn\b": "Catelyn",
    r"\bcatelyn stark\b": "Catelyn Stark",
    r"\bedard\b": "Eddard",
    r"\beddard stark\b": "Eddard Stark",
    r"\brhaegar targarian\b": "Rhaegar Targaryen",
    r"\bviserion\b": "Viserion",
    r"\bbarathean\b": "Baratheon",
    r"\btargarian\b": "Targaryen",
    r"\blanister\b": "Lannister",
    r"\bmontain\b": "Mountain",
    r"\bmelisandra\b": "Melisandre",
    r"\bvalyrian\b": "Valyrian",
    r"\bvalyria\b": "Valyria",
    # Places
    r"\bwesteros\b": "Westeros",
    r"\bessos\b": "Essos",
    r"\bwinterfel\b": "Winterfell",
    r"\bking['\s]?s landing\b": "King's Landing",
    r"\bdragonston\b": "Dragonstone",
    r"\bbraavos\b": "Braavos",
    r"\bold town\b": "Oldtown",
    r"\bthe eyrie\b": "The Eyrie",
    r"\briverun\b": "Riverrun",
}

# Westeros alias and nickname resolution dictionary
WESTEROS_ALIASES = {
    r"\bkingslayer\b": "Jaime Lannister (The Kingslayer)",
    r"\bthe imp\b": "Tyrion Lannister (The Imp)",
    r"\bhalfman\b": "Tyrion Lannister",
    r"\bonion knight\b": "Davos Seaworth (The Onion Knight)",
    r"\blittlefinger\b": "Petyr Baelish (Littlefinger)",
    r"\bthe hound\b": "Sandor Clegane (The Hound)",
    r"\bthe mountain\b": "Gregor Clegane (The Mountain That Rides)",
    r"\byoung wolf\b": "Robb Stark (The Young Wolf)",
    r"\bred viper\b": "Oberyn Martell (The Red Viper)",
    r"\bqueen of thorns\b": "Olenna Tyrell (The Queen of Thorns)",
    r"\blady stoneheart\b": "Catelyn Stark (Lady Stoneheart)",
    r"\bbloodraven\b": "Brynden Rivers (Bloodraven / Three-Eyed Crow)",
    r"\bthree[-\s]eyed crow\b": "Brynden Rivers (Three-Eyed Crow)",
    r"\begg\b": "Aegon V Targaryen (Egg)",
    r"\byoung griff\b": "Aegon VI Targaryen (Young Griff)",
    r"\bthe spider\b": "Varys (The Spider)",
    r"\bblackfish\b": "Brynden Tully (The Blackfish)",
    r"\bbarristan the bold\b": "Barristan Selmy (Barristan the Bold)",
    r"\bmad king\b": "Aerys II Targaryen (The Mad King)",
}

# TV Series / HBO markers
SERIES_PATTERNS = [
    r"\b(tv show|series|hbo|season \d|actor|actress|emilia clarke|kit harington|peter dinklage|house of the dragon|hotd)\b",
    r"\b(show ending|differs in the show|in the tv show|show vs book|book vs show)\b"
]

# Casual chat patterns
CASUAL_PATTERNS = [
    r"^(hi|hello|hey|greetings|hail|good\s+(morning|afternoon|evening|day))(\s+(grand\s+)?maester)?[\s!.,?]*$",
    r"^who\s+are\s+you[\s?]*$",
    r"^(what\s+can\s+you\s+do|how\s+can\s+you\s+help\s+me|what\s+is\s+your\s+purpose|help)[\s?]*$",
    r"\b(valar\s+morghulis|valar\s+dohaeris)\b",
    r"^(thank\s+you|thanks|much\s+obliged|farewell|goodbye)(\s+(grand\s+)?maester)?[\s!.,?]*$",
    r"^(how\s+are\s+you|how\s+is\s+the\s+weather|tell\s+me\s+a\s+joke|are\s+you\s+alive)[\s!.,?]*$"
]

# Out-of-Universe markers (modern tech, science, coding, external philosophy)
OUT_OF_UNIVERSE_PATTERNS = [
    r"\b(python|javascript|code|algorithm|database|api|machine learning|physics|quantum|calculus)\b",
    r"\b(stock market|cryptocurrency|blockchain|real estate|modern medicine|antibiotics)\b",
    r"\b(meaning of life|stoicism|nietzsche|aristotle|kant|democracy|capitalism)\b"
]


def classify_domain(query: str) -> str:
    """
    Categorizes the user inquiry across universal domains:
    - 'casual_chat'
    - 'series_lore'
    - 'out_of_universe'
    - 'book_canon'
    """
    cleaned = query.strip().lower()
    
    for pat in CASUAL_PATTERNS:
        if re.search(pat, cleaned):
            return "casual_chat"

    for pat in SERIES_PATTERNS:
        if re.search(pat, cleaned):
            return "series_lore"

    for pat in OUT_OF_UNIVERSE_PATTERNS:
        if re.search(pat, cleaned):
            return "out_of_universe"

    return "book_canon"


def correct_spelling(query: str) -> Tuple[str, List[str]]:
    """Detects and corrects common spelling mistakes and phonetics."""
    corrected = query
    changes_made = []
    
    for pattern, replacement in COMMON_SPELLING_CORRECTIONS.items():
        if re.search(pattern, corrected, re.IGNORECASE):
            old = corrected
            corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
            if old != corrected:
                changes_made.append(f"Corrected spelling to '{replacement}'")
                
    return corrected, changes_made


def resolve_westeros_aliases(query: str) -> Tuple[str, List[str]]:
    """Enriches query by resolving Westeros nicknames to their canonical names."""
    enriched = query
    expansions = []
    for pattern, expansion in WESTEROS_ALIASES.items():
        if re.search(pattern, enriched, re.IGNORECASE):
            if not any(name_part.lower() in enriched.lower() for name_part in expansion.split()[:2]):
                enriched = re.sub(pattern, f"{expansion}", enriched, flags=re.IGNORECASE)
                expansions.append(expansion)
    return enriched, expansions


def enrich_entity_query(query: str) -> Tuple[str, bool]:
    """Detects broad biographical questions and appends appendix anchors."""
    cleaned = query.strip()
    is_broad = bool(re.search(
        r"^(who\s+is|tell\s+me\s+about|what\s+is\s+the\s+story\s+of|explain\s+who|describe)\s+([a-zA-Z\s]+)",
        cleaned,
        re.IGNORECASE
    ))
    
    if is_broad:
        return f"{cleaned} biography character history lineage appendix summary", True
    
    return cleaned, False
