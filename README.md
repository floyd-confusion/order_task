In order to launch the application, you may use docker. First, you need to build the container:

```
docker build --tag sdet_task:latest .
```

Then, in order to launch the container, please use command:

```
docker run --publish 8000:8080 sdet_task:latest
```

In case your local port 8000 is occupied, you are welcome to use the alternative one. 

Same method applies to tests. IN order to assemble and launch testing container for the app the following commands shoyld be ran in order:

```
docker build --file Dockerfile.test --tag sdet_task_test:latest .
```

```
docker run sdet_task_test
```

This testrun implies generating an HTML file, which is generated within the contained. Accessing it may prove difficult, hence the tests can be ran outside of container with the following command 

```python -m pytest --html=report.html test/```

# How it works

The API has 4 endpoints:

1. POST - /orders
This endpoint creates the order. The payload syntax is as follows:
```
{
    "stocks": "EURUSD",
    "quantity": 0.1
}
```
The eligible currency pair is any that consits of two of the following currencies: USD,EUR,JPY,GBP,AUD,CAD,CHF,CNY,SEK,NZD.

It returns an ID with a status, which is initially PENDING
```
{
    "id": "880123f1",
    "status": "PENDING"
}
```

2. GET /orders
Returns all created orders in an array. Contains all info related to the order: quantity, status, ID and stock

3. GET /orders/{orderId}
Returns a particular created order. Contains all info related to the order: quantity, status, ID and stock

4. DELETE /orders/{orderId}
Changes order's status to CANCELLED

5. WebSocket /ws
Establishes a connection which is used to broadcast updates regarding new order, executed orders or deeted orders

Upon creating an order, it is deposited into the list. In a random time interval (1:10 seconds) the order changes status to EXECUTED. 

The broadcast capabilities, update clients over websocket connections in these cases:
1. Order created
2. Order cancelled
3. Order executed 