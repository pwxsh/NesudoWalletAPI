from secrets import token_hex
from time import time
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from raziosapi.enums import InvoiceStates
from raziosapi.schemas import (
    CreateInvoice,
    InvoicePay,
    InvoiceResponse,
    OwnInvoiceResponse,
    TransferResponse
)
from raziosapi.database.crud import CRUD
from raziosapi.database.core import get_session
from raziosapi.database.models import (
    InvoiceModel,
    TransferModel,
    WalletModel
)


invoices_router = APIRouter(prefix="/invoices", tags=["Invoices"])

@invoices_router.get("/{id}", response_model=InvoiceResponse)
async def get_invoice(
    access_token: Annotated[str, Header()],
    id: str,
    session: AsyncSession = Depends(get_session)
):
    return await CRUD(InvoiceModel, session).get(id=id)

@invoices_router.post("/new", response_model=OwnInvoiceResponse)
async def create_invoice(
    access_token: Annotated[str, Header()],
    data: CreateInvoice,
    session: AsyncSession = Depends(get_session)
):
    wallet = await CRUD(WalletModel, session).get(access_token=access_token)
    invoice = await CRUD(InvoiceModel, session).create(
        id=token_hex(18),
        state=InvoiceStates.ACTIVE,
        owner_id=wallet.id,
        amount=data.amount,
        max_payments_count=data.max_payments_count,
        expiration_at=data.expiration_at
    )

    return invoice

@invoices_router.put("/{id}/pay", response_model=TransferResponse)
async def pay_invoice(
    access_token: Annotated[str, Header()],
    id: str,
    data: InvoicePay,
    session: AsyncSession = Depends(get_session)
):
    wallet = await CRUD(WalletModel, session).get(access_token=access_token)
    invoice = await CRUD(InvoiceModel, session).get(id=id)

    if invoice.state != InvoiceStates.ACTIVE:
        raise HTTPException(status_code=403, detail="Invoice is not active")

    if invoice.expiration_at >= time():
        raise HTTPException(status_code=404, detail="Invoice is expired")

    if wallet.balance < invoice.amount:
        raise HTTPException(status_code=402, detail="Not enough coins")

    payment_amount = invoice.amount if invoice.amount != 0 else data.amount

    transfer = await CRUD(TransferModel, session).create(
        id=token_hex(20),
        sender_id=wallet.id,
        receiver_id=invoice.owner.id,
        amount=payment_amount,
        from_invoice_id=invoice.id
    )

    wallet.balance -= payment_amount
    invoice.owner.balance += payment_amount

    invoice.payments_count += 1

    if invoice.payments_count == invoice.max_payments_count:
        invoice.state = InvoiceStates.PAID
        invoice.paid_at = time()

    await CRUD(WalletModel, session).update(wallet)
    await CRUD(InvoiceModel, session).update(invoice)

    return transfer

@invoices_router.delete("/{id}/delete")
async def delete_invoice(
    access_token: Annotated[str, Header()],
    id: str,
    session: AsyncSession = Depends(get_session)
):
    wallet = await CRUD(WalletModel, session).get(access_token=access_token)
    invoice = await CRUD(InvoiceModel, session).get(id=id)

    if invoice.state != InvoiceStates.ACTIVE:
        raise HTTPException(status_code=403, detail="Invoice is not active")

    if invoice.owner_id != wallet.id:
        raise HTTPException(status_code=403, detail="You are not owner of invoice")

    await CRUD(InvoiceModel, session).delete(id=id)

    return {"status_code": 400}
