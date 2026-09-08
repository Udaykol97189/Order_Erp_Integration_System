import httpx
from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


# --------------------------------------------------
# POST /orders
# --------------------------------------------------

def test_create_order_success(monkeypatch):
    def mock_create_order(order_data):
        return [101]

    monkeypatch.setattr(
        "backend.app.main.odoo_client.create_order",
        mock_create_order,
    )

    response = client.post(
        "/orders",
        json={
            "name": "Test Order",
            "external_id": "PYTEST-001",
            "customer_name": "John",
            "customer_email": "john@example.com",
            "amount_total": 100,
            "state": "draft",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Order created in Odoo"
    assert response.json()["order"] == [101]


def test_create_order_invalid_state():
    response = client.post(
        "/orders",
        json={
            "name": "Test Order",
            "external_id": "PYTEST-002",
            "customer_name": "John",
            "customer_email": "john@example.com",
            "amount_total": 100,
            "state": "invalid",
        },
    )

    assert response.status_code == 422


def test_create_order_negative_amount():
    response = client.post(
        "/orders",
        json={
            "name": "Test Order",
            "external_id": "PYTEST-003",
            "customer_name": "John",
            "customer_email": "john@example.com",
            "amount_total": -100,
            "state": "draft",
        },
    )

    assert response.status_code == 422


def test_create_order_invalid_email():
    response = client.post(
        "/orders",
        json={
            "name": "Test Order",
            "external_id": "PYTEST-004",
            "customer_name": "John",
            "customer_email": "invalid-email",
            "amount_total": 100,
            "state": "draft",
        },
    )

    assert response.status_code == 422


def test_create_order_duplicate_external_id(monkeypatch):
    def mock_create_order(order_data):
        request = httpx.Request(
            "POST",
            "http://testserver/orders",
        )

        response = httpx.Response(
            400,
            request=request,
            text="External Order ID must be unique.",
        )

        raise httpx.HTTPStatusError(
            "Duplicate external_id",
            request=request,
            response=response,
        )

    monkeypatch.setattr(
        "backend.app.main.odoo_client.create_order",
        mock_create_order,
    )

    response = client.post(
        "/orders",
        json={
            "name": "Test Order",
            "external_id": "PYTEST-DUPLICATE",
            "customer_name": "John",
            "customer_email": "john@example.com",
            "amount_total": 100,
            "state": "draft",
        },
    )

    assert response.status_code == 409


# --------------------------------------------------
# GET /odoo/orders/{order_id}
# --------------------------------------------------

def test_get_order_success(monkeypatch):
    def mock_get_order(order_id):
        return {
            "id": order_id,
            "name": "Test Order",
            "external_id": "PYTEST-GET-001",
            "customer_name": "John",
            "customer_email": "john@example.com",
            "amount_total": 100,
            "state": "draft",
            "created_at": "2026-09-08 10:00:00",
            "updated_at": "2026-09-08 10:00:00",
        }

    monkeypatch.setattr(
        "backend.app.main.odoo_client.get_order",
        mock_get_order,
    )

    response = client.get("/odoo/orders/101")

    assert response.status_code == 200

def test_get_order_not_found(monkeypatch):
    def mock_get_order(order_id):
        return None

    monkeypatch.setattr(
        "backend.app.main.odoo_client.get_order",
        mock_get_order,
    )

    response = client.get("/odoo/orders/999999")

    assert response.status_code == 404


# --------------------------------------------------
# PUT /odoo/orders/{order_id}
# --------------------------------------------------

def test_update_order_success(monkeypatch):
    def mock_update_order(order_id, order_data):
        return {
            "id": order_id,
            "name": "Updated Order",
            "external_id": "PYTEST-UPDATE-001",
            "customer_name": "John Updated",
            "customer_email": "john@example.com",
            "amount_total": 200,
            "state": "confirmed",
            "created_at": "2026-09-08 10:00:00",
            "updated_at": "2026-09-08 11:00:00",
        }

    monkeypatch.setattr(
        "backend.app.main.odoo_client.update_order",
        mock_update_order,
    )

    response = client.put(
        "/odoo/orders/101",
        json={
            "name": "Updated Order",
            "external_id": "PYTEST-UPDATE-001",
            "customer_name": "John Updated",
            "customer_email": "john@example.com",
            "amount_total": 200,
            "state": "confirmed",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Order updated in Odoo"
    assert response.json()["order"]["amount_total"] == 200


def test_update_order_not_found(monkeypatch):
    def mock_update_order(order_id, order_data):
        return None

    monkeypatch.setattr(
        "backend.app.main.odoo_client.update_order",
        mock_update_order,
    )

    response = client.put(
        "/odoo/orders/999999",
        json={
            "name": "Updated Order",
            "external_id": "PYTEST-UPDATE-002",
            "customer_name": "John",
            "customer_email": "john@example.com",
            "amount_total": 100,
            "state": "draft",
        },
    )

    assert response.status_code == 404


def test_update_order_invalid_state():
    response = client.put(
        "/odoo/orders/101",
        json={
            "name": "Updated Order",
            "external_id": "PYTEST-UPDATE-003",
            "customer_name": "John",
            "customer_email": "john@example.com",
            "amount_total": 100,
            "state": "invalid",
        },
    )

    assert response.status_code == 422


def test_update_order_negative_amount():
    response = client.put(
        "/odoo/orders/101",
        json={
            "name": "Updated Order",
            "external_id": "PYTEST-UPDATE-004",
            "customer_name": "John",
            "customer_email": "john@example.com",
            "amount_total": -50,
            "state": "draft",
        },
    )

    assert response.status_code == 422


def test_update_order_duplicate_external_id(monkeypatch):
    def mock_update_order(order_id, order_data):
        request = httpx.Request(
            "PUT",
            "http://testserver/odoo/orders/101",
        )

        response = httpx.Response(
            400,
            request=request,
            text="External Order ID must be unique.",
        )

        raise httpx.HTTPStatusError(
            "Duplicate external_id",
            request=request,
            response=response,
        )

    monkeypatch.setattr(
        "backend.app.main.odoo_client.update_order",
        mock_update_order,
    )

    response = client.put(
        "/odoo/orders/101",
        json={
            "name": "Updated Order",
            "external_id": "PYTEST-DUPLICATE",
            "customer_name": "John",
            "customer_email": "john@example.com",
            "amount_total": 100,
            "state": "draft",
        },
    )

    assert response.status_code == 409