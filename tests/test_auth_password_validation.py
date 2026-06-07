import unittest
from unittest.mock import patch

from app.services.auth import (
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    PasswordHashingError,
    PasswordValidationError,
    authenticate_user,
    hash_password,
    normalize_password,
    register_user,
    validate_password,
    validate_password_for_reset,
    verify_password,
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

    def test_bcrypt_verify_succeeds_for_valid_password(self):
        password = "validpass123"
        password_hash = hash_password(password)
        self.assertTrue(verify_password(password, password_hash))

    def test_bcrypt_verify_fails_for_wrong_password(self):
        password_hash = hash_password("validpass123")
        self.assertFalse(verify_password("wrongpass123", password_hash))


class AuthFlowTest(unittest.TestCase):
    def test_account_creation_hashes_and_persists_user(self):
        mock_db = object()
        with patch("app.services.auth.repository.get_user_by_email", return_value=None), patch(
            "app.services.auth.repository.create_user",
            side_effect=lambda db, email, password_hash: {
                "db": db,
                "email": email,
                "password_hash": password_hash,
            },
        ):
            created = register_user(mock_db, "user@example.com", "validpass123")

        self.assertEqual(created["db"], mock_db)
        self.assertEqual(created["email"], "user@example.com")
        self.assertNotEqual(created["password_hash"], "validpass123")
        self.assertTrue(verify_password("validpass123", created["password_hash"]))

    def test_account_creation_rejects_65_character_password(self):
        with patch("app.services.auth.repository.get_user_by_email", return_value=None):
            with self.assertRaisesRegex(PasswordValidationError, "Password cannot exceed 64 characters."):
                register_user(object(), "user@example.com", "a" * 65)

    def test_login_succeeds_with_valid_credentials(self):
        password_hash = hash_password("validpass123")
        user = type("User", (), {"password_hash": password_hash})()
        with patch("app.services.auth.repository.get_user_by_email", return_value=user):
            authenticated = authenticate_user(object(), "user@example.com", "validpass123")
        self.assertIs(authenticated, user)

    def test_login_fails_for_invalid_password_length(self):
        with patch("app.services.auth.repository.get_user_by_email") as get_user:
            authenticated = authenticate_user(object(), "user@example.com", "short7!")
        self.assertIsNone(authenticated)
        get_user.assert_not_called()

    def test_login_fails_for_65_character_password(self):
        with patch("app.services.auth.repository.get_user_by_email") as get_user:
            authenticated = authenticate_user(object(), "user@example.com", "a" * 65)
        self.assertIsNone(authenticated)
        get_user.assert_not_called()

    def test_login_accepts_64_character_password(self):
        password = "a" * 64
        password_hash = hash_password(password)
        user = type("User", (), {"password_hash": password_hash})()
        with patch("app.services.auth.repository.get_user_by_email", return_value=user):
            authenticated = authenticate_user(object(), "user@example.com", password)
        self.assertIs(authenticated, user)

    def test_database_errors_do_not_escape_register_user_as_raw_exceptions(self):
        with patch("app.services.auth.repository.get_user_by_email", return_value=None), patch(
            "app.services.auth.repository.create_user",
            side_effect=RuntimeError("database down"),
        ):
            with self.assertRaisesRegex(
                ValueError,
                "Unable to create account. Please use a shorter password.",
            ):
                register_user(object(), "user@example.com", "validpass123")


if __name__ == "__main__":
    unittest.main()
