from .models import TrafficCollision, Neightborhood, Locality_bar, UPZ, ZAT, UrbanPerimeter, Municipality, TreePlot, LandSurfaceTemperature, NDVI, Rainfall, AirTemperature

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.templatetags.static import static
            

# Colecciones de datos de [TrafficCollision]
class TrafficCollisionSerializer (GeoFeatureModelSerializer):
    
    class Meta:
        model = TrafficCollision
        geo_field = "POINT"
        fields = ['COLID', 'COLYEAR', 'COLMONTH', 'COLDAY', 'COLHOUR', 'COLMIN',
                  'COLZONE', 'COLAREA', 'COLVICNUM', 'COLSEV', 'COLTYP', 'COLOBJ',
                  'COLOBJTYP', 'COLHYP', 'COLADDR', 'POINT']

class TrafficCollisionPointSerializer (GeoFeatureModelSerializer):
    
    class Meta:
        model = TrafficCollision
        geo_field = "POINT"
        fields = ['COLID', 'POINT']

# Colecciones de datos de [Neightborhood]
class NeightborhoodSerializer (GeoFeatureModelSerializer):
    
    class Meta:
        model = Neightborhood
        geo_field = "POLY"
        fields = ['ID_NEIGHB', 'NAME', 'POLY', 'LOCALITY']

# Colecciones de datos de [Locality_bar]
class Locality_barSerializer (GeoFeatureModelSerializer):
    
    class Meta:
        model = Locality_bar
        geo_field = "POLY"
        fields = ['ID_LOCALITY', 'NAME', 'POLY']

# Colecciones de datos de [UPZ]
class UPZSerializer (GeoFeatureModelSerializer):
    
    class Meta:
        model = UPZ
        geo_field = "POLY"
        fields = ['ID_UPZ', 'NAME', 'POLY']

# Colecciones de datos de [ZAT]
class ZATSerializer (GeoFeatureModelSerializer):
    chart = 'map'
    
    class Meta:
        model = ZAT
        geo_field = "POLY"
        fields = ['ID_ZAT', 'POLY']

# Colecciones de datos de [UrbanPerimeter]
class UrbanPerimeterSerializer (GeoFeatureModelSerializer):
    
    class Meta:
        model = UrbanPerimeter
        geo_field = "POLY"
        fields = ['ID_URBPER', 'NAME', 'POLY']

# Colecciones de datos de [Municipality]
class MunicipalitySerializer (GeoFeatureModelSerializer):
    
    class Meta:
        model = Municipality
        geo_field = "POLY"
        fields = ['ID_MUN', 'NAME', 'POLY']
        
class MunicipalityNameSerializer (serializers.ModelSerializer):
    
    class Meta:
        model = Municipality
        fields = ['ID_MUN', 'NAME']
        
# Colecciones de datos de [TreePlot]
class TreePlotSerializer (GeoFeatureModelSerializer):
    
    class Meta:
        model = TreePlot
        geo_field = "POINT"
        fields = ['IDPLOT', 'TPAREA', 'TPABUND', 'TPSP', 'TPDBH', 'TPHEIG',
                  'TPBAS', 'TPCAREA', 'TPCAPLOT', 'TPCCV', 'POINT']

class TreePlotPointSerializer (GeoFeatureModelSerializer):
    
    class Meta:
        model = TreePlot
        geo_field = "POINT"
        fields = ['IDPLOT', 'POINT']

# Colecciones de datos de [AirTemperature]
class AirTemperatureSerializer (serializers.ModelSerializer):
    
    class Meta:
        model = AirTemperature
        geo_field = "RASTER"
        fields = ['YEAR', 'MONTH', 'DAY', 'RASTER']

# Colecciones de datos de [Rainfall]
class RainfallSerializer (serializers.ModelSerializer):
    
    class Meta:
        model = Rainfall
        geo_field = "RASTER"
        fields = ['YEAR', 'MONTH', 'DAY', 'RASTER']

# Colecciones de datos de [LandSurfaceTemperature]
class LandSurfaceTemperatureSerializer (serializers.ModelSerializer):
    RASTER_URL = serializers.SerializerMethodField()
    RASTER_AUX = serializers.SerializerMethodField()
    RASTER_LEGEND = serializers.SerializerMethodField()
    
    class Meta:
        model = LandSurfaceTemperature
        geo_field = "RASTER"
        fields = ['YEAR', 'RASTER_URL', 'RASTER_AUX', 'RASTER_LEGEND']
    
    def get_RASTER_URL(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(static(f'LST_bar/PNG/{obj.ID_LST}.png'))
    
    def get_RASTER_AUX(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(static(f'LST_bar/PNG/{obj.ID_LST}.png.aux.xml'))
    
    def get_RASTER_LEGEND(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(static(f'LST_bar/legend.png'))


# Colecciones de datos de [NDVI]
class NDVISerializer (serializers.ModelSerializer):
    RASTER_URL = serializers.SerializerMethodField()
    RASTER_AUX = serializers.SerializerMethodField()
    RASTER_LEGEND = serializers.SerializerMethodField()
    
    class Meta:
        model = NDVI
        geo_field = "RASTER"
        fields = ['YEAR', 'RASTER_URL', 'RASTER_AUX', 'RASTER_LEGEND']
        
    def get_RASTER_URL(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(static(f'NDVI_bar/PNG/{obj.ID_NDVI}.png'))
    
    def get_RASTER_AUX(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(static(f'NDVI_bar/PNG/{obj.ID_NDVI}.png.aux.xml'))
    
    def get_RASTER_LEGEND(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(static(f'NDVI_bar/legend.png'))


class NDVITestSerializer (serializers.ModelSerializer):
    RASTER_URL = serializers.SerializerMethodField()
    RASTER_AUX = serializers.SerializerMethodField()
    
    class Meta:
        model = NDVI
        geo_field = "RASTER"
        fields = ['YEAR', 'RASTER_URL', 'RASTER_AUX']
        
    def get_RASTER_URL(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(static(f'NDVI_bar/{obj.ID_NDVI}.tif'))
    
    def get_RASTER_AUX(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(static(f'NDVI_bar/PNG/{obj.ID_NDVI}.png.aux.xml'))
                

# Colecciones de datos de [LandSurfaceTemperature]
class LSTDownloadSerializer (serializers.ModelSerializer):
    RASTER_URL = serializers.SerializerMethodField()
    
    class Meta:
        model = LandSurfaceTemperature
        geo_field = "RASTER"
        fields = ['YEAR', 'RASTER_URL']
    
    def get_RASTER_URL(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(reverse("download_lst", args=[obj.ID_LST.replace(".tif", ".png")]))
        else:
            return request.build_absolute_uri("")
    
    

class NDVIDownloadSerializer (serializers.ModelSerializer):
    RASTER_URL = serializers.SerializerMethodField()
    
    class Meta:
        model = NDVI
        geo_field = "RASTER"
        fields = ['YEAR', 'RASTER_URL']
        
    def get_RASTER_URL(self, obj):
        request = self.context.get('request')
        if request:
            print(obj.ID_NDVI)
            return request.build_absolute_uri(reverse("download_ndvi", args=[obj.ID_NDVI.replace(".tif", ".png")]))
        else:
            return request.build_absolute_uri("")
        
    
        
        
'''
class Serializer (serializers.ModelSerializer):
    
    class Meta:
        model = 
        fields = []
'''



