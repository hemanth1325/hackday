# API/E2E Testing

## Scenario 1: Protect sample text file
- Command:
  - `python -m app.sensitive_protector protect --input examples/sensitive-input.txt --output examples/sensitive-output.txt --key-file examples/receiver.key`
- Expected:
  - output file created,
  - sensitive values replaced by `ENC[...]`,
  - non-sensitive lines unchanged.
- Result: Pass.

## Scenario 2: Decrypt protected sample file
- Command:
  - `python -m app.sensitive_protector decrypt --input examples/sensitive-output.txt --output examples/sensitive-restored.txt --key-file examples/receiver.key`
- Expected:
  - restored file equals original sample.
- Result: Pass.

## Scenario 3: Automated unit tests
- Command:
  - `python -m unittest tests/test_sensitive_protector.py`
- Expected:
  - tests pass.
- Result: Pass.
