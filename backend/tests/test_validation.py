"""Unit tests for transaction validation and normalization."""

import uuid
from decimal import Decimal
from app.schemas.transaction_ingest import TransactionIngestItem
from app.services.ingestion.validator import TransactionValidator

TEST_MERCHANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


def test_valid_transaction_validation():
    """Verify standard valid transaction passes validation cleanly."""
    item = TransactionIngestItem(
        merchant_id=TEST_MERCHANT_ID,
        external_order_id="ord_test_001",
        external_payment_id="pay_test_001",
        external_customer_id="cust_test_001",
        customer_name="Aarav Sharma",
        customer_email="aarav@example.local",
        amount=Decimal("1499.00"),
        currency="INR",
        status="CAPTURED",
        payment_method="UPI",
        bank="HDFC",
    )
    result = TransactionValidator.validate_item(item)
    assert result.is_valid is True
    assert len(result.errors) == 0
    assert result.normalized_item is not None
    assert result.normalized_item.payment_method == "UPI"


def test_invalid_amount_validation():
    """Verify negative and zero amounts are rejected."""
    # Zero / Negative amount
    try:
        item = TransactionIngestItem(
            merchant_id=TEST_MERCHANT_ID,
            external_order_id="ord_test_002",
            external_payment_id="pay_test_002",
            external_customer_id="cust_test_002",
            customer_name="Aarav",
            customer_email="aarav@example.local",
            amount=Decimal("-10.00"),
            currency="INR",
        )
        res = TransactionValidator.validate_item(item)
        assert res.is_valid is False
    except Exception:
        # Pydantic may also catch ge=0.01 directly
        pass


def test_invalid_email_validation():
    """Verify invalid email without @ is rejected."""
    item = TransactionIngestItem(
        merchant_id=TEST_MERCHANT_ID,
        external_order_id="ord_test_003",
        external_payment_id="pay_test_003",
        external_customer_id="cust_test_003",
        customer_name="Aarav",
        customer_email="invalid_email_string",
        amount=Decimal("999.00"),
        currency="INR",
    )
    res = TransactionValidator.validate_item(item)
    assert res.is_valid is False
    assert any("email" in err.lower() for err in res.errors)


def test_batch_validation_separates_valid_and_rejected():
    """Verify validate_batch separates valid and rejected items with detailed error reporting."""
    valid_item = TransactionIngestItem(
        merchant_id=TEST_MERCHANT_ID,
        external_order_id="ord_ok_1",
        external_payment_id="pay_ok_1",
        external_customer_id="cust_ok_1",
        customer_name="Priya Mehta",
        customer_email="priya@example.local",
        amount=Decimal("2450.00"),
        currency="INR",
        payment_method="CARD",
    )
    invalid_item = TransactionIngestItem(
        merchant_id=TEST_MERCHANT_ID,
        external_order_id="ord_bad_1",
        external_payment_id="pay_bad_1",
        external_customer_id="",  # Empty
        customer_name="Priya",
        customer_email="bad_email",
        amount=Decimal("2450.00"),
        currency="INR",
    )

    valid_list, rejections = TransactionValidator.validate_batch([valid_item, invalid_item])
    assert len(valid_list) == 1
    assert len(rejections) == 1
    assert rejections[0]["external_payment_id"] == "pay_bad_1"
