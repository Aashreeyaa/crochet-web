from datetime import datetime
from backend.extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(40), default="🧶")  # emoji accent

    products = db.relationship("Product", backref="category", lazy="dynamic")

    def __repr__(self):
        return f"<Category {self.name}>"


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    slug = db.Column(db.String(160), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)
    image = db.Column(db.String(255), default="placeholder.jpg")
    yarn_type = db.Column(db.String(80))          # e.g. Cotton, Acrylic, Wool
    size = db.Column(db.String(40))               # e.g. One Size, M, L
    colors = db.Column(db.String(120))            # comma-separated
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cart_items = db.relationship("CartItem", backref="product", lazy="dynamic")
    order_items = db.relationship("OrderItem", backref="product", lazy="dynamic")

    def is_in_stock(self, qty: int = 1) -> bool:
        return self.is_active and self.stock >= qty

    def __repr__(self):
        return f"<Product {self.name}>"
