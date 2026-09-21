from flask import Blueprint, redirect, url_for, flash, request, jsonify, render_template
from flask_login import login_required, current_user
from backend.extensions import db
from backend.models.cart import CartItem
from backend.models.product import Product

cart_bp = Blueprint("cart", __name__)


@cart_bp.route("/")
@login_required
def view():
    items = current_user.cart_items.order_by(CartItem.added_at.desc()).all()
    total = sum(item.subtotal for item in items)
    return render_template("cart/view.html", items=items, total=total)


@cart_bp.route("/add/<int:product_id>", methods=["POST"])
@login_required
def add(product_id):
    product = Product.query.get_or_404(product_id)
    qty = request.form.get("quantity", 1, type=int)
    if qty < 1:
        qty = 1

    if not product.is_in_stock(qty):
        flash(f"Sorry, only {product.stock} left in stock.", "warning")
        return redirect(request.referrer or url_for("products.list_products"))

    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
    if item:
        new_qty = item.quantity + qty
        if not product.is_in_stock(new_qty):
            flash(f"Cannot add more. Only {product.stock} available.", "warning")
            return redirect(request.referrer or url_for("cart.view"))
        item.quantity = new_qty
    else:
        item = CartItem(user_id=current_user.id, product_id=product.id, quantity=qty)
        db.session.add(item)

    db.session.commit()
    flash(f"“{product.name}” added to your cart.", "success")

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"ok": True, "cart_count": current_user.cart_items.count()})
    return redirect(request.referrer or url_for("cart.view"))


@cart_bp.route("/update/<int:item_id>", methods=["POST"])
@login_required
def update(item_id):
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    qty = request.form.get("quantity", 1, type=int)

    if qty <= 0:
        db.session.delete(item)
        db.session.commit()
        flash("Item removed.", "info")
    else:
        if not item.product.is_in_stock(qty):
            flash(f"Only {item.product.stock} available.", "warning")
        else:
            item.quantity = qty
            db.session.commit()
            flash("Cart updated.", "success")

    return redirect(url_for("cart.view"))


@cart_bp.route("/remove/<int:item_id>", methods=["POST"])
@login_required
def remove(item_id):
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    name = item.product.name
    db.session.delete(item)
    db.session.commit()
    flash(f"“{name}” removed from cart.", "info")
    return redirect(url_for("cart.view"))
