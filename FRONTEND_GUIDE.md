# 🎨 Frontend Developer Guide: Bookstore Administration & Shopping Portal

Hello Frontend Developer! 👋 

This document is your complete roadmap for building a **Multi-Page Application (MPA)** or a robust Single Page Application (like Next.js/React Router) that consumes this FastAPI backend.

The backend is fully built, tested, and ready to go. It uses stateless **JWT Authentication** and supports two distinct user roles: `customer` and `admin`.

---

## 🏗️ Suggested Multi-Page Architecture

To build a comprehensive experience, we map the available backend endpoints to the following core pages/views:

### 1. Public Pages (No Auth Required)
*   **`/` (Home Page):** Featured books, newly added books (`sort_by=newest`), and search bar.
*   **`/books` (Catalog Page):** 
    *   **Features:** Pagination, fuzzy search by Title/Author/ISBN, grid/list view.
    *   **Sidebar Filters:** Filter by category, min price slider, max price slider, and "Sort By" dropdown.
    *   **Endpoints:** `GET /books/`
*   **`/books/:id` (Product Detail Page):** 
    *   **Features:** Book cover image, full description, price, "Add to Cart" button (if stock > 0), and customer reviews section.
    *   **Endpoints:** `GET /books/{id}`
*   **`/login` & `/register` (Auth Pages):**
    *   **Features:** Forms to authenticate. Store the returned `access_token` securely (e.g., HTTP-only cookie or LocalStorage) to attach to future API calls as a `Bearer {token}` header.
    *   **Endpoints:** `POST /auth/login` (Standard OAuth2 urlencoded form data), `POST /auth/register` (JSON payload).

---

### 2. Customer Portal (Requires `customer` or `admin` Role)
*   **`/profile` (My Account):**
    *   **Features:** View and edit personal details (address, phone number) and update passwords safely.
    *   **Endpoints:** `GET /users/me`, `PUT /users/me`, `PUT /users/me/password`
*   **`/cart` (Shopping Cart):**
    *   **Features:** View items, update quantities live (e.g., a `+` and `-` button), see total price, and a big "Checkout" button.
    *   **Endpoints:** `GET /sales/cart`, `PUT /sales/cart/{id}`, `DELETE /sales/cart/{id}`
*   **`/checkout/success` (Order Confirmation):**
    *   **Features:** Triggered immediately after the backend successfully processes the checkout transaction.
    *   **Endpoints:** `POST /sales/sale`
*   **`/orders` (Order History):**
    *   **Features:** A table of past purchases and their current delivery statuses.
    *   **Endpoints:** `GET /sales/history`
*   **`/favorites` (Wishlist):**
    *   **Features:** Books the user has favorited from the catalog page.
    *   **Endpoints:** `GET /favorites/`, `POST /favorites/`, `DELETE /favorites/{id}`

---

### 3. Admin Dashboard (Requires `admin` Role)
*   **`/admin` (Dashboard Overview):**
    *   **Features:** Big KPI cards (Total Revenue, Orders, Customers). Charts for Top 5 Best Selling Books and Top 5 Customers. A critical alert section for "Low Stock Inventory" (`stock_quantity < 10`).
    *   **Endpoints:** `GET /admin/dashboard`
*   **`/admin/inventory` (Stock Management):**
    *   **Features:** A data table of all books. Buttons to Edit price/stock and Upload Cover Images.
    *   **Endpoints:** `POST /books/`, `PUT /books/{id}`, `POST /books/{id}/cover`, `DELETE /books/{id}`
*   **`/admin/orders` (Order Fulfillment):**
    *   **Features:** View all customer orders across the system. Update statuses from "Pending" to "Shipped" or "Delivered".
    *   **Endpoints:** `PUT /sales/{id}/status` *(Note: requires ensuring a global order view is implemented if you want to track all users' orders, currently `/sales/history` is user-specific)*
*   **`/admin/requisitions` (Publisher Orders):**
    *   **Features:** The lifeline of the store. A UI to manually order restocks or a massive **"Auto-Restock Magic Button"** that calculates expected demand based on the last 3 months of sales to automatically draft publisher orders!
    *   **Endpoints:** `GET /requisitions/`, `POST /requisitions/`, `POST /requisitions/auto` (The magic button), `PUT /requisitions/{id}/receive` (Marking publisher delivery as arrived).

---

## 🛠️ Key Technical Implementations for the Frontend

1.  **Axios / Fetch Interceptors:** Set up a global interceptor that automatically attaches the `Authorization: Bearer <token>` header to every request if the user is logged in. Automatically redirect to `/login` if the API returns a `401 Unauthorized` or `403 Forbidden`.
2.  **State Management:** Use Redux, Zustand, or React Context to globally store the Shopping Cart count so the navbar cart icon is always accurate across multiple pages!
3.  **Visual Feedback (Toast Notifications):** Because the backend strictly validates data (like preventing duplicate reviews or ordering an out-of-stock book), you *must* catch `400` errors and display the backend's `detail` message in a sexy popup "Toast" notification for the user.
4.  **Static Images:** The backend returns image paths like `/static/images/cover.jpg`. When rendering an `<img src={...} />`, simply prepend the backend's base URL (e.g., `http://localhost:8000/static/images/cover.jpg`).

You are ready to build an incredible, production-grade application! 🚀

---

## 💻 React Code Snippets to Get Started

### 1. The Super Axios Interceptor (`src/api/axios.js`)
This automatically attaches your JWT token to every request and redirects users who aren't logged in!

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// Automatically attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Automatically handle unauthorized errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login'; // Redirect to login
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 2. Login Component Example (`src/pages/Login.jsx`)
Notice how we send `FormData` because OAuth2 strictly requires urlencoded data!

```javascript
import { useState } from 'react';
import api from '../api/axios';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      // OAuth2 requires form data, not JSON!
      const formData = new URLSearchParams();
      formData.append('username', email); // send email as 'username'
      formData.append('password', password);

      const response = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      
      // Save the token and redirect!
      localStorage.setItem('token', response.data.access_token);
      window.location.href = '/profile';
      
    } catch (err) {
      alert(err.response?.data?.detail || "Login failed");
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input type="email" placeholder="Email" onChange={e => setEmail(e.target.value)} required />
      <input type="password" placeholder="Password" onChange={e => setPassword(e.target.value)} required />
      <button type="submit">Log In</button>
    </form>
  );
}
```

### 3. Fetching the Catalog with Filters (`src/pages/Catalog.jsx`)
How to pass query parameters for complex sorting and filtering!

### 🔍 Advanced Search Bar Flexibilities
The `GET /books/` endpoint is incredibly powerful because it uses PostgreSQL's `pg_trgm` (Trigram) extensions under the hood. It doesn't just look for exact matches; it understands *similarity*. 

You can build a highly flexible Search Bar with the following UI approaches:

1.  **The "Omni-Search" Bar:** 
    *   Because the backend checks the `search` query against the **Title**, **Author**, AND **ISBN**, you do *not* need separate dropdowns for "Search by Title" vs "Search by Author". A single, clean text input is all the user needs! 
    *   *Example:* If a user types `"Rowling"`, it will find *Harry Potter* because it matches the Author column. If they type `"978-3-16"`, it will find the exact book by ISBN.
2.  **Typo-Tolerance (Fuzzy Searching):**
    *   The backend calculates a similarity score `> 0.3`. This means if a user accidentally types `"Harri Potter"` instead of `"Harry Potter"`, the backend will *still find it* and return it! It also automatically ranks the results, putting the highest similarity scores at the very top.
3.  **Live "As-You-Type" Search (Debouncing):**
    *   Instead of waiting for the user to press an "Enter" button, you can fetch results on every keystroke! 
    *   *Crucial Frontend Tip:* Use a **Debounce** hook (e.g., `useDebounce`) to wait 300ms after the user *stops* typing before calling the API. This prevents spamming the backend with 10 requests if they type "Harry" really fast.

```javascript
import { useState, useEffect } from 'react';
import api from '../api/axios';

// A simple debounce hook implementation
function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);
  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(handler);
  }, [value, delay]);
  return debouncedValue;
}

export default function Catalog() {
  const [books, setBooks] = useState([]);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('newest');
  
  // Wait 300ms after the user stops typing
  const debouncedSearch = useDebounce(search, 300);

  const fetchBooks = async () => {
    try {
      const response = await api.get('/books/', {
        params: {
          search: debouncedSearch || null, // Uses the Delayed Search Term!
          sort_by: sortBy,
          limit: 20
        }
      });
      setBooks(response.data);
    } catch (error) {
      console.error("Failed to fetch books", error);
    }
  };

  // Re-fetch ONLY when the debounced search or sorting changes
  useEffect(() => {
    fetchBooks();
  }, [debouncedSearch, sortBy]); 

  return (
    <div>
      <input 
        placeholder="Try 'Harri Potter' or 'Tolkien'..." 
        value={search} 
        onChange={e => setSearch(e.target.value)} 
      />
      <select value={sortBy} onChange={e => setSortBy(e.target.value)}>
        <option value="newest">Newest First</option>
        <option value="price_asc">Price: Low to High</option>
        <option value="price_desc">Price: High to Low</option>
      </select>

      <div className="book-grid">
        {books.map(book => (
          <div key={book.id}>
            <h3>{book.title}</h3>
            <p className="author">By {book.author}</p>
            <p>${book.price}</p>
            <img src={`http://localhost:8000${book.cover_image_url}`} alt="cover" />
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 4. Live Shopping Cart Component (`src/components/Cart.jsx`)
This component shows how to fetch the cart, calculate totals, update quantities, and process a checkout.

```javascript
import { useState, useEffect } from 'react';
import api from '../api/axios';

export default function ShoppingCart() {
  const [cart, setCart] = useState({ items: [], total_price: 0 });

  const fetchCart = async () => {
    try {
      const response = await api.get('/sales/cart');
      setCart(response.data);
    } catch (err) {
      console.error("Error fetching cart", err);
    }
  };

  useEffect(() => { fetchCart(); }, []);

  const updateQuantity = async (itemId, newQuantity) => {
    if (newQuantity < 0) return;
    try {
      await api.put(`/sales/cart/${itemId}`, { quantity: newQuantity });
      fetchCart(); // Refresh the cart after update
    } catch (err) {
      alert(err.response?.data?.detail || "Could not update quantity");
    }
  };

  const handleCheckout = async () => {
    try {
      await api.post('/sales/sale');
      alert("Checkout Successful! 🎉");
      setCart({ items: [], total_price: 0 }); // Empty cart locally
      window.location.href = '/checkout/success';
    } catch (err) {
      alert(err.response?.data?.detail || "Checkout Failed!");
    }
  };

  return (
    <div className="cart-container">
      <h2>Your Cart</h2>
      {cart.items.length === 0 ? <p>Cart is empty</p> : (
        <>
          {cart.items.map(item => (
            <div key={item.id} className="cart-item">
              <span>{item.book.title}</span>
              <button onClick={() => updateQuantity(item.id, item.quantity - 1)}>-</button>
              <span>{item.quantity}</span>
              <button onClick={() => updateQuantity(item.id, item.quantity + 1)}>+</button>
            </div>
          ))}
          <h3>Total: ${cart.total_price.toFixed(2)}</h3>
          <button onClick={handleCheckout} className="checkout-btn">Checkout Now</button>
        </>
      )}
    </div>
  );
}
```

### 5. Multi-Part File Upload for Books (`src/pages/admin/AddCover.jsx`)
Admins need to upload images. Because images are physical files, you must use `multipart/form-data` instead of standard JSON.

```javascript
import { useState } from 'react';
import api from '../../api/axios';

export default function BookCoverUpload({ bookId }) {
  const [file, setFile] = useState(null);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    // Use FormData for file uploads!
    const formData = new FormData();
    formData.append("file", file);

    try {
      await api.post(`/books/${bookId}/cover`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      alert("Cover uploaded successfully!");
    } catch (err) {
      alert(err.response?.data?.detail || "Upload failed");
    }
  };

  return (
    <form onSubmit={handleUpload}>
      <input 
        type="file" 
        accept="image/*" 
        onChange={e => setFile(e.target.files[0])} 
      />
      <button type="submit">Upload Cover</button>
    </form>
  );
}
```

### 6. Admin Data Dashboard Chart Fetching (`src/pages/admin/Dashboard.jsx`)
The analytics endpoint is highly optimized. Here is how you fetch it to feed into a charting library like `recharts` or `chart.js`.

```javascript
import { useState, useEffect } from 'react';
import api from '../../api/axios';
// import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await api.get('/admin/dashboard');
        setStats(response.data);
      } catch (err) {
        console.error("Failed to load dashboard data");
      }
    };
    fetchDashboard();
  }, []);

  if (!stats) return <p>Loading Analytics...</p>;

  return (
    <div className="dashboard">
      <h1>Store Overview</h1>
      <div className="kpi-cards">
        <div className="card">Total Revenue: ${stats.total_revenue.toFixed(2)}</div>
        <div className="card">Total Orders: {stats.total_orders}</div>
        <div className="card">Inventory Size: {stats.total_books} Books</div>
      </div>

      {stats.low_stock_alerts.length > 0 && (
        <div className="alert-box">
          <h2>⚠️ LOW STOCK WARNING</h2>
          <ul>
            {stats.low_stock_alerts.map(book => (
              <li key={book.id}>
                {book.title} - Only {book.stock_quantity} left!
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Example: Feed stats.top_selling_books into an actual Chart library here */}
      <h2>Top Selling Books</h2>
      <ul>
        {stats.top_selling_books.map((b, idx) => (
           <li key={b.book_id}>#{idx + 1} {b.title} ({b.total_sold} sold)</li>
        ))}
      </ul>
    </div>
  );
}
```
