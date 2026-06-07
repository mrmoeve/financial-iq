import unittest
from unittest.mock import patch

from app.services.auth import (
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    PasswordHashingError,
    PasswordValidationError,
    hash_password,
    normalize_password,
    validate_password,
    validate_password_for_reset,
)


class PasswordValidationTest(unittest.TestCase):
    def test_7_characters_fails(self):
        with self.assertRaisesRegex(PasswordValidationError, "Password must be at least 8 characters."):
            validate_password("1234567")

    def test_8_characters_passes(self):
        self.assertEqual(validate_password("12345678"), "12345678")

    def test_64_characters_passes(self):
        password = "a" * PASSWORD_MAX_LENGTH
        self.assertEqual(validate_password(password), password)

    def test_65_characters_fails(self):
        with self.assertRaisesRegex(PasswordValidationError, "Password cannot exceed 64 characters."):
            validate_password("a" * (PASSWORD_MAX_LENGTH + 1))

    def test_100_plus_characters_fail(self):
        with self.assertRaisesRegex(PasswordValidationError, "Password cannot exceed 64 characters."):
            validate_password("a" * 120)

    def test_whitespace_is_trimmed_before_validation(self):
        self.assertEqual(normalize_password(" 12345678 "), "12345678")
        self.assertEqual(validate_password(" 12345678 "), "12345678")

    def test_password_reset_uses_same_validation_rules(self):
        self.assertEqual(validate_password_for_reset("abcdefgh"), "abcdefgh")
        with self.assertRaisesRegex(PasswordValidationError, "Password cannot exceed 64 characters."):
            validate_password_for_reset("b" * 120)

    def test_hashing_exception_is_converted_to_friendly_message(self):
        with patch("app.services.auth.pwd_context.hash", side_effect=RuntimeError("bcrypt exploded")):
            with self.assertRaisesRegex(
                PasswordHashingError,
                "Unable to create account. Please use a shorter password.",
            ):
                hash_password("validpass")

    def test_hash_password_accepts_boundary_lengths(self):
        self.assertTrue(hash_password("a" * PASSWORD_MIN_LENGTH))
        self.assertTrue(hash_password("a" * PASSWORD_MAX_LENGTH))


if __name__ == "__main__":
    unittest.main()
