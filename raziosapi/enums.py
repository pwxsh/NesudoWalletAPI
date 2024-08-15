from enum import Enum


class InvoiceStates(str, Enum):
    ACTIVE = "ACTIVE"
    PAID = "PAID"
    DELETED = "DELETED"

class ChequeStates(str, Enum):
    ACTIVE = "ACTIVE"
    ACTIVATED = "ACTIVATED"
    DELETED = "DELETED"
