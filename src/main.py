from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
from src.api.favourites import router as favourite_router
from src.api.users import router as user_router
from src.api.admin import router as admin_router
from src.api.requisitions import router as requisition_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.include_router(book_router)
app.include_router(auth_router)
app.include_router(sales_router)
app.include_router(review_router)
app.include_router(favourite_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(requisition_router)

@app.get("/")
def read_root():
    return {"Message": "Hello Bookstore!"}