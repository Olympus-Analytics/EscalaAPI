"""
URL configuration for escala_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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

from django.conf.urls.static import static 
from django.conf import settings 

from visualization import router as visualization_api_router
from visualization.views import DownloadFilesView, AUXFilesView

import sys
sys.path.insert(0, r"C:\Users\Sebastian\Desktop\Cuarto de Diseño\Trabajos en desarrollo\Olympus Analytics - Proyecto Empresa\Proyectos\Producto - ESCALA (Uninorte)\Programa\Escala-main\Escala")

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@local.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

api_url_patterns = [
    path(r'data/', include(visualization_api_router.router.urls)),
    path(r"download/", DownloadFilesView.as_view(), name="download_files"),
    path(r"raster/", AUXFilesView.as_view(), name="raster_aux_files"),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_url_patterns)),
    path('documentation/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
