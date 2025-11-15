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
        fields = ['id', 'username', 'email','first_name','last_name', 'is_superuser', 'is_active']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, required=True)
    is_superuser = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'is_superuser', 'is_active']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        is_superuser = validated_data.pop('is_superuser', False)
        user = User.objects.create_user(**validated_data)
        if is_superuser:
            user.is_superuser = True
            user.is_staff = True  # Обычно суперпользователь также является staff
            user.save()
        return user
        
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'last_login', 'is_superuser']