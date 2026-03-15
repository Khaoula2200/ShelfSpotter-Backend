import requests
import os
from rapidfuzz import process, fuzz

GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")
if not GOOGLE_BOOKS_API_KEY:
    raise ValueError("GOOGLE_BOOKS_API_KEY environment variable not set")

def search_google_books(query: str, max_results=5):
    """
    Query Google Books API with a cleaned string and return top results.
    """
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "maxResults": max_results,
        "key": GOOGLE_BOOKS_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    print(f"Google Books API response for query '{query}': {data}")  # Debug log
    books = []
    for item in data.get("items", []):
        info = item["volumeInfo"]
        books.append({
            "title": info.get("title"),
            "author": ", ".join(info.get("authors", [])),
            "categories": info.get("categories", []),
            "description": info.get("description", ""),
        })
    return books

def pick_best_match(ocr_text: str, candidates):
    """
    Use fuzzy matching to pick the closest book title from candidates.
    """
    if not candidates:
        return {"title": ocr_text, "author": "Unknown"}
    
    best_score = 0
    best_book = None
    for book in candidates:
        title = book["title"].lower()
        score = fuzz.token_set_ratio(ocr_text.lower(), title)
        if score > best_score:
            best_score = score
            best_book = book
    
    # threshold to avoid bad matches
    if best_score < 50:
        return {"title": ocr_text, "author": "Unknown"}
    print(f"Best match for '{ocr_text}' is '{best_book['title']}' with score {best_score}")  # Debug log
    return best_book