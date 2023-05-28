import pytest
from fastapi.testclient import TestClient
from src.server import app

client = TestClient(app)


class DummyOrder:
    def __init__(self, id, quantity, status):
        self.id = id
        self.quantity = quantity
        self.stocks = "USDUSD"
        self.status = status


@pytest.mark.parametrize(
    "test_body,expected_response_code",
    [
        ({"stocks": "GBPUSD", "quantity": 123}, 201),
        ({"stocks": "GBPUSD", "quantity": "invalid_qty"}, 400),
        ({"stocks": "invalid_stock", "quantity": 123}, 400),
        ({"stocks": "invalid_stock"}, 400),
        ({"stocks": "NNNUSD", "quantity": 123}, 400),
    ],
)
def test_create_order(test_body, expected_response_code):
    test_request = client.post("/orders", json=test_body)
    assert test_request.status_code == expected_response_code


def test_get_orders(mocker):
    test_order_db = ["order_1", "order_2"]
    mocker.patch("src.server.orders_db", test_order_db)
    test_request = client.get("/orders")
    assert test_request.status_code == 200
    assert test_request.json() == test_order_db


@pytest.mark.parametrize(
    "order_id, order_id_target, status_code",
    [
        ("UUID1111", "UUID1111", 200),
        ("UUID1111", "UUID2222", 404),
    ],
)
def test_get_order(mocker, order_id, order_id_target, status_code):
    test_order_db = [DummyOrder(id=order_id, quantity=10, status="PENDING")]
    mocker.patch("src.server.orders_db", test_order_db)
    test_request = client.get(f"/orders/{order_id_target}")

    assert test_request.status_code == status_code


@pytest.mark.parametrize(
    "order_id, order_id_target, status_code, final_status",
    [
        ("UUID1111", "UUID1111", 204, "CANCELLED"),
        ("UUID1111", "UUID2222", 404, "PENDING"),
    ],
)
def test_delete_order(mocker, order_id, order_id_target, status_code, final_status):
    test_order_db = [DummyOrder(id=order_id, quantity=10, status="PENDING")]
    mocker.patch("src.server.orders_db", test_order_db)
    test_request = client.delete(f"/orders/{order_id_target}")

    assert test_request.status_code == status_code
    assert test_order_db[0].status == final_status


# def test_websocket():
#     with client.websocket_connect("/ws") as websocket:
#         assert data == {"msg": "Hello WebSocket"}
