from pydantic import ValidationError
import uvicorn
from fastapi import FastAPI, HTTPException, Response, WebSocket, status
from fastapi.responses import JSONResponse
from order import Order

app = FastAPI()

active_connections = []
orders_db = []

@app.post("/orders", response_model=dict)
async def create_order(orderBody: dict):    
    exception = None 
    
    try:
        new_order = Order(stocks = orderBody["stocks"], 
                          quantity = orderBody["quantity"], 
                          status = "PENDING")
    except ValidationError as e:
        error_message = f'{e.raw_errors[0]._loc} value is invalid'
        exception = {"message": error_message,"code": 10}
    except KeyError as e:
        error_message = f'{e.args[0]} value is missing'
        exception = {"message": error_message, "code": 20}
        
    if exception:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, 
                            content={"message": error_message,
                                    "code": 10})

    orders_db.append(new_order)
    
    response_body = {"id": new_order.id, 
                     "status": new_order.status}
    
    await broadcast_over_websocket(
        f"Order {new_order.id} for {new_order.stocks} received.\n\
        Current status - {new_order.status}")

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=response_body)


@app.get("/orders/{order_id}")
async def read_item(order_id: str) -> dict:
    order = retrieve_order(order_id=order_id, order_list=orders_db)

    if order:        
        response_body = {
            "stocks": order.stocks,
            "quantity": order.quantity
        }
        response_code = status.HTTP_200_OK
    else:
        response_body = {
            "message": f"order {order_id} not found",
            "code": 40
        }
        response_code = status.HTTP_404_NOT_FOUND
    
    return JSONResponse(status_code=response_code, content=response_body)


@app.get("/orders")
async def read_item() -> list:
    return orders_db


@app.delete("/orders/{order_id}")
async def delete_order(order_id: str) -> dict:
    order = retrieve_order(order_id=order_id, order_list=orders_db)
    
    if order:        
        response_body = {"message": "Order cancelled"}
        response_code = status.HTTP_204_OK
    else:
        response_body = {
            "message": f"Order {order_id} not found",
            "code": 40
        }
        response_code = status.HTTP_404_NOT_FOUND

    return JSONResponse(status_code=response_code, content=response_body)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    active_connections.append(websocket)
    await websocket.accept()
    while True:
        #think about keep-alive mechanism
        await websocket.receive_text()

async def broadcast_over_websocket(message: str):
    if len(active_connections) > 0:
        for connection in active_connections:
            await connection.send_text(message)
    else:
        print('No websocket connected; skipping update')         


def retrieve_order(order_id: str, order_list: list, delete: bool = False) -> dict:    
    for id in range (len(order_list)):
        if order_list[id].id == order_id:
            if delete:
                order_list[id] = 2
            return order_list[id]


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
