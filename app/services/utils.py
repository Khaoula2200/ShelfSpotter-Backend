import re

def clean_ocr_text(text: str) -> str:
    """
    Remove numbers, punctuation, extra spaces and lowercase the text.
    """
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)  # remove anything that is not letters
    text = re.sub(r"\s+", " ", text).strip()
    return text