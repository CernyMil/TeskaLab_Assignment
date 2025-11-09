import polars as pl
from typing import Iterator, Optional, List
from datetime import timezone, datetime
from models import ContainerRecord, IPAddress

def _extract_ips_from_state(state: Optional[dict]) -> List[IPAddress]:
    if not state or not isinstance(state, dict):
        return []
    net = state.get("network") or {}
    out: List[IPAddress] = []
    if isinstance(net, dict):
        for _, meta in net.items():
            addrs = (meta or {}).get("addresses") or []
            for a in addrs:
                fam = a.get("family")
                addr = a.get("address")
                scope = a.get("scope")
                if not addr or fam not in ("inet","inet6"):
                    continue
                out.append(IPAddress(ip_address=addr, family=fam, scope=scope))
    return out

def read_json_records(path: str) -> pl.DataFrame:
    return pl.read_json(path)

def iter_validated_records(df: pl.DataFrame) -> Iterator[ContainerRecord]:
    for row in df.iter_rows(named=True):
        name = row.get("name")
        status = row.get("status")
        created_at = row.get("created_at")
        state = row.get("state") or None

        if created_at is None:
            continue
        if isinstance(created_at, str):
            try:
                if created_at.endswith("Z"):
                    created_at = datetime.fromisoformat(created_at[:-1]).replace(tzinfo=timezone.utc)
                else:
                    created_at = datetime.fromisoformat(created_at)
            except Exception:

                continue
        if not isinstance(created_at, datetime):
            continue

        cpu_usage = None
        mem_usage = None
        if isinstance(state, dict):
            cpu_usage = (state.get("cpu") or {}).get("usage")
            mem_usage = (state.get("memory") or {}).get("usage")

        ips = _extract_ips_from_state(state)

        if not isinstance(name, str):
            continue

        rec = ContainerRecord(
            name=name,
            status=status,
            created_at=created_at,
            cpu_usage=cpu_usage,
            memory_usage_bytes=mem_usage,
            ips=ips,
        )
        if rec.created_at.tzinfo is not None:
            rec.created_at = rec.created_at.astimezone(timezone.utc)
        else:
            rec.created_at = rec.created_at.replace(tzinfo=timezone.utc)

        yield rec

def chunked(iterator, size: int):
    batch = []
    for item in iterator:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch