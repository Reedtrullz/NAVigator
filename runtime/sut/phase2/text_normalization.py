import unicodedata


def normalize_match_text(text: str) -> str:
    folded = unicodedata.normalize("NFC", text.casefold()).translate(
        str.maketrans({"æ": "ae", "ø": "o", "å": "aa"}))
    return "".join(ch for ch in unicodedata.normalize("NFKD", folded)
                   if not unicodedata.combining(ch))
