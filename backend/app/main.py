from fastapi import FastAPI
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