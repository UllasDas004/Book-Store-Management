from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.api.books import router as book_router
from src.db.database import engine, Base
from src.models.book import Book
from src.models.user import User
from src.models.interaction import CartItem, Favourite, Sale
from src.models.requisition import Requisition
from src.api.auth import router as auth_router
from src.api.sales import router as sales_router
from src.api.reviews import router as review_router

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.include_router(book_router)
app.include_router(auth_router)
app.include_router(sales_router)
app.include_router(review_router)

@app.get("/")
def read_root():
    return {"Message": "Hello Bookstore!"}