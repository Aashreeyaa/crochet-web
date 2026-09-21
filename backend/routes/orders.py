from datetime import datetime
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from backend.extensions import db
from backend.models.cart import CartItem
from backend.models.order import Order, OrderItem
from backend.models.product import Product

orders_bp = Blueprint("orders", __name__)


class CheckoutForm(FlaskForm):
    shipping_name = StringField("Full Name", validators=[DataRequired(), Length(2, 100)])
    shipping_phone = StringField("Phone", validators=[DataRequired(), Length(7, 20)])
    shipping_address = TextAreaField("Shipping Address", validators=[DataRequired(), Length(10, 500)])
    payment_method = SelectField(
        "Payment Method",
        choices=[
            ("card", "Credit / Debit Card (Demo)"),
            ("cod", "Cash on Delivery"),
            ("esewa", "eSewa (Demo)"),
            ("khalti", "Khalti (Demo)"),
        ],
        validators=[DataRequired()],
    )
    notes = TextAreaField("Order Notes (optional)")
    submit = SubmitField("Place Order & Pay")


def _generate_order_number() -> str:
    return "CR-" + datetime.utcnow().strftime("%y%m%d") + "-" + uuid.uuid4().hex[:6].upper()


def _generate_invoice_number() -> str:
    return "INV-" + datetime.utcnow().strftime("%y%m%d") + "-" + uuid.uuid4().hex[:5].upper()


@orders_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    items = current_user.cart_items.all()
    if not items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("products.list_products"))

    # Stock check
    for item in items:
        if not item.product.is_in_stock(item.quantity):
            flash(f"“{item.product.name}” is out of stock or insufficient quantity.", "danger")
            return redirect(url_for("cart.view"))

    form = CheckoutForm()
    if not form.shipping_name.data and current_user.full_name:
        form.shipping_name.data = current_user.full_name
    if not form.shipping_phone.data and current_user.phone:
        form.shipping_phone.data = current_user.phone
    if not form.shipping_address.data and current_user.address:
        form.shipping_address.data = current_user.address

    subtotal = sum(item.subtotal for item in items)
    shipping_fee = 0 if subtotal >= 1500 else 120  # free over Rs 1500
    total = subtotal + shipping_fee

    if form.validate_on_submit():
        order = Order(
            order_number=_generate_order_number(),
            user_id=current_user.id,
            shipping_name=form.shipping_name.data.strip(),
            shipping_phone=form.shipping_phone.data.strip(),
            shipping_address=form.shipping_address.data.strip(),
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            total=total,
            payment_method=form.payment_method.data,
            notes=form.notes.data.strip() if form.notes.data else None,
            status="pending",
            payment_status="pending",
        )
        db.session.add(order)
        db.session.flush()  # get order.id

        for item in items:
            oi = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                product_name=item.product.name,
                unit_price=item.product.price,
                quantity=item.quantity,
                line_total=item.subtotal,
            )
            db.session.add(oi)
            # Reduce stock
            item.product.stock -= item.quantity

        # Simulate payment gateway (include <<Process Payment>>)
        if form.payment_method.data == "cod":
            order.payment_status = "pending"
            order.status = "processing"
        else:
            # Demo success
            order.payment_status = "paid"
            order.payment_ref = "PAY-" + uuid.uuid4().hex[:10].upper()
            order.paid_at = datetime.utcnow()
            order.status = "paid"
            order.invoice_number = _generate_invoice_number()

        # Clear cart
        for item in items:
            db.session.delete(item)

        db.session.commit()
        flash(f"Order {order.order_number} placed successfully!", "success")
        return redirect(url_for("orders.detail", order_id=order.id))

    return render_template(
        "orders/checkout.html",
        form=form,
        items=items,
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        total=total,
    )


@orders_bp.route("/")
@login_required
def my_orders():
    orders = (
        Order.query.filter_by(user_id=current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return render_template("orders/list.html", orders=orders)


@orders_bp.route("/<int:order_id>")
@login_required
def detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin():
        abort(403)
    return render_template("orders/detail.html", order=order)


@orders_bp.route("/<int:order_id>/invoice")
@login_required
def invoice(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin():
        abort(403)
    if order.payment_status != "paid" and not current_user.is_admin():
        flash("Invoice available after payment.", "info")
        return redirect(url_for("orders.detail", order_id=order.id))
    return render_template("orders/invoice.html", order=order)
