import geopandas as gpd
import pandas as pd

import sys, os
sys.path.insert(0, r"C:\Users\Sebastian\Desktop\Cuarto de Diseño\Trabajos en desarrollo\Olympus Analytics - Proyecto Empresa\Proyectos\Producto - ESCALA (Uninorte)\Programa\Escala-main\Escala")

from visualization.models import Homicides, TrafficCollision, Locality_bar, Neightborhood, Municipality, UrbanPerimeter, TreePlot, NDVI
from shapely.geometry.multipolygon import MultiPolygon
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.gdal.raster.source import GDALRaster

def read_locality_bar ():
    locality_bar = gpd.read_file(r"BaseDatos\Archivos\Shape_GEOGRAPHIC LAYERS\Locality_bar\Locality_bar.shp")
    for i in locality_bar.index:
        if isinstance(locality_bar.iloc[i]['geometry'], MultiPolygon):
            geometry = locality_bar.iloc[i]['geometry']
        else:
            geometry = MultiPolygon([locality_bar.iloc[i]['geometry']])
        geometry = GEOSGeometry(f"{geometry}")
        
        Locality_bar.objects.create(
        ID_LOCALITY = locality_bar.iloc[i]['ID_LOCALIT'],
        NAME = locality_bar.iloc[i]['NAME'],
        POLY = geometry
        )
        print(f"Localidad {locality_bar.iloc[i]['NAME']} fue ingresada a la Base de Datos")
        
def read_municipality_bar ():
    municipality_bar = gpd.read_file(r"BaseDatos\Archivos\Shape_GEOGRAPHIC LAYERS\Municipality_bar\Municipality_bar.shp")
    
    try:
        for i in municipality_bar.index:
            if isinstance(municipality_bar.iloc[i]['geometry'], MultiPolygon):
                    geometry = municipality_bar.iloc[i]['geometry']
            else:
                    geometry = MultiPolygon([municipality_bar.iloc[i]['geometry']])
            geometry = GEOSGeometry(f"{geometry}")
            
            Municipality.objects.create(
            ID_MUN = municipality_bar.iloc[i]['ID_MUN'],
            NAME = municipality_bar.iloc[i]['NAME'],
            POLY = geometry
        )
        print(f"Municipio {municipality_bar.iloc[i]['NAME']} fue ingresado a la Base de Datos")
    except Exception as e:
        print(e)

def read_neighborhood_bar ():
    neighborhood_bar = gpd.read_file(r"BaseDatos\Archivos\Shape_GEOGRAPHIC LAYERS\Neighborhood_bar\Neighborhood_bar.shp")
    for i in neighborhood_bar.index:
        if isinstance(neighborhood_bar.iloc[i]['geometry'], MultiPolygon):
            geometry = neighborhood_bar.iloc[i]['geometry']
        else:
            geometry = MultiPolygon([neighborhood_bar.iloc[i]['geometry']])
        geometry = GEOSGeometry(f"{geometry}")
        
        try:
            Neightborhood.objects.create(
                ID_NEIGHB = neighborhood_bar.iloc[i]['ID_NEIGHB'],
                NAME = neighborhood_bar.iloc[i]['NAME'],
                LOCALITY = Locality_bar.objects.get(NAME=neighborhood_bar.iloc[i]['LOCALITY']),
                POLY = geometry
            )
            print(f"Barrio {neighborhood_bar.iloc[i]['NAME']} fue ingresada a la Base de Datos")
        except Exception as e:
            print(e)

def read_tree_plot_bar ():
    tree_plot_bar = gpd.read_file(r"BaseDatos\Archivos\Shape_GEOGRAPHIC LAYERS\Tree plot_bar\Tree plot_bar.shp")
    
    for i in tree_plot_bar.index:
        try:
            geometry = GEOSGeometry(f"{tree_plot_bar.iloc[i]['geometry']}")
            
            TreePlot.objects.create(
                IDPLOT = tree_plot_bar.iloc[i]['IDPLOT'],
                TPAREA = tree_plot_bar.iloc[i]['TPAREA'],
                TPABUND = tree_plot_bar.iloc[i]['TPABUND'],
                TPSP = tree_plot_bar.iloc[i]['TPSP'],
                TPDBH = tree_plot_bar.iloc[i]['TPDBH'],
                TPHEIG = tree_plot_bar.iloc[i]['TPHEIG'],
                TPBAS = tree_plot_bar.iloc[i]['TPBAS'],
                TPCAREA = tree_plot_bar.iloc[i]['TPCAREA'],
                TPCAPLOT = tree_plot_bar.iloc[i]['TPCAPLOT'],
                TPCCV = tree_plot_bar.iloc[i]['TPCCV'],
                POINT = geometry
            )
            print(f"TreePlot Nº {i} fue ingresada a la Base de Datos")
        except Exception as e:
            print(e)

