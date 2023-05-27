from pydantic import ValidationError
import uvicorn
from fastapi import FastAPI, HTTPException, Response, WebSocket, status
from fastapi.responses import JSONResponse
from order import Order

app = FastAPI()

active_connections = []
orders = []

@app.post("/orders", response_model=dict)
async def create_order(orderBody: dict):    
    exception = None 
    
    try:
        new_order = Order(stocks = orderBody["stocks"], quantity = orderBody["quantity"])
    except ValidationError as e:
        error_message = f'{e.raw_errors[0]._loc} value is invalid'
        exception = {"message": error_message,"code": 10}
    except KeyError as e:
        error_message = f'{e.args[0]} value is missing'
        exception = {"message": error_message, "code": 20}
        
    if exception:
        return JSONResponse(status_code=400, 
                            content={"message": error_message,
                                    "code": 10})

    orders.append(new_order)
    
    response_body = {"id": new_order.id, 
                     "status": new_order.status.name}
    
    await broadcast_over_websocket(
        f"Order {new_order.id} for {new_order.stocks} received.\
        Current status - {new_order.status.name}")

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=response_body)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    active_connections.append(websocket)
    await websocket.accept()
    while True:
        #think about keep-alive mechanism
        await websocket.receive_text()

async def broadcast_over_websocket(message):
    try:
        for connection in active_connections:
            await connection.send_text(message)
    except:
        print('No websocket connected; skipping update')         

def process_order(orderBody):
    new_order = Order(stocks=orderBody.stocks, quantity=orderBody.quantity)
    return new_order

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
