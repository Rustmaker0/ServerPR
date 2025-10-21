from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token #Import Token
from Data.models import *
from Data.serializers import *

class MeasuringViewset(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Measuring.objects.all()
    serializer_class = MeasuringSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 1. Получаем User ID из заголовка
        user_id = request.headers.get('X-User-Id')
        if user_id is None:
            return Response({"error": "User ID missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"error": "Invalid User ID"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Добавляем пользователя в validated_data
        validated_data = serializer.validated_data
        validated_data['user'] = user

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()  # Сохраняем, user уже есть в validated_data)

class TransportViewset(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Transport.objects.all()
    serializer_class = TransportSerializer


class IntensivityViewset(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Intensivity.objects.all()
    serializer_class = IntensivitySerializer


class PublicTransportViewset(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = PublicTransport.objects.all()
    serializer_class = PublicTransportSerializer


class PublicTransportNumberViewset(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = PublicTransportNumber.objects.all()
    serializer_class = PublicTransportNumberSerializer


class PeopleInPublicTransportViewset(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = PeopleInPublicTransport.objects.all()
    serializer_class = PeopleInPublicTransportSerializer


class UserViewset(GenericViewSet):
    @action(url_path="login", methods=["POST"], detail=False)
    def login(self, request, *args, **kwargs):
        username = request.data.get("user")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            serializer = UserSerializer(user)  # Serialize user data
            token, created = Token.objects.get_or_create(user=user) #Создание токена
            return Response({'token': token.key, **serializer.data}) # Возвращаем токен вместе с данными пользователя
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    @action(url_path="logout", methods=["POST"], detail=False)
    def logout(self, request, *args, **kwargs):
        logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)