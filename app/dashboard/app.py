import os
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///prices.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Import models after db is set up
from app.db.models import Product, PriceHistory
from app.db.database import init_db, get_session
from app.scrapers import get_scraper


@app.route("/")
def index():
    with get_session() as session:
        products = session.query(Product).filter(Product.active == True).all()
        data = []
        for p in products:
            prices = (
                session.query(PriceHistory)
                .filter(PriceHistory.product_id == p.id)
                .order_by(PriceHistory.checked_at.desc())
                .limit(30)
                .all()
            )
            data.append({
                "id": p.id,
                "name": p.name,
                "store": p.store,
                "url": p.url,
                "target_price": p.target_price,
                "latest_price": prices[0].price if prices else None,
                "available": prices[0].available if prices else False,
                "price_count": len(prices),
            })
    return render_template("index.html", products=data)


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    with get_session() as session:
        product = session.get(Product, product_id)
        if not product:
            flash("Produto não encontrado.", "error")
            return redirect(url_for("index"))

        prices = (
            session.query(PriceHistory)
            .filter(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.checked_at.asc())
            .all()
        )
        chart_data = [
            {"date": p.checked_at.strftime("%d/%m %H:%M"), "price": p.price}
            for p in prices
        ]
    return render_template("product.html", product=product, chart_data=chart_data)


@app.route("/api/products", methods=["GET"])
def api_products():
    with get_session() as session:
        products = session.query(Product).all()
        return jsonify([
            {
                "id": p.id, "name": p.name, "store": p.store,
                "url": p.url, "target_price": p.target_price,
                "active": p.active, "latest_price": p.latest_price,
            }
            for p in products
        ])


@app.route("/api/add", methods=["POST"])
def api_add():
    data = request.get_json()
    url          = data.get("url", "").strip()
    target_price = data.get("target_price")

    if not url:
        return jsonify({"error": "URL é obrigatória"}), 400

    try:
        scraper = get_scraper(url)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    result = scraper.scrape(url)

    with get_session() as session:
        existing = session.query(Product).filter(Product.url == url).first()
        if existing:
            return jsonify({"error": "Produto já monitorado"}), 409

        product = Product(
            name=result.name,
            url=url,
            store=result.store,
            target_price=float(target_price) if target_price else None,
        )
        session.add(product)
        session.flush()

        if result.price:
            session.add(PriceHistory(
                product_id=product.id,
                price=result.price,
                available=result.available,
            ))
        session.commit()
        return jsonify({"message": "Produto adicionado!", "name": result.name}), 201


@app.route("/api/delete/<int:product_id>", methods=["DELETE"])
def api_delete(product_id):
    with get_session() as session:
        product = session.get(Product, product_id)
        if not product:
            return jsonify({"error": "Não encontrado"}), 404
        session.delete(product)
        session.commit()
    return jsonify({"message": "Removido com sucesso"})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
