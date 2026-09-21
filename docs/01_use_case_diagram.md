# Use Case Diagram – Crochet Stitch Shop

## System Boundary
**Crochet Website / App**

## Actors
- **Customer** (primary)
- **Admin** (primary)
- **Payment Gateway** (external)
- **Delivery Service** (external)

## Use Cases & Relationships

```
Customer
  ├── Login / Authenticate
  ├── Browse Products
  ├── Add to Cart
  ├── Place Order  ──<<include>>──► Make Payment ──<<include>>──► Process Payment (Payment Gateway)
  │                      │
  │                      └──<<include>>──► Generate Invoice
  └── My Order ──<<include>>──► Update Delivery Status

Admin
  ├── Login / Authenticate
  ├── Manage Users
  ├── Manage Catalog
  └── Manage Orders ──► Update Delivery Status (also linked to Delivery Service)
```

## Include Relationships (from diagram)
1. **Place Order** includes **Make Payment**
2. **Make Payment** includes **Process Payment**
3. **Process Payment** includes **Generate Invoice**
4. **My Order** includes **Update Delivery Status**

## Status Lifecycle (Order)
`pending → paid → processing → shipped → delivered`  
(also `cancelled` from early states)

## Implementation Mapping

| Use Case              | Module / Route                          |
|-----------------------|-----------------------------------------|
| Login / Authenticate  | `routes/auth.py`                        |
| Browse Products       | `routes/products.py`                    |
| Add to Cart           | `routes/cart.py`                        |
| Place Order           | `routes/orders.py` → checkout           |
| Make / Process Payment| Simulated gateway inside checkout       |
| Generate Invoice      | `orders.invoice` template               |
| My Order              | `orders.my_orders` + detail             |
| Update Delivery Status| `admin.order_status`                    |
| Manage Users          | `admin.users`                           |
| Manage Catalog        | `admin.products` + `admin.categories`   |
| Manage Orders         | `admin.orders` + detail                 |
