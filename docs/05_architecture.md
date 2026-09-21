# Architecture – The Cozy Knot

## Application Factory Pattern
`backend/app.py` → `create_app()` registers extensions and blueprints.  
Allows easy testing and multiple configs.

## Blueprint Separation (matches use-case processes)

| Blueprint   | Responsibility                          |
|-------------|-----------------------------------------|
| main        | Landing, about                          |
| auth        | Login, register, profile, logout        |
| products    | Browse, search, detail                  |
| cart        | Add / update / remove cart items        |
| orders      | Checkout, payment simulation, invoice, my orders |
| admin       | Catalog, users, order status management |

## Security
- Flask-Login session management
- Werkzeug password hashing
- Flask-WTF CSRF protection on every form
- Role decorator `@admin_required`
- `is_active` flag for soft user disable

## Extensibility
- Swap SQLite → PostgreSQL via `DATABASE_URL`
- Replace payment simulation with real eSewa/Khalti SDK
- Add image upload (Pillow already in requirements)
- Future React/Vue frontend can consume the same routes or a JSON API layer
