from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from .base import BaseModel
from .instrument import Instrument
from .strategy import Strategy

User = get_user_model()

class Portfolio(BaseModel):
    """Модель торгового портфеля."""
    
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='portfolios'
    )
    initial_capital = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField(max_length=3)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'portfolios'
        indexes = [
            models.Index(fields=['owner']),
        ]
        
    def __str__(self) -> str:
        return f"{self.name} ({self.owner.username})"
        
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            'name': self.name,
            'owner_id': self.owner_id,
            'initial_capital': str(self.initial_capital),
            'currency': self.currency,
            'description': self.description,
        })
        return data

class PortfolioPosition(BaseModel):
    """Модель позиции в портфеле."""
    
    POSITION_TYPES = [
        ('long', 'Длинная'),
        ('short', 'Короткая'),
    ]
    
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='positions'
    )
    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.CASCADE,
        related_name='positions'
    )
    strategy = models.ForeignKey(
        Strategy,
        on_delete=models.SET_NULL,
        null=True,
        related_name='positions'
    )
    type = models.CharField(max_length=5, choices=POSITION_TYPES)
    quantity = models.DecimalField(
        max_digits=15,
        decimal_places=8,
        validators=[MinValueValidator(0)]
    )
    entry_price = models.DecimalField(
        max_digits=15,
        decimal_places=8,
        validators=[MinValueValidator(0)]
    )
    current_price = models.DecimalField(
        max_digits=15,
        decimal_places=8,
        validators=[MinValueValidator(0)]
    )
    stop_loss = models.DecimalField(
        max_digits=15,
        decimal_places=8,
        null=True,
        blank=True
    )
    take_profit = models.DecimalField(
        max_digits=15,
        decimal_places=8,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'portfolio_positions'
        indexes = [
            models.Index(fields=['portfolio']),
            models.Index(fields=['instrument']),
            models.Index(fields=['strategy']),
            models.Index(fields=['type']),
        ]
        
    def __str__(self) -> str:
        return f"{self.instrument.symbol} in {self.portfolio.name}"
        
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            'portfolio_id': self.portfolio_id,
            'instrument_id': self.instrument_id,
            'strategy_id': self.strategy_id,
            'type': self.type,
            'quantity': str(self.quantity),
            'entry_price': str(self.entry_price),
            'current_price': str(self.current_price),
            'stop_loss': str(self.stop_loss) if self.stop_loss else None,
            'take_profit': str(self.take_profit) if self.take_profit else None,
        })
        return data 