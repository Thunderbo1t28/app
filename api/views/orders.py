from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import logging
from sysdata.data_blob import dataBlob
from sysexecution.stack_handler.stack_handler import stackHandler
from quotes.models import INSTRUMENT_ORDER_STACK, CONTRACT_ORDER_STACK
from api.services.base import OrderService
from api.exceptions import OrderNotFoundError, InvalidOrderDataError
from django.conf import settings
import os
from api.serializers.serializers import InstrumentOrderSerializer, ContractOrderSerializer

logger = logging.getLogger(__name__)

class OrderViewSet(viewsets.ViewSet):
    """ViewSet для работы с ордерами"""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.order_service = OrderService()
    
    def list(self, request):
        """Получить список всех ордеров"""
        try:
            # Создаем лог файл
            log_file = os.path.join(settings.BASE_DIR, 'private', 'orders.log')
            log_dir = os.path.dirname(log_file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            instrument_orders = self.order_service.get_instrument_orders()
            contract_orders = self.order_service.get_contract_orders()
            with open(log_file, 'w') as f:
                f.write(str(instrument_orders))
                f.write(str(contract_orders))
            return Response({
                'instrument_orders': instrument_orders,
                'contract_orders': contract_orders
            })
        except Exception as e:
            logger.error(f"Error getting orders: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def refresh(self, request):
        """Обновить стеки ордеров вручную"""
        try:
            with dataBlob(log_name="API-Order-Stack") as data:
                stack_handler = stackHandler(data)
                
                # Обновляем инструментальные ордера
                instrument_orders = []
                for order_id in stack_handler.instrument_stack.get_list_of_order_ids():
                    order = stack_handler.instrument_stack.get_order_with_id_from_stack(order_id)
                    instrument_orders.append({
                        'id': order_id,
                        'type': str(order.order_type),
                        'status': order.fill_status(),
                        'instrument': order.instrument_code,
                        'quantity': float(order.trade),
                        'filled': float(order.fill),
                        'price': float(order.filled_price) if order.filled_price else None,
                        'created_at': order.fill_datetime.strftime('%Y-%m-%d %H:%M:%S') if order.fill_datetime else None
                    })
                
                instrument_stack = INSTRUMENT_ORDER_STACK.objects.first()
                if not instrument_stack:
                    instrument_stack = INSTRUMENT_ORDER_STACK()
                instrument_stack.data = instrument_orders
                instrument_stack.save()
                
                # Обновляем контрактные ордера
                contract_orders = []
                for order_id in stack_handler.contract_stack.get_list_of_order_ids():
                    order = stack_handler.contract_stack.get_order_with_id_from_stack(order_id)
                    contract_orders.append({
                        'id': order_id,
                        'type': str(order.order_type),
                        'status': order.fill_status(),
                        'instrument': order.instrument_code,
                        'quantity': float(order.trade),
                        'filled': float(order.fill),
                        'price': float(order.filled_price) if order.filled_price else None,
                        'created_at': order.fill_datetime.strftime('%Y-%m-%d %H:%M:%S') if order.fill_datetime else None
                    })
                
                contract_stack = CONTRACT_ORDER_STACK.objects.first()
                if not contract_stack:
                    contract_stack = CONTRACT_ORDER_STACK()
                contract_stack.data = contract_orders
                contract_stack.save()
                
                # Обновляем брокерские ордера
                broker_orders = []
                for order_id in stack_handler.broker_stack.get_list_of_order_ids():
                    order = stack_handler.broker_stack.get_order_with_id_from_stack(order_id)
                    broker_orders.append({
                        'id': order_id,
                        'type': str(order.order_type),
                        'status': order.fill_status(),
                        'instrument': order.instrument_code,
                        'quantity': float(order.trade),
                        'filled': float(order.fill),
                        'price': float(order.filled_price) if order.filled_price else None,
                        'created_at': order.fill_datetime.strftime('%Y-%m-%d %H:%M:%S') if order.fill_datetime else None
                    })
                
                
                
                return Response({
                    'status': 'success',
                    'message': 'Ордера обновлены',
                    'data': {
                        'instrument_orders': instrument_orders,
                        'contract_orders': contract_orders,
                        'broker_orders': broker_orders
                    }
                })
                
        except Exception as e:
            logger.error(f"Error refreshing orders: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def create_instrument_order(self, request):
        """Создать инструментальный ордер"""
        try:
            order = self.order_service.create_instrument_order(request.data)
            return Response(order, status=status.HTTP_201_CREATED)
        except InvalidOrderDataError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating instrument order: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Отменить ордер"""
        try:
            result = self.order_service.cancel_order(int(pk))
            return Response(result)
        except OrderNotFoundError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error cancelling order: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def spawn_children(self, request):
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
            result = self.order_service.spawn_children()
            return Response(result)
        except OrderNotFoundError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error spawning children: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def manual_fill(self, request, pk=None):
        """Ручное заполнение ордера"""
        try:
            result = self.order_service.generate_manual_fill(
                order_id=int(pk),
                fill_data=request.data
            )
            return Response(result)
        except (OrderNotFoundError, InvalidOrderDataError) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error generating manual fill: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def instrument_orders(self, request):
        instrument_orders = [order for order in INSTRUMENT_ORDER_STACK.objects.all() if order.ident != '_ORDER_ID_STORE_KEY']
        serializer = InstrumentOrderSerializer(instrument_orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])  
    def contract_orders(self, request):
        contract_orders = [order for order in CONTRACT_ORDER_STACK.objects.all() if order.ident != '_ORDER_ID_STORE_KEY']
        serializer = ContractOrderSerializer(contract_orders, many=True)
        return Response(serializer.data) 