from datetime import datetime
import uuid
import os
import base64
import hashlib
import hmac
import json
import requests

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
    abort,
)

from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

from backend.extensions import db
from backend.models.cart import CartItem
from backend.models.order import Order, OrderItem
from backend.models.product import Product


# =========================================================
# eSewa Configuration
# =========================================================

ESEWA_PRODUCT_CODE = os.getenv(
    "ESEWA_PRODUCT_CODE",
    "EPAYTEST"
)

ESEWA_SECRET_KEY = os.getenv(
    "ESEWA_SECRET_KEY",
    "8gBm/:&EnhH.1/q"
)

ESEWA_PAYMENT_URL = os.getenv(
    "ESEWA_PAYMENT_URL",
    "https://rc-epay.esewa.com.np/api/epay/main/v2/form"
)

ESEWA_STATUS_URL = os.getenv(
    "ESEWA_STATUS_URL",
    "https://rc.esewa.com.np/api/epay/transaction/status/"
)


# =========================================================
# Blueprint
# =========================================================

orders_bp = Blueprint("orders", __name__)


# =========================================================
# eSewa Signature
# =========================================================

def generate_esewa_signature(
    total_amount,
    transaction_uuid,
    product_code
):
    """
    Generate HMAC-SHA256 signature required by eSewa.
    """

    message = (
        f"total_amount={total_amount},"
        f"transaction_uuid={transaction_uuid},"
        f"product_code={product_code}"
    )

    signature = hmac.new(
        ESEWA_SECRET_KEY.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).digest()

    return base64.b64encode(signature).decode("utf-8")


# =========================================================
# Checkout Form
# =========================================================

# =========================================================
# Checkout Form
# =========================================================

class CheckoutForm(FlaskForm):

    shipping_name = StringField(
        "Full Name",
        validators=[
            DataRequired(),
            Length(2, 100)
        ]
    )

    shipping_phone = StringField(
        "Phone",
        validators=[
            DataRequired(),
            Length(7, 20)
        ]
    )

    shipping_address = TextAreaField(
        "Shipping Address",
        validators=[
            DataRequired(),
            Length(1, 500)
        ]
    )

    postal_code = SelectField(
        "Postal Code",
        choices=[
            ("44600", "44600 - Kathmandu"),
            ("44700", "44700 - Lalitpur"),
            ("44800", "44800 - Bhaktapur"),
            ("44200", "44200 - Chitwan"),
            ("33700", "33700 - Pokhara"),
            ("32900", "32900 - Butwal"),
            ("21900", "21900 - Biratnagar"),
            ("11800", "11800 - Birgunj"),
            ("57300", "57300 - Dharan"),
        ],
        validators=[DataRequired()]
    )

    payment_method = SelectField(
        "Payment Method",
        choices=[
            ("card", "Credit / Debit Card (Demo)"),
            ("cod", "Cash on Delivery"),
            ("esewa", "eSewa"),
            ("khalti", "Khalti (Demo)"),
        ],
        validators=[
            DataRequired()
        ]
    )

    notes = TextAreaField(
        "Order Notes (optional)"
    )

    submit = SubmitField(
        "Place Order & Pay"
    )

# =========================================================
# Generate Order Number
# =========================================================

def _generate_order_number() -> str:
    return (
        "CR-"
        + datetime.utcnow().strftime("%y%m%d")
        + "-"
        + uuid.uuid4().hex[:6].upper()
    )


# =========================================================
# Generate Invoice Number
# =========================================================

def _generate_invoice_number() -> str:
    return (
        "INV-"
        + datetime.utcnow().strftime("%y%m%d")
        + "-"
        + uuid.uuid4().hex[:5].upper()
    )


# =========================================================
# Checkout
# =========================================================

@orders_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():

    items = current_user.cart_items.all()

    # Check empty cart
    if not items:
        flash(
            "Your cart is empty.",
            "warning"
        )

        return redirect(
            url_for("products.list_products")
        )

    # -----------------------------------------------------
    # Stock Check
    # -----------------------------------------------------

    for item in items:

        if not item.product.is_in_stock(item.quantity):

            flash(
                f"“{item.product.name}” is out of stock "
                "or insufficient quantity.",
                "danger"
            )

            return redirect(
                url_for("cart.view")
            )

    # -----------------------------------------------------
    # Checkout Form
    # -----------------------------------------------------

    form = CheckoutForm()

    if not form.shipping_name.data and current_user.full_name:
        form.shipping_name.data = current_user.full_name

    if not form.shipping_phone.data and current_user.phone:
        form.shipping_phone.data = current_user.phone

    if not form.shipping_address.data and current_user.address:
        form.shipping_address.data = current_user.address

    # -----------------------------------------------------
    # Calculate Price
    # -----------------------------------------------------

    subtotal = sum(
        item.subtotal
        for item in items
    )

    shipping_fee = (
        0
        if subtotal >= 1500
        else 120
    )

    total = subtotal + shipping_fee

    # -----------------------------------------------------
    # Submit Checkout
    # -----------------------------------------------------

    if form.validate_on_submit():

        # Create order
        order = Order(
            order_number=_generate_order_number(),
            user_id=current_user.id,

            shipping_name=form.shipping_name.data.strip(),

            shipping_phone=form.shipping_phone.data.strip(),

            shipping_address=form.shipping_address.data.strip(),

            postal_code=form.postal_code.data,

            subtotal=subtotal,

            shipping_fee=shipping_fee,

            total=total,

            payment_method=form.payment_method.data,

            notes=(
                form.notes.data.strip()
                if form.notes.data
                else None
            ),

            status="pending",

            payment_status="pending",
        )

        db.session.add(order)

        # Get order ID
        db.session.flush()

        # -------------------------------------------------
        # Create Order Items
        # -------------------------------------------------

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

            # -------------------------------------------------
            # IMPORTANT:
            # Do NOT reduce stock before eSewa payment.
            # -------------------------------------------------

            if form.payment_method.data != "esewa":

                item.product.stock -= item.quantity

        # -------------------------------------------------
        # Payment Method
        # -------------------------------------------------

        if form.payment_method.data == "cod":

            order.payment_status = "pending"

            order.status = "processing"

        elif form.payment_method.data == "esewa":

            # eSewa payment has not happened yet
            order.payment_status = "pending"

            order.status = "pending_payment"

        else:

            # Demo payment for card/khalti
            order.payment_status = "paid"

            order.status = "paid"

            order.payment_ref = (
                "PAY-"
                + uuid.uuid4().hex[:10].upper()
            )

            order.paid_at = datetime.utcnow()

            order.invoice_number = (
                _generate_invoice_number()
            )

        # -------------------------------------------------
        # Clear Cart
        # -------------------------------------------------

        for item in items:
            db.session.delete(item)

        db.session.commit()

        # -------------------------------------------------
        # eSewa
        # -------------------------------------------------

        if form.payment_method.data == "esewa":

            return redirect(
                url_for(
                    "orders.esewa_payment",
                    order_id=order.id
                )
            )

        # -------------------------------------------------
        # Other Payments
        # -------------------------------------------------

        flash(
            f"Order {order.order_number} placed successfully!",
            "success"
        )

        return redirect(
            url_for(
                "orders.detail",
                order_id=order.id
            )
        )

    # -----------------------------------------------------
    # Checkout Page
    # -----------------------------------------------------

    return render_template(
        "orders/checkout.html",

        form=form,

        items=items,

        subtotal=subtotal,

        shipping_fee=shipping_fee,

        total=total,
    )


# =========================================================
# eSewa Payment Page
# =========================================================

@orders_bp.route(
    "/payment/esewa/<int:order_id>"
)
@login_required
def esewa_payment(order_id):

    order = Order.query.get_or_404(
        order_id
    )

    # -----------------------------------------------------
    # Security Check
    # -----------------------------------------------------

    if (
        order.user_id != current_user.id
        and not current_user.is_admin()
    ):
        abort(403)

    # -----------------------------------------------------
    # Check Payment Method
    # -----------------------------------------------------

    if order.payment_method != "esewa":

        flash(
            "Invalid payment method.",
            "danger"
        )

        return redirect(
            url_for(
                "orders.detail",
                order_id=order.id
            )
        )

    # -----------------------------------------------------
    # Already Paid
    # -----------------------------------------------------

    if order.payment_status == "paid":

        return redirect(
            url_for(
                "orders.invoice",
                order_id=order.id
            )
        )

    # -----------------------------------------------------
    # Transaction UUID
    # -----------------------------------------------------

    transaction_uuid = order.order_number

    # eSewa amount format
    total_amount = f"{float(order.total):.2f}"

    # -----------------------------------------------------
    # Generate Signature
    # -----------------------------------------------------

    signature = generate_esewa_signature(
        total_amount,
        transaction_uuid,
        ESEWA_PRODUCT_CODE
    )

    # -----------------------------------------------------
    # Success URL
    # -----------------------------------------------------

    success_url = url_for(
        "orders.esewa_success",
        _external=True
    )

    # -----------------------------------------------------
    # Failure URL
    # -----------------------------------------------------

    failure_url = url_for(
        "orders.esewa_failure",
        _external=True
    )

    # -----------------------------------------------------
    # Display eSewa Payment Page
    # -----------------------------------------------------

    return render_template(
        "orders/esewa_payment.html",

        order=order,

        payment_url=ESEWA_PAYMENT_URL,

        amount=total_amount,

        total_amount=total_amount,

        transaction_uuid=transaction_uuid,

        product_code=ESEWA_PRODUCT_CODE,

        signature=signature,

        success_url=success_url,

        failure_url=failure_url
    )


# =========================================================
# eSewa SUCCESS
# =========================================================

@orders_bp.route(
    "/payment/esewa/success"
)
@login_required
def esewa_success():

    # -----------------------------------------------------
    # Get eSewa Response
    # -----------------------------------------------------

    encoded_data = request.args.get("data")

    if not encoded_data:

        flash(
            "Invalid eSewa payment response.",
            "danger"
        )

        return redirect(
            url_for("orders.my_orders")
        )

    # -----------------------------------------------------
    # Decode Base64 Response
    # -----------------------------------------------------

    try:

        decoded_data = (
            base64.b64decode(
                encoded_data
            ).decode("utf-8")
        )

        response_data = json.loads(
            decoded_data
        )

    except Exception:

        flash(
            "Could not read eSewa payment response.",
            "danger"
        )

        return redirect(
            url_for("orders.my_orders")
        )

    # -----------------------------------------------------
    # Get Response Data
    # -----------------------------------------------------

    transaction_uuid = response_data.get(
        "transaction_uuid"
    )

    status = response_data.get(
        "status"
    )

    product_code = response_data.get(
        "product_code"
    )

    total_amount = response_data.get(
        "total_amount"
    )

    # -----------------------------------------------------
    # Check Transaction UUID
    # -----------------------------------------------------

    if not transaction_uuid:

        flash(
            "Invalid transaction.",
            "danger"
        )

        return redirect(
            url_for("orders.my_orders")
        )

    # -----------------------------------------------------
    # Find Order
    # -----------------------------------------------------

    order = Order.query.filter_by(
        order_number=transaction_uuid
    ).first()

    if not order:

        flash(
            "Order not found.",
            "danger"
        )

        return redirect(
            url_for("orders.my_orders")
        )

    # -----------------------------------------------------
    # Security Check
    # -----------------------------------------------------

    if order.user_id != current_user.id:

        abort(403)

    # -----------------------------------------------------
    # Check Product Code
    # -----------------------------------------------------

    if product_code != ESEWA_PRODUCT_CODE:

        flash(
            "Invalid eSewa product code.",
            "danger"
        )

        return redirect(
            url_for(
                "orders.detail",
                order_id=order.id
            )
        )

    # -----------------------------------------------------
    # Check Amount
    # -----------------------------------------------------

    try:

        if float(total_amount) != float(order.total):

            flash(
                "Payment amount does not match "
                "order amount.",
                "danger"
            )

            return redirect(
                url_for(
                    "orders.detail",
                    order_id=order.id
                )
            )

    except (TypeError, ValueError):

        flash(
            "Invalid payment amount.",
            "danger"
        )

        return redirect(
            url_for(
                "orders.detail",
                order_id=order.id
            )
        )

    # -----------------------------------------------------
    # Verify Payment with eSewa
    # -----------------------------------------------------

    params = {

        "product_code":
            ESEWA_PRODUCT_CODE,

        "total_amount":
            f"{float(order.total):.2f}",

        "transaction_uuid":
            order.order_number,
    }

    try:

        response = requests.get(
            ESEWA_STATUS_URL,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        verification_data = response.json()

    except Exception as e:

        current_app.logger.error(
            f"eSewa verification error: {e}"
        )

        flash(
            "Could not verify payment with eSewa.",
            "danger"
        )

        return redirect(
            url_for(
                "orders.detail",
                order_id=order.id
            )
        )

    # -----------------------------------------------------
    # Check eSewa Status
    # -----------------------------------------------------

    verification_status = (
        verification_data.get("status")
    )

    if verification_status != "COMPLETE":

        flash(
            "eSewa payment was not completed.",
            "warning"
        )

        return redirect(
            url_for(
                "orders.detail",
                order_id=order.id
            )
        )

    # -----------------------------------------------------
    # Prevent Duplicate Processing
    # -----------------------------------------------------

    if order.payment_status == "paid":

        return redirect(
            url_for(
                "orders.invoice",
                order_id=order.id
            )
        )

    # -----------------------------------------------------
    # Mark Payment as Paid
    # -----------------------------------------------------

    order.payment_status = "paid"

    order.status = "paid"

    # eSewa may return refId or ref_id
    order.payment_ref = (
        verification_data.get("refId")
        or verification_data.get("ref_id")
        or response_data.get("transaction_code")
    )

    order.paid_at = datetime.utcnow()

    # -----------------------------------------------------
    # Reduce Stock AFTER Successful Payment
    # -----------------------------------------------------

    for item in order.items:

        item.product.stock -= item.quantity

    # -----------------------------------------------------
    # Generate Invoice
    # -----------------------------------------------------

    if not order.invoice_number:

        order.invoice_number = (
            _generate_invoice_number()
        )

    # -----------------------------------------------------
    # Save Changes
    # -----------------------------------------------------

    db.session.commit()

    from backend.email_utils import send_invoice_email

    try:
        send_invoice_email(order)
    except Exception as e:
        print("Invoice email failed:", e)

    flash(
        "eSewa payment successful!",
        "success"
    )

    # -----------------------------------------------------
    # Open Invoice
    # -----------------------------------------------------

    return redirect(
        url_for(
            "orders.invoice",
            order_id=order.id
        )
    )


# =========================================================
# eSewa FAILURE
# =========================================================

@orders_bp.route(
    "/payment/esewa/failure"
)
@login_required
def esewa_failure():

    transaction_uuid = request.args.get(
        "transaction_uuid"
    )

    if transaction_uuid:

        order = Order.query.filter_by(
            order_number=transaction_uuid
        ).first()

        if order:

            # Security check
            if order.user_id != current_user.id:

                abort(403)

            order.payment_status = "failed"

            order.status = "payment_failed"

            db.session.commit()

    flash(
        "eSewa payment was cancelled or failed.",
        "warning"
    )

    return redirect(
        url_for("orders.my_orders")
    )


# =========================================================
# My Orders
# =========================================================

@orders_bp.route("/")
@login_required
def my_orders():

    orders = (
        Order.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Order.created_at.desc()
        )
        .all()
    )

    return render_template(
        "orders/list.html",
        orders=orders
    )


# =========================================================
# Order Detail
# =========================================================

@orders_bp.route("/<int:order_id>")
@login_required
def detail(order_id):

    order = Order.query.get_or_404(
        order_id
    )

    if (
        order.user_id != current_user.id
        and not current_user.is_admin()
    ):
        abort(403)

    return render_template(
        "orders/detail.html",
        order=order
    )


# =========================================================
# Invoice
# =========================================================

@orders_bp.route(
    "/<int:order_id>/invoice"
)
@login_required
def invoice(order_id):

    order = Order.query.get_or_404(
        order_id
    )

    # Security check
    if (
        order.user_id != current_user.id
        and not current_user.is_admin()
    ):
        abort(403)

    # Invoice only after payment
    if (
        order.payment_status != "paid"
        and not current_user.is_admin()
    ):

        flash(
            "Invoice available after payment.",
            "info"
        )

        return redirect(
            url_for(
                "orders.detail",
                order_id=order.id
            )
        )

    return render_template(
        "orders/invoice.html",
        order=order
    )