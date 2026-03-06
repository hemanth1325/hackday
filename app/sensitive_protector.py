import argparse
import csv
import json
import mimetypes
import os
import re
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib import request
from urllib.error import HTTPError, URLError

from cryptography.fernet import Fernet, InvalidToken

ENCRYPTED_TOKEN_PATTERN = re.compile(r"ENC\[([A-Za-z0-9_\-=]+)\]")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"(?<!\w)(?:\+?\d{1,3}[ .-]?)?(?:\(?\d{3}\)?[ .-]?)\d{3}[ .-]?\d{4}(?!\w)")
CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d[ -]?){13,19}\b")
SENSITIVE_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b(password|passwd|pwd|secret|token|api[_-]?key)\b(\s*[:=]\s*)([^\s,;]+)"
)
SENSITIVE_KEYS = {"password", "passwd", "pwd", "secret", "token", "api_key", "apikey"}


@dataclass
class ProtectionSummary:
    encrypted_counts: dict[str, int] = field(default_factory=dict)
    encrypted_total: int = 0

    def bump(self, category: str) -> None:
        self.encrypted_counts[category] = self.encrypted_counts.get(category, 0) + 1
        self.encrypted_total += 1


@dataclass
class UploadConfig:
    upload_url: str
    upload_field: str = "file"
    token: str | None = None
    auth_header: str = "Authorization"
    upload_all_files: bool = True


def is_sensitive_key(key: str | None) -> bool:
    if not key:
        return False
    normalized = key.strip().lower().replace("-", "_")
    return normalized in SENSITIVE_KEYS


def is_encrypted_token(value: str) -> bool:
    return bool(ENCRYPTED_TOKEN_PATTERN.fullmatch(value.strip()))


def create_or_load_fernet(key_file: Path) -> Fernet:
    if key_file.exists():
        key = key_file.read_bytes().strip()
    else:
        key_file.parent.mkdir(parents=True, exist_ok=True)
        key = Fernet.generate_key()
        key_file.write_bytes(key + b"\n")
    return Fernet(key)


def load_fernet_from_key_file(key_file: Path) -> Fernet:
    if not key_file.exists():
        raise FileNotFoundError(f"Key file not found: {key_file}")
    return Fernet(key_file.read_bytes().strip())


def encrypt_text_value(value: str, fernet: Fernet) -> str:
    token = fernet.encrypt(value.encode("utf-8")).decode("utf-8")
    return f"ENC[{token}]"


def decrypt_token_value(value: str, fernet: Fernet) -> str:
    match = ENCRYPTED_TOKEN_PATTERN.fullmatch(value.strip())
    if not match:
        return value
    token = match.group(1).encode("utf-8")
    return fernet.decrypt(token).decode("utf-8")


def replace_pattern_with_encryption(
    text: str,
    pattern: re.Pattern[str],
    category: str,
    fernet: Fernet,
    summary: ProtectionSummary,
) -> str:
    def _replacer(match: re.Match[str]) -> str:
        matched_value = match.group(0)
        if is_encrypted_token(matched_value):
            return matched_value
        summary.bump(category)
        return encrypt_text_value(matched_value, fernet)

    return pattern.sub(_replacer, text)


def protect_string(value: str, fernet: Fernet, summary: ProtectionSummary, key_hint: str | None = None) -> str:
    if is_encrypted_token(value):
        return value

    if is_sensitive_key(key_hint):
        summary.bump("sensitive_key")
        return encrypt_text_value(value, fernet)

    def _assignment_replacer(match: re.Match[str]) -> str:
        key_part = match.group(1)
        separator = match.group(2)
        secret_value = match.group(3)
        if is_encrypted_token(secret_value):
            return match.group(0)
        summary.bump("sensitive_assignment")
        return f"{key_part}{separator}{encrypt_text_value(secret_value, fernet)}"

    protected = SENSITIVE_ASSIGNMENT_PATTERN.sub(_assignment_replacer, value)
    protected = replace_pattern_with_encryption(protected, EMAIL_PATTERN, "email", fernet, summary)
    protected = replace_pattern_with_encryption(protected, PHONE_PATTERN, "phone", fernet, summary)
    protected = replace_pattern_with_encryption(protected, CREDIT_CARD_PATTERN, "credit_card", fernet, summary)
    return protected


