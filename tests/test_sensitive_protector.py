import json
import tempfile
import unittest
from pathlib import Path

from app.sensitive_protector import create_or_load_fernet, decrypt_file, protect_file


class SensitiveProtectorTests(unittest.TestCase):
    def test_txt_encrypts_only_sensitive_content(self) -> None:
        original_text = (
            "customer=Alice\n"
            "project=Alpha\n"
            "email=alice@example.com\n"
            "phone=+1 202-555-0112\n"
            "password=SuperSecret123\n"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            key_file = root / "secret.key"
            input_path = root / "input.txt"
            encrypted_path = root / "encrypted.txt"
            decrypted_path = root / "decrypted.txt"
            input_path.write_text(original_text, encoding="utf-8")

            fernet = create_or_load_fernet(key_file)
            summary = protect_file(input_path, encrypted_path, fernet)
            encrypted_text = encrypted_path.read_text(encoding="utf-8")

            self.assertIn("project=Alpha", encrypted_text)
            self.assertNotIn("alice@example.com", encrypted_text)
            self.assertNotIn("SuperSecret123", encrypted_text)
            self.assertIn("ENC[", encrypted_text)
            self.assertGreaterEqual(summary.encrypted_total, 3)

            decrypt_file(encrypted_path, decrypted_path, fernet)
            self.assertEqual(original_text, decrypted_path.read_text(encoding="utf-8"))

    def test_json_preserves_non_sensitive_fields(self) -> None:
        payload = {
            "name": "Rahul",
            "department": "sales",
            "password": "abc123",
            "contact": {"email": "rahul@example.com", "city": "Berlin"},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            key_file = root / "secret.key"
            input_path = root / "input.json"
            encrypted_path = root / "encrypted.json"
            decrypted_path = root / "decrypted.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")

            fernet = create_or_load_fernet(key_file)
            protect_file(input_path, encrypted_path, fernet)
            encrypted_payload = json.loads(encrypted_path.read_text(encoding="utf-8"))

            self.assertEqual("Rahul", encrypted_payload["name"])
            self.assertEqual("sales", encrypted_payload["department"])
            self.assertEqual("Berlin", encrypted_payload["contact"]["city"])
            self.assertNotEqual("abc123", encrypted_payload["password"])
            self.assertNotEqual("rahul@example.com", encrypted_payload["contact"]["email"])
            self.assertTrue(str(encrypted_payload["password"]).startswith("ENC["))

            decrypt_file(encrypted_path, decrypted_path, fernet)
            decrypted_payload = json.loads(decrypted_path.read_text(encoding="utf-8"))
            self.assertEqual(payload, decrypted_payload)


if __name__ == "__main__":
    unittest.main()
