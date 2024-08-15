from typing import Annotated

from pydantic import BaseModel, Field

from raziosapi.enums import ChequeStates, InvoiceStates


TelegramId = Annotated[int, Field(gt=0)]
WalletIdStr = Annotated[str, Field(min_length=16, max_length=16)]
TransferIdStr = Annotated[str, Field(min_length=20, max_length=20)]
ChequeIdStr = Annotated[str, Field(min_length=18, max_length=18)]
InvoiceIdStr = Annotated[str, Field(min_length=18, max_length=18)]
PasswordStr = Annotated[str, Field(min_length=1, max_length=128)]
Timestamp = Annotated[float, Field(gt=0)]

class CreateWallet(BaseModel):
    telegram_id: TelegramId

class CreateTransfer(BaseModel):
    receiver_id: WalletIdStr
    amount: int = Field(gt=0)

class CreateCheque(BaseModel):
    amount: int = Field(gt=0)
    max_activations_count: int = Field(gt=0)
    password: str | None

class ChequeActivate(BaseModel):
    password: PasswordStr | None = None

class CreateInvoice(BaseModel):
    amount: int = Field(ge=0)
    max_payments_count: int = Field(ge=0)
    expiration_at: Timestamp | None

class InvoicePay(BaseModel):
    amount: int | None = Field(ge=0)

class OwnWalletResponse(BaseModel):
    id: WalletIdStr
    telegram_id: TelegramId
    balance: int = Field(ge=0)

class TransferResponse(BaseModel):
    id: TransferIdStr
    sender_id: WalletIdStr
    receiver_id: WalletIdStr
    amount: int = Field(gt=0)
    from_cheque_id: ChequeIdStr | None
    from_invoice_id: InvoiceIdStr | None

class ChequeResponse(BaseModel):
    id: ChequeIdStr
    state: ChequeStates
    owner_id: WalletIdStr
    amount: int = Field(gt=0)
    max_activations_count: int = Field(gt=0)
    activations_count: int = Field(ge=0)
    has_password: bool
    created_at: Timestamp

class OwnChequeResponse(ChequeResponse):
    password: PasswordStr | None
    activations: list["TransferResponse"]

    class Config:
        from_attributes = True

class InvoiceResponse(BaseModel):
    id: InvoiceIdStr
    state: InvoiceStates
    owner_id: WalletIdStr
    amount: int = Field(ge=0)
    max_payments_count: int = Field(gt=0)
    payments_count: int = Field(ge=0)
    expiration_at: Timestamp | None
    created_at: Timestamp

class OwnInvoiceResponse(InvoiceResponse):
    payments: list["TransferResponse"]

    class Config:
        from_attributes = True
