import asyncpg #type: ignore
import asyncio
from typing import List, Tuple
from models import ContainerRecord

class PgWriter:
    def __init__(self, dsn: str):
        self._dsn = dsn
        self._pool: asyncpg.Pool | None = None

    async def start(self, timeout: float = 30.0, max_attempts: int = 6):
        """
        Try to create the asyncpg pool with exponential backoff.
        Raises the last exception if unable to connect within timeout/attempts.
        """
        attempt = 0
        start_time = asyncio.get_event_loop().time()
        while True:
            try:
                self._pool = await asyncpg.create_pool(self._dsn, min_size=1, max_size=5)
                # ensure schema
                async with self._pool.acquire() as con:
                    await con.execute(open("/app/schema.sql", "r", encoding="utf-8").read())
                return
            except (OSError, asyncpg.PostgresError, ConnectionError) as exc:
                attempt += 1
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > timeout or attempt >= max_attempts:
                    raise RuntimeError(f"unable to connect to Postgres after {attempt} attempts") from exc
                backoff = min(2 ** attempt, 10)
                await asyncio.sleep(backoff)

    async def stop(self):
        if self._pool:
            await self._pool.close()

    async def upsert_batch(self, batch: List[ContainerRecord]):
        if not batch:
            return
        container_rows = [
            (r.name, r.status, r.created_at, r.cpu_usage, r.memory_usage_bytes)
            for r in batch
        ]
        if self._pool is None:
            raise RuntimeError("PgWriter has not been started; call start() before upsert_batch()")
        async with self._pool.acquire() as con:
            # run temp-table CREATE, COPY and upsert in a single transaction
            async with con.transaction():
                await con.execute("""
                    CREATE TEMP TABLE tmp_containers (
                        name TEXT,
                        status TEXT,
                        created_at TIMESTAMPTZ,
                        cpu_usage BIGINT,
                        memory_usage_bytes BIGINT
                    ) ON COMMIT DROP;
                """)
                await con.copy_records_to_table(
                    "tmp_containers",
                    records=container_rows,
                    columns=["name", "status", "created_at", "cpu_usage", "memory_usage_bytes"],
                )
                await con.execute("""
                    INSERT INTO containers (name, status, created_at, cpu_usage, memory_usage_bytes)
                    SELECT name, status, created_at, cpu_usage, memory_usage_bytes FROM tmp_containers
                    ON CONFLICT (name, created_at) DO UPDATE
                    SET status = EXCLUDED.status,
                        cpu_usage = EXCLUDED.cpu_usage,
                        memory_usage_bytes = EXCLUDED.memory_usage_bytes;
                """)
                rows = await con.fetch('''
                    SELECT id, name, created_at FROM containers
                    WHERE (name, created_at) IN (
                        SELECT name, created_at FROM tmp_containers
                    );
                ''')
                id_map = {(r["name"], r["created_at"]): r["id"] for r in rows}

                ip_rows: List[Tuple[int, str, str, str | None]] = []
                for rec in batch:
                    cid = id_map.get((rec.name, rec.created_at))
                    if not cid:
                        continue
                    for ip in rec.ips:
                        ip_rows.append((cid, ip.ip_address, ip.family, ip.scope))

                if ip_rows:
                    await con.execute('''
                        CREATE TEMP TABLE tmp_ips (
                          container_id BIGINT, ip_address TEXT, family TEXT, scope TEXT
                        ) ON COMMIT DROP;
                    ''')
                    await con.copy_records_to_table("tmp_ips",
                        records=ip_rows,
                        columns=["container_id","ip_address","family","scope"]
                    )
                    await con.execute('''
                        INSERT INTO container_ips (container_id, ip_address, family, scope)
                        SELECT container_id, ip_address, family, scope FROM tmp_ips
                        ON CONFLICT (container_id, ip_address) DO UPDATE
                          SET family = EXCLUDED.family,
                              scope = EXCLUDED.scope;
                    ''')