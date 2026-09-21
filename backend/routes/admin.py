from functools import wraps
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, DecimalField, IntegerField, BooleanField,
    SelectField, SubmitField, FileField
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from backend.extensions import db
from backend.models.user import User
from backend.models.product import Product, Category
from backend.models.order import Order

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated


class ProductForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(2, 140)])
    description = TextAreaField("Description")
    price = DecimalField("Price (Rs)", validators=[DataRequired(), NumberRange(min=1)])
    stock = IntegerField("Stock", validators=[DataRequired(), NumberRange(min=0)])
    category_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    yarn_type = StringField("Yarn Type", validators=[Optional(), Length(0, 80)])
    size = StringField("Size", validators=[Optional(), Length(0, 40)])
    colors = StringField("Colors (comma-separated)", validators=[Optional(), Length(0, 120)])
    is_active = BooleanField("Active", default=True)
    is_featured = BooleanField("Featured")
    submit = SubmitField("Save Product")


class CategoryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(2, 80)])
    description = TextAreaField("Description")
    icon = StringField("Icon (emoji)", default="🧶")
    submit = SubmitField("Save Category")


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    stats = {
        "products": Product.query.count(),
        "orders": Order.query.count(),
        "customers": User.query.filter_by(role="customer").count(),
        "revenue": db.session.query(db.func.coalesce(db.func.sum(Order.total), 0))
        .filter(Order.payment_status == "paid")
        .scalar(),
        "pending_orders": Order.query.filter(Order.status.in_(["pending", "paid", "processing"])).count(),
    }
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(8).all()
    return render_template("admin/dashboard.html", stats=stats, recent_orders=recent_orders)


# ---------- Products ----------
@admin_bp.route("/products")
@login_required
@admin_required
def products():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template("admin/products.html", products=products)


@admin_bp.route("/products/new", methods=["GET", "POST"])
@login_required
@admin_required
def product_new():
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name)]
    if form.validate_on_submit():
        from slugify_simple import slugify
        slug = slugify(form.name.data)
        # ensure unique
        base = slug
        i = 1
        while Product.query.filter_by(slug=slug).first():
            slug = f"{base}-{i}"
            i += 1
        p = Product(
            name=form.name.data.strip(),
            slug=slug,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            category_id=form.category_id.data,
            yarn_type=form.yarn_type.data,
            size=form.size.data,
            colors=form.colors.data,
            is_active=form.is_active.data,
            is_featured=form.is_featured.data,
            image="placeholder.jpg",
        )
        db.session.add(p)
        db.session.commit()
        flash("Product created.", "success")
        return redirect(url_for("admin.products"))
    return render_template("admin/product_form.html", form=form, title="New Product")


@admin_bp.route("/products/<int:pid>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def product_edit(pid):
    product = Product.query.get_or_404(pid)
    form = ProductForm(obj=product)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name)]
    if form.validate_on_submit():
        product.name = form.name.data.strip()
        product.description = form.description.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.category_id = form.category_id.data
        product.yarn_type = form.yarn_type.data
        product.size = form.size.data
        product.colors = form.colors.data
        product.is_active = form.is_active.data
        product.is_featured = form.is_featured.data
        db.session.commit()
        flash("Product updated.", "success")
        return redirect(url_for("admin.products"))
    return render_template("admin/product_form.html", form=form, title="Edit Product", product=product)


@admin_bp.route("/products/<int:pid>/delete", methods=["POST"])
@login_required
@admin_required
def product_delete(pid):
    product = Product.query.get_or_404(pid)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted.", "info")
    return redirect(url_for("admin.products"))


# ---------- Categories ----------
@admin_bp.route("/categories", methods=["GET", "POST"])
@login_required
@admin_required
def categories():
    form = CategoryForm()
    if form.validate_on_submit():
        from slugify_simple import slugify
        slug = slugify(form.name.data)
        if Category.query.filter_by(slug=slug).first():
            flash("Category already exists.", "warning")
        else:
            c = Category(
                name=form.name.data.strip(),
                slug=slug,
                description=form.description.data,
                icon=form.icon.data or "🧶",
            )
            db.session.add(c)
            db.session.commit()
            flash("Category added.", "success")
            return redirect(url_for("admin.categories"))
    cats = Category.query.order_by(Category.name).all()
    return render_template("admin/categories.html", form=form, categories=cats)


# ---------- Orders (Manage Orders + Update Delivery Status) ----------
@admin_bp.route("/orders")
@login_required
@admin_required
def orders():
    status = request.args.get("status", "")
    q = Order.query
    if status:
        q = q.filter_by(status=status)
    orders = q.order_by(Order.created_at.desc()).all()
    return render_template("admin/orders.html", orders=orders, current_status=status)


@admin_bp.route("/orders/<int:oid>")
@login_required
@admin_required
def order_detail(oid):
    order = Order.query.get_or_404(oid)
    return render_template("admin/order_detail.html", order=order)


@admin_bp.route("/orders/<int:oid>/status", methods=["POST"])
@login_required
@admin_required
def order_status(oid):
    order = Order.query.get_or_404(oid)
    new_status = request.form.get("status")
    if new_status not in Order.STATUS_FLOW:
        flash("Invalid status.", "danger")
        return redirect(url_for("admin.order_detail", oid=oid))

    order.status = new_status
    now = datetime.utcnow()
    if new_status == "shipped":
        order.shipped_at = now
    elif new_status == "delivered":
        order.delivered_at = now
    elif new_status == "paid" and not order.paid_at:
        order.paid_at = now
        order.payment_status = "paid"
        if not order.invoice_number:
            import uuid
            order.invoice_number = "INV-" + now.strftime("%y%m%d") + "-" + uuid.uuid4().hex[:5].upper()

    db.session.commit()
    flash(f"Order status updated to “{new_status}”.", "success")
    return redirect(url_for("admin.order_detail", oid=oid))


# ---------- Users ----------
@admin_bp.route("/users")
@login_required
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/users/<int:uid>/toggle", methods=["POST"])
@login_required
@admin_required
def user_toggle(uid):
    user = User.query.get_or_404(uid)
    if user.id == current_user.id:
        flash("You cannot deactivate yourself.", "warning")
    else:
        user.is_active = not user.is_active
        db.session.commit()
        flash(f"User {'activated' if user.is_active else 'deactivated'}.", "success")
    return redirect(url_for("admin.users"))
