import random
from statistics import mean, stdev
from datetime import datetime
import aiohttp
import asyncio
import re
from src.order import available_currencies


async def send_request(session, url, data, order_times):
    async with session.post(url, json=data) as resp:
        response_json = await resp.json()
        order_id = response_json.get("order_id")
        post_time = datetime.now()
        order_times[order_id] = {"post_time": post_time}

async def listen_for_executions(ws, order_times):
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            match = re.search(r"Order (\d+) has been executed", msg.data)
            if match:
                order_id = int(match.group(1))
                if order_id in order_times:
                    execute_time = datetime.now()
                    order_times[order_id]["execute_time"] = execute_time

async def main():
    host = "http://localhost:8080"
    post_url = f"{host}/"
    ws_url = f"{host}/ws"
    order_times = {}

    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(ws_url) as ws:
            listen_task = asyncio.create_task(listen_for_executions(ws, order_times))

            post_tasks = []
            for _ in range(10):
                stock = str(
                    random.choice(available_currencies) + random.choice(available_currencies)
                )
                body = {"stocks": stock, "quantity": round(random.uniform(1, 100), 1)}
                task = send_request(session, post_url, body, order_times)
                post_tasks.append(task)

            await asyncio.gather(*post_tasks)
            await asyncio.sleep(10)
            listen_task.cancel()

        execution_times = [
            (times["execute_time"] - times["post_time"]).total_seconds()
            for times in order_times.values()
            if "execute_time" in times
        ]

        avg_execution_time = mean(execution_times)
        print(f"Average execution time: {avg_execution_time} seconds")

        std_dev_execution_time = stdev(execution_times)
        print(f"Standard deviation of execution time: {std_dev_execution_time} seconds")

asyncio.run(main())
