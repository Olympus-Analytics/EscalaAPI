from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from django.views import View
from django.templatetags.static import static
from django.shortcuts import render

from .models import NDVI, LandSurfaceTemperature

# Create your views here.
class NDVIDownloadView (View):
    
    def get (self, request, raster_id, *args, **kwargs):
        try:
            raster = NDVI.objects.get(ID_NDVI=raster_id).RASTER
        except:
            return JsonResponse({"ERROR": "Raster not Found"})
        
        print(raster)
        
        raster_buffer = raster.vsi_buffer
        
        response = HttpResponse(raster_buffer, content_type="image/tiff")
        response['Content-Disposition'] = f'inline; filename="{raster_id}.tif"'
        
        return response
    
class LSTDownloadView (View):
    
    def get (self, request, raster_id, *args, **kwargs):
        try:
            raster = LandSurfaceTemperature.objects.get(ID_LST=raster_id).RASTER
        except:
            return JsonResponse({"ERROR": "Raster not Found"})
        
        print(raster)
        
        raster_buffer = raster.vsi_buffer
        
        response = HttpResponse(raster_buffer, content_type="image/tiff")
        response['Content-Disposition'] = f'inline; filename="{raster_id}.tif"'
        
        return response