from rest_framework import serializers
from django.contrib.auth.models import User
from quotes.models import Instrument, contract_positions, arctic_capital, optimal_positions, INSTRUMENT_ORDER_STACK, CONTRACT_ORDER_STACK
from api.models import LoadHistory, Task, ContractPosition
from django.contrib.auth import get_user_model
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Пароли не совпадают")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class instrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = '__all__'

class contract_positionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = contract_positions
        fields = '__all__'

class arctic_capitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = arctic_capital
        fields = '__all__'

class LoadHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoadHistory
        fields = ('id', 'status', 'message', 'details', 'created_at', 'completed_at')

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'task_id', 'status', 'result', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

class ContractPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractPosition
        fields = ('id', 'contract_id', 'quantity', 'average_price', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

class OptimalPositionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = optimal_positions
        fields = '__all__' 

class InstrumentOrderStackSerializer(serializers.ModelSerializer):
    class Meta:
        model = INSTRUMENT_ORDER_STACK
        fields = '__all__'

class ContractOrderStackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CONTRACT_ORDER_STACK
        fields = '__all__'

class InstrumentOrderSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    instrument = serializers.CharField(source='data.key')
    trade = serializers.ListField(child=serializers.IntegerField(), source='data.trade')
    fill = serializers.ListField(child=serializers.IntegerField(), source='data.fill')
    filled_price = serializers.FloatField(source='data.filled_price')
    reference_price = serializers.FloatField(source='data.reference_price')
    order_id = serializers.IntegerField(source='data.order_id')
    active = serializers.BooleanField(source='data.active')
    order_type = serializers.CharField(source='data.order_type')
    reference_price = serializers.FloatField(source='data.reference_price')
    reference_datetime = serializers.DateTimeField(source='data.reference_datetime')

class ContractOrderSerializer(serializers.Serializer):
    id = serializers.IntegerField()  
    instrument = serializers.CharField(source='data.key')
    trade = serializers.ListField(child=serializers.IntegerField(), source='data.trade')
    fill = serializers.ListField(child=serializers.IntegerField(), source='data.fill')
    filled_price = serializers.FloatField(source='data.filled_price')
    reference_price = serializers.FloatField(source='data.reference_price')
    order_id = serializers.IntegerField(source='data.order_id')
    active = serializers.BooleanField(source='data.active')
    order_type = serializers.CharField(source='data.order_type')
    reference_price = serializers.FloatField(source='data.reference_price')
    generated_datetime = serializers.DateTimeField(source='data.generated_datetime')
