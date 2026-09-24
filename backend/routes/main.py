from flask import Blueprint, render_template
from backend.models.product import Product, Category

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    featured = (
        Product.query.filter_by(is_active=True, is_featured=True)
        .order_by(Product.created_at.desc())
        .limit(6)
        .all()
    )
    categories = Category.query.order_by(Category.name).all()
    latest = (
        Product.query.filter_by(is_active=True)
        .order_by(Product.created_at.desc())
        .limit(8)
        .all()
    )
    return render_template(
        "index.html",
        featured=featured,
        categories=categories,
        latest=latest,
    )


@main_bp.route("/about")
def about():
    return render_template("about.html")

@main_bp.route("/contact")
def contact():
    return render_template("contact.html")
