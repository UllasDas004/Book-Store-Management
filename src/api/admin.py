from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from src.db.database import get_db
from src.models.user import User
from src.models.book import Book
from src.models.interaction import Sale
from src.api.deps import get_current_admin_user

router = APIRouter(
    prefix = "/admin",
    tags = ["Admin Dashboard"]
)

@router.get("/dashboard")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    total_customers = db.query(func.count(User.id)).filter(User.role == "customer").scalar()

    total_books = db.query(func.count(Book.id)).scalar()

    total_orders = db.query(func.count(Sale.id)).scalar()

    total_revenue = db.query(func.sum(Sale.total_price)).scalar() or 0.0

    low_stock_books = db.query(Book).filter(Book.stock_quantity < 10).all()

    # Advanced Analytics: Top 5 Best Selling Books
    top_books_data = db.query(
        Book.title,
        func.sum(Sale.quantity).label("total_sold")
    ).join(Sale, Book.id == Sale.book_id).group_by(Book.id).order_by(desc("total_sold")).limit(5).all()

    # Advanced Analytics: Top 5 Customers by Revenue
    top_customers_data = db.query(
        User.username,
        User.email,
        func.sum(Sale.total_price).label("total_spent")
    ).join(Sale, User.id == Sale.user_id).group_by(User.id).order_by(desc("total_spent")).limit(5).all()

    return {
        "metrics": {
            "total_customers": total_customers,
            "total_books_in_catalog": total_books,
            "total_revenue": total_revenue,
            "total_orders": total_orders
        },
        "advanced_analytics": {
            "top_selling_books": [
                {"title": book.title, "total_sold": book.total_sold} for book in top_books_data
            ],
            "top_customers": [
                {"username": customer.username, "email": customer.email, "total_spent": customer.total_spent} for customer in top_customers_data
            ]
        },
        "alerts": {
            "low_stock_count": len(low_stock_books),
            "low_stock_items": [
                {"id": book.id, "title": book.title, "stock_quantity": book.stock_quantity}
                for book in low_stock_books
            ]
        }
    }