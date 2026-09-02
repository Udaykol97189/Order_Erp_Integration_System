import httpx

from backend.app.config import settings


class OdooClient:
    def __init__(self):
        self.base_url = settings.odoo_url.rstrip("/")
        self.headers = {
            "Authorization": f"bearer {settings.odoo_api_key}",
            "X-Odoo-Database": settings.odoo_db,
            "Content-Type": "application/json",
        }

    def search_orders(self):
        url = f"{self.base_url}/json/2/order.erp.order/search_read"

        response = httpx.post(
            url,
            headers=self.headers,
            json={
                "domain": [],
                "fields": [
                    "id",
                    "name",
                    "external_id",
                    "customer_name",
                    "state",
                ],
                "limit": 10,
            },
            timeout=10.0,
        )

        response.raise_for_status()
        return response.json()

    def create_order(self, order_data):
        url = f"{self.base_url}/json/2/order.erp.order/create"
    
        response = httpx.post(
            url,
            headers=self.headers,
            json={
                "vals_list": [order_data],
            },
            timeout=10.0,
        )

        response.raise_for_status()
        return response.json()

odoo_client = OdooClient()