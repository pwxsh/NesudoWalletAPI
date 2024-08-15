from secrets import token_hex
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from raziosapi.schemas import (
    CreateTransfer,
    TransferResponse
)
from raziosapi.database.crud import CRUD
from raziosapi.database.core import get_session
from raziosapi.database.models import (
    WalletModel,
    TransferModel
)


transfers_router = APIRouter(prefix="/transfers", tags=["Transfers"])

@transfers_router.get("/{id}", response_model=TransferResponse)
async def get_transfer(
    access_token: Annotated[str, Header()],
    id: str,
    session: AsyncSession = Depends(get_session)
):
    return await CRUD(TransferModel, session).get(id=id)

@transfers_router.post("/new", response_model=TransferResponse)
async def create_transfer(
    access_token: Annotated[str, Header()],
    data: CreateTransfer,
    session: AsyncSession = Depends(get_session)
):
    wallet = await CRUD(WalletModel, session).get(access_token=access_token)

    if wallet.balance < data.amount:
        raise HTTPException(status_code=402, details="Not enough coins")

    transfer = await CRUD(TransferModel, session).create(
        id=token_hex(20),
        sender_id=wallet.id,
        receiver_id=data.receiver_id,
        amount=data.amount
    )
    return transfer
