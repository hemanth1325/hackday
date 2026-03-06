# Assess openclow encryption

This folder contains only the sensitive-data encryption project.

## Recommended (one-time setup, no manual start each time)
Run once:
```powershell
.\scripts\setup-auto-folder-encryption.ps1
```
After that:
- drop files in `outgoing\`
- send the same file from `outgoing\` (it is encrypted in-place)
- watcher auto-starts on every Windows login

Disable later:
```powershell
.\scripts\remove-auto-folder-encryption.ps1
```

## Connect to Clawmatry (optional)
1. Create config file:
```powershell
.\scripts\configure-clawmatry.ps1
```
2. Edit `clawmatry.config.json` with your real API endpoint/token.
3. Restart watcher:
```powershell
.\scripts\stop-auto-protect-agent.ps1
.\scripts\start-auto-protect-agent.ps1
```
4. Now each processed file is also uploaded to Clawmatry.

## Demo Dashboard
Run:
```powershell
.\scripts\start-dashboard.ps1
```
Open:
- [http://localhost:8501](http://localhost:8501)

Dashboard shows:
- watcher running/stopped state
- files in `outgoing`
- encrypted marker counts (`ENC[...]`)
- possible plain sensitive matches
- file preview and logs

## Install
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Protect file
```powershell
python -m app.sensitive_protector protect --input examples\sensitive-input.txt --output examples\sensitive-output.txt --key-file examples\receiver.key
```

## Decrypt file
```powershell
python -m app.sensitive_protector decrypt --input examples\sensitive-output.txt --output examples\sensitive-restored.txt --key-file examples\receiver.key
```

## Automatic mode (no manual protect command each time)
1. Start background agent:
```powershell
.\scripts\start-auto-protect-agent.ps1
```
2. Drop any `.txt`, `.json`, `.csv` files you plan to send into:
`outgoing\`
3. Agent encrypts sensitive values directly in that same file (in-place).
4. Send files from `outgoing\`.
5. Stop agent when needed:
```powershell
.\scripts\stop-auto-protect-agent.ps1
```

## Important limitation
This is automatic for files routed through the `outgoing\` folder.
Intercepting every possible app/channel on Windows (email clients, browsers, chat apps, USB, etc.) requires deeper OS/app-specific integration (enterprise DLP style).

## Build EXE files
```powershell
.\scripts\build-exe.ps1
```

Generated files:
- `release\AutoProtectAgent.exe` (continuous folder watcher)
- `release\SensitiveProtectorCLI.exe` (manual protect/decrypt CLI)

## Use EXE directly
1. Put `AutoProtectAgent.exe` in any folder.
2. Run it.
3. It automatically creates:
   - `outgoing\`
   - `ready-to-send\`
   - `keys\`
4. Copy files to `outgoing\`.
5. Send files from `ready-to-send\`.

Run now with helper scripts:
```powershell
.\scripts\start-exe-agent-now.ps1
.\scripts\stop-exe-agent-now.ps1
```

## Auto-start on Windows login
After building EXE, run:
```powershell
.\scripts\install-startup.ps1
```
Remove auto-start:
```powershell
.\scripts\uninstall-startup.ps1
```
