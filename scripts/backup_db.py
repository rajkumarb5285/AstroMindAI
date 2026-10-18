#!/usr/bin/env python3
"""
Automated Database Backup Script for AstroMind AI
Supports both SQLite (local/dev) and PostgreSQL (production).
Generates SHA-256 checksums and metadata for disaster recovery verification.
"""

import argparse
import gzip
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path


def calculate_sha256(filepath: Path) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def backup_sqlite(db_path: Path, output_dir: Path, compress: bool = False) -> tuple[Path, str]:
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    backup_filename = f"astromind_sqlite_{timestamp}.db"
    dest_path = output_dir / backup_filename

    # Perform thread-safe online backup
    source_conn = sqlite3.connect(str(db_path))
    dest_conn = sqlite3.connect(str(dest_path))
    try:
        source_conn.backup(dest_conn)
    finally:
        dest_conn.close()
        source_conn.close()

    if compress:
        compressed_path = dest_path.with_suffix(".db.gz")
        with open(dest_path, "rb") as f_in, gzip.open(compressed_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        os.remove(dest_path)
        dest_path = compressed_path

    checksum = calculate_sha256(dest_path)
    return dest_path, checksum


def backup_postgres(db_url: str, output_dir: Path) -> tuple[Path, str]:
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    dest_path = output_dir / f"astromind_pg_{timestamp}.dump"

    # Use pg_dump with custom directory format
    cmd = ["pg_dump", "--format=c", f"--file={dest_path}", db_url]
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"pg_dump failed: {result.stderr}")

    checksum = calculate_sha256(dest_path)
    return dest_path, checksum


def prune_old_backups(output_dir: Path, keep: int = 7) -> list[Path]:
    backup_files = sorted(
        [f for f in output_dir.glob("astromind_*") if f.suffix in (".db", ".gz", ".dump")],
        key=os.path.getmtime,
        reverse=True,
    )
    pruned = []
    if len(backup_files) > keep:
        for old_file in backup_files[keep:]:
            try:
                old_file.unlink()
                sha_file = old_file.with_name(old_file.name + ".sha256")
                if sha_file.exists():
                    sha_file.unlink()
                meta_file = old_file.with_name(old_file.name + ".meta.json")
                if meta_file.exists():
                    meta_file.unlink()
                pruned.append(old_file)
            except Exception as e:  # noqa: BLE001
                print(f"Warning: Failed to prune {old_file}: {e}", file=sys.stderr)
    return pruned


def main() -> int:
    parser = argparse.ArgumentParser(description="Backup AstroMind AI database")
    parser.add_argument("--output-dir", default="backend/backups", help="Destination directory for backups")
    parser.add_argument("--database-url", default=None, help="Database URL (default: read from backend settings)")
    parser.add_argument("--compress", action="store_true", help="Gzip compress backup")
    parser.add_argument("--keep", type=int, default=7, help="Number of backups to retain")
    args = parser.parse_args()

    # Determine database URL
    db_url = args.database_url
    if not db_url:
        try:
            from backend.app.core.config import settings

            db_url = settings.DATABASE_URL
        except Exception:  # noqa: BLE001
            db_url = os.environ.get("DATABASE_URL", "sqlite:///dev_astromind.db")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    start_time = time.time()
    try:
        if "sqlite" in db_url:
            # Extract file path from sqlite:/// or sqlite:////
            clean_path = db_url.split("sqlite:///")[-1].split("?")[0]
            db_path = Path(clean_path)
            if not db_path.exists():
                # Check root directory fallback
                if Path("dev_astromind.db").exists():
                    db_path = Path("dev_astromind.db")
                else:
                    raise FileNotFoundError(f"SQLite database file not found at: {db_path}")

            backup_path, checksum = backup_sqlite(db_path, output_dir, compress=args.compress)
            db_type = "sqlite"
        elif "postgres" in db_url:
            backup_path, checksum = backup_postgres(db_url, output_dir)
            db_type = "postgresql"
        else:
            raise ValueError(f"Unsupported database scheme in URL: {db_url}")

        duration = time.time() - start_time

        # Write checksum file
        sha_file = backup_path.with_name(backup_path.name + ".sha256")
        sha_file.write_text(checksum, encoding="utf-8")

        # Write metadata file
        meta = {
            "backup_file": backup_path.name,
            "database_type": db_type,
            "timestamp": datetime.now(UTC).isoformat(),
            "sha256": checksum,
            "size_bytes": backup_path.stat().st_size,
            "duration_seconds": round(duration, 3),
        }
        meta_file = backup_path.with_name(backup_path.name + ".meta.json")
        meta_file.write_text(json.dumps(meta, indent=2), encoding="utf-8")

        # Prune old backups
        pruned = prune_old_backups(output_dir, keep=args.keep)

        print(json.dumps({
            "status": "SUCCESS",
            "backup_file": str(backup_path),
            "sha256": checksum,
            "size_bytes": meta["size_bytes"],
            "duration_seconds": meta["duration_seconds"],
            "pruned_count": len(pruned),
        }, indent=2))
        return 0

    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "FAILED", "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
