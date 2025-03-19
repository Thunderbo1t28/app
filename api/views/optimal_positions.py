from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from quotes.models import optimal_positions
from api.serializers.serializers import OptimalPositionsSerializer



class OptimalPositionsListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OptimalPositionsSerializer
    queryset = optimal_positions.objects.all() 