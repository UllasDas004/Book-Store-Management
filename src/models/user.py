from sqlalchemy import Column, Integer, String, Boolean
from src.db.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="customer", nullable=False)  # "admin" or "customer"
    is_active = Column(Boolean, default=True)
    address = Column(String)
    phone_number = Column(String)

    cart_items = relationship("CartItem", back_populates="user")
    favourites = relationship("Favourite", back_populates="user")
    sales = relationship("Sale", back_populates="user")
    requisitions = relationship("Requisition", back_populates="user")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")