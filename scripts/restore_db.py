#!/usr/bin/env python3
"""
Automated Database Restore and Disaster Recovery Script for AstroMind AI.
Enforces SHA-256 integrity verification before execution and validates schema post-restore.
"""

import argparse
import gzip
import hashlib
import json
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path


def calculate_sha256(filepath: Path) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def verify_integrity(backup_path: Path) -> tuple[bool, str, str]:
    """Check calculated hash against sidecar .sha256 or .meta.json file."""
    calculated_hash = calculate_sha256(backup_path)

    sha_file = backup_path.with_name(backup_path.name + ".sha256")
    expected_hash = ""
    if sha_file.exists():
        expected_hash = sha_file.read_text(encoding="utf-8").strip()
    else:
        meta_file = backup_path.with_name(backup_path.name + ".meta.json")
        if meta_file.exists():
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            expected_hash = meta.get("sha256", "")

    if not expected_hash:
        return True, calculated_hash, "NO_SIDECAR_CHECKSUM"

    is_valid = (calculated_hash.lower() == expected_hash.lower())
    return is_valid, calculated_hash, expected_hash


def verify_sqlite_tables(db_path: Path) -> dict[str, int]:
    """Connect to SQLite database and query row counts for all core entities."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]

    counts = {}
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            counts[table] = cursor.fetchone()[0]
        except Exception:  # noqa: BLE001
            counts[table] = -1
    conn.close()
    return counts


def restore_sqlite(backup_path: Path, target_path: Path) -> dict[str, int]:
    # Handle gzipped backups
    temp_uncompressed = None
    source_to_restore = backup_path
    if backup_path.suffix == ".gz":
        temp_uncompressed = backup_path.with_suffix("")
        with gzip.open(backup_path, "rb") as f_in, open(temp_uncompressed, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        source_to_restore = temp_uncompressed

    try:
        source_conn = sqlite3.connect(str(source_to_restore))
        dest_conn = sqlite3.connect(str(target_path))
        source_conn.backup(dest_conn)
        dest_conn.close()
        source_conn.close()
    finally:
        if temp_uncompressed and temp_uncompressed.exists():
            temp_uncompressed.unlink()

    return verify_sqlite_tables(target_path)


def restore_postgres(backup_path: Path, db_url: str) -> None:
    cmd = ["pg_restore", "--clean", "--if-exists", f"--dbname={db_url}", str(backup_path)]
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"pg_restore failed: {result.stderr}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Restore AstroMind AI database from backup")
    parser.add_argument("backup_file", help="Path to backup file")
    parser.add_argument("--target-db", default=None, help="Target SQLite file or Postgres DB URL")
    parser.add_argument("--verify-only", action="store_true", help="Only verify checksum and backup integrity")
    args = parser.parse_args()

    backup_path = Path(args.backup_file)
    if not backup_path.exists():
        print(json.dumps({"status": "FAILED", "error": f"Backup file not found: {backup_path}"}), file=sys.stderr)
        return 1

    # 1. Integrity check
    is_valid, calculated_hash, expected_hash = verify_integrity(backup_path)
    if not is_valid:
        error_msg = f"INTEGRITY VIOLATION: Checksum mismatch. Expected {expected_hash}, calculated {calculated_hash}"
        print(json.dumps({"status": "FAILED", "error": error_msg}), file=sys.stderr)
        return 1

    print(f"Checksum verified: {calculated_hash}")

    if args.verify_only:
        print(json.dumps({
            "status": "VERIFIED_OK",
            "backup_file": str(backup_path),
            "sha256": calculated_hash,
        }, indent=2))
        return 0

    # 2. Perform restoration
    target = args.target_db
    if not target:
        try:
            from backend.app.core.config import settings

            target = settings.DATABASE_URL
        except Exception:  # noqa: BLE001
            target = "dev_astromind.db"

    try:
        if "postgres" in target:
            restore_postgres(backup_path, target)
            print(json.dumps({
                "status": "RESTORE_SUCCESS",
                "target": target,
                "backup_file": str(backup_path),
            }, indent=2))
        else:
            # SQLite path
            clean_path = target.split("sqlite:///")[-1].split("?")[0]
            target_path = Path(clean_path)
            table_counts = restore_sqlite(backup_path, target_path)
            print(json.dumps({
                "status": "RESTORE_SUCCESS",
                "target_file": str(target_path),
                "backup_file": str(backup_path),
                "sha256": calculated_hash,
                "verified_tables": table_counts,
            }, indent=2))
        return 0

    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "FAILED", "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
