# Sensitive File Protector (MVP)

This tool scans a file, encrypts only detected sensitive values, and keeps non-sensitive content unchanged.

## Supported file types
- `.txt`
- `.json`
- `.csv`

## Install
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Or run:
```powershell
.\scripts\install-sensitive-protector.ps1
```

## Protect a file before sending
```powershell
python -m app.sensitive_protector protect --input examples\sensitive-input.txt --output examples\sensitive-output.txt --key-file examples\receiver.key
```

## Optional decrypt check
```powershell
python -m app.sensitive_protector decrypt --input examples\sensitive-output.txt --output examples\sensitive-restored.txt --key-file examples\receiver.key
```

## Quick sample run
```powershell
.\scripts\run-sensitive-protector-sample.ps1
```

## Automatic mode (folder watcher)
Put files into an outgoing folder and the tool will auto-create protected copies in another folder.

```powershell
python -m app.sensitive_protector watch --input-dir outgoing --output-dir ready-to-send --key-file keys\receiver.key --interval-seconds 2
```

## Notes
- Share the protected file with receiver.
- Share the key file only with trusted receiver through a separate secure channel.
- Receiver without key can still read non-sensitive content, but sensitive parts remain encrypted.
