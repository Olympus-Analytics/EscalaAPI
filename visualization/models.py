from django.db import models
from django.contrib.gis.db import models as geo_models

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


# GEOGRAPHIC LAYERS

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
    COLHYP = models.CharField(max_length = 61)
    COLADDR = models.CharField(max_length = 53)
    POINT = geo_models.PointField()

class Neightborhood (models.Model):
    ID_NEIGHB = models.CharField(max_length = 11, primary_key=True)
    NAME = models.CharField(max_length = 50)
    LOCALITY = models.CharField(max_length = 50)
    POLY = geo_models.PolygonField()

class Locality_bar (models.Model):
    ID_LOCALITY = models.CharField(max_length = 11, primary_key=True)
    NAME = models.CharField(max_length = 50)
    POLY = geo_models.PolygonField()
    
class UPZ (models.Model):
    ID_UPZ = models.CharField(max_length = 10, primary_key=True)
    NAME = models.CharField(max_length = 50)
    POLY = geo_models.PolygonField()
    
class ZAT (models.Model):
    ID_ZAT = models.CharField(max_length = 10, primary_key=True)
    POLY = geo_models.PolygonField()

class UrbanPerimeter (models.Model):
    ID_URBPER = models.CharField(max_length = 10, primary_key=True)
    NAME = models.CharField(max_length = 50)
    POLY = geo_models.PolygonField()
    
class Municipality (models.Model):
    ID_MUN = models.CharField(max_length = 10, primary_key=True)
    NAME = models.CharField(max_length = 50)
    POLY = geo_models.PolygonField()
    
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