from typing import Optional, Dict, Any
from datetime import datetime
from sysdata.data_blob import dataBlob
from sysexecution.stack_handler.stack_handler import stackHandler
from quotes.models import INSTRUMENT_ORDER_STACK, CONTRACT_ORDER_STACK
from api.exceptions import OrderNotFoundError, InvalidOrderDataError
from api.serializers.serializers import InstrumentOrderStackSerializer, ContractOrderStackSerializer
from sysexecution.orders.named_order_objects import missing_order, no_children
from django.conf import settings
import os

class OrderService:
    """Базовый сервис для работы с ордерами"""
    
    def __init__(self):
        self.data = dataBlob(log_name="API-Order-Service")
        self.stack_handler = stackHandler(self.data)
    
    def get_instrument_orders(self) -> list:
        """Получить список инструментальных ордеров"""
        stack = INSTRUMENT_ORDER_STACK.objects.all()
        return InstrumentOrderStackSerializer(stack, many=True).data
    
    def get_contract_orders(self) -> list:
        """Получить список контрактных ордеров"""
        stack = CONTRACT_ORDER_STACK.objects.all()
        return ContractOrderStackSerializer(stack, many=True).data
    
    
    
    def create_instrument_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создать инструментальный ордер"""
        try:
            # Валидация данных ордера
            if not all(key in order_data for key in ['instrument', 'quantity', 'type']):
                raise InvalidOrderDataError("Missing required order data")
            
            # Создание ордера через stack_handler
            order_id = self.stack_handler.instrument_stack.put_manual_order_on_stack(
                strategy_name="manual",
                instrument_code=order_data['instrument'],
                trade=float(order_data['quantity']),
                order_type=order_data['type']
            )
            
            return {'order_id': order_id, 'status': 'created'}
            
        except Exception as e:
            raise InvalidOrderDataError(f"Error creating instrument order: {str(e)}")
    
    def cancel_order(self, order_id: int) -> Dict[str, Any]:
        """Отменить ордер"""
        try:
            self.stack_handler.cancel_order_given_order_id(order_id)
            return {'order_id': order_id, 'status': 'cancelled'}
        except Exception as e:
            raise OrderNotFoundError(f"Error cancelling order {order_id}: {str(e)}")
     
    def spawn_children(self) -> Dict[str, Any]:
        """Создать дочерние ордера"""
        try:
            # Создаем лог файл
            log_file = os.path.join(settings.BASE_DIR, 'private', 'spawn_orders.log')
            log_dir = os.path.dirname(log_file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            # Валидация данных заполнения
            with open(log_file, 'w') as f:
                f.write(str('spawn_children'))
            
            self.stack_handler.spawn_children_from_new_instrument_orders()
            return {'status': 'all_children_spawned'}
        except Exception as e:
            raise OrderNotFoundError(f"Error spawning children for order {order_id}: {str(e)}")
    
    def generate_manual_fill(self, order_id: int, fill_data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерировать ручное заполнение ордера"""
        try:
            # Создаем лог файл
            log_file = os.path.join(settings.BASE_DIR, 'private', 'fill_orders.log')
            log_dir = os.path.dirname(log_file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            # Валидация данных заполнения
            
            with open(log_file, 'w') as f:
                #f.write(str(order_id))
                if not all(key in fill_data for key in ['fill_price', 'fill_quantity']):
                    raise InvalidOrderDataError("Missing required fill data")
                f.write(str(fill_data['fill_price']))
                f.write(str(type(fill_data['fill_quantity'])))
                
                fill_qty = [fill_data['fill_quantity']]
                
                
               
                order = self.stack_handler.contract_stack.get_order_with_id_from_stack(order_id)
                #f.write(str(order))
                
                f.write(str(fill_qty))
                if order is missing_order:
                    f.write("Order doesn't exist on stack")
                    return None
                if len(order.trade) > 1:
                    f.write("Can't manually fill spread orders; delete and replace with legs")
                    return None
                if not no_children:
                    f.write(
                        "Don't manually fill order with children: can cause problems! Manually fill the child instead"
                    )
                    return None
                
                order.fill_order(
                    fill_qty=fill_qty, filled_price=float(fill_data['fill_quantity']), fill_datetime=None
                )
                f.write(str(order))
            self.stack_handler.contract_stack.mark_as_manual_fill_for_order_id(order_id)
            self.stack_handler.apply_contract_order_fill_to_database(order)
            order = self.stack_handler.contract_stack.get_order_with_id_from_stack(order_id)
            print("Order now %s" % str(order))
            print("If stack process not running, your next job will be to pass fills upwards")
            return {'order_id': order_id, 'status': 'manually_filled'}
            
        except Exception as e:
            raise OrderNotFoundError(f"Error generating manual fill for order {order_id}: {str(e)}") 