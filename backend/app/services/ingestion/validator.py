"""Transaction validation and normalization layer for RecoverAI."""

import uuid
from decimal import Decimal
from typing import Any
from pydantic import BaseModel
from app.schemas.transaction_ingest import TransactionIngestItem

VALID_PAYMENT_METHODS = {"UPI", "CARD", "NETBANKING", "WALLET", "OTHER"}
VALID_STATUSES = {"CAPTURED", "FAILED", "CREATED", "AUTHORIZED", "REFUNDED", "CANCELLED"}
VALID_CURRENCIES = {"INR", "USD", "EUR", "GBP"}


class ValidationResult(BaseModel):
    """Validation output with structured error telemetry."""

    is_valid: bool
    errors: list[str] = []
    normalized_item: TransactionIngestItem | None = None


class TransactionValidator:
    """Validates raw and synthetic payment transaction payloads prior to persistence."""

    @classmethod
    def validate_item(cls, item: TransactionIngestItem | dict[str, Any]) -> ValidationResult:
        """Validate and normalize a single transaction payload."""
        errors: list[str] = []

        if isinstance(item, dict):
            try:
                item = TransactionIngestItem(**item)
            except Exception as exc:
                return ValidationResult(is_valid=False, errors=[f"Malformed schema: {str(exc)}"])

        # 1. Merchant ID validation
        if not isinstance(item.merchant_id, uuid.UUID):
            try:
                uuid.UUID(str(item.merchant_id))
            except (ValueError, TypeError):
                errors.append("Invalid merchant_id format; must be a valid UUID.")

        # 2. External identifiers
        if not item.external_order_id or not item.external_order_id.strip():
            errors.append("external_order_id cannot be empty.")
        if not item.external_payment_id or not item.external_payment_id.strip():
            errors.append("external_payment_id cannot be empty.")
        if not item.external_customer_id or not item.external_customer_id.strip():
            errors.append("external_customer_id cannot be empty.")

        # 3. Customer info
        if not item.customer_name or not item.customer_name.strip():
            errors.append("customer_name cannot be empty.")
        if not item.customer_email or "@" not in item.customer_email:
            errors.append("customer_email must be a valid email address.")

        # 4. Amount and currency
        if item.amount is None or item.amount <= Decimal("0.00"):
            errors.append("amount must be a positive decimal greater than 0.00.")
        if item.currency.upper() not in VALID_CURRENCIES:
            errors.append(f"currency '{item.currency}' is unsupported; allowed: {VALID_CURRENCIES}")

        # 5. Method and Status enums
        norm_method = item.payment_method.upper()
        if norm_method not in VALID_PAYMENT_METHODS:
            errors.append(f"payment_method '{item.payment_method}' is invalid; allowed: {VALID_PAYMENT_METHODS}")

        norm_status = item.status.upper()
        if norm_status not in VALID_STATUSES:
            errors.append(f"status '{item.status}' is invalid; allowed: {VALID_STATUSES}")

        if errors:
            return ValidationResult(is_valid=False, errors=errors)

        # Return normalized object
        normalized = item.model_copy(
            update={
                "payment_method": norm_method,
                "status": norm_status,
                "currency": item.currency.upper(),
            }
        )
        return ValidationResult(is_valid=True, errors=[], normalized_item=normalized)

    @classmethod
    def validate_batch(cls, items: list[TransactionIngestItem]) -> tuple[list[TransactionIngestItem], list[dict[str, Any]]]:
        """Validate a batch of transactions, separating valid items from rejected payloads."""
        valid_items: list[TransactionIngestItem] = []
        rejections: list[dict[str, Any]] = []

        for idx, item in enumerate(items):
            res = cls.validate_item(item)
            if res.is_valid and res.normalized_item:
                valid_items.append(res.normalized_item)
            else:
                rejections.append({
                    "index": idx,
                    "external_payment_id": getattr(item, "external_payment_id", "unknown"),
                    "errors": res.errors,
                })

        return valid_items, rejections
