from pydantic import BaseModel, EmailStr, Field
from typing import Literal
from fastapi import FastAPI, HTTPException

import httpx

from backend.app.odoo_client import odoo_client


app = FastAPI(
    title="Integrated Sales & Order Management API",
    version="0.1.0",
)


class OrderCreate(BaseModel):
    name: str
    external_id: str
    customer_name: str
    customer_email: EmailStr | None = None
    amount_total: float = Field(default=0.0, ge=0)
    state: Literal["draft", "confirmed", "cancelled"] = "draft"


class OrderUpdate(BaseModel):
    name: str
    external_id: str
    customer_name: str
    customer_email: EmailStr | None = None
    amount_total: float = Field(default=0.0, ge=0)
    state: Literal["draft", "confirmed", "cancelled"] = "draft"


class OrderResponse(BaseModel):
    id: int
    name: str
    external_id: str
    customer_name: str
    customer_email: EmailStr | None = None
    amount_total: float
    state: Literal["draft", "confirmed", "cancelled"]
    created_at: str
    updated_at: str

class OrderCreateResponse(BaseModel):
    message: str
    order: list[int]

class OrderUpdateResponse(BaseModel):
    message: str
    order: OrderResponse

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/orders", response_model=OrderCreateResponse)
def create_order(order: OrderCreate):
    try:
        created_order = odoo_client.create_order(
            order.model_dump()
        )

        return {
            "message": "Order created in Odoo",
            "order": created_order,
        }

    except httpx.HTTPStatusError as e:
        error_text = e.response.text

        if "unique" in error_text.lower() or "external_id" in error_text.lower():
            raise HTTPException(
                status_code=409,
                detail="External Order ID already exists"
            )

        if "amount_non_negative" in error_text.lower():
            raise HTTPException(
                status_code=422,
                detail="Order amount cannot be negative"
            )

        raise HTTPException(
            status_code=502,
            detail="Odoo request failed"
        )

@app.get("/odoo/orders")
def get_odoo_orders():
    return {
        "orders": odoo_client.search_orders()
    }

@app.get("/odoo/orders/{order_id}", response_model=OrderResponse)
def get_odoo_order(order_id: int):
    order = odoo_client.get_order(order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail=f"Order {order_id} not found"
        )

    return order

@app.put(
    "/odoo/orders/{order_id}",
    response_model=OrderUpdateResponse,
)
def update_odoo_order(order_id: int, order: OrderUpdate):
    try:
        updated_order = odoo_client.update_order(
            order_id,
            order.model_dump()
        )

        if updated_order is None:
            raise HTTPException(
                status_code=404,
                detail=f"Order {order_id} not found"
            )

        return {
            "message": "Order updated in Odoo",
            "order": updated_order,
        }

    except httpx.HTTPStatusError as e:
        error_text = e.response.text

        if "unique" in error_text.lower() or "external_id" in error_text.lower():
            raise HTTPException(
                status_code=409,
                detail="External Order ID already exists"
            )

        if "amount_non_negative" in error_text.lower():
            raise HTTPException(
                status_code=422,
                detail="Order amount cannot be negative"
            )

        raise HTTPException(
            status_code=502,
            detail="Odoo request failed"
        )
