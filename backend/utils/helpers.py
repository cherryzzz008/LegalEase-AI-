import re


def safe_filename(name: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*]+', '_', name)
    cleaned = re.sub(r'\s+', '_', cleaned.strip())

    return cleaned or "legal_document"