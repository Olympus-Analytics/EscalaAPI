from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from django.views import View
from django.urls import reverse
from django.templatetags.static import static
from django.shortcuts import render
from django.http import FileResponse, Http404
from rest_framework.views import APIView
import os, io, csv
import zipfile
from osgeo import gdal


from .models import NDVI, LandSurfaceTemperature, TrafficCollision, TreePlot

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
    
class DownloadFilesView(APIView):
    def get(self, request, *args, **kwargs):
        # Extract filters from query params
        include_treeplot = request.query_params.get('treeplot', 'false').lower() == 'true'
        include_traffic = request.query_params.get('traffic_collisions', 'false').lower() == 'true'
        ndvi_year = request.query_params.get('ndvi_year')
        lst_year = request.query_params.get('lst_year')
        files_to_zip = []

       
        if include_treeplot:
            treeplot_path = ("TreePlot.zip", static('TreePlot.zip'))
            files_to_zip.append(treeplot_path)
            meta = ("TreePlot_metadata.xlsx", static("metadata/TreePlot.xlsx"))
            files_to_zip.append(meta)

        if include_traffic:
            traffic_path = ("TrafficCollisions.csv", static('TrafficCollisions.zip'))
            files_to_zip.append(traffic_path)
            meta = ("TrafficCollision_metadata.xlsx", static("metadata/TrafficCollision.xlsx"))
            files_to_zip.append(meta)

        if ndvi_year:
            ndvi_path = (f"NDVIbar_{ndvi_year}__mean.tif", static(f'NDVI_bar/NDVIbar_{ndvi_year}__mean.tif'))
            files_to_zip.append(ndvi_path)
            meta = ("NDVIbar_metadata.xlsx", static("metadata/NDVIbar.xlsx"))
            files_to_zip.append(meta)

        if lst_year:
            LST_path = (f"LSTbar_{lst_year}__mean.tif", static(f'LST_bar/LSTbar_{lst_year}__mean.tif'))
            files_to_zip.append(LST_path)
            meta = ("LSTbar_metadata.xlsx", static("metadata/LSTbar.xlsx"))
            files_to_zip.append(meta)

        # Ensure there are files to zip
        if not files_to_zip:
            return HttpResponse("No files selected for download.", status=400)
        else:
            locality_meta = ("Locality_metadata.xlsx", static("metadata/Locality.xlsx"))
            neighborhood_meta = ("Neighborhood_metadata.xlsx", static("metadata/Neighborhood.xlsx"))
            files_to_zip.append(locality_meta)
            files_to_zip.append(neighborhood_meta)

        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="datasets.zip"'

        with zipfile.ZipFile(response, 'w') as zip_file:
            for file_name, file_path in files_to_zip:
                local_path = os.getcwd() + file_path.replace(request.build_absolute_uri('/'), '')
                try:
                    zip_file.write(local_path, arcname=file_name)
                except:
                    return HttpResponse(f"File not found: {file_name}", status=404)

        return response