from fastapi import APIRouter


router = APIRouter(
    prefix = "/books",
    tags = ["Books"]
)

@router.get("/")
def get_all_books():
    return {"message": "Here are all the books!"}

@router.get("/{book_id}")
def get_single_book(book_id: int):
    return {"message": f"Here is the book with id: {book_id}"}


