CREATE TABLE IF NOT EXISTS containers (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  status TEXT,
  created_at TIMESTAMPTZ NOT NULL,
  cpu_usage BIGINT,
  memory_usage_bytes BIGINT,
  UNIQUE (name, created_at)
);

CREATE TABLE IF NOT EXISTS container_ips (
  container_id BIGINT REFERENCES containers(id) ON DELETE CASCADE,
  ip_address TEXT NOT NULL,
  family TEXT CHECK (family IN ('inet','inet6')),
  scope TEXT,
  PRIMARY KEY (container_id, ip_address)
);