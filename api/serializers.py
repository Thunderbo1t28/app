from rest_framework import serializers
from quotes.models import Instrument, contract_positions, arctic_capital

class contract_positionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = contract_positions
        fields = '__all__'

class arctic_capitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = arctic_capital
        fields = '__all__'
class instrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = '__all__'