def decrypt_string(value: str, fernet: Fernet) -> str:
    def _replacer(match: re.Match[str]) -> str:
        token = match.group(1).encode("utf-8")
        try:
            return fernet.decrypt(token).decode("utf-8")
        except InvalidToken:
            return match.group(0)

    return ENCRYPTED_TOKEN_PATTERN.sub(_replacer, value)


def protect_json_value(value: Any, fernet: Fernet, summary: ProtectionSummary, key_hint: str | None = None) -> Any:
    if isinstance(value, dict):
        return {k: protect_json_value(v, fernet, summary, key_hint=k) for k, v in value.items()}
    if isinstance(value, list):
        return [protect_json_value(v, fernet, summary, key_hint=key_hint) for v in value]
    if isinstance(value, str):
        return protect_string(value, fernet, summary, key_hint=key_hint)
    if key_hint and is_sensitive_key(key_hint):
        summary.bump("sensitive_key")
        return encrypt_text_value(str(value), fernet)
    return value


def decrypt_json_value(value: Any, fernet: Fernet) -> Any:
    if isinstance(value, dict):
        return {k: decrypt_json_value(v, fernet) for k, v in value.items()}
    if isinstance(value, list):
        return [decrypt_json_value(v, fernet) for v in value]
    if isinstance(value, str):
        return decrypt_string(value, fernet)
    return value


def protect_csv(
    input_path: Path,
    output_path: Path,
    fernet: Fernet,
    summary: ProtectionSummary,
    write_if_unchanged: bool = True,
) -> None:
    with input_path.open("r", newline="", encoding="utf-8") as in_file:
        reader = csv.DictReader(in_file)
        fieldnames = reader.fieldnames or []
        rows = []
        for row in reader:
            protected_row: dict[str, str] = {}
            for key, raw_value in row.items():
                value = raw_value if raw_value is not None else ""
                protected_row[key] = protect_string(value, fernet, summary, key_hint=key)
            rows.append(protected_row)

    same_path = input_path.resolve() == output_path.resolve()
    should_write = (not same_path) or write_if_unchanged or (summary.encrypted_total > 0)
    if should_write:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", newline="", encoding="utf-8") as out_file:
            writer = csv.DictWriter(out_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


def decrypt_csv(input_path: Path, output_path: Path, fernet: Fernet) -> None:
    with input_path.open("r", newline="", encoding="utf-8") as in_file:
        reader = csv.DictReader(in_file)
        fieldnames = reader.fieldnames or []
        rows = []
        for row in reader:
            decrypted_row: dict[str, str] = {}
            for key, raw_value in row.items():
                value = raw_value if raw_value is not None else ""
                decrypted_row[key] = decrypt_string(value, fernet)
            rows.append(decrypted_row)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as out_file:
        writer = csv.DictWriter(out_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _build_multipart_body(file_path: Path, field_name: str, boundary: str) -> bytes:
    filename = file_path.name
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    file_bytes = file_path.read_bytes()
    parts: list[bytes] = []
    parts.append(f"--{boundary}\r\n".encode("utf-8"))
    parts.append(
        (
            f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode("utf-8")
    )
    parts.append(file_bytes)
    parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(parts)


def upload_file(file_path: Path, config: UploadConfig) -> tuple[bool, str]:
    boundary = f"----SensitiveProtectBoundary{uuid.uuid4().hex}"
    body = _build_multipart_body(file_path, config.upload_field, boundary)
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body)),
    }
    if config.token:
        headers[config.auth_header] = f"Bearer {config.token}"

    req = request.Request(config.upload_url, data=body, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=30) as resp:
            status = getattr(resp, "status", 200)
            payload = resp.read(200).decode("utf-8", errors="ignore")
            return True, f"HTTP {status} {payload}".strip()
    except HTTPError as exc:
        detail = exc.read(200).decode("utf-8", errors="ignore")
        return False, f"HTTPError {exc.code} {detail}".strip()
    except URLError as exc:
        return False, f"URLError {exc.reason}"
    except TimeoutError:
        return False, "TimeoutError upload timed out"