def read_urban_perimeter_bar ():
    urban_perimeter_bar = gpd.read_file(r"BaseDatos\Archivos\Shape_GEOGRAPHIC LAYERS\Urban_Perimeter_bar\Urban_Perimeter_bar.shp")
    try:
        for i in urban_perimeter_bar.index:
            if isinstance(urban_perimeter_bar.iloc[i]['geometry'], MultiPolygon):
                    geometry = urban_perimeter_bar.iloc[i]['geometry']
            else:
                    geometry = MultiPolygon([urban_perimeter_bar.iloc[i]['geometry']])
            geometry = GEOSGeometry(f"{geometry}")
            
            UrbanPerimeter.objects.create(
            ID_URBPER = urban_perimeter_bar.iloc[i]['ID_URBPER'],
            NAME = urban_perimeter_bar.iloc[i]['NAME'],
            POLY = geometry
        )
        print(f"Perímetro Urbano {urban_perimeter_bar.iloc[i]['NAME']} fue ingresado a la Base de Datos")
    except Exception as e:
        print(e)

def read_homicides ():
    homicides = pd.read_csv("BaseDatos\Archivos\Homicides_Values.csv", delimiter=";")

    for i in homicides.index:
        try:
            Homicides.objects.create(
                HOMYEAR = homicides.iloc[i]['HOMYEAR'],
                HOMMONTH = homicides.iloc[i]['HOMMONTH'],
                HOMDAY = homicides.iloc[i]['HOMDAY'],
                HOMDAYWEEK = homicides.iloc[i]['HOMDAYWEEK'],
                HOMHOUR = homicides.iloc[i]['HOMHOUR'],
                HOMMIN = homicides.iloc[i]['HOMMIN'],
                HOMAREA = homicides.iloc[i]['HOMAREA'],
                HOMSITE = homicides.iloc[i]['HOMSITE'],
                HOMWPN = homicides.iloc[i]['HOMWPN'],
                HOMASLT = homicides.iloc[i]['HOMASLT'],
                HOMVICT = homicides.iloc[i]['HOMVICT'],
                HOMVICAGE = homicides.iloc[i]['HOMVICAGE'],
                HOMVICSEX = homicides.iloc[i]['HOMVICSEX'],
                HOMVICMS = homicides.iloc[i]['HOMVICMS'],
                HOMVICCB = homicides.iloc[i]['HOMVICCB'],
                HOMVICES = homicides.iloc[i]['HOMVICES'],
                HOMVICPRO = homicides.iloc[i]['HOMVICPRO'],
                HOMVICEL = homicides.iloc[i]['HOMVICEL'],
                
                ID_NEIGHB = Neightborhood.objects.get(ID_NEIGHB=homicides.iloc[i]['ID_NEIGHB'])
            )
            
            print(f"Homicidio Nº {i} fue ingresado a la Base de Datos")
        except Exception as e:
            print(e)
    
def read_traffic_collisions ():
    traffic_collisions = gpd.read_file(r"BaseDatos\Archivos\ROAD TRAFFIC COLLISIONS\TrafficCollision.shp")
    
    for i in traffic_collisions.index:
        geometry = GEOSGeometry(f"{traffic_collisions.iloc[i]['geometry']}")
        
        try:
            TrafficCollision.objects.create(
                COLID = traffic_collisions.iloc[i]['COLID'],
                COLYEAR = traffic_collisions.iloc[i]['COLYEAR'],
                COLMONTH = traffic_collisions.iloc[i]['COLMONTH'],
                COLDAY = traffic_collisions.iloc[i]['COLDAY'],
                COLHOUR = traffic_collisions.iloc[i]['COLHOUR'],
                COLMIN = traffic_collisions.iloc[i]['COLMIN'],
                COLZONE = traffic_collisions.iloc[i]['COLZONE'],
                COLAREA = traffic_collisions.iloc[i]['COLAREA'],
                COLVICNUM = traffic_collisions.iloc[i]['COLVICNUM'],
                COLSEV = traffic_collisions.iloc[i]['COLSEV'],
                COLTYP = traffic_collisions.iloc[i]['COLTYP'],
                COLOBJ = traffic_collisions.iloc[i]['COLOBJ'],
                COLOBJTYP = traffic_collisions.iloc[i]['COLOBJTYP'],
                COLHYP = traffic_collisions.iloc[i]['COLHYP'],
                COLADDR = traffic_collisions.iloc[i]['COLADDR'],
                POINT = geometry
            )
            print(f"Barrio {traffic_collisions.iloc[i]['COLID']} fue ingresada a la Base de Datos")
        except Exception as e:
            print(len(traffic_collisions.iloc[i]['COLHYP']))
            print(e)
    
def read_weather_stations ():
    pass

def read_weather_data ():
    pass

def read_rasters ():
    direccion = r"BaseDatos\Archivos\Raster_LST_NDVI\NDVI_bar"
    lista_lst = os.listdir(direccion)
    
    for raster in lista_lst:
        try:
            print(raster)
            nombre, formato = raster.split(".")
            fecha = nombre.split("_")[4]
            landsat = int(nombre.split("_")[3][3:5])
            geometries = GDALRaster(f"{direccion}\{raster}", write=True)
            print(geometries.bands)
            
            NDVI.objects.create(
                ID_NDVI = nombre,
                YEAR = fecha[0:4],
                MONTH = fecha[4:6],
                DAY = fecha[6:8],
                LANDSAT = landsat,
                RASTER = geometries
            )
            
            print(f"Raster {raster} cargado exitosamente a la Base de Datos")
        except Exception as e:
            print(e)
    
    
    
    print()


def run ():
    
    #read_neighborhood_bar()
    #read_homicides()
    #read_tree_plot_bar()
    #read_traffic_collisions ()
    #read_rasters()
    
    print("EJECUTANDO PROGRAMA") 