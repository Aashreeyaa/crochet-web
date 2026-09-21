from datetime import datetime
from backend.extensions import db


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Snapshot of shipping info at order time
    shipping_name = db.Column(db.String(100), nullable=False)
    shipping_phone = db.Column(db.String(20))
    shipping_address = db.Column(db.Text, nullable=False)

    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    shipping_fee = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False)

    # Status flow matching use-case: pending → paid → processing → shipped → delivered / cancelled
    status = db.Column(db.String(30), default="pending", nullable=False)
    payment_status = db.Column(db.String(20), default="pending")  # pending | paid | failed | refunded
    payment_method = db.Column(db.String(40), default="card")
    payment_ref = db.Column(db.String(80))

    invoice_number = db.Column(db.String(30))
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)

    items = db.relationship(
        "OrderItem", backref="order", lazy="joined", cascade="all, delete-orphan"
    )

    STATUS_FLOW = ("pending", "paid", "processing", "shipped", "delivered", "cancelled")

    def can_transition_to(self, new_status: str) -> bool:
        if new_status == "cancelled":
            return self.status in ("pending", "paid", "processing")
        try:
            return self.STATUS_FLOW.index(new_status) > self.STATUS_FLOW.index(self.status)
        except ValueError:
            return False

    def __repr__(self):
        return f"<Order {self.order_number} ({self.status})>"


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    # Snapshot so price changes don't affect past orders
    product_name = db.Column(db.String(140), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    line_total = db.Column(db.Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f"<OrderItem {self.product_name} x{self.quantity}>"
