from rest_framework import serializers
from django.contrib.auth import get_user_model

from Data.models import *


User = get_user_model()

class MeasuringSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        allow_null=True,
        required=False
    )
    def get_user(self, obj):
        return obj.user.username if obj.user else None 
    class Meta:
        model = Measuring
        fields = '__all__'

class TransportSerializer(serializers.ModelSerializer):

    class Meta:
        model=Transport
        fields="__all__"

class IntensivitySerializer(serializers.ModelSerializer):
    """
    transport=TransportSerializer(read_only=True)
    transport_id=serializers.PrimaryKeyRelatedField(queryset=Transport.objects.all(), write_only=True, source="transport")
    measuring=MeasuringSerializer(read_only=True)
    measuring_id=serializers.PrimaryKeyRelatedField(queryset=Measuring.objects.all(), write_only=True, source="measuring")
    """
    class Meta:
        model=Intensivity
        fields="__all__"

class PublicTransportSerializer(serializers.ModelSerializer):

    class Meta:
        model=PublicTransport
        fields="__all__"

class PublicTransportNumberSerializer(serializers.ModelSerializer):
    """
    public_transport=PublicTransportSerializer(read_only=True)
    public_transport_id=serializers.PrimaryKeyRelatedField(queryset=PublicTransport.objects.all(), write_only=True, source="publicTransport")
    """
    class Meta:
        model=PublicTransportNumber
        fields="__all__"

class PeopleInPublicTransportSerializer(serializers.ModelSerializer):
    """
    public_transport_number=PublicTransportNumberSerializer(read_only=True)
    public_transport_number_id=serializers.PrimaryKeyRelatedField(queryset=PublicTransportNumber.objects.all(), write_only=True, source="publicTransportNumber")
    measuring=MeasuringSerializer(read_only=True)
    measuring_id=serializers.PrimaryKeyRelatedField(queryset=Measuring.objects.all(), write_only=True, source="measuring")
    """
    class Meta:
        model=PeopleInPublicTransport
        fields="__all__"

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email','first_name','last_name']