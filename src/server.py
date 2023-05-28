import asyncio
import random
from pydantic import ValidationError
import uvicorn
from fastapi import FastAPI, WebSocket, status
from fastapi.responses import JSONResponse
from src.order import Order, retrieve_order

app = FastAPI()

active_connections = []
orders_db = []


@app.post("/orders", response_model=dict)
async def create_order(orderBody: dict):
    exception = None

    try:
        new_order = Order(
            stocks=orderBody["stocks"], quantity=orderBody["quantity"], status="PENDING"
        )
    except ValidationError as e:
        exception = give_error(f"{e.raw_errors[0]._loc} value is invalid", 10)
    except KeyError as e:
        exception = give_error(f"{e.args[0]} value is missing", 20)

    if exception:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=exception,
        )

    orders_db.append(new_order)
    asyncio.create_task(execute_order(new_order.id))

    response_body = {"id": new_order.id, "status": new_order.status}

    await broadcast_over_websocket(
        f"Order {new_order.id} for {new_order.stocks} received. Current status - {new_order.status}"
    )

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=response_body)


@app.get("/orders/{order_id}")
async def read_item(order_id: str) -> dict:
    order = retrieve_order(order_id=order_id, order_list=orders_db)

    if order:
        response_body = {"stocks": order.stocks, "quantity": order.quantity}
        response_code = status.HTTP_200_OK
    else:
        response_body = give_error(f"order {order_id} not found", 40)
        response_code = status.HTTP_404_NOT_FOUND

    return JSONResponse(status_code=response_code, content=response_body)


@app.get("/orders")
async def read_item() -> list:
    return orders_db


@app.delete("/orders/{order_id}")
async def delete_order(order_id: str) -> dict:
    order = retrieve_order(order_id=order_id, order_list=orders_db, delete=True)

    if order:
        response_body = None
        response_code = status.HTTP_204_NO_CONTENT
    else:
        response_body = give_error(f"Order {order_id} not found", 40)
        response_code = status.HTTP_404_NOT_FOUND

    return JSONResponse(status_code=response_code, content=response_body)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    active_connections.append(websocket)
    await websocket.accept()
    while True:
        # think about keep-alive mechanism
        await websocket.receive_text()


async def broadcast_over_websocket(message: str):
    if len(active_connections) > 0:
        for connection in active_connections:
            await connection.send_text(message)
    else:
        print("No websocket connected; skipping update")


def give_error(message: str, code: int) -> dict:
    return {"message": message, "code": code}


async def execute_order(order_id):
    # Wait for a random delay between 1 and 10 seconds
    await asyncio.sleep(random.uniform(1, 10))

    # Change the status of the order to 'executed'
    for order in orders_db:
        if order.id == order_id:
            # Change the status of the order to 'executed'
            order.status = "EXECUTED"
            await broadcast_over_websocket(f"Order {order.id} has been executed")
            break


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)


# USD USD currency pair can not exist
