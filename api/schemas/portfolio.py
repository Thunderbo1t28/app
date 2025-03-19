from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field
from .base import BaseSchema

class PortfolioBase(BaseModel):
    """Базовая схема портфеля."""
    
    name: str = Field(..., description="Название портфеля")
    initial_capital: Decimal = Field(..., description="Начальный капитал")
    currency: str = Field(..., description="Валюта")
    description: Optional[str] = Field(None, description="Описание")

class PortfolioCreate(PortfolioBase):
    """Схема для создания портфеля."""
    pass

class PortfolioUpdate(BaseModel):
    """Схема для обновления портфеля."""
    
    name: Optional[str] = None
    initial_capital: Optional[Decimal] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class PortfolioResponse(PortfolioBase, BaseSchema):
    """Схема ответа с портфелем."""
    
    owner_id: int = Field(..., description="ID владельца портфеля")

class PortfolioPositionBase(BaseModel):
    """Базовая схема позиции в портфеле."""
    
    type: str = Field(..., description="Тип позиции (long/short)")
    quantity: Decimal = Field(..., description="Количество")
    entry_price: Decimal = Field(..., description="Цена входа")
    current_price: Decimal = Field(..., description="Текущая цена")
    stop_loss: Optional[Decimal] = Field(None, description="Стоп-лосс")
    take_profit: Optional[Decimal] = Field(None, description="Тейк-профит")

class PortfolioPositionCreate(PortfolioPositionBase):
    """Схема для создания позиции."""
    
    portfolio_id: int = Field(..., description="ID портфеля")
    instrument_id: int = Field(..., description="ID инструмента")
    strategy_id: Optional[int] = Field(None, description="ID стратегии")

class PortfolioPositionUpdate(BaseModel):
    """Схема для обновления позиции."""
    
    type: Optional[str] = None
    quantity: Optional[Decimal] = None
    current_price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    is_active: Optional[bool] = None

class PortfolioPositionResponse(PortfolioPositionBase, BaseSchema):
    """Схема ответа с позицией."""
    
    portfolio_id: int = Field(..., description="ID портфеля")
    instrument_id: int = Field(..., description="ID инструмента")
    strategy_id: Optional[int] = Field(None, description="ID стратегии") 