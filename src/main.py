from fastapi import FastAPI
from src.api.books import router as book_router
from src.db.database import engine, Base
from src.models.book import Book
from src.models.user import User
from src.models.interaction import CartItem, Favourite, Sale
from src.models.requisition import Requisition

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(book_router)

@app.get("/")
def read_root():
    return {"Message": "Hello Bookstore!"}