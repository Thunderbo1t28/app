from django.db import models
from django.contrib.auth import get_user_model
from .base import BaseModel

User = get_user_model()

class Strategy(BaseModel):
    """Модель торговой стратегии."""
    
    STRATEGY_TYPES = [
        ('trend', 'Трендовая'),
        ('mean_reversion', 'Возврат к среднему'),
        ('momentum', 'Моментум'),
        ('volatility', 'Волатильность'),
        ('arbitrage', 'Арбитраж'),
        ('custom', 'Пользовательская'),
    ]
    
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=32, choices=STRATEGY_TYPES)
    description = models.TextField(blank=True)
    parameters = models.JSONField(default=dict)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='strategies'
    )
    is_active = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'strategies'
        verbose_name_plural = 'strategies'
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['owner']),
            models.Index(fields=['is_active']),
        ]
        
    def __str__(self) -> str:
        return f"{self.name} ({self.type})"
        
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'parameters': self.parameters,
            'owner_id': self.owner_id,
            'is_active': self.is_active,
        })
        return data 