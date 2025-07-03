import aiohttp
import asyncio
import random
import time

NUM_TASKS = 10
LOAD_BALANCER_URL = "http://localhost:8000"

async def send_task(session, task_id):
    payload = {
        "operation": "sum",
        "numbers": [random.randint(1, 100) for _ in range(random.randint(2, 6))]
    }
    print(f"[Client] Sending task {task_id}: {payload}")
    async with session.post(f"{LOAD_BALANCER_URL}/request", json=payload) as resp:
        result = await resp.json()
        return result.get("task_id")

async def get_result(session, task_id):
    while True:
        async with session.get(f"{LOAD_BALANCER_URL}/result/{task_id}") as resp:
            try:
                result = await resp.json()
            except aiohttp.ContentTypeError:
                text = await resp.text()
                print(f"[Client] Failed to parse JSON. Got HTML:\n{text}")
                return

            if result["status"] == "complete":
                print(f"[Client] Task {task_id} result: {result['result']}")
                break
            elif result["status"] == "pending":
                await asyncio.sleep(1)
            else:
                print(f"[Client] Task {task_id} status: {result['status']}")
                break

async def main():
    async with aiohttp.ClientSession() as session:
        task_ids = await asyncio.gather(*[send_task(session, i) for i in range(NUM_TASKS)])
        await asyncio.gather(*[get_result(session, task_id) for task_id in task_ids if task_id])

if __name__ == "__main__":
    asyncio.run(main())