def protect_file(
    input_path: Path,
    output_path: Path,
    fernet: Fernet,
    write_if_unchanged: bool = True,
) -> ProtectionSummary:
    suffix = input_path.suffix.lower()
    summary = ProtectionSummary()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if suffix == ".txt":
        original = input_path.read_text(encoding="utf-8")
        protected = protect_string(original, fernet, summary)
        same_path = input_path.resolve() == output_path.resolve()
        should_write = (not same_path) or write_if_unchanged or (summary.encrypted_total > 0)
        if should_write:
            output_path.write_text(protected, encoding="utf-8")
        return summary

    if suffix == ".json":
        original = json.loads(input_path.read_text(encoding="utf-8"))
        protected = protect_json_value(original, fernet, summary)
        protected_text = json.dumps(protected, indent=2)
        same_path = input_path.resolve() == output_path.resolve()
        should_write = (not same_path) or write_if_unchanged or (summary.encrypted_total > 0)
        if should_write:
            output_path.write_text(protected_text, encoding="utf-8")
        return summary

    if suffix == ".csv":
        protect_csv(input_path, output_path, fernet, summary, write_if_unchanged=write_if_unchanged)
        return summary

    raise ValueError(f"Unsupported file type: {suffix}. Supported: .txt, .json, .csv")


def decrypt_file(input_path: Path, output_path: Path, fernet: Fernet) -> None:
    suffix = input_path.suffix.lower()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if suffix == ".txt":
        encrypted_text = input_path.read_text(encoding="utf-8")
        output_path.write_text(decrypt_string(encrypted_text, fernet), encoding="utf-8")
        return

    if suffix == ".json":
        encrypted_json = json.loads(input_path.read_text(encoding="utf-8"))
        decrypted_json = decrypt_json_value(encrypted_json, fernet)
        output_path.write_text(json.dumps(decrypted_json, indent=2), encoding="utf-8")
        return

    if suffix == ".csv":
        decrypt_csv(input_path, output_path, fernet)
        return

    raise ValueError(f"Unsupported file type: {suffix}. Supported: .txt, .json, .csv")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect sensitive data in a file and encrypt only sensitive values before sharing."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    protect = subparsers.add_parser("protect", help="Protect sensitive data in a file.")
    protect.add_argument("--input", required=True, type=Path, help="Path to input file (.txt/.json/.csv)")
    protect.add_argument("--output", required=True, type=Path, help="Path to write protected output file")
    protect.add_argument("--key-file", required=True, type=Path, help="Path to encryption key file")

    decrypt = subparsers.add_parser("decrypt", help="Decrypt a previously protected file.")
    decrypt.add_argument("--input", required=True, type=Path, help="Path to protected input file")
    decrypt.add_argument("--output", required=True, type=Path, help="Path to write decrypted output file")
    decrypt.add_argument("--key-file", required=True, type=Path, help="Path to encryption key file")

    watch = subparsers.add_parser(
        "watch",
        help="Automatically watch a folder and protect supported files into an output folder.",
    )
    watch.add_argument("--input-dir", required=True, type=Path, help="Folder to monitor for outgoing files")
    watch.add_argument("--output-dir", type=Path, default=None, help="Folder where protected files are written")
    watch.add_argument(
        "--in-place",
        action="store_true",
        help="Encrypt files directly inside input-dir (no separate output folder).",
    )
    watch.add_argument("--key-file", required=True, type=Path, help="Path to encryption key file")
    watch.add_argument("--interval-seconds", type=float, default=2.0, help="Polling interval in seconds")
    watch.add_argument("--upload-url", type=str, default=None, help="Upload endpoint URL (e.g. Clawmatry API).")
    watch.add_argument("--upload-token", type=str, default=None, help="Bearer token for upload endpoint.")
    watch.add_argument(
        "--upload-auth-header",
        type=str,
        default="Authorization",
        help="Auth header name used for bearer token.",
    )
    watch.add_argument(
        "--upload-field",
        type=str,
        default="file",
        help="Multipart form field name for file upload.",
    )
    watch.add_argument(
        "--upload-only-if-sensitive",
        action="store_true",
        help="Upload only when at least one sensitive value was encrypted.",
    )
    return parser.parse_args()


