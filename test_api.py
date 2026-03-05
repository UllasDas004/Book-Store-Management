import httpx
import time
import os
import sys

# Base URL for the API
BASE_URL = "http://127.0.0.1:8000"

def print_result(step_name, success, details=""):
    if success:
        print(f"[OK] {step_name}")
    else:
        print(f"[FAIL] {step_name} - {details}")

def run_tests():
    print("-> Starting API Tests...\n")
    
    # Let's generate a unique username so we can run tests multiple times
    timestamp = int(time.time())
    customer_username = f"testuser_{timestamp}"
    customer_email = f"{customer_username}@example.com"
    customer_password = "testpassword123"
    
    # ---------------------------------------------------------
    # 1. AUTH & USERS
    # ---------------------------------------------------------
    print("--- User Authentication & Profile ---")
    
    # Register Customer
    res = httpx.post(f"{BASE_URL}/auth/register", json={
        "username": customer_username,
        "email": customer_email,
        "password": customer_password
    })
    print_result("Register Customer", res.status_code in [200, 201], res.text)
    
    # Login Customer
    res = httpx.post(f"{BASE_URL}/auth/login", data={
        "username": customer_email, # OAuth2 uses username field for email
        "password": customer_password
    })
    print_result("Login Customer", res.status_code == 200, res.text)
    customer_token = res.json().get("access_token")
    customer_headers = {"Authorization": f"Bearer {customer_token}"}
    
    # Get Profile
    res = httpx.get(f"{BASE_URL}/users/me", headers=customer_headers)
    print_result("Get Profile", res.status_code == 200, res.text)
    
    # Update Profile
    res = httpx.put(f"{BASE_URL}/users/me", headers=customer_headers, json={
        "address": "123 Test St",
        "phone_number": "555-1234"
    })
    print_result("Update Profile", res.status_code == 200 and res.json().get("address") == "123 Test St", res.text)
    
    # ---------------------------------------------------------
    # 2. BOOKS (Public Browsing)
    # ---------------------------------------------------------
    print("\n--- Book Catalog ---")
    
    res = httpx.get(f"{BASE_URL}/books/")
    print_result("Get All Books", res.status_code == 200, res.text)
    
    print("\n--- Sales & Cart ---")
    # Test Cart flow
    books = httpx.get(f"{BASE_URL}/books/").json()
    if books:
        book_id = books[0]["id"]
        print(f"Testing with book ID: {book_id}")
        
        # Add to cart
        res = httpx.post(f"{BASE_URL}/sales/", headers=customer_headers, json={
            "book_id": book_id,
            "quantity": 1
        })
        print_result("Add to Cart", res.status_code == 201, res.text)
        
        # View cart
        res = httpx.get(f"{BASE_URL}/sales/cart", headers=customer_headers)
        print_result("View Cart", res.status_code == 200, res.text)
        cart = res.json()
        
        if cart and len(cart.get("items", [])) > 0:
            item_id = cart["items"][0]["id"]
            
            # Update quantity
            res = httpx.put(f"{BASE_URL}/sales/cart/{item_id}", headers=customer_headers, json={
                "quantity": 2
            })
            print_result("Update Cart Quantity", res.status_code == 200, res.text)
            
            # Checkout
            res = httpx.post(f"{BASE_URL}/sales/sale", headers=customer_headers)
            print_result("Checkout Cart", res.status_code == 201, res.text)
            
            # View History
            res = httpx.get(f"{BASE_URL}/sales/history", headers=customer_headers)
            print_result("View Order History", res.status_code == 200, res.text)
            
            # Add Review
            res = httpx.post(f"{BASE_URL}/books/{book_id}/reviews", headers=customer_headers, json={
                "rating": 5,
                "comment": "Great testing book!"
            })
            print_result("Add Book Review", res.status_code == 201, res.text)
            
            # Add to Favorites
            res = httpx.post(f"{BASE_URL}/favourites/", headers=customer_headers, json={
                "book_id": book_id
            })
            print_result("Add to Favorites", res.status_code == 201, res.text)
            
            # View Favorites
            res = httpx.get(f"{BASE_URL}/favourites/", headers=customer_headers)
            print_result("View Favorites", res.status_code == 200, res.text)
    else:
        print("⚠️ No books in database to test cart/checkout flows.")

    print("\n[DONE] API Tests Completed.")

if __name__ == "__main__":
    run_tests()
