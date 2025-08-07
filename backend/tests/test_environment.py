"""Test environment setup"""
import os


def test_environment_variables():
    """Verify environment variables are set correctly"""
    print("\n=== Environment Variables in Test ===")
    print(f"CI: {os.getenv('CI')}")
    print(f"DATABASE_PUBLIC_URL: {os.getenv('DATABASE_PUBLIC_URL', 'NOT SET')[:50]}...")
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT SET')[:50]}...")
    print(f"SECRET_KEY: {os.getenv('SECRET_KEY', 'NOT SET')}")
    
    # In CI, these should be set
    if os.getenv('CI'):
        assert os.getenv('DATABASE_PUBLIC_URL'), "DATABASE_PUBLIC_URL must be set in CI"
        assert os.getenv('SECRET_KEY'), "SECRET_KEY must be set in CI"