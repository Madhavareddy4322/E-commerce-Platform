# 🛒 E-Commerce Platform (Django Full-Stack Project)

A full-stack **E-Commerce web application** built using **Python (Django)** with **HTML, CSS, JavaScript, Bootstrap**, and **MySQL/SQLite**.  
The platform supports product listings, categories, cart and checkout flow, coupon discounts, wishlist, user authentication, and a powerful **Admin Dashboard** for sales and inventory analytics.

---

## 🚀 Features

### 🧭 User Features
- Product catalog with category, price, and keyword filters  
- Product detail pages with image, description, and average rating  
- Add to cart, update quantity, and checkout  
- Apply coupon codes for discounts  
- View and track past orders  
- Add/remove items from Wishlist  
- Write and edit product reviews (only after purchase)

### 🧩 Admin Features
- Manage products, categories, and orders via Django Admin  
- Custom Admin Dashboard:
  - Total orders today  
  - Monthly revenue chart (Chart.js)  
  - Low-stock product alerts  

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-------------|
| Backend | Python, Django |
| Database | SQLite / MySQL |
| Frontend | HTML, CSS, JS, Bootstrap 5 |
| Analytics | Chart.js |
| Payment (mock) | Razorpay Sandbox / Simulated |
| Auth | Django’s built-in authentication |

---

## 📁 Project Structure

ecommerce_site/
│
├── ecommerce_site/ # Project configuration (settings, URLs)
│ ├── settings.py
│ ├── urls.py
│ └── ...
│
├── shop/ # Main app (business logic)
│ ├── models.py # Category, Product, Order, Review, Wishlist, etc.
│ ├── views.py # All view functions
│ ├── urls.py # App-level URLs
│ ├── forms.py # Checkout, search, and review forms
│ ├── cart.py # Session-based cart logic
│ └── templates/shop/ # HTML templates
│ ├── base.html
│ ├── home.html
│ ├── product_detail.html
│ ├── cart_detail.html
│ ├── checkout.html
│ ├── order_success.html
│ ├── my_orders.html
│ ├── wishlist_list.html
│ ├── admin_dashboard.html
│ └── ...
│
├── static/ # CSS, JS, images
│ ├── css/style.css
│ ├── js/script.js
│ └── images/
│
├── media/ # Uploaded product images
├── db.sqlite3 # Default database
├── manage.py
└── README.md


---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/ecommerce_site.git
cd ecommerce_site

2️⃣ Create and Activate Virtual Environment
python -m venv venv
venv\Scripts\activate        # On Windows
# source venv/bin/activate   # On macOS/Linux

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Apply Migrations
python manage.py makemigrations
python manage.py migrate

5️⃣ Create Superuser
python manage.py createsuperuser

6️⃣ Run the Server
python manage.py runserver


Visit http://127.0.0.1:8000/

🧠 How It Works

Products and Categories are managed through the admin interface.

Users can browse products, add to cart, and place orders.

Orders are stored and displayed under “My Orders”.

Coupons and discounts are validated server-side at checkout.

Admin Dashboard summarizes daily sales, revenue, and stock status.

🧩 Optional Enhancements

REST API endpoints with Django REST Framework (DRF)

Real-time payments integration (Razorpay/Stripe)

Email order confirmation

User profile management & saved addresses

Product search with Elasticsearch

Docker deployment setup

📸 Screenshots (optional)

(Add your actual screenshots here)

Home Page – Product listing and search

Product Detail – Review and wishlist

Cart & Checkout – Order summary + coupon field

Admin Dashboard – Revenue chart & low-stock alerts

🧑‍💻 Author

Your Name
📧 your.email@example.com

💼 LinkedIn
 • GitHub

📝 License

This project is licensed under the MIT License – you are free to use and modify it for learning or portfolio purposes.


---

### ✅ Next Step for You
- Save this as `README.md` in your root folder.  
- Replace `yourusername`, email, and LinkedIn with your info.  
- Add screenshots later to make it visually appealing.

Would you like me to generate a **requirements.txt** for this project next (with all Python packages and versions)?
