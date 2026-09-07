"""JobForge: a tiny SQLite-backed job queue with retries and dead-letter jobs."""
from __future__ import annotations
import argparse
import sqlite3
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Job:
    id: int
    payload: str
    attempts: int
    status: str

class Queue:
    def __init__(self, db: str | Path = "jobforge.db"):
        self.db = sqlite3.connect(db)
        self.db.execute("CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY, payload TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL DEFAULT 'queued')")
        self.db.commit()
    def enqueue(self, payload: str) -> int:
        cur = self.db.execute("INSERT INTO jobs(payload) VALUES (?)", (payload,)); self.db.commit(); return int(cur.lastrowid)
    def claim(self) -> Job | None:
        self.db.execute("BEGIN IMMEDIATE")
        row = self.db.execute("SELECT id,payload,attempts,status FROM jobs WHERE status='queued' ORDER BY id LIMIT 1").fetchone()
        if not row: self.db.commit(); return None
        self.db.execute("UPDATE jobs SET status='running', attempts=attempts+1 WHERE id=?", (row[0],)); self.db.commit()
        return Job(row[0], row[1], row[2] + 1, "running")
    def complete(self, job_id: int) -> None:
        self.db.execute("UPDATE jobs SET status='done' WHERE id=? AND status='running'", (job_id,)); self.db.commit()
    def fail(self, job_id: int, max_attempts: int = 3) -> None:
        self.db.execute("UPDATE jobs SET status=CASE WHEN attempts>=? THEN 'dead' ELSE 'queued' END WHERE id=? AND status='running'", (max_attempts, job_id)); self.db.commit()
    def stats(self) -> dict[str, int]:
        return dict(self.db.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status").fetchall())

def main() -> int:
    p = argparse.ArgumentParser(description="SQLite-backed job queue")
    p.add_argument("db", nargs="?", default="jobforge.db")
    sub = p.add_subparsers(dest="command", required=True)
    e = sub.add_parser("enqueue"); e.add_argument("payload")
    sub.add_parser("claim"); sub.add_parser("stats")
    args = p.parse_args(); q = Queue(args.db)
    if args.command == "enqueue": print(q.enqueue(args.payload))
    elif args.command == "claim": print(q.claim() or "empty")
    else: print(q.stats())
    return 0

if __name__ == "__main__": raise SystemExit(main())
