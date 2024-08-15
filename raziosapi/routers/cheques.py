from secrets import token_hex
from time import time
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from raziosapi.enums import ChequeStates
from raziosapi.schemas import (
    CreateCheque,
    ChequeActivate,
    ChequeResponse,
    TransferResponse,
    OwnChequeResponse
)
from raziosapi.database.crud import CRUD
from raziosapi.database.core import get_session
from raziosapi.database.models import (
    ChequeModel,
    TransferModel,
    WalletModel
)


cheques_router = APIRouter(prefix="/cheques", tags=["Cheques"])

@cheques_router.get("/{id}", response_model=ChequeResponse)
async def get_cheque(
    access_token: Annotated[str, Header()],
    id: str,
    session: AsyncSession = Depends(get_session)
):
    return await CRUD(ChequeModel, session).get(id=id)

@cheques_router.post("/new", response_model=OwnChequeResponse)
async def create_cheque(
    access_token: Annotated[str, Header()],
    data: CreateCheque,
    session: AsyncSession = Depends(get_session)
):
    wallet = await CRUD(WalletModel, session).get(access_token=access_token)

    if wallet.balance < data.amount * data.max_activations_count:
        raise HTTPException(status_code=402, details="Not enough coins")

    cheque = await CRUD(ChequeModel, session).create(
        id=token_hex(18),
        state=ChequeStates.ACTIVE,
        owner_id=wallet.id,
        amount=data.amount,
        max_activations_count=data.max_activation_count,
        password=data.password,
        has_password=data.password is not None
    )

    return cheque

@cheques_router.put("/{id}/activate", response_model=TransferResponse)
async def activate_cheque(
    access_token: Annotated[str, Header()],
    id: str,
    data: ChequeActivate,
    session: AsyncSession = Depends(get_session)
):
    cheque = await CRUD(ChequeModel, session).get(id=id)
    wallet = await CRUD(WalletModel, session).get(access_token=access_token)

    if cheque.state != ChequeStates.ACTIVE:
        raise HTTPException(status_code=403, detail="Cheque is not active")

    if await CRUD(TransferModel, session).is_exist(receiver_id=wallet.id, from_cheque_id=id):
        raise HTTPException(status_code=403, detail="Cheque is already activated")

    if cheque.has_password:
        if cheque.password != data.password:
            raise HTTPException(status_code=403, detail="Invalid password")

    transfer = await CRUD(TransferModel, session).create(
        id=token_hex(20),
        sender_id=cheque.owner_id,
        receiver_id=wallet.id,
        amount=cheque.amount,
        from_cheque_id=cheque.id
    )

    cheque.activations_count += 1
    
    if cheque.activations_count == cheque.max_activations_count:
        cheque.state = ChequeStates.ACTIVATED
        cheque.activated_at = time()

    wallet.balance += cheque.amount

    await CRUD(ChequeModel, session).update(cheque)
    await CRUD(WalletModel, session).update(wallet)

    return transfer

@cheques_router.delete("/{id}/delete")
async def delete_cheque(
    access_token: Annotated[str, Header()],
    id: str,
    session: AsyncSession = Depends(get_session)
):
    wallet = await CRUD(WalletModel, session).get(access_token=access_token)
    cheque = await CRUD(ChequeModel, session).get(id=id)

    if cheque.state != ChequeStates.ACTIVE:
        raise HTTPException(status_code=403, detail="Cheque is not active")

    if not cheque.owner_id == wallet.id:
        raise HTTPException(status_code=403, detail="You are not owner of cheque")

    refund_amount = cheque.amount * (cheque.max_activations_count - cheque.activations_count)
    wallet.balance += refund_amount

    await CRUD(ChequeModel, session).delete(cheque)
    await CRUD(WalletModel, session).update(wallet)
    
    return {"status_code": 400}
