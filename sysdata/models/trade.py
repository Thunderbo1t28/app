from django.db import models
from django.core.validators import MinValueValidator
from .base import BaseModel
from .portfolio import Portfolio, PortfolioPosition
from .instrument import Instrument
from .strategy import Strategy

class Trade(BaseModel):
    """Модель торговой операции."""
    
    TRADE_TYPES = [
        ('buy', 'Покупка'),
        ('sell', 'Продажа'),
    ]
    
    TRADE_STATUSES = [
        ('pending', 'Ожидает исполнения'),
        ('executed', 'Исполнен'),
        ('cancelled', 'Отменен'),
        ('rejected', 'Отклонен'),
        ('expired', 'Истек'),
    ]
    
    ORDER_TYPES = [
        ('market', 'Рыночный'),
        ('limit', 'Лимитный'),
        ('stop', 'Стоп'),
        ('stop_limit', 'Стоп-лимит'),
    ]
    
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='trades'
    )
    position = models.ForeignKey(
        PortfolioPosition,
        on_delete=models.SET_NULL,
        null=True,
        related_name='trades'
    )
    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.CASCADE,
        related_name='trades'
    )
    strategy = models.ForeignKey(
        Strategy,
        on_delete=models.SET_NULL,
        null=True,
        related_name='trades'
    )
    type = models.CharField(max_length=4, choices=TRADE_TYPES)
    order_type = models.CharField(max_length=10, choices=ORDER_TYPES)
    status = models.CharField(
        max_length=10,
        choices=TRADE_STATUSES,
        default='pending'
    )
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=8,
        validators=[MinValueValidator(0)]
    )
    price = models.DecimalField(
        max_digits=15,
        decimal_places=8,
        validators=[MinValueValidator(0)]
    )
    executed_price = models.DecimalField(
        max_digits=15,
        decimal_places=8,
        null=True,
        blank=True
    )
    commission = models.DecimalField(
        max_digits=15,
        decimal_places=8,
        default=0
    )
    executed_at = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'trades'
        indexes = [
            models.Index(fields=['portfolio']),
            models.Index(fields=['position']),
            models.Index(fields=['instrument']),
            models.Index(fields=['strategy']),
            models.Index(fields=['type']),
            models.Index(fields=['status']),
            models.Index(fields=['executed_at']),
        ]
        
    def __str__(self) -> str:
        return f"{self.type} {self.instrument.symbol} at {self.price}"
        
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            'portfolio_id': self.portfolio_id,
            'position_id': self.position_id,
            'instrument_id': self.instrument_id,
            'strategy_id': self.strategy_id,
            'type': self.type,
            'order_type': self.order_type,
            'status': self.status,
            'quantity': str(self.quantity),
            'price': str(self.price),
            'executed_price': str(self.executed_price) if self.executed_price else None,
            'commission': str(self.commission),
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'reason': self.reason,
        })
        return data 