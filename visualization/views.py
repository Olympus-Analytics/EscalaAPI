from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from django.views import View
from django.urls import reverse
from django.templatetags.static import static
from django.shortcuts import render
from django.http import FileResponse, Http404
from rest_framework.views import APIView
import os, io
import zipfile
from osgeo import gdal

from .models import NDVI, LandSurfaceTemperature

# Create your views here.
class NDVIDownloadView (View):
    
    def get (self, request, raster_id, *args, **kwargs):
        try:
            raster = NDVI.objects.get(ID_NDVI=raster_id).RASTER
        except:
            return JsonResponse({"ERROR": "Raster not Found"})
        
        
        raster_buffer = raster.vsi_buffer
        
        response = HttpResponse(raster_buffer, content_type="image/tiff")
        response['Content-Disposition'] = f'inline; filename="{raster_id}.tif"'
        
        return response
    
class LSTDownloadView (View):
    
    def get (self, request, raster_id, *args, **kwargs):
        try:
            raster = LandSurfaceTemperature.objects.get(YEAR=raster_id).RASTER
        except:
            return JsonResponse({"ERROR": "Raster not Found"})
        
        print(raster.is_vsi_based)
        
        mem_driver = gdal.GetDriverByName('MEM')
        mem_dataset = mem_driver.Create('', raster.width, raster.height, len(raster.bands), gdal.GDT_Float32)
        mem_dataset.SetGeoTransform(raster.geotransform)
        mem_dataset.SetProjection(raster.ds.GetProjection()
                                  )

        # Copy raster data to in-memory dataset
        for band_idx in range(raster.count):
            band = raster.bands[band_idx]
            mem_band = mem_dataset.GetRasterBand(band_idx + 1)
            mem_band.WriteArray(band.read())

        # Save the in-memory raster as a GeoTIFF to a buffer
        buffer = io.BytesIO()
        gdal.GetDriverByName('GTiff').CreateCopy(buffer, mem_dataset)
        
        buffer.seek(0)
        binary_data = buffer.read()
        
        response = HttpResponse(binary_data, content_type="image/tiff")
        response['Content-Disposition'] = f'inline; filename="{raster_id}.tif"'
        
        return response
    
class LSTMetaDownload(APIView):
    
    def get(self, request, raster_year, *args, **kwargs):
        try:
            raster = LandSurfaceTemperature.objects.get(YEAR=raster_year).RASTER
        except LandSurfaceTemperature.DoesNotExist:
            return JsonResponse({"ERROR": "Raster not Found"})
        
        raster_buffer = raster.vsi_buffer
        
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<RasterMetadata>
    <RasterID>{raster_year}</RasterID>
    <Description>Metadata for Raster ID {raster_year}</Description>
</RasterMetadata>"""
        
        zip_buffer = io.BytesIO()
        
        print(raster_buffer)
        print(type(raster_buffer))
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f"{raster_year}.tif", raster_buffer)
            
            zip_file.writestr(f"{raster_year}.xml", xml_content)
            
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type="application/zip")
        response['Content-Disposition'] = f'attachment; filename="LST_{raster_year}.zip"'
        
        return response