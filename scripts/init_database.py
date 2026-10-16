#!/usr/bin/env python
"""Create the small enterprise database used by tool-calling labs.

The data is intentionally fictional. The database is real SQLite so students can
inspect queries and tool results without mocking an enterprise system in Python.
"""

from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "enterprise.db"

SCHEMA = """
DROP TABLE IF EXISTS incidents;
DROP TABLE IF EXISTS service_status;
DROP TABLE IF EXISTS contracts;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    tier TEXT NOT NULL,
    region TEXT NOT NULL
);

CREATE TABLE services (
    service_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL
);

CREATE TABLE contracts (
    contract_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    service_id TEXT NOT NULL,
    response_minutes_p1 INTEGER NOT NULL,
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY(service_id) REFERENCES services(service_id)
);

CREATE TABLE service_status (
    service_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    message TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(service_id) REFERENCES services(service_id)
);

CREATE TABLE incidents (
    incident_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    service_id TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL,
    title TEXT NOT NULL,
    opened_at TEXT NOT NULL,
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY(service_id) REFERENCES services(service_id)
);
"""


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA)
        conn.executemany(
            "INSERT INTO customers VALUES (?, ?, ?, ?)",
            [
                ("C001", "Asteria Retail", "premium", "Spain"),
                ("C002", "BlueWave Logistics", "standard", "France"),
                ("C003", "NovaHealth Services", "premium", "Portugal"),
            ],
        )
        conn.executemany(
            "INSERT INTO services VALUES (?, ?, ?)",
            [
                ("S001", "Managed VPN", "Corporate remote-access VPN service"),
                ("S002", "Managed Network", "Managed WAN and campus connectivity"),
                ("S003", "Identity Platform", "Managed identity and MFA service"),
            ],
        )
        conn.executemany(
            "INSERT INTO contracts VALUES (?, ?, ?, ?)",
            [
                ("CTR001", "C001", "S001", 30),
                ("CTR002", "C001", "S002", 30),
                ("CTR003", "C002", "S001", 60),
                ("CTR004", "C003", "S003", 30),
            ],
        )
        conn.executemany(
            "INSERT INTO service_status VALUES (?, ?, ?, ?)",
            [
                ("S001", "degraded", "Intermittent VPN authentication failures", "2026-10-16T06:30:00Z"),
                ("S002", "operational", "No known service impact", "2026-10-16T06:30:00Z"),
                ("S003", "operational", "No known service impact", "2026-10-16T06:30:00Z"),
            ],
        )
        conn.executemany(
            "INSERT INTO incidents VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                ("INC-1043", "C001", "S001", "P1", "open", "VPN authentication failures affecting multiple users", "2026-10-16T06:10:00Z"),
                ("INC-1039", "C001", "S001", "P2", "monitoring", "Intermittent VPN latency", "2026-10-15T16:40:00Z"),
                ("INC-1011", "C002", "S002", "P3", "open", "Packet loss in branch office", "2026-10-15T09:20:00Z"),
            ],
        )
        conn.commit()

    print(f"Created sample enterprise database: {DB_PATH}")


if __name__ == "__main__":
    main()
