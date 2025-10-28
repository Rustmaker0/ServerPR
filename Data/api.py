from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from Data.models import *
from Data.serializers import *

from django.http import HttpResponse
import pandas as pd
import io
from django.core.exceptions import ValidationError

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

        user_id = request.headers.get('X-User-Id')
        if user_id is None:
            return Response({"error": "User ID missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"error": "Invalid User ID"}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        validated_data['user'] = user

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

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
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'register':
            return UserRegistrationSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'list':
            return UserDetailSerializer
        return UserSerializer

    # Вход для суперпользователя
    @action(url_path="superuser-login", methods=["POST"], detail=False)
    def superuser_login(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)
        if user and user.is_superuser:
            # Удаляем старый токен, если есть
            Token.objects.filter(user=user).delete()
            
            # Создаем новый токен
            token = Token.objects.create(user=user)
            
            # Логиним пользователя в сессии
            login(request, user)
            
            return Response({
                'token': token.key, 
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_superuser': user.is_superuser
                },
                'message': 'Успешный вход как суперпользователь'
            })
        else:
            return Response({
                "error": "Неверные учетные данные или недостаточно прав"
            }, status=status.HTTP_401_UNAUTHORIZED)

    @action(url_path="check-superuser", methods=["GET"], detail=False)
    def check_superuser(self, request, *args, **kwargs):
        # Проверяем как по токену, так и по сессии
        if request.user.is_authenticated and request.user.is_superuser:
            return Response({
                "is_superuser": True, 
                "user": UserSerializer(request.user).data
            })
        
        # Дополнительная проверка по токену
        if request.auth and hasattr(request.auth, 'user'):
            user = request.auth.user
            if user.is_superuser:
                return Response({
                    "is_superuser": True, 
                    "user": UserSerializer(user).data
                })
        
        return Response({"is_superuser": False}, status=status.HTTP_403_FORBIDDEN)

    # Защищенные endpoints - требуют права суперпользователя
    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return Response({"error": "Требуются права суперпользователя"}, status=status.HTTP_403_FORBIDDEN)
        
        users = User.objects.all().order_by('-date_joined')
        serializer = UserDetailSerializer(users, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return Response({"error": "Требуются права суперпользователя"}, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return Response({"error": "Требуются права суперпользователя"}, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        serializer = UserUpdateSerializer(user, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Пользователь успешно обновлен",
                "user": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return Response({"error": "Требуются права суперпользователя"}, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Пользователь успешно обновлен",
                "user": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return Response({"error": "Требуются права суперпользователя"}, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        username = user.username
        
        if user.is_superuser:
            return Response({
                "error": "Нельзя удалить суперпользователя"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.delete()
        return Response({
            "message": f"Пользователь {username} успешно удален"
        }, status=status.HTTP_200_OK)

    # Регистрация пользователя (только для суперпользователей)
    @action(url_path="register", methods=["POST"], detail=False)
    def register(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return Response({"error": "Требуются права суперпользователя"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Пользователь успешно зарегистрирован",
                "user": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Импорт пользователей (только для суперпользователей)
    @action(url_path="import-users", methods=["POST"], detail=False)
    def import_users(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return Response({"error": "Требуются права суперпользователя"}, status=status.HTTP_403_FORBIDDEN)
        
        if 'excel_file' not in request.FILES:
            return Response({"error": "Файл не найден"}, status=status.HTTP_400_BAD_REQUEST)

        excel_file = request.FILES['excel_file']
        
        try:
            df = pd.read_excel(excel_file)
            
            required_columns = ['username', 'email', 'password']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return Response({
                    "error": f"Отсутствуют обязательные колонки: {', '.join(missing_columns)}"
                }, status=status.HTTP_400_BAD_REQUEST)

            created_users = []
            errors = []

            for index, row in df.iterrows():
                try:
                    user_data = {
                        'username': str(row['username']).strip(),
                        'email': str(row['email']).strip(),
                        'password': str(row['password']),
                        'password_confirm': str(row['password'])
                    }

                    if 'first_name' in df.columns and pd.notna(row['first_name']):
                        user_data['first_name'] = str(row['first_name']).strip()
                    if 'last_name' in df.columns and pd.notna(row['last_name']):
                        user_data['last_name'] = str(row['last_name']).strip()

                    serializer = UserRegistrationSerializer(data=user_data)
                    
                    if serializer.is_valid():
                        user = serializer.save()
                        created_users.append(user.username)
                    else:
                        errors.append(f"Строка {index + 2}: {serializer.errors}")

                except Exception as e:
                    errors.append(f"Строка {index + 2}: {str(e)}")

            result = {
                "total_created": len(created_users),
                "total_errors": len(errors),
                "created_users": created_users,
                "errors": errors
            }

            if errors:
                return Response(result, status=status.HTTP_207_MULTI_STATUS)
            else:
                return Response(result, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Ошибка при обработке файла: {str(e)}"}, 
                          status=status.HTTP_400_BAD_REQUEST)

    # Скачивание шаблона (доступно всем)
    @action(url_path="download-template", methods=["GET"], detail=False)
    def download_template(self, request, *args, **kwargs):
        template_data = {
            'username': ['example_user1', 'example_user2'],
            'email': ['user1@example.com', 'user2@example.com'],
            'password': ['password123', 'password456'],
            'first_name': ['Иван', 'Петр'],
            'last_name': ['Иванов', 'Петров']
        }
        
        df = pd.DataFrame(template_data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Шаблон', index=False)
        
        output.seek(0)
        
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="user_import_template.xlsx"'
        
        return response

    # Старый метод входа (оставляем для совместимости)
    @action(url_path="login", methods=["POST"], detail=False)
    def login(self, request, *args, **kwargs):
        username = request.data.get("user")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            serializer = UserSerializer(user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, **serializer.data})
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    @action(url_path="logout", methods=["POST"], detail=False)
    def logout(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # Удаляем токен аутентификации
            try:
                Token.objects.filter(user=request.user).delete()
            except Token.DoesNotExist:
                pass
            
            # Выход из системы Django
            logout(request)
            
            return Response({
                "message": "Успешный выход из системы"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": "Пользователь не был аутентифицирован"
            }, status=status.HTTP_200_OK)