from rest_framework import viewsets
from quotes.models import Instrument
from api.serializers.serializers import instrumentSerializer

class InstrumentViewSet(viewsets.ModelViewSet):
    queryset = Instrument.objects.all()
    serializer_class = instrumentSerializer