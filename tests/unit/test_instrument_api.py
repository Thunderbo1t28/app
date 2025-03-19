import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework import status

from tests.factories.instrument import InstrumentFactory

pytestmark = pytest.mark.django_db

def test_instrument_list(authenticated_client):
    """Тест получения списка инструментов."""
    # Создаем тестовые данные
    instruments = [InstrumentFactory() for _ in range(3)]
    
    # Отправляем запрос
    url = reverse('api:instrument-list')
    response = authenticated_client.get(url)
    
    # Проверяем ответ
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3
    
    for instrument_data, instrument in zip(response.json(), instruments):
        assert instrument_data['symbol'] == instrument.symbol
        assert instrument_data['name'] == instrument.name
        assert instrument_data['type'] == instrument.type
        assert instrument_data['exchange'] == instrument.exchange
        assert instrument_data['currency'] == instrument.currency
        assert Decimal(instrument_data['tick_size']) == instrument.tick_size
        assert Decimal(instrument_data['multiplier']) == instrument.multiplier

def test_instrument_detail(authenticated_client):
    """Тест получения детальной информации об инструменте."""
    # Создаем тестовые данные
    instrument = InstrumentFactory()
    
    # Отправляем запрос
    url = reverse('api:instrument-detail', kwargs={'pk': instrument.id})
    response = authenticated_client.get(url)
    
    # Проверяем ответ
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['symbol'] == instrument.symbol
    assert response.json()['name'] == instrument.name
    assert response.json()['type'] == instrument.type
    assert response.json()['exchange'] == instrument.exchange
    assert response.json()['currency'] == instrument.currency
    assert Decimal(response.json()['tick_size']) == instrument.tick_size
    assert Decimal(response.json()['multiplier']) == instrument.multiplier

def test_instrument_create(authenticated_client):
    """Тест создания инструмента."""
    # Подготавливаем данные
    data = {
        'symbol': 'GOOGL',
        'name': 'Alphabet Inc.',
        'type': 'stock',
        'exchange': 'NASDAQ',
        'currency': 'USD',
        'tick_size': '0.01',
        'multiplier': '1.0',
        'description': 'Google parent company'
    }
    
    # Отправляем запрос
    url = reverse('api:instrument-list')
    response = authenticated_client.post(url, data)
    
    # Проверяем ответ
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['symbol'] == data['symbol']
    assert response.json()['name'] == data['name']
    assert response.json()['type'] == data['type']
    assert response.json()['exchange'] == data['exchange']
    assert response.json()['currency'] == data['currency']
    assert Decimal(response.json()['tick_size']) == Decimal(data['tick_size'])
    assert Decimal(response.json()['multiplier']) == Decimal(data['multiplier'])
    assert response.json()['description'] == data['description']

def test_instrument_update(authenticated_client):
    """Тест обновления инструмента."""
    # Создаем тестовые данные
    instrument = InstrumentFactory()
    
    # Подготавливаем данные для обновления
    data = {
        'name': 'Updated Name',
        'description': 'Updated description'
    }
    
    # Отправляем запрос
    url = reverse('api:instrument-detail', kwargs={'pk': instrument.id})
    response = authenticated_client.patch(url, data)
    
    # Проверяем ответ
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['name'] == data['name']
    assert response.json()['description'] == data['description']
    assert response.json()['symbol'] == instrument.symbol  # Не должно измениться

def test_instrument_delete(authenticated_client):
    """Тест удаления инструмента."""
    # Создаем тестовые данные
    instrument = InstrumentFactory()
    
    # Отправляем запрос
    url = reverse('api:instrument-detail', kwargs={'pk': instrument.id})
    response = authenticated_client.delete(url)
    
    # Проверяем ответ
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Проверяем, что инструмент удален
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND 