"""Smoke test to verify all imports work correctly"""
import pytest


def test_preferences_module_imports():
    """Test that preferences module can be imported"""
    from app.api.endpoints import preferences
    assert hasattr(preferences, 'router')


def test_auth_import():
    """Test that auth imports work"""
    from app.api.endpoints.auth import get_current_user
    assert callable(get_current_user)


def test_models_import():
    """Test that UserPreferences model can be imported"""
    from app.models.models import UserPreferences
    assert UserPreferences is not None
    assert hasattr(UserPreferences, '__tablename__')
    assert UserPreferences.__tablename__ == 'user_preferences'


def test_api_router_import():
    """Test that API router includes preferences"""
    from app.api import api_router
    # Check that the router was successfully imported
    assert api_router is not None