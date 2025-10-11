import pytest

@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username="padrao", email="p@example.com", password="123456"
    )

@pytest.fixture(autouse=True)
def _auto_login(client, user):
    client.force_login(user)