# Future-State Runtime Call Stack

## Use Case: Protect File Before Sending
1. User runs CLI: `python -m app.sensitive_protector protect --input ... --output ... --key-file ...`
2. CLI validates extension and loads content.
3. Detector scans content:
- structured traversal for json/csv fields,
- regex sweep for txt.
4. For each sensitive match:
- plaintext value passed to `encrypt_value`,
- returned token wrapped as `ENC[...]`,
- value replaced in-memory.
5. Transformed content saved to output file.
6. Key material saved once to key file if not already present.
7. CLI prints summary counts.

## Use Case: Optional Decrypt Validation
1. User runs CLI decrypt command with key file.
2. Parser loads file and finds `ENC[...]` markers.
3. Decrypt service restores original values.
4. Restored output is written to validation output file.
