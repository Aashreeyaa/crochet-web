# System Design – Crochet Stitch Shop

## High-Level Architecture

```
┌─────────────┐     HTTP      ┌──────────────────┐     SQL      ┌────────────┐
│  Browser    │◄─────────────►│  Flask App       │◄────────────►│  SQLite /  │
│  (Jinja2 +  │               │  (Blueprints)    │              │  PostgreSQL│
│   Bootstrap)│               └──────────────────┘              └────────────┘
└─────────────┘                        │
                                       │ simulated
                                       ▼
                              ┌──────────────────┐
                              │ Payment Gateway  │
                              │ Delivery Service │
                              └──────────────────┘
```

## Layered Design

1. **Presentation** – Jinja2 templates + Bootstrap 5 + custom CSS/JS
2. **Application** – Flask blueprints (auth, products, cart, orders, admin)
3. **Domain** – SQLAlchemy models (User, Product, Category, CartItem, Order, OrderItem)
4. **Infrastructure** – SQLite (dev), session auth, CSRF protection

## Key Flows

### Place Order (happy path)
1. Customer adds items → CartItem rows
2. Checkout form validates shipping + payment method
3. Order + OrderItems created (price snapshot)
4. Stock decremented
5. Payment simulated → status = paid, invoice generated
6. Cart cleared
7. Redirect to order detail

### Update Delivery Status
1. Admin opens order
2. Selects new status (processing / shipped / delivered…)
3. Timestamps (`shipped_at`, `delivered_at`) set when appropriate
4. Customer sees updated status under “My Orders”

## Non-Functional
- CSRF on all forms
- Password hashing (Werkzeug)
- Role checks (`@admin_required`)
- Responsive UI (mobile-first)
- Free shipping over Rs 1,500
