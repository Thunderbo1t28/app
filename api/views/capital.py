from rest_framework import viewsets
from rest_framework.response import Response
from quotes.models import arctic_capital
from api.serializers.serializers import arctic_capitalSerializer

class ArcticCapitalViewSet(viewsets.ModelViewSet):
    queryset = arctic_capital.objects.all()
    serializer_class = arctic_capitalSerializer 

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Получаем данные из запроса
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Обновляем массив data, добавляя новую запись
        instance.data.append(serializer.validated_data['data'][0])
        
        # Сохраняем обновленный объект
        self.perform_update(serializer)
        
        return Response(serializer.data)