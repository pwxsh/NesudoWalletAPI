from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from raziosapi.schemas import (
    OwnWalletResponse,
    TransferResponse,
    OwnChequeResponse,
    OwnInvoiceResponse
)
from raziosapi.database.crud import CRUD
from raziosapi.database.core import get_session
from raziosapi.database.models import (
    WalletModel,
    ChequeModel,
    InvoiceModel
)


wallet_router = APIRouter(prefix="/wallet", tags=["Wallet"])

@wallet_router.get("/", response_model=OwnWalletResponse)
async def get_me(
    access_token: Annotated[str, Header()],
    session: AsyncSession = Depends(get_session)
):
    return await CRUD(WalletModel, session).get(access_token=access_token)

@wallet_router.get("/transfers", response_model=list[TransferResponse])
async def get_transfers(
    access_token: Annotated[str, Header()],
    session: AsyncSession = Depends(get_session)
):
    wallet = await CRUD(WalletModel, session).get(access_token=access_token)
    return wallet.sended + wallet.received

@wallet_router.get("/transfers/sended", response_model=list[TransferResponse])
async def get_sended_transfers(
    access_token: Annotated[str, Header()],
    session: AsyncSession = Depends(get_session)
):
    wallet = await CRUD(WalletModel, session).get(access_token=access_token)
    return wallet.sended

@wallet_router.get("/transfers/received", response_model=list[TransferResponse])
async def get_received_transfers(
    access_token: Annotated[str, Header()],
    session: AsyncSession = Depends(get_session)
):
    wallet = await CRUD(WalletModel, session).get(access_token=access_token)
    return wallet.received

@wallet_router.get("/cheques", response_model=list[OwnChequeResponse])
async def get_cheques(
    access_token: Annotated[str, Header()],
    session: AsyncSession = Depends(get_session)
):
    wallet = await CRUD(WalletModel, session).get(access_token=access_token)
    return wallet.cheques

@wallet_router.get("/cheques/{id}", response_model=OwnChequeResponse)
async def get_my_cheque(
    access_token: Annotated[str, Header()],
    id: str,
    session: AsyncSession = Depends(get_session)
):
    wallet = await CRUD(WalletModel, session).get(access_token=access_token)
    return await CRUD(ChequeModel, session).get(id=id, owner_id=wallet.id)

@wallet_router.get("/invoices", response_model=list[OwnInvoiceResponse])
async def get_invoices(
    access_token: Annotated[str, Header()],
    session: AsyncSession = Depends(get_session)
):
    wallet = await CRUD(WalletModel, session).get(access_token=access_token)
    return wallet.invoices

@wallet_router.get("/invoices/{id}", response_model=OwnInvoiceResponse)
async def get_my_invoice(
    access_token: Annotated[str, Header()],
    id: str,
    session: AsyncSession = Depends(get_session)
):
    wallet = await CRUD(WalletModel, session).get(access_token=access_token)
    return await CRUD(InvoiceModel, session).get(id=id, owner_id=wallet.id)
