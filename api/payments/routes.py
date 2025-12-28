"""Payment FastAPI routes."""

import logging
from typing import Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, status

from packages.db.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from .models import (
    PaymentCreateRequest, PaymentExecuteRequest, RefundRequest,
    PaymentCreateResponse, PaymentExecuteResponse, RefundResponse
)
from .service import PaymentService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/paypal/create", response_model=PaymentCreateResponse)
async def create_paypal_payment(
    request: PaymentCreateRequest,
    db: AsyncSession = Depends(get_async_db)
) -> PaymentCreateResponse:
    """Create a PayPal payment for an order."""
    result = await PaymentService.create_paypal_payment(
        db=db,
        order_id=request.order_id,
        return_url=request.return_url,
        cancel_url=request.cancel_url
    )

    if not result["success"]:
        if "not found" in result["error"].lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
        elif "already paid" in result["error"].lower() or "cannot be paid" in result["error"].lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["error"])

    return PaymentCreateResponse(**result)


@router.post("/paypal/execute", response_model=PaymentExecuteResponse)
async def execute_paypal_payment(
    request: PaymentExecuteRequest,
    db: AsyncSession = Depends(get_async_db)
) -> PaymentExecuteResponse:
    """Execute a PayPal payment after user approval."""
    result = await PaymentService.execute_paypal_payment(
        db=db,
        payment_id=request.payment_id,
        payer_id=request.payer_id
    )

    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])

    return PaymentExecuteResponse(**result)


@router.get("/paypal/{payment_id}/details")
async def get_payment_details(payment_id: str) -> Dict[str, Any]:
    """Get PayPal payment details."""
    result = PaymentService.get_payment_details(payment_id)

    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])

    return result["payment"]


@router.post("/paypal/{order_id}/refund", response_model=RefundResponse)
async def refund_paypal_payment(
    order_id: UUID,
    request: RefundRequest,
    db: AsyncSession = Depends(get_async_db)
) -> RefundResponse:
    """Refund a PayPal payment for an order."""
    result = await PaymentService.refund_paypal_payment(
        db=db,
        order_id=order_id,
        amount=request.amount
    )

    if not result["success"]:
        if "not found" in result["error"].lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])

    return RefundResponse(**result)