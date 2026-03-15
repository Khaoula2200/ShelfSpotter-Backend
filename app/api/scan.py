from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from app.services.ocr_service import extract_text_from_image
from app.services.google_books import search_google_books, pick_best_match
from app.services.utils import clean_ocr_text

router = APIRouter()

@router.post("/")
async def scan_shelf(image: UploadFile = File(...)):
    # Call OCR service
    detected_titles = await extract_text_from_image(image)

    books = []
    for spine_title in detected_titles:
        cleaned_title = clean_ocr_text(spine_title)         # remove numbers, punctuation, lowercase
        print(f'Cleaned OCR text: \'{cleaned_title}\' from original \'{spine_title}\'')  # Debug log
        candidates = search_google_books(cleaned_title)     # query Google Books
        best_book = pick_best_match(cleaned_title, candidates)

        books.append({
            "title": best_book["title"],
            "author": best_book["author"],
            "confidence": 1.0
        })

    # Optional: pick top 3 as temporary recommendations
    top_picks = books[:3]

    return JSONResponse({
        "books": books,
        "top_picks": top_picks
    })
