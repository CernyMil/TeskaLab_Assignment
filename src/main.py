import os, asyncio
from dotenv import load_dotenv

from parser import read_json_records, iter_validated_records, chunked
from writer import PgWriter

load_dotenv()

JSON_PATH   = str(os.getenv("JSON_PATH"))
DB_DSN      = os.getenv("DB_DSN")
BATCH_ROWS  = int(os.getenv("BATCH_ROWS") or "100")
MAX_QUEUE   = int(os.getenv("MAX_QUEUE") or "1")

async def producer(queue: asyncio.Queue):
    df = await asyncio.to_thread(read_json_records, JSON_PATH)
    for batch in chunked(iter_validated_records(df), BATCH_ROWS):
        await queue.put(batch)
    await queue.put(None)

async def consumer(queue: asyncio.Queue, writer: PgWriter):
    while True:
        batch = await queue.get()
        if batch is None:
            await queue.put(None)
            break
        await writer.upsert_batch(batch)
        queue.task_done()

async def main():
    q = asyncio.Queue(MAX_QUEUE)
    writer = PgWriter(DB_DSN)
    await writer.start()
    try:
        prod = asyncio.create_task(producer(q))
        cons = asyncio.create_task(consumer(q, writer))
        await asyncio.gather(prod, cons)
    finally:
        await writer.stop()

if __name__ == "__main__":
    asyncio.run(main())