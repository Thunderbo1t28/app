import factory
from decimal import Decimal
from sysdata.models.instrument import Instrument

class InstrumentFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания тестовых инструментов."""
    
    class Meta:
        model = Instrument
    
    symbol = factory.Sequence(lambda n: f'AAPL{n}')
    name = factory.Sequence(lambda n: f'Apple Inc. {n}')
    type = 'stock'
    exchange = 'NASDAQ'
    currency = 'USD'
    tick_size = Decimal('0.01')
    multiplier = Decimal('1.0')
    description = factory.Faker('text') 