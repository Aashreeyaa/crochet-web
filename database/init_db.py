#!/usr/bin/env python3
"""Create tables and seed demo data for The Cozy Knot."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.app import create_app
from backend.extensions import db
from backend.models.user import User
from backend.models.product import Category, Product
from backend.slugify_simple import slugify


def seed():
    app = create_app()

    with app.app_context():

        # =========================================
        # CREATE TABLES
        # =========================================

        db.create_all()

        # =========================================
        # ADMIN USER
        # =========================================

        admin = User.query.filter_by(
            email="admin@stitchshop.com"
        ).first()

        if not admin:
            admin = User(
                email="admin@stitchshop.com",
                full_name="Admin Weaver",
                role="admin"
            )

            admin.set_password("admin123")
            db.session.add(admin)

        # =========================================
        # CUSTOMER USER
        # =========================================

        customer = User.query.filter_by(
            email="customer@stitchshop.com"
        ).first()

        if not customer:
            customer = User(
                email="customer@stitchshop.com",
                full_name="Maya Customer",
                role="customer",
                phone="9800000000",
                address="Lalitpur, Nepal",
            )

            customer.set_password("cust123")
            db.session.add(customer)

        # =========================================
        # CATEGORIES
        # =========================================

        cats_data = [
            ("Blankets", "Cozy throws and baby blankets", "🛏️"),
            ("Amigurumi", "Cute stuffed animals & figures", "🧸"),
            ("Accessories", "Hats, scarves, bags & more", "🧣"),
            ("Home Decor", "Plant hangers, coasters, wall art", "🪴"),
            ("Baby Items", "Soft sets for little ones", "👶"),
        ]

        categories = {}

        for name, desc, icon in cats_data:

            slug = slugify(name)

            # Check if category already exists
            category = Category.query.filter_by(
                slug=slug
            ).first()

            if not category:
                category = Category(
                    name=name,
                    slug=slug,
                    description=desc,
                    icon=icon
                )

                db.session.add(category)

            categories[name] = category

        # Save categories so IDs are available
        db.session.flush()

        # =========================================
        # PRODUCTS
        # =========================================

        products = [

            (
                "Cloud Soft Baby Blanket",
                "Blankets",
                2450,
                12,
                "Cotton blend",
                "75×90 cm",
                "Cream, Blush",
                True,
                "Ultra-soft baby blanket worked in gentle granny squares. Perfect shower gift.",
                "baby-blankie.jpg"
            ),

            (
                "Rainbow Granny Throw",
                "Blankets",
                3890,
                5,
                "Acrylic",
                "120×150 cm",
                "Rainbow",
                True,
                "Vibrant full-size throw. Machine washable and surprisingly light.",
                "granny-blankie.jpg"
            ),

            (
                "Lil' Bear Amigurumi",
                "Amigurumi",
                890,
                20,
                "Cotton",
                "15 cm",
                "Honey Brown",
                True,
                "Hand-crocheted bear with safety eyes. Ideal for kids 3+.",
                "lil-bear.jpg"
            ),

            (
                "Sleepy Bunny",
                "Amigurumi",
                950,
                15,
                "Cotton",
                "18 cm",
                "White, Grey",
                False,
                "Floppy-eared bunny ready for bedtime cuddles.",
                "sleepy-bunny.jpg"
            ),

            (
                "Chunky Beanie",
                "Accessories",
                650,
                25,
                "Wool blend",
                "One size",
                "Terracotta, Sage",
                True,
                "Warm double-layered beanie with fold-over brim.",
                "chunkie-beanie.jpg"
            ),

            (
                "Market Tote Bag",
                "Accessories",
                1250,
                10,
                "Cotton rope",
                "Large",
                "Natural",
                False,
                "Sturdy crochet tote that holds a full market haul.",
                "tote-bag.jpg"
            ),

            (
                "Macrame-Style Plant Hanger",
                "Home Decor",
                780,
                18,
                "Cotton cord",
                "90 cm drop",
                "Natural, Black",
                True,
                "Boho plant hanger for medium pots. Knot-free crochet version.",
                "macrame-hanger.jpg"
            ),

            (
                "Hexagon Coaster Set",
                "Home Decor",
                450,
                30,
                "Cotton",
                "10 cm",
                "Mixed pastels",
                False,
                "Set of 4 hexagon coasters. Protects tables in style.",
                "hexagon-set.jpg"
            ),

            (
                "Newborn Booties",
                "Baby Items",
                520,
                22,
                "Bamboo yarn",
                "0–3 months",
                "Mint, Peach",
                True,
                "Soft non-slip booties. Gentle on newborn skin.",
                "newborn-bootie.jpg"
            ),

            (
                "Baby Bonnet",
                "Baby Items",
                680,
                14,
                "Cotton",
                "0–6 months",
                "Ivory",
                False,
                "Classic lace-edge bonnet with chin ties.",
                "bonnet.jpg"
            ),

            (
                "Heart Cushion Cover",
                "Home Decor",
                1100,
                8,
                "Chenille",
                "40×40 cm",
                "Dusty Rose",
                True,
                "Plush heart-shaped pillow cover. Insert not included.",
                "heart-cushion.jpg"
            ),

            (
                "Fingerless Gloves",
                "Accessories",
                720,
                16,
                "Merino",
                "One size",
                "Charcoal",
                False,
                "Warm gloves that keep fingertips free for typing or crafting.",
                "fingerless-gloves.jpg"
            ),
        ]

        # =========================================
        # ADD / UPDATE PRODUCTS
        # =========================================

        for (
            name,
            cat_name,
            price,
            stock,
            yarn,
            size,
            colors,
            featured,
            desc,
            image
        ) in products:

            product_slug = slugify(name)

            # Find existing product
            existing_product = Product.query.filter_by(
                slug=product_slug
            ).first()

            if existing_product:

                # =====================================
                # UPDATE EXISTING PRODUCT
                # =====================================

                existing_product.name = name
                existing_product.description = desc
                existing_product.price = price
                existing_product.stock = stock
                existing_product.yarn_type = yarn
                existing_product.size = size
                existing_product.colors = colors
                existing_product.is_featured = featured
                existing_product.is_active = True
                existing_product.category_id = categories[cat_name].id

                # IMPORTANT:
                # Update image filename
                existing_product.image = image

            else:

                # =====================================
                # CREATE NEW PRODUCT
                # =====================================

                new_product = Product(
                    name=name,
                    slug=product_slug,
                    description=desc,
                    price=price,
                    stock=stock,
                    yarn_type=yarn,
                    size=size,
                    colors=colors,
                    is_featured=featured,
                    is_active=True,
                    category_id=categories[cat_name].id,
                    image=image,
                )

                db.session.add(new_product)

        # =========================================
        # SAVE DATABASE
        # =========================================

        db.session.commit()

        print()
        print("=========================================")
        print(" Database initialized successfully!")
        print("=========================================")
        print("Existing products were updated.")
        print("Missing products were added.")
        print("Image filenames were updated.")
        print()
        print("Admin   : admin@stitchshop.com / admin123")
        print("Customer: customer@stitchshop.com / cust123")
        print()


if __name__ == "__main__":
    seed()