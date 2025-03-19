from django.db import models
from django.utils import timezone
from typing import Any, Dict

class BaseModel(models.Model):
    """Базовый класс для всех моделей."""
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
        
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование модели в словарь."""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        } 