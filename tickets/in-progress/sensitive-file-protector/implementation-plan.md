# Implementation Plan

## Goal
Create an installable local CLI that detects sensitive data in text/json/csv files and encrypts only sensitive values.

## Components
1. `sensitive_protector.py`
- File loader/saver for txt/json/csv.
- Sensitive detector (regex + sensitive-key heuristics).
- Encryption service using `cryptography.fernet.Fernet`.
- CLI command:
  - `protect`: process file and write output.
  - `decrypt`: optional validation command.

2. Sample files
- Add input file containing normal and sensitive fields.
- Add expected behavior docs.

3. Tests
- Verify sensitive values are encrypted.
- Verify non-sensitive values remain unchanged.
- Verify decrypt restores original values.

## Output Contract
- Encrypted token format in content: `ENC[<base64-token>]`.
- Summary report at CLI end with detection counts and output paths.
