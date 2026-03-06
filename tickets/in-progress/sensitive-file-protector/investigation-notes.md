# Investigation Notes

## Repo Context
- Existing repository is Python-based and currently focused on webcam gesture control.
- No existing module handles file security/redaction.
- Existing test setup uses `pytest`.

## Triage
- Scope classification: Small.
- Safe approach: add isolated CLI module and tests to avoid regressions in existing app.

## Constraints
- Must preserve non-sensitive data exactly.
- Must be easy to install and test locally.
- Should not require cloud services.

## Implementation Direction
- Build a standalone CLI script under `app/`.
- Support text-based formats first: txt, csv, json.
- Use deterministic marker format around encrypted payload.
- Encrypt sensitive matches with symmetric key (`Fernet`).
