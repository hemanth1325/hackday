# Requirements: Sensitive File Protector

Status: Draft

## User Intent
- Install software on sender device.
- Before sending a file, software detects sensitive data in the file.
- Encrypt only sensitive data.
- Keep non-sensitive data unchanged.
- Receiver gets same file content except sensitive parts are encrypted.

## MVP Scope
- Local CLI tool for manual run before sending and optional watch mode for automatic folder processing.
- Supported file types: `.txt`, `.csv`, `.json`.
- Sensitive detection via rules:
  - email addresses,
  - phone numbers,
  - credit card number patterns,
  - password-like key/value fields (`password`, `passwd`, `pwd`, `secret`, `token`, `api_key`).
- Output:
  - protected file with encrypted sensitive values,
  - key file required for decryption by trusted recipient.

## Non-Goals (MVP)
- OS-level automatic interception of every transfer channel (email/chat/USB/browser uploads).
- Perfect detection for all document/image formats.

## Acceptance Criteria
- Given an input file containing both normal and sensitive values, output file preserves normal values.
- Detected sensitive values are replaced with ciphertext markers.
- Tool reports detection counts by data type.
- Receiver cannot read encrypted values without key.
