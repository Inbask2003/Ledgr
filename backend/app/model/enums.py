from enum import StrEnum


class PaymentStatus(StrEnum):
    CREATED = "created"
    CAPTURED = "captured"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PARTIALLY_REFUNDED = "partially_refunded"
    REFUNDED = "refunded"


class LedgerDirection(StrEnum):
    DEBIT = "debit"
    CREDIT = "credit"


class LedgerAccount(StrEnum):
    MERCHANT_BALANCE = "merchant_balance"
    PAYMENTS_CLEARING = "payments_clearing"


class WebhookStatus(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
