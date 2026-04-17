from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id           = Column(Integer, primary_key=True)
    name         = Column(String(300), nullable=False)
    url          = Column(Text, nullable=False, unique=True)
    store        = Column(String(50), nullable=False)   # amazon, mercadolivre …
    target_price = Column(Float, nullable=True)         # alerta abaixo deste valor
    active       = Column(Boolean, default=True)
    created_at   = Column(DateTime, default=datetime.utcnow)

    prices = relationship("PriceHistory", back_populates="product",
                          cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product {self.store} | {self.name[:40]}>"

    @property
    def latest_price(self):
        if self.prices:
            return sorted(self.prices, key=lambda p: p.checked_at)[-1].price
        return None


class PriceHistory(Base):
    __tablename__ = "price_history"

    id         = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    price      = Column(Float, nullable=False)
    available  = Column(Boolean, default=True)
    checked_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="prices")

    def __repr__(self):
        return f"<Price R${self.price:.2f} @ {self.checked_at:%Y-%m-%d %H:%M}>"