def resolve_upload_config(args: argparse.Namespace) -> UploadConfig | None:
    upload_url = args.upload_url or os.getenv("CLAWMATRY_UPLOAD_URL")
    if not upload_url:
        return None
    token = args.upload_token or os.getenv("CLAWMATRY_API_TOKEN")
    auth_header = args.upload_auth_header or os.getenv("CLAWMATRY_AUTH_HEADER", "Authorization")
    upload_field = args.upload_field or os.getenv("CLAWMATRY_UPLOAD_FIELD", "file")
    return UploadConfig(
        upload_url=upload_url,
        upload_field=upload_field,
        token=token,
        auth_header=auth_header,
        upload_all_files=not args.upload_only_if_sensitive,
    )


def run_watch(
    input_dir: Path,
    output_dir: Path,
    key_file: Path,
    interval_seconds: float,
    in_place: bool = False,
    upload_config: UploadConfig | None = None,
) -> int:
    supported_suffixes = {".txt", ".json", ".csv"}
    if input_dir.resolve() == output_dir.resolve() and not in_place:
        raise ValueError("input-dir and output-dir must be different folders.")
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    fernet = create_or_load_fernet(key_file)
    seen_versions: dict[Path, float] = {}
    if not in_place:
        output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Watching: {input_dir}")
    if in_place:
        print("Mode: in-place (files are encrypted directly inside input folder)")
    else:
        print(f"Protected files written to: {output_dir}")
    if upload_config:
        print(f"Upload enabled: {upload_config.upload_url}")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            for path in input_dir.rglob("*"):
                if not path.is_file() or path.suffix.lower() not in supported_suffixes:
                    continue
                mtime = path.stat().st_mtime
                if seen_versions.get(path) == mtime:
                    continue
                relative_path = path.relative_to(input_dir)
                output_path = path if in_place else (output_dir / relative_path)
                summary = protect_file(path, output_path, fernet, write_if_unchanged=not in_place)
                seen_versions[path] = path.stat().st_mtime
                if in_place:
                    print(f"Scanned {relative_path} (encrypted: {summary.encrypted_total})")
                else:
                    print(
                        f"Protected {relative_path} -> {output_path.name} "
                        f"(encrypted: {summary.encrypted_total})"
                    )
                if upload_config and (upload_config.upload_all_files or summary.encrypted_total > 0):
                    ok, message = upload_file(output_path, upload_config)
                    if ok:
                        print(f"Uploaded {relative_path}: {message}")
                    else:
                        print(f"Upload failed for {relative_path}: {message}")
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("Watcher stopped.")
        return 0


def main() -> int:
    args = parse_args()

    if args.command == "protect":
        if not args.input.exists():
            raise FileNotFoundError(f"Input file not found: {args.input}")
        fernet = create_or_load_fernet(args.key_file)
        summary = protect_file(args.input, args.output, fernet)
        print(f"Protected file written to: {args.output}")
        print(f"Key file: {args.key_file}")
        print(f"Encrypted values total: {summary.encrypted_total}")
        if summary.encrypted_counts:
            print("Encrypted by category:")
            for key, count in sorted(summary.encrypted_counts.items()):
                print(f"  - {key}: {count}")
        return 0

    if args.command == "decrypt":
        if not args.input.exists():
            raise FileNotFoundError(f"Input file not found: {args.input}")
        fernet = load_fernet_from_key_file(args.key_file)
        decrypt_file(args.input, args.output, fernet)
        print(f"Decrypted file written to: {args.output}")
        return 0

    if args.command == "watch":
        output_dir = args.output_dir or (args.input_dir.parent / "ready-to-send")
        if args.in_place:
            output_dir = args.input_dir
        upload_config = resolve_upload_config(args)
        return run_watch(
            args.input_dir,
            output_dir,
            args.key_file,
            args.interval_seconds,
            in_place=args.in_place,
            upload_config=upload_config,
        )

    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
