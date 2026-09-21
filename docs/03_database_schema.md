# Database Schema – Crochet Stitch Shop

## ER Overview

```
users 1──* cart_items *──1 products
users 1──* orders 1──* order_items *──1 products
categories 1──* products
```

## Tables

### users
| Column         | Type         | Notes                    |
|----------------|--------------|--------------------------|
| id             | Integer PK   |                          |
| email          | String(120)  | unique, indexed          |
| password_hash  | String(256)  |                          |
| full_name      | String(100)  |                          |
| role           | String(20)   | customer \| admin        |
| phone          | String(20)   | nullable                 |
| address        | Text         | nullable                 |
| is_active      | Boolean      | default True             |
| created_at     | DateTime     |                          |
| updated_at     | DateTime     |                          |

### categories
| Column      | Type        | Notes          |
|-------------|-------------|----------------|
| id          | Integer PK  |                |
| name        | String(80)  | unique         |
| slug        | String(80)  | unique         |
| description | Text        |                |
| icon        | String(40)  | emoji          |

### products
| Column       | Type         | Notes                |
|--------------|--------------|----------------------|
| id           | Integer PK   |                      |
| name         | String(140)  |                      |
| slug         | String(160)  | unique, indexed      |
| description  | Text         |                      |
| price        | Numeric(10,2)|                      |
| stock        | Integer      |                      |
| image        | String(255)  |                      |
| yarn_type    | String(80)   |                      |
| size         | String(40)   |                      |
| colors       | String(120)  |                      |
| is_active    | Boolean      |                      |
| is_featured  | Boolean      |                      |
| category_id  | FK → categories |                   |
| created_at   | DateTime     |                      |
| updated_at   | DateTime     |                      |

### cart_items
| Column     | Type       | Notes                        |
|------------|------------|------------------------------|
| id         | Integer PK |                              |
| user_id    | FK users   |                              |
| product_id | FK products|                              |
| quantity   | Integer    |                              |
| added_at   | DateTime   |                              |
| UNIQUE(user_id, product_id)    |          |

### orders
| Column            | Type         | Notes                              |
|-------------------|--------------|------------------------------------|
| id                | Integer PK   |                                    |
| order_number      | String(30)   | unique (e.g. CR-260921-A1B2C3)     |
| user_id           | FK users     |                                    |
| shipping_name     | String(100)  | snapshot                           |
| shipping_phone    | String(20)   |                                    |
| shipping_address  | Text         |                                    |
| subtotal          | Numeric(10,2)|                                    |
| shipping_fee      | Numeric(10,2)|                                    |
| total             | Numeric(10,2)|                                    |
| status            | String(30)   | pending…delivered / cancelled      |
| payment_status    | String(20)   | pending / paid / failed            |
| payment_method    | String(40)   | card / cod / esewa / khalti        |
| payment_ref       | String(80)   |                                    |
| invoice_number    | String(30)   |                                    |
| notes             | Text         |                                    |
| created_at        | DateTime     |                                    |
| paid_at / shipped_at / delivered_at | DateTime | nullable |

### order_items
| Column       | Type         | Notes (price snapshot) |
|--------------|--------------|------------------------|
| id           | Integer PK   |                        |
| order_id     | FK orders    |                        |
| product_id   | FK products  |                        |
| product_name | String(140)  |                        |
| unit_price   | Numeric(10,2)|                        |
| quantity     | Integer      |                        |
| line_total   | Numeric(10,2)|                        |
