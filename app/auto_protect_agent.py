import argparse
import sys
from pathlib import Path

from app.sensitive_protector import run_watch


def default_root_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Background auto-protect agent. Watches outgoing folder and writes protected files."
    )
    parser.add_argument(
        "--root-dir",
        type=Path,
        default=None,
        help="Base directory where outgoing/ready-to-send/keys folders are created.",
    )
    parser.add_argument(
        "--interval-seconds",
        type=float,
        default=2.0,
        help="Polling interval in seconds.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root_dir = args.root_dir.resolve() if args.root_dir else default_root_dir()

    outgoing_dir = root_dir / "outgoing"
    ready_to_send_dir = root_dir / "ready-to-send"
    keys_dir = root_dir / "keys"
    key_file = keys_dir / "receiver.key"

    outgoing_dir.mkdir(parents=True, exist_ok=True)
    ready_to_send_dir.mkdir(parents=True, exist_ok=True)
    keys_dir.mkdir(parents=True, exist_ok=True)

    print(f"Root: {root_dir}")
    print(f"Drop files into: {outgoing_dir}")
    print(f"Protected files appear in: {ready_to_send_dir}")
    print(f"Key file: {key_file}")
    return run_watch(outgoing_dir, ready_to_send_dir, key_file, args.interval_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
