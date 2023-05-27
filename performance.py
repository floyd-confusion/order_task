import aiohttp
import asyncio

async def send_request(session, url):
    async with session.get(url) as resp:
        print(f"Response status: {resp.status}")

async def main():
    url = "http://localhost:8000/one"  # replace with your URL

    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(10):
            task = send_request(session, url)
            tasks.append(task)

        await asyncio.gather(*tasks)

asyncio.run(main())