import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture
def api_client():
    """Фикстура для API клиента."""
    return APIClient()

@pytest.fixture
def user():
    """Фикстура для создания тестового пользователя."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def authenticated_client(api_client, user):
    """Фикстура для аутентифицированного API клиента."""
    api_client.force_authenticate(user=user)
    return api_client 