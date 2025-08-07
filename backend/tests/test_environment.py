"""Test environment setup"""
import os


def test_environment_variables():
    """Verify environment variables are set correctly"""
    # In CI, these should be set
    if os.getenv('CI'):
        assert os.getenv('DATABASE_PUBLIC_URL'), "DATABASE_PUBLIC_URL must be set in CI"
        assert os.getenv('SECRET_KEY'), "SECRET_KEY must be set in CI"