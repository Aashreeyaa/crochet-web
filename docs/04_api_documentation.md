# API / Route Documentation – Crochet Stitch Shop

This project is primarily **server-rendered** (Jinja2). Routes below act as the application API surface.

## Public

| Method | Path                    | Description              |
|--------|-------------------------|--------------------------|
| GET    | `/`                     | Home (featured + latest) |
| GET    | `/about`                | About page               |
| GET    | `/products/`            | Product list + filters   |
| GET    | `/products/<slug>`      | Product detail           |

## Authentication

| Method | Path              | Description        |
|--------|-------------------|--------------------|
| GET/POST | `/auth/login`   | Sign in            |
| GET/POST | `/auth/register`| Create account     |
| GET    | `/auth/logout`    | Sign out           |
| GET/POST | `/auth/profile` | Edit profile       |

## Cart (login required)

| Method | Path                         | Description     |
|--------|------------------------------|-----------------|
| GET    | `/cart/`                     | View cart       |
| POST   | `/cart/add/<product_id>`     | Add item        |
| POST   | `/cart/update/<item_id>`     | Update qty      |
| POST   | `/cart/remove/<item_id>`     | Remove item     |

## Orders (login required)

| Method | Path                         | Description              |
|--------|------------------------------|--------------------------|
| GET/POST | `/orders/checkout`         | Place order + pay        |
| GET    | `/orders/`                   | My orders list           |
| GET    | `/orders/<id>`               | Order detail             |
| GET    | `/orders/<id>/invoice`       | Invoice (after payment)  |

## Admin (admin role required)

| Method | Path                              | Description            |
|--------|-----------------------------------|------------------------|
| GET    | `/admin/`                         | Dashboard              |
| GET    | `/admin/products`                 | Catalog list           |
| GET/POST | `/admin/products/new`           | Create product         |
| GET/POST | `/admin/products/<id>/edit`     | Edit product           |
| POST   | `/admin/products/<id>/delete`     | Delete product         |
| GET/POST | `/admin/categories`             | Manage categories      |
| GET    | `/admin/orders`                   | All orders + filter    |
| GET    | `/admin/orders/<id>`              | Order detail           |
| POST   | `/admin/orders/<id>/status`       | Update delivery status |
| GET    | `/admin/users`                    | User list              |
| POST   | `/admin/users/<id>/toggle`        | Activate / deactivate  |

All POST forms require valid CSRF token.
