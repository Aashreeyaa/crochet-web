# The Cozy Knot 🧶

Full-stack **crochet e-commerce** web application built with **Flask**, mapped 1:1 to the provided **Use Case Diagram**.

Designed as a clean, reactive, undergraduate Software Engineering project — unique soft-yarn aesthetic (not a copy of the sneaker reference).

## Features (mapped to Use Cases)

| Actor            | Use Cases                                      |
|------------------|------------------------------------------------|
| **Customer**     | Login / Authenticate, Browse Products, Add to Cart, Place Order, My Orders, Make Payment |
| **Admin**        | Login, Manage Users, Manage Catalog, Manage Orders, Update Delivery Status |
| **Payment Gateway** | Process Payment (included from Place Order / Make Payment) |
| **Delivery Service** | Update Delivery Status (admin-driven) |

Also implements: Generate Invoice, stock management, free-shipping threshold, role-based access.

## Tech Stack

- **Backend**: Flask 3 + SQLAlchemy + Flask-Login + Flask-WTF
- **Database**: SQLite (easy swap to PostgreSQL)
- **Frontend**: Bootstrap 5 + custom CSS (soft terracotta / lavender yarn theme) + light JS
- **Auth**: Session-based + RBAC (customer / admin)

## Directory Structure

```
crochet-stitch-shop/
├── docs/                          # Complete documentation
│   ├── 01_use_case_diagram.md
│   ├── 02_system_design.md
│   ├── 03_database_schema.md
│   ├── 04_api_documentation.md
│   ├── 05_architecture.md
│   └── 06_deployment.md
├── backend/
│   ├── app.py                     # Application factory
│   ├── config.py
│   ├── extensions.py
│   ├── models/                    # User, Product, Category, Cart, Order
│   ├── routes/                    # Blueprints (auth, products, cart, orders, admin)
│   ├── templates/                 # Full responsive UI
│   ├── static/css|js|images
│   ├── requirements.txt
│   └── run.py
├── database/
│   └── init_db.py                 # Create tables + seed data
└── README.md
```

## Quick Start

```bash
cd crochet-stitch-shop

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r backend/requirements.txt

# Seed database (creates tables + demo products + users)
PYTHONPATH=. python database/init_db.py

# Run
PYTHONPATH=. python backend/run.py
```

Open **http://127.0.0.1:5000**

### Demo Accounts

| Role     | Email                     | Password  |
|----------|---------------------------|-----------|
| Admin    | admin@The Cozy Knot.com      | admin123  |
| Customer | customer@The Cozy Knot.com   | cust123   |

## Design Notes (vs Sneaky Point reference)

- Completely new visual language: warm cream + terracotta + dusty rose (yarn aesthetic) instead of dark/orange sneakers.
- Domain models adapted for crochet (yarn type, size, colors, categories like Amigurumi / Blankets).
- Same solid Flask patterns (blueprints, application factory, CSRF, RBAC) but unique flows and UI.
- Reactive touches: cart badge, quantity steppers, sticky checkout summary, status pills, print-ready invoice.

## License

MIT — Undergraduate Software Engineering project.
