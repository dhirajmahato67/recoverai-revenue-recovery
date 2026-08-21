"""Transaction Ingestion Service handling high-throughput idempotent batch persistence."""

import datetime
import time
import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import get_logger
from app.db.models import AuditLog, Customer, Order, Payment, PaymentEvent
from app.db.repositories.payment import PaymentRepository
from app.schemas.simulation import SyntheticTransactionItem
from app.schemas.transaction_ingest import (
    BatchIngestResponse,
    TransactionIngestItem,
)
from app.services.ingestion.validator import TransactionValidator

logger = get_logger("app.services.ingestion")


class TransactionIngestionService:
    """Production-grade transaction ingestion service ensuring multi-tenant isolation, data validity, and idempotency."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.payment_repo = PaymentRepository(session)

    async def ingest_batch(
        self,
        merchant_id: uuid.UUID,
        transactions: Sequence[TransactionIngestItem | SyntheticTransactionItem],
        chunk_size: int = 500,
        request_id: str | None = None,
    ) -> BatchIngestResponse:
        """Process and persist a batch of synthetic or external payment transactions with idempotent safety."""
        start_time = time.perf_counter()
        total_requested = len(transactions)

        if total_requested == 0:
            return BatchIngestResponse(
                merchant_id=merchant_id,
                requested=0,
                accepted=0,
                duplicates=0,
                rejected=0,
                duration_ms=0.0,
            )

        # 1. Convert to TransactionIngestItem if passed as synthetic model
        items_to_validate: list[TransactionIngestItem] = []
        for item in transactions:
            if isinstance(item, SyntheticTransactionItem):
                items_to_validate.append(
                    TransactionIngestItem(
                        merchant_id=merchant_id,
                        external_order_id=item.external_order_id,
                        external_payment_id=item.external_payment_id,
                        external_customer_id=item.external_customer_id,
                        customer_name=item.customer_name,
                        customer_email=item.customer_email,
                        customer_phone=item.customer_phone,
                        amount=item.amount,
                        currency=item.currency,
                        status=item.status,
                        payment_method=item.payment_method,
                        bank=item.bank,
                        error_code=item.error_code,
                        error_reason=item.error_reason,
                        created_at=item.created_at,
                        captured_at=item.captured_at,
                        event_id=item.event_id,
                        event_type=item.event_type,
                    )
                )
            elif isinstance(item, TransactionIngestItem):
                items_to_validate.append(item)
            else:
                try:
                    items_to_validate.append(TransactionIngestItem(**item))
                except Exception as exc:
                    logger.warning(f"Failed to parse transaction item: {exc}")

        # 2. Validation phase
        valid_items, rejections = TransactionValidator.validate_batch(items_to_validate)
        rejected_count = len(rejections)

        if not valid_items:
            duration_ms = (time.perf_counter() - start_time) * 1000
            return BatchIngestResponse(
                merchant_id=merchant_id,
                requested=total_requested,
                accepted=0,
                duplicates=0,
                rejected=rejected_count,
                duration_ms=round(duration_ms, 2),
                rejection_details=rejections,
            )

        accepted_count = 0
        duplicate_count = 0

        # 3. Process in chunks for high-throughput batching
        for i in range(0, len(valid_items), chunk_size):
            chunk = valid_items[i : i + chunk_size]
            chunk_accepted, chunk_duplicates = await self._process_chunk(merchant_id, chunk)
            accepted_count += chunk_accepted
            duplicate_count += chunk_duplicates

        # 4. Record Audit Log for the batch
        audit_log = AuditLog(
            merchant_id=merchant_id,
            actor_type="SYSTEM",
            actor_id="ingestion_service_v1",
            action="TRANSACTION_BATCH_INGESTED",
            resource_type="Payment",
            resource_id=f"batch_{uuid.uuid4().hex[:12]}",
            request_id=request_id,
            metadata_={
                "requested": total_requested,
                "accepted": accepted_count,
                "duplicates": duplicate_count,
                "rejected": rejected_count,
            },
        )
        self.session.add(audit_log)
        await self.session.commit()

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            f"Batch ingestion finished for merchant {merchant_id}: "
            f"requested={total_requested}, accepted={accepted_count}, "
            f"duplicates={duplicate_count}, rejected={rejected_count} in {duration_ms:.2f}ms"
        )

        return BatchIngestResponse(
            merchant_id=merchant_id,
            requested=total_requested,
            accepted=accepted_count,
            duplicates=duplicate_count,
            rejected=rejected_count,
            duration_ms=round(duration_ms, 2),
            rejection_details=rejections,
        )

    async def _process_chunk(
        self, merchant_id: uuid.UUID, chunk: list[TransactionIngestItem]
    ) -> tuple[int, int]:
        """Process and persist a single chunk with batch deduplication and resolution."""
        # A. Deduplicate external payment IDs
        payment_ext_ids = [item.external_payment_id for item in chunk]
        existing_payment_ids = await self.payment_repo.get_by_external_ids(merchant_id, payment_ext_ids)

        new_items = [item for item in chunk if item.external_payment_id not in existing_payment_ids]
        duplicates_in_chunk = len(chunk) - len(new_items)

        if not new_items:
            return 0, duplicates_in_chunk

        # B. Batch resolve or insert Customers
        customer_map: dict[str, uuid.UUID] = {}
        cust_ext_ids = list({item.external_customer_id for item in new_items})
        existing_cust_stmt = select(Customer).where(
            Customer.merchant_id == merchant_id,
            Customer.external_customer_id.in_(cust_ext_ids),
        )
        existing_customers = (await self.session.execute(existing_cust_stmt)).scalars().all()
        for cust in existing_customers:
            customer_map[cust.external_customer_id] = cust.id

        for item in new_items:
            if item.external_customer_id not in customer_map:
                new_cust = Customer(
                    merchant_id=merchant_id,
                    external_customer_id=item.external_customer_id,
                    name=item.customer_name,
                    email=item.customer_email,
                    phone_last4=item.customer_phone[-4:] if item.customer_phone else None,
                    status="ACTIVE",
                )
                self.session.add(new_cust)
                await self.session.flush()
                customer_map[item.external_customer_id] = new_cust.id

        # C. Batch resolve or insert Orders
        order_map: dict[str, uuid.UUID] = {}
        order_ext_ids = list({item.external_order_id for item in new_items})
        existing_order_stmt = select(Order).where(
            Order.merchant_id == merchant_id,
            Order.external_order_id.in_(order_ext_ids),
        )
        existing_orders = (await self.session.execute(existing_order_stmt)).scalars().all()
        for ord_entity in existing_orders:
            order_map[ord_entity.external_order_id] = ord_entity.id

        for item in new_items:
            if item.external_order_id not in order_map:
                new_order = Order(
                    merchant_id=merchant_id,
                    customer_id=customer_map[item.external_customer_id],
                    external_order_id=item.external_order_id,
                    amount=item.amount,
                    currency=item.currency,
                    status="PAID" if item.status == "CAPTURED" else "FAILED",
                    description=f"Purchase order {item.external_order_id}",
                    created_at=item.created_at or datetime.datetime.now(datetime.timezone.utc),
                )
                self.session.add(new_order)
                await self.session.flush()
                order_map[item.external_order_id] = new_order.id

        # D. Insert Payments and PaymentEvents
        payments_to_add: list[Payment] = []
        events_to_add: list[PaymentEvent] = []

        for item in new_items:
            payment_id = uuid.uuid4()
            now_ts = item.created_at or datetime.datetime.now(datetime.timezone.utc)

            payment = Payment(
                id=payment_id,
                merchant_id=merchant_id,
                order_id=order_map[item.external_order_id],
                customer_id=customer_map[item.external_customer_id],
                external_payment_id=item.external_payment_id,
                amount=item.amount,
                currency=item.currency,
                status=item.status,
                payment_method=item.payment_method,
                bank=item.bank,
                error_code=item.error_code,
                error_reason=item.error_reason,
                captured_at=item.captured_at,
                created_at=now_ts,
            )
            payments_to_add.append(payment)

            event = PaymentEvent(
                merchant_id=merchant_id,
                payment_id=payment_id,
                event_id=item.event_id or f"evt_{uuid.uuid4().hex[:16]}",
                event_type=item.event_type or ("payment.captured" if item.status == "CAPTURED" else "payment.failed"),
                payload=item.raw_event_payload
                or {
                    "payment_id": item.external_payment_id,
                    "order_id": item.external_order_id,
                    "amount": float(item.amount),
                    "status": item.status,
                    "method": item.payment_method,
                    "bank": item.bank,
                    "error_code": item.error_code,
                },
                signature_valid=True,
                status="PROCESSED",
                received_at=now_ts,
                processed_at=now_ts,
                created_at=now_ts,
            )
            events_to_add.append(event)

        self.session.add_all(payments_to_add)
        self.session.add_all(events_to_add)
        await self.session.flush()

        return len(new_items), duplicates_in_chunk
