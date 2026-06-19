"""
Auth API Tests – registration, login, token refresh.
"""

import pytest
from unittest.mock import AsyncMock, patch


class TestAuthEndpoints:
    """Test suite for authentication endpoints."""

    def test_password_hashing(self):
        from app.core.security import hash_password, verify_password
        hashed = hash_password("TestPassword123!")
        assert hashed != "TestPassword123!"
        assert verify_password("TestPassword123!", hashed) is True
        assert verify_password("WrongPassword", hashed) is False

    def test_jwt_token_creation(self):
        from app.core.security import create_access_token, create_refresh_token, decode_token
        access = create_access_token({"sub": "test-user-id"})
        assert access is not None

        payload = decode_token(access)
        assert payload["sub"] == "test-user-id"
        assert payload["type"] == "access"

    def test_refresh_token_creation(self):
        from app.core.security import create_refresh_token, decode_token
        refresh = create_refresh_token({"sub": "test-user-id"})
        payload = decode_token(refresh)
        assert payload["sub"] == "test-user-id"
        assert payload["type"] == "refresh"

    def test_user_register_schema_validation(self):
        from app.schemas.user import UserRegister
        # Valid registration
        user = UserRegister(email="test@example.com", username="testuser", password="securepassword123")
        assert user.email == "test@example.com"
        assert user.username == "testuser"

    def test_user_register_invalid_username(self):
        from app.schemas.user import UserRegister
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            UserRegister(email="test@example.com", username="ab", password="password123")  # Too short

    def test_user_register_invalid_password(self):
        from app.schemas.user import UserRegister
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            UserRegister(email="test@example.com", username="testuser", password="short")  # Too short
