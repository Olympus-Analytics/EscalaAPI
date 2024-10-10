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

from visualization import router as visualization_api_router
from visualization.views import NDVIView, LSTView

import sys
sys.path.insert(0, r"C:\Users\Sebastian\Desktop\Cuarto de Diseño\Trabajos en desarrollo\Olympus Analytics - Proyecto Empresa\Proyectos\Producto - ESCALA (Uninorte)\Programa\Escala-main\Escala")

api_url_patterns = [
    path(r'data/', include(visualization_api_router.router.urls)),
    path(r"download/raster/ndvi/<str:raster_id>/", NDVIView.as_view(), name="download_ndvi"),
    path(r"download/raster/lst/<str:raster_id>/", LSTView.as_view(), name="download_lst")
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_url_patterns))
]
