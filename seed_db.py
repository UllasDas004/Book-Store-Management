import requests
import random
from sqlalchemy.orm import Session
from src.db.database import SessionLocal
from src.models.book import Book
from src.models.user import User
from src.core.security import get_password_hash
import src.models.interaction
import src.models.requisition

SEARCH_TERMS = ["subject:fantasy","subject:romance","subject:mythology","subject:scifi","subject:thriller","subject:action","subject:adventure","subject:history","subject:biography","subject:mystery","subject:comedy"]

BOOKS_PER_CATEGORY = 10

def fetch_books_from_google(query, max_results):
    print(f"Fetching {max_results} books for query: '{query}'...")
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={max_results}"
    response = requests.get(url)
    return response.json().get('items',[]) if response.status_code == 200 else []

def ensure_vendors_exists(db: Session):
    vendor_data = [
        {"first": "Ullas", "last": "Das", "username": "ullasdas", "email": "ullasdas123@gmail.com"},
        {"first": "Chittajit", "last": "Nath", "username": "chittajitnath", "email": "chitta@gmail.com"},
        {"first": "Ishita", "last": "Roy", "username": "ishitaroy", "email": "ishita123@gmail.com"}
    ]

    vendor_ids = []

    for v in vendor_data:
        existing = db.query(User).filter(User.email == v["email"]).first()
        if existing:
            vendor_ids.append(existing.id)

            if existing.role != "admin":
                existing.role = "admin"
                db.commit()
        else:
            new_vendor = User(
                first_name=v["first"],
                last_name=v["last"],
                username=v["username"],
                email=v["email"],
                hashed_password=get_password_hash("password123"), # Default password
                role="admin", # Make them an admin!
                is_active=True
            )
            db.add(new_vendor)
            db.commit()
            db.refresh(new_vendor)
            vendor_ids.append(new_vendor.id)
            print(f"Created Admin Vendor: {v['first']} {v['last']}")

    return vendor_ids

def seed_database():
    db = SessionLocal()
    books_added = 0

    try:
        print("Setting up marketplace vendors...")
        admin_ids = ensure_vendors_exists(db)

        for term in SEARCH_TERMS:
            google_books = fetch_books_from_google(term,BOOKS_PER_CATEGORY)

            for item in google_books:
                volume_info = item.get("volumeInfo", {})

                isbn = None
                for identifier in volume_info.get('industryIdentifiers', []):
                    if identifier.get('type') == 'ISBN_13':
                        isbn = identifier.get('identifier')
                        break
                
                if not isbn:
                    isbn = f"978{random.randint(1000000000000, 9999999999999)}"

                if db.query(Book).filter(Book.isbn == isbn).first():
                    continue

                images = volume_info.get('imageLinks', {})
                cover_url = images.get('thumbnail', '').replace('http:', 'https:')
                pub_date = volume_info.get('publishedDate','2020')
                pub_year = int(pub_date[:4]) if len(pub_date) >= 4 and pub_date[:4].isdigit() else 2020
                authors = volume_info.get('authors', ["Unknown Author"])
                categories = volume_info.get('categories', ["General"])

                random_admin_id = random.choice(admin_ids)

                new_book = Book(
                    isbn = isbn,
                    title = volume_info.get('title', 'Unknown Title')[:255],
                    author = ", ".join(authors)[:255],
                    publisher = volume_info.get('publisher', 'Independent')[:255],
                    edition = "1st",
                    publication_year = pub_year,
                    price = round(random.uniform(100, 2000), 2),
                    category = categories,
                    description = volume_info.get('description', 'No description available.'),
                    cover_image_url = cover_url,
                    discount_percentage = round(random.choice([0.0,0.0,10.0,15.0,20.0]), 2),
                    stock_quantity = random.randint(15, 100),
                    is_active = True,
                    admin_id = random_admin_id
                )

                db.add(new_book)
                books_added += 1
            
            db.commit()
            print(f"\n✅ SUCCESS: Instantly seeded {books_added} books across 3 different active Vendors!")

    except Exception as e:
        db.rollback()
        print(f"❌ ERROR saving to database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting database seeding...")
    seed_database()
    print("\n🎉 Database seeding completed!")