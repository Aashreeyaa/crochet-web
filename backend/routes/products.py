from flask import Blueprint, render_template, request, abort
from backend.models.product import Product, Category

products_bp = Blueprint("products", __name__)


@products_bp.route("/")
def list_products():
    q = request.args.get("q", "").strip()
    category_slug = request.args.get("category", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 12

    query = Product.query.filter_by(is_active=True)

    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Product.name.ilike(like),
                Product.description.ilike(like),
                Product.yarn_type.ilike(like),
            )
        )

    selected_category = None
    if category_slug:
        selected_category = Category.query.filter_by(slug=category_slug).first()
        if selected_category:
            query = query.filter_by(category_id=selected_category.id)

    pagination = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    categories = Category.query.order_by(Category.name).all()

    return render_template(
        "products/list.html",
        products=pagination.items,
        pagination=pagination,
        categories=categories,
        selected_category=selected_category,
        q=q,
    )


# Need db import for ilike
from backend.extensions import db  # noqa: E402


@products_bp.route("/<slug>")
def detail(slug):
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    related = (
        Product.query.filter(
            Product.category_id == product.category_id,
            Product.id != product.id,
            Product.is_active.is_(True),
        )
        .limit(4)
        .all()
    )
    return render_template("products/detail.html", product=product, related=related)
