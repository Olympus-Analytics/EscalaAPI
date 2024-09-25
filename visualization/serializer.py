from .models import Homicides, TrafficCollision, Neightborhood, Locality_bar, UPZ, ZAT, UrbanPerimeter, Municipality, TreePlot, LandSurfaceTemperature, NDVI, Rainfall, AirTemperature, AirTempWS, RainfallWS, RelHumidityWS, WeatherStation

from rest_framework import serializers
            
# Colecciones de datos de [Homicides]     
class HomicidesSerializer (serializers.ModelSerializer):
    
    class Meta:
        model = Homicides
        fields = ['HOMYEAR', 'HOMMONTH', 'HOMDAY', 'HOMDAYWEEK', 'HOMHOUR',
                  'HOMMIN', 'HOMAREA', 'HOMSITE', 'HOMWPN', 'HOMASLT',
                  'HOMVICT', 'HOMVICAGE', 'HOMVICSEX', 'HOMVICMS',
                  'HOMVICCB', 'HOMVICES', 'HOMVICPRO', 'HOMVICEL',
                  'ID_NEIGHB']
        
class HomicidesDateSerializer (serializers.ModelSerializer):
    
    class Meta:
        model = Homicides
        fields = ['HOMYEAR', 'HOMMONTH', 'HOMDAY', 'HOMDAYWEEK', 'HOMHOUR',
                  'HOMMIN', 'ID_NEIGHB']

# Colecciones de datos de [TrafficCollision]
class TrafficCollisionSerializer (serializers.ModelSerializer):
    
    class Meta:
        model = TrafficCollision
        fields = ['COLID', 'COLYEAR', 'COLMONTH', 'COLDAY', 'COLHOUR', 'COLMIN',
                  'COLZONE', 'COLAREA', 'COLVICNUM', 'COLSEV', 'COLTYP', 'COLOBJ',
                  'COLOBJTYP', 'COLHYP', 'COLADDR', 'POINT']

class TrafficCollisionDateSerializer (serializers.ModelSerializer):    
    class Meta:
        model = TrafficCollision
        fields = ['COLID', 'COLYEAR', 'COLMONTH', 'COLDAY', 'COLHOUR', 'chart']
        
class TrafficCollisionVictimsNumberSerializer (serializers.ModelSerializer):    
    class Meta:
        model = TrafficCollision
        fields = ['COLID', 'COLYEAR', 'COLMONTH', 'COLVICNUM']
        
class TrafficCollisionPlaceSerializer (serializers.ModelSerializer):   
    class Meta:
        model = TrafficCollision
        fields = ['COLID', 'COLZONE', 'COLAREA', 'POINT']
        
class TrafficCollisionSeveritySerializer (serializers.ModelSerializer):
    class Meta:
        model = TrafficCollision
        fields = ['COLID', 'COLSEV']
        
class TrafficCollisionRoadSerializer (serializers.ModelSerializer):    
    class Meta:
        model = TrafficCollision
        fields = ['COLID', 'COLTYP']
        
class TrafficCollisionObjectSerializer (serializers.ModelSerializer):
    
    class Meta:
        model = TrafficCollision
        fields = ['COLID', 'COLOBJ', 'COLOBJTYP']

# Colecciones de datos de [Neightborhood]
class NeightborhoodSerializer (serializers.ModelSerializer):
    chart = 'map'
    
    class Meta:
        model = Neightborhood
        fields = ['ID_NEIGHB', 'NAME', 'POLY', 'LOCALITY']

# Colecciones de datos de [Locality_bar]
class Locality_barSerializer (serializers.ModelSerializer):
    chart = 'map'
    
    class Meta:
        model = Locality_bar
        fields = ['ID_LOCALITY', 'NAME', 'POLY']

# Colecciones de datos de [UPZ]
class UPZSerializer (serializers.ModelSerializer):
    chart = 'map'
    
    class Meta:
        model = UPZ
        fields = ['ID_UPZ', 'NAME', 'POLY']

# Colecciones de datos de [ZAT]
class ZATSerializer (serializers.ModelSerializer):
    chart = 'map'
    
    class Meta:
        model = ZAT
        fields = ['ID_ZAT', 'POLY']

# Colecciones de datos de [UrbanPerimeter]
class UrbanPerimeterSerializer (serializers.ModelSerializer):
    chart = 'map'
    
    class Meta:
        model = UrbanPerimeter
        fields = ['ID_URBPER', 'NAME', 'POLY']

# Colecciones de datos de [Municipality]
class MunicipalitySerializer (serializers.ModelSerializer):
    chart = 'map'
    
    class Meta:
        model = Municipality
        fields = ['ID_MUN', 'NAME', 'POLY']
        
class MunicipalityNameSerializer (serializers.ModelSerializer):
    chart = 'map'
    
    class Meta:
        model = Municipality
        fields = ['ID_MUN', 'NAME']
        
# Colecciones de datos de [TreePlot]
class TreePlotSerializer (serializers.ModelSerializer):
    
    class Meta:
        model = TreePlot
        fields = ['IDPLOT', 'TPAREA', 'TPABUND', 'TPSP', 'TPDBH', 'TPHEIG',
                  'TPBAS', 'TPCAREA', 'TPCAPLOT', 'TPCCV', 'POINT']

class TreePlotPointSerializer (serializers.ModelSerializer):
    chart = ['map']
    
    class Meta:
        model = TreePlot
        fields = ['IDPLOT', 'POINT']
       
class TreePlotAreaSerializer (serializers.ModelSerializer):
    chart = ['bar']
    
    class Meta:
        model = TreePlot
        fields = ['IDPLOT', 'TPAREA']

class TreePlotRecordsSerializer (serializers.ModelSerializer):
    chart = ['bar']
    
    class Meta:
        model = TreePlot
        fields = ['IDPLOT', 'TPABUND', 'TPSP']
        
class TreePlotDiameterSerializer (serializers.ModelSerializer):
    chart = ['bar']
    
    class Meta:
        model = TreePlot
        fields = ['IDPLOT', 'TPDBH']
        
class TreePlotHeightSerializer (serializers.ModelSerializer):
    chart = ['bar']
    
    class Meta:
        model = TreePlot
        fields = ['IDPLOT', 'TPHEIG']

class TreePlotBasalSerializer (serializers.ModelSerializer):
    chart = ['bar']
    
    class Meta:
        model = TreePlot
        fields = ['IDPLOT', 'TPBAS']
        
class TreePlotCanopySerializer (serializers.ModelSerializer):
    chart = ['bar']
    
    class Meta:
        model = TreePlot
        fields = ['IDPLOT', 'TPCAREA', 'TPCAPLOT', 'TPCCV']

# Colecciones de datos de [AirTemperature]
class AirTemperatureSerializer (serializers.ModelSerializer):
    chart = ['raster']
    
    class Meta:
        model = AirTemperature
        fields = ['YEAR', 'MONTH', 'DAY', 'RASTER']

# Colecciones de datos de [Rainfall]
class RainfallSerializer (serializers.ModelSerializer):
    chart = ['raster']
    
    class Meta:
        model = Rainfall
        fields = ['YEAR', 'MONTH', 'DAY', 'RASTER']

# Colecciones de datos de [LandSurfaceTemperature]
class LandSurfaceTemperatureSerializer (serializers.ModelSerializer):
    chart = ['raster']
    
    class Meta:
        model = LandSurfaceTemperature
        fields = ['YEAR', 'MONTH', 'DAY', 'LANDSAT', 'RASTER']

# Colecciones de datos de [NDVI]
class NDVISerializer (serializers.ModelSerializer):
    chart = ['raster']
    
    class Meta:
        model = NDVI
        fields = ['YEAR', 'MONTH', 'DAY', 'LANDSAT', 'RASTER']
        
        
        
'''
class Serializer (serializers.ModelSerializer):
    
    class Meta:
        model = 
        fields = []
'''



