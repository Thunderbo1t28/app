from django.db import models
from django.core.validators import MinValueValidator
from .base import BaseModel

class Instrument(BaseModel):
    """Модель торгового инструмента."""
    
    INSTRUMENT_TYPES = [
        ('stock', 'Акция'),
        ('bond', 'Облигация'),
        ('future', 'Фьючерс'),
        ('option', 'Опцион'),
        ('forex', 'Валютная пара'),
        ('crypto', 'Криптовалюта'),
    ]
    
    symbol = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=32, choices=INSTRUMENT_TYPES)
    exchange = models.CharField(max_length=32)
    currency = models.CharField(max_length=3)
    tick_size = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        validators=[MinValueValidator(0)]
    )
    multiplier = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1.0
    )
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'instruments'
        indexes = [
            models.Index(fields=['symbol']),
            models.Index(fields=['type']),
            models.Index(fields=['exchange']),
        ]
        
    def __str__(self) -> str:
        return f"{self.symbol} ({self.exchange})"
        
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            'symbol': self.symbol,
            'name': self.name,
            'type': self.type,
            'exchange': self.exchange,
            'currency': self.currency,
            'tick_size': str(self.tick_size),
            'multiplier': str(self.multiplier),
            'description': self.description,
        })
        return data 