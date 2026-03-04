from sqlalchemy import Column, Integer, String, Float, Text
from src.db.database import Base
from sqlalchemy.orm import relationship

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String, unique=True, nullable=False)
    title = Column(String, index=True, nullable=False)
    author = Column(String, index=True, nullable=False)
    publisher = Column(String, index=True, nullable=False)
    edition = Column(String)
    publication_year = Column(Integer)
    price = Column(Float, nullable=False)
    category = Column(String,index=True, nullable=False)
    description = Column(Text)
    cover_image_url = Column(String)
    discount_percentage = Column(Float, default=0.0)
    short_reviews = Column(Text)
    stock_quantity = Column(Integer, default=0, nullable=False)

    cart_items = relationship("CartItem", back_populates="book")
    favourites = relationship("Favourite", back_populates="book")
    sales = relationship("Sale", back_populates="book")
    requisitions = relationship("Requisition", back_populates="book")
    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")
