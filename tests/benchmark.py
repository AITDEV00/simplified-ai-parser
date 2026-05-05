"""
Benchmark: Concurrent document parsing performance test.

Sends the 5 test files from tests/files/ to the /v1/parse-file endpoint
in 10 rounds. Each round multiplies the files by the round number:
  Round 1  →  5 files
  Round 2  → 10 files
  ...
  Round 10 → 50 files

All files in a round are sent simultaneously using asyncio + aiohttp.
"""

import asyncio
import aiohttp
import os
import time
import statistics
from pathlib import Path

# ── Config ──────────────────────────────────────────────────
SERVER_URL = "http://localhost:7656/v1/parse-file"
TEST_FILES_DIR = Path(__file__).parent / "files" / "email"
ROUNDS = 10
# ────────────────────────────────────────────────────────────


def discover_files() -> list[Path]:
    """Find all files in the test directory."""
    files = sorted(TEST_FILES_DIR.iterdir())
    files = [f for f in files if f.is_file()]
    if not files:
        raise FileNotFoundError(f"No files found in {TEST_FILES_DIR}")
    return files


async def send_file(session: aiohttp.ClientSession, file_path: Path) -> dict:
    """Upload a single file and return timing info."""
    start = time.perf_counter()
    
    data = aiohttp.FormData()
    data.add_field(
        "file",
        open(file_path, "rb"),
        filename=file_path.name,
        content_type="application/octet-stream",
    )
    
    try:
        async with session.post(SERVER_URL, data=data) as resp:
            elapsed_ms = (time.perf_counter() - start) * 1000
            status = resp.status
            body = await resp.json() if status == 200 else await resp.text()
            return {
                "file": file_path.name,
                "status": status,
                "latency_ms": round(elapsed_ms, 1),
                "success": status == 200,
                "processing_time": body.get("processing_time", None) if isinstance(body, dict) else None,
                "error": body if status != 200 else None,
            }
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "file": file_path.name,
            "status": 0,
            "latency_ms": round(elapsed_ms, 1),
            "success": False,
            "processing_time": None,
            "error": str(e),
        }


async def run_round(round_num: int, base_files: list[Path]) -> dict:
    """Run a single benchmark round with round_num × base_files."""
    # Build the file list for this round: duplicate base files round_num times
    files_to_send = base_files * round_num
    total = len(files_to_send)

    print(f"\n{'='*70}")
    print(f"  Round {round_num:>2} — Sending {total} files concurrently")
    print(f"{'='*70}")

    connector = aiohttp.TCPConnector(limit=0)  # no connection limit
    timeout = aiohttp.ClientTimeout(total=300)  # 5 min timeout per request
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        round_start = time.perf_counter()
        results = await asyncio.gather(*[send_file(session, f) for f in files_to_send])
        round_elapsed_ms = (time.perf_counter() - round_start) * 1000

    # Compute stats
    latencies = [r["latency_ms"] for r in results if r["success"]]
    successes = sum(1 for r in results if r["success"])
    failures = total - successes

    stats = {
        "round": round_num,
        "total_files": total,
        "successes": successes,
        "failures": failures,
        "round_wall_time_ms": round(round_elapsed_ms, 1),
    }

    if latencies:
        stats["min_ms"] = round(min(latencies), 1)
        stats["max_ms"] = round(max(latencies), 1)
        stats["avg_ms"] = round(statistics.mean(latencies), 1)
        stats["median_ms"] = round(statistics.median(latencies), 1)
        stats["p95_ms"] = round(sorted(latencies)[int(len(latencies) * 0.95)], 1)
    else:
        stats["min_ms"] = stats["max_ms"] = stats["avg_ms"] = stats["median_ms"] = stats["p95_ms"] = 0

    # Print per-file results
    for r in results:
        marker = "✅" if r["success"] else "❌"
        srv_time = f"  (server: {r['processing_time']:.3f}s)" if r["processing_time"] else ""
        err = f"  ERR: {r['error']}" if r["error"] else ""
        print(f"  {marker}  {r['latency_ms']:>8.1f} ms  {r['file'][:60]}{srv_time}{err}")

    print(f"\n  Summary: {successes}/{total} ok | "
          f"Wall: {stats['round_wall_time_ms']:.0f}ms | "
          f"Avg: {stats['avg_ms']:.0f}ms | "
          f"Min: {stats['min_ms']:.0f}ms | "
          f"Max: {stats['max_ms']:.0f}ms | "
          f"P95: {stats['p95_ms']:.0f}ms")

    return stats


async def main():
    base_files = discover_files()
    print(f"Discovered {len(base_files)} test files:")
    for f in base_files:
        print(f"  • {f.name}  ({f.stat().st_size / 1024:.0f} KB)")

    all_stats = []
    total_start = time.perf_counter()

    for round_num in range(1, ROUNDS + 1):
        stats = await run_round(round_num, base_files)
        all_stats.append(stats)

    total_elapsed = time.perf_counter() - total_start

    # ── Final summary table ──
    print(f"\n\n{'='*90}")
    print(f"  BENCHMARK COMPLETE — Total time: {total_elapsed:.1f}s")
    print(f"{'='*90}")
    print(f"{'Round':>6} {'Files':>6} {'OK':>5} {'Fail':>5} "
          f"{'Wall(ms)':>10} {'Avg(ms)':>9} {'Min(ms)':>9} "
          f"{'Max(ms)':>9} {'Med(ms)':>9} {'P95(ms)':>9}")
    print(f"{'-'*90}")
    for s in all_stats:
        print(f"{s['round']:>6} {s['total_files']:>6} {s['successes']:>5} {s['failures']:>5} "
              f"{s['round_wall_time_ms']:>10.0f} {s['avg_ms']:>9.0f} {s['min_ms']:>9.0f} "
              f"{s['max_ms']:>9.0f} {s['median_ms']:>9.0f} {s['p95_ms']:>9.0f}")
    print(f"{'='*90}")


if __name__ == "__main__":
    asyncio.run(main())
