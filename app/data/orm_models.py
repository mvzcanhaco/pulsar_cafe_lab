"""
SQLAlchemy ORM models — data layer only, not exposed to domain.
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.data.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class MerchantORM(Base):
    __tablename__ = "merchants"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="BRL")
    address: Mapped[str] = mapped_column(Text, default="")
    phone_number: Mapped[str] = mapped_column(String(50), default="")
    cnpj: Mapped[str] = mapped_column(String(20), default="")


class ProductORM(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    price_type: Mapped[str] = mapped_column(String(20), default="FIXED")
    available: Mapped[bool] = mapped_column(Boolean, default=True)
    category: Mapped[str] = mapped_column(String(100), default="")
    description: Mapped[str] = mapped_column(Text, default="")


class OrderORM(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    state: Mapped[str] = mapped_column(String(20), default="OPEN")
    note: Mapped[str] = mapped_column(Text, default="")
    currency: Mapped[str] = mapped_column(String(10), default="BRL")
    merchant_id: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    line_items: Mapped[list["LineItemORM"]] = relationship(
        "LineItemORM", back_populates="order", cascade="all, delete-orphan"
    )


class LineItemORM(Base):
    __tablename__ = "line_items"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    order: Mapped["OrderORM"] = relationship("OrderORM", back_populates="line_items")


class PaymentORM(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    tip_amount_cents: Mapped[int] = mapped_column(Integer, default=0)
    tax_amount_cents: Mapped[int] = mapped_column(Integer, default=0)
    result: Mapped[str] = mapped_column(String(20), nullable=False)
    card_type: Mapped[str] = mapped_column(String(20), default="UNKNOWN")
    last4: Mapped[str] = mapped_column(String(4), default="")
    nsu: Mapped[str] = mapped_column(String(50), default="")
    auth_code: Mapped[str] = mapped_column(String(50), default="")
    card_brand: Mapped[str] = mapped_column(String(50), default="")
    installments: Mapped[int] = mapped_column(Integer, default=1)
    merchant_receipt: Mapped[str] = mapped_column(Text, default="")
    customer_receipt: Mapped[str] = mapped_column(Text, default="")
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
