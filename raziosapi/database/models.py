from time import time

from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)


class BaseModel(DeclarativeBase):
    __abstract__ = True

    id: Mapped[str] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[float] = mapped_column(default=time)
    updated_at: Mapped[float] = mapped_column(default=time, onupdate=time)

class WalletModel(BaseModel):
    __tablename__ = "wallets" 

    telegram_id: Mapped[int] = mapped_column(index=True, unique=True)
    access_token: Mapped[str] = mapped_column(index=True, unique=True)
    balance: Mapped[int] = mapped_column(default=0)

    sended: Mapped[list["TransferModel"]] = relationship(
        back_populates="sender",
        foreign_keys="[TransferModel.sender_id]",
        lazy="joined"
    )

    received: Mapped[list["TransferModel"]] = relationship(
        back_populates="receiver",
        foreign_keys="[TransferModel.receiver_id]",
        lazy="joined"
    )

    cheques: Mapped[list["ChequeModel"]] = relationship(
        back_populates="owner", lazy="joined"
    )

    invoices: Mapped[list["InvoiceModel"]] = relationship(
        back_populates="owner", lazy="joined"
    )

class TransferModel(BaseModel):
    __tablename__ = "transfers"

    sender_id: Mapped[str] = mapped_column(ForeignKey("wallets.id"))
    receiver_id: Mapped[str] = mapped_column(ForeignKey("wallets.id"))
    amount: Mapped[int] = mapped_column()
    from_cheque_id: Mapped[str] = mapped_column(
        ForeignKey("cheques.id"), nullable=True
    )

    from_invoice_id: Mapped[str] = mapped_column(
        ForeignKey("invoices.id"), nullable=True
    )

    sender: Mapped["WalletModel"] = relationship(
        back_populates="sended",
        foreign_keys=[sender_id],
        lazy="joined"
    )

    receiver: Mapped["WalletModel"] = relationship(
        back_populates="received",
        foreign_keys=[receiver_id],
        lazy="joined"
    )

    from_cheque: Mapped["ChequeModel"] = relationship(
        back_populates="activations",
        foreign_keys=[from_cheque_id],
        lazy="joined"
    )

    from_invoice: Mapped["InvoiceModel"] = relationship(
        back_populates="payments",
        foreign_keys=[from_invoice_id],
        lazy="joined"
    )

class ChequeModel(BaseModel):
    __tablename__ = "cheques"

    state: Mapped[str] = mapped_column()
    owner_id: Mapped[str] = mapped_column(ForeignKey("wallets.id"))
    amount: Mapped[int] = mapped_column()
    max_activations_count: Mapped[int] = mapped_column(default=1)
    activations_count: Mapped[int] = mapped_column(default=0)
    activated_at: Mapped[float] = mapped_column(nullable=True)
    password: Mapped[str] = mapped_column(nullable=True)
    has_password: Mapped[bool] = mapped_column(nullable=True)

    owner: Mapped["WalletModel"] = relationship(
        back_populates="cheques",
        foreign_keys=[owner_id],
        lazy="joined"
    )

    activations: Mapped[list["TransferModel"]] = relationship(
        back_populates="from_cheque", lazy="joined"
    )

class InvoiceModel(BaseModel):
    __tablename__ = "invoices" 
 
    state: Mapped[str] = mapped_column()
    owner_id: Mapped[str] = mapped_column(ForeignKey("wallets.id"))
    amount: Mapped[int] = mapped_column(default=0)
    max_payments_count: Mapped[int] = mapped_column(default=1)
    payments_count: Mapped[int] = mapped_column(default=0)
    expiration_at: Mapped[float] = mapped_column(nullable=True)
    paid_at: Mapped[float] = mapped_column(nullable=True)
    
    owner: Mapped["WalletModel"] = relationship(
        back_populates="invoices",
        foreign_keys=[owner_id],
        lazy="joined"
    )

    payments: Mapped[list["TransferModel"]] = relationship(
        back_populates="from_invoice", lazy="joined"
    )
