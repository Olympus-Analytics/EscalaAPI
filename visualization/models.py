from django.db import models
from django.contrib.gis.db import models as geo_models
from django.contrib.gis import geos

# TABLES

class Homicides (models.Model):
    HOMYEAR = models.IntegerField() 
    HOMMONTH = models.IntegerField() 
    HOMDAY = models.IntegerField() 
    HOMDAYWEEK = models.IntegerField() 
    HOMHOUR = models.IntegerField() 
    HOMMIN = models.IntegerField() 
    HOMAREA = models.IntegerField() 
    HOMSITE = models.IntegerField() 
    HOMWPN = models.IntegerField() 
    HOMASLT = models.IntegerField() 
    HOMVICT = models.IntegerField() 
    HOMVICAGE = models.IntegerField() 
    HOMVICSEX = models.IntegerField() 
    HOMVICMS = models.IntegerField() 
    HOMVICCB = models.IntegerField() 
    HOMVICES = models.IntegerField() 
    HOMVICPRO = models.IntegerField() 
    HOMVICEL = models.IntegerField() 
    
    ID_NEIGHB = models.ForeignKey(
        "Neightborhood", on_delete=models.CASCADE)


class AirTempWS (models.Model):
    TEMP_MEAN = models.FloatField()
    TEMP_MAX = models.FloatField()
    TEMP_MIN = models.FloatField()
    
    ID_ST = models.ForeignKey(
        "WeatherStation", on_delete=models.CASCADE)

class RainfallWS (models.Model):
    RAIN = models.FloatField()
    
    ID_ST = models.ForeignKey(
        "WeatherStation", on_delete=models.CASCADE)

class RelHumidityWS (models.Model):
    RH_MEAN = models.FloatField()
    RH_MAX = models.FloatField()
    RH_MIN = models.FloatField()
    
    ID_ST = models.ForeignKey(
        "WeatherStation", on_delete=models.CASCADE)

# GEOGRAPHIC LAYERS

class WeatherStation (models.Model):
    ID_ST =models.CharField(max_length = 10, primary_key=True)
    NAME = models.CharField(max_length = 50)
    POINT = geo_models.PointField()

class TrafficCollision (models.Model):
    COLID = models.IntegerField(primary_key=True)
    COLYEAR = models.IntegerField() 
    COLMONTH = models.IntegerField() 
    COLDAY = models.IntegerField() 
    COLHOUR = models.IntegerField()
    COLMIN = models.IntegerField() 
    COLZONE = models.IntegerField() 
    COLAREA = models.IntegerField() 
    COLVICNUM = models.IntegerField() 
    COLSEV = models.IntegerField() 
    COLTYP = models.IntegerField() 
    COLOBJ = models.IntegerField() 
    COLOBJTYP = models.IntegerField() 
    COLHYP = models.CharField(max_length = 250)
    COLADDR = models.CharField(max_length = 53)
    POINT = geo_models.PointField()
    
    # Conectar al ID del Barrio o zona geográfica del accidente

class Neightborhood (models.Model):
    ID_NEIGHB = models.CharField(max_length = 11, primary_key=True)
    NAME = models.CharField(max_length = 50)
    POLY = geo_models.MultiPolygonField()
    
    LOCALITY = models.ForeignKey(
        "Locality_bar", on_delete=models.CASCADE)

class Locality_bar (models.Model):
    ID_LOCALITY = models.CharField(max_length = 11, primary_key=True)
    NAME = models.CharField(max_length = 50)
    POLY = geo_models.MultiPolygonField()
    
    # Conectar al ID del [Municipality]
    
class UPZ (models.Model):
    ID_UPZ = models.CharField(max_length = 10, primary_key=True)
    NAME = models.CharField(max_length = 50)
    POLY = geo_models.MultiPolygonField()
    
class ZAT (models.Model):
    ID_ZAT = models.CharField(max_length = 10, primary_key=True)
    POLY = geo_models.MultiPolygonField()

class UrbanPerimeter (models.Model):
    ID_URBPER = models.CharField(max_length = 10, primary_key=True)
    NAME = models.CharField(max_length = 50)
    POLY = geo_models.MultiPolygonField()
    
class Municipality (models.Model):
    ID_MUN = models.CharField(max_length = 10, primary_key=True)
    NAME = models.CharField(max_length = 50)
    POLY = geo_models.MultiPolygonField(dim=3)
    
class TreePlot (models.Model):
    IDPLOT = models.CharField(max_length = 5, primary_key=True)
    TPAREA = models.FloatField()
    TPABUND = models.FloatField()
    TPSP = models.FloatField()
    TPDBH = models.FloatField()
    TPHEIG = models.FloatField()
    TPBAS = models.FloatField()
    TPCAREA = models.FloatField()
    TPCAPLOT = models.FloatField()
    TPCCV = models.FloatField()
    POINT = geo_models.PointField(null=True)
    

# RASTERS

class AirTemperature (models.Model):
    YEAR = models.IntegerField()
    MONTH = models.IntegerField()
    DAY = models.IntegerField()
    RASTER = geo_models.RasterField()
    
class Rainfall (models.Model):
    YEAR = models.IntegerField()
    MONTH = models.IntegerField()
    DAY = models.IntegerField()
    RASTER = geo_models.RasterField()
    
class LandSurfaceTemperature (models.Model):
    ID_LST =models.CharField(max_length = 35, primary_key=True)
    YEAR = models.IntegerField(null=True)
    MONTH = models.IntegerField(null=True)
    DAY = models.IntegerField(null=True)
    LANDSAT = models.IntegerField(null=True)
    RASTER = geo_models.RasterField(null=False)
    
class NDVI (models.Model):
    ID_NDVI =models.CharField(max_length = 35, primary_key=True)
    YEAR = models.IntegerField(null=True)
    MONTH = models.IntegerField(null=True)
    DAY = models.IntegerField(null=True)
    LANDSAT = models.IntegerField(null=True)
    RASTER = geo_models.RasterField(null=False)