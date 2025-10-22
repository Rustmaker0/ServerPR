"""
URL configuration for RoadData project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse  # Добавьте этот импорт
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from Data.api import *

def home_view(request):
    return HttpResponse("Добро пожаловать в RoadData API!")

router = DefaultRouter()
router.register(r'measurings', MeasuringViewset)
router.register(r'transports', TransportViewset)
router.register(r'intensivitys', IntensivityViewset)
router.register(r'publicTransports', PublicTransportViewset)
router.register(r'publicTransportsNumbers', PublicTransportNumberViewset)
router.register(r'peoplesInPublicsTransport', PeopleInPublicTransportViewset)
router.register(r'user', UserViewset, basename='users')

urlpatterns = [
    path('', home_view, name='home'),  # Обработчик для корневого URL
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)