from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from datetime import datetime

class IPAddress(BaseModel):
    ip_address: str
    family: Literal["inet", "inet6"]
    scope: Optional[str] = None

class ContainerRecord(BaseModel):
    name: str
    status: Optional[str] = None
    created_at: datetime
    cpu_usage: Optional[int] = None
    memory_usage_bytes: Optional[int] = None
    ips: List[IPAddress] = Field(default_factory=list)