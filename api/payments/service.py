"""Payment service layer for business logic."""

import logging
from typing import Dict, Any, Optional
from uuid import UUID
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from packages.db.models import Order as OrderModel, PaymentStatus, OrderStatus
from .providers.paypal.service import paypal_provider

logger = logging.getLogger(__name__)


class PaymentService:
    """Business logic for payment operations."""

    @staticmethod
    async def create_paypal_payment(
        db: AsyncSession,
        order_id: UUID,
        return_url: Optional[str] = None,
        cancel_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a PayPal payment for an order."""
        try:
            # Get order
            query = select(OrderModel).where(OrderModel.id == order_id)
            result = await db.execute(query)
            order = result.scalar_one_or_none()

            if not order:
                return {"success": False, "error": "Order not found"}

            if order.status not in [OrderStatus.DRAFT, OrderStatus.PENDING_PAYMENT]:
                return {"success": False, "error": f"Order cannot be paid in {order.status} status"}

            if order.payment_status == PaymentStatus.CAPTURED:
                return {"success": False, "error": "Order is already paid"}

            # Create PayPal payment
            description = f"Farm Order #{str(order.id)[:8]} - From Field to You"
            payment_result = paypal_provider.create_payment(
                amount=order.total_amount,
                currency=order.currency,
                description=description,
                return_url=return_url,
                cancel_url=cancel_url,
                order_id=str(order.id)
            )

            if not payment_result["success"]:
                return {"success": False, "error": f"PayPal payment creation failed: {payment_result.get('error')}"}

            # Update order
            update_stmt = update(OrderModel).where(OrderModel.id == order_id).values(
                payment_provider="PAYPAL",
                payment_reference=payment_result["payment_id"],
                payment_status=PaymentStatus.PENDING,
                status=OrderStatus.PENDING_PAYMENT
            )

            await db.execute(update_stmt)
            await db.commit()

            return {
                "success": True,
                "order_id": str(order_id),
                "payment_id": payment_result["payment_id"],
                "approval_url": payment_result["approval_url"],
                "amount": float(order.total_amount),
                "currency": order.currency
            }

        except Exception as e:
            logger.error(f"Error creating PayPal payment: {str(e)}")
            await db.rollback()
            return {"success": False, "error": "Internal server error"}

    @staticmethod
    async def execute_paypal_payment(
        db: AsyncSession,
        payment_id: str,
        payer_id: str
    ) -> Dict[str, Any]:
        """Execute PayPal payment after approval."""
        try:
            execution_result = paypal_provider.execute_payment(payment_id, payer_id)

            if not execution_result["success"]:
                return {"success": False, "error": f"PayPal payment execution failed: {execution_result.get('error')}"}

            # Update order status
            order_id = execution_result.get("order_id")
            if order_id:
                try:
                    order_uuid = UUID(order_id)
                    update_stmt = update(OrderModel).where(OrderModel.id == order_uuid).values(
                        payment_status=PaymentStatus.CAPTURED,
                        status=OrderStatus.PAID,
                        payment_reference=execution_result.get("transaction_id") or payment_id
                    )
                    await db.execute(update_stmt)
                    await db.commit()
                except ValueError:
                    logger.warning(f"Invalid order ID from PayPal: {order_id}")

            return {
                "success": True,
                "payment_id": payment_id,
                "transaction_id": execution_result.get("transaction_id"),
                "payment_state": execution_result.get("payment_state"),
                "order_id": order_id,
                "amount": execution_result.get("amount"),
                "currency": execution_result.get("currency")
            }

        except Exception as e:
            logger.error(f"Error executing PayPal payment: {str(e)}")
            await db.rollback()
            return {"success": False, "error": "Internal server error"}

    @staticmethod
    def get_payment_details(payment_id: str) -> Dict[str, Any]:
        """Get PayPal payment details."""
        try:
            result = paypal_provider.get_payment_details(payment_id)
            if result["success"]:
                return {"success": True, "payment": result["payment"]}
            else:
                return {"success": False, "error": "Payment not found"}
        except Exception as e:
            logger.error(f"Error getting PayPal payment details: {str(e)}")
            return {"success": False, "error": "Internal server error"}

    @staticmethod
    async def refund_paypal_payment(
        db: AsyncSession,
        order_id: UUID,
        amount: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Refund PayPal payment for an order."""
        try:
            # Get order
            query = select(OrderModel).where(OrderModel.id == order_id)
            result = await db.execute(query)
            order = result.scalar_one_or_none()

            if not order:
                return {"success": False, "error": "Order not found"}

            if order.payment_provider != "PAYPAL":
                return {"success": False, "error": "Order was not paid with PayPal"}

            if order.payment_status != PaymentStatus.CAPTURED:
                return {"success": False, "error": "Order payment is not captured"}

            if not order.payment_reference:
                return {"success": False, "error": "No PayPal transaction reference found"}

            # Process refund
            refund_result = paypal_provider.refund_payment(order.payment_reference, amount)

            if not refund_result["success"]:
                return {"success": False, "error": f"PayPal refund failed: {refund_result.get('error')}"}

            # Update order status
            new_payment_status = PaymentStatus.REFUNDED
            if amount and amount < order.total_amount:
                new_payment_status = PaymentStatus.CAPTURED

            update_stmt = update(OrderModel).where(OrderModel.id == order_id).values(
                payment_status=new_payment_status
            )

            await db.execute(update_stmt)
            await db.commit()

            return {
                "success": True,
                "order_id": str(order_id),
                "refund_id": refund_result["refund_id"],
                "refund_state": refund_result["refund_state"],
                "refund_amount": amount or order.total_amount,
                "currency": order.currency
            }

        except Exception as e:
            logger.error(f"Error processing PayPal refund: {str(e)}")
            await db.rollback()
            return {"success": False, "error": "Internal server error"}