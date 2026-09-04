from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.app.odoo_client import odoo_client

app = FastAPI(
    title="Integrated Sales & Order Management API",
    version="0.1.0",
)


class OrderCreate(BaseModel):
    name: str
    external_id: str
    customer_name: str
    state: str = "draft"


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/orders")
def create_order(order: OrderCreate):
    created_order = odoo_client.create_order(
        order.model_dump()
    )

    return {
        "message": "Order created in Odoo",
        "order": created_order,
    }


@app.get("/odoo/orders")
def get_odoo_orders():
    return {
        "orders": odoo_client.search_orders()
    }

@app.get("/odoo/orders/{order_id}")
def get_odoo_order(order_id: int):
    order = odoo_client.get_order(order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail=f"Order {order_id} not found"
        )

    return {
        "order": order
    }

@app.put("/odoo/orders/{order_id}")
def update_odoo_order(order_id: int, order: OrderCreate):
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