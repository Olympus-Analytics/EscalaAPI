from rest_framework.response import Response
from django.db.models import Sum, Count, Max, Min

from rest_framework import viewsets
import re, math
import numpy as np

from django.contrib.gis.gdal.raster.source import GDALRaster

from .models import TrafficCollision, Neightborhood, Locality_bar, UPZ, ZAT, UrbanPerimeter, Municipality, TreePlot, AirTemperature, Rainfall, LandSurfaceTemperature, NDVI
from .serializer import TrafficCollisionSerializer, TrafficCollisionPointSerializer
from .serializer import TreePlotSerializer, TreePlotPointSerializer
from .serializer import AirTemperatureSerializer, RainfallSerializer, LandSurfaceTemperatureSerializer, NDVISerializer, NDVITestSerializer
from .serializer import TrafficCollisionSerializer, NeightborhoodSerializer, Locality_barSerializer, UPZSerializer, ZATSerializer, UrbanPerimeterSerializer, MunicipalitySerializer, TreePlotSerializer, AirTemperatureSerializer, RainfallSerializer, LandSurfaceTemperatureSerializer, NDVISerializer

#Chart Domains
BAR = 'bar'
LINE = 'line'
PIE = 'pie'
DOUGHNUT = 'doughnut'

# Time Filters List
YEARS = "YY"
MONTHS = "MM"
DAYS = "DD"
HOURS = "HH"

# Spatial Filters List
MUNICIPALITY = "municipality"
LOCALITY = "locality"
NEIGHTBORHOOD = "neighborhood"

# Time vs Spatial Filters List
MUNBYYEAR = f"{MUNICIPALITY}_{YEARS}"
MUNBYMONTH = f"{MUNICIPALITY}_{MONTHS}"
LOCBYYEAR = f"{LOCALITY}_{YEARS}"
LOCBYMONTH = f"{LOCALITY}_{MONTHS}"
NEIGHBYYEAR = f"{NEIGHTBORHOOD}_{YEARS}"
NEIGHBYMONTH = f"{NEIGHTBORHOOD}_{MONTHS}"

# Filters [TrafficCollision] Only
ZONE = "zone"
AREA = "area"
SEVERITY = "severity"
TYPE = "type"
OBJ = "object"
OBJTYP = "object_type"

# Filters [TreePlot] Only
AREA_RANGE = "area_range"
DIAMETER = "avg_diameter"
HEIGHT = "avg_height"
BASAL = "basal_area"
CAREA = "canopy_area"
CAPLOT = "area_covered"
CCV = "canopy_volume"
    


class EscalaFilter:
    def timeFilter (self, class_, time_col, params):
        if 'time' in params:
            years_list = list(class_.objects.order_by(time_col).values_list(time_col, flat=True).distinct())
            years_filtered = [int(year) for year in re.findall(r'[0-9]+', params.get('time'))]
            
            start = years_list.index(years_filtered[0])
            end = years_list.index(years_filtered[1])
            
            return years_list[start:end+1]
        else:
           return list(class_.objects.order_by(time_col).values_list(time_col, flat=True).distinct())
       
    def spaceFilter (self, class_, space_col, params):
        if 'space' in params:
            filter = params.get('space').split(",")
            
            space_list = list(Neightborhood.objects.filter(NAME__in=filter).values('ID_NEIGHB', 'NAME'))
            space_filtered = [neigh['ID_NEIGHB'] for neigh in space_list]
            
            return space_filtered
        else:
            space_list = list(Neightborhood.objects.values('ID_NEIGHB'))
            space_filtered = [neigh['ID_NEIGHB'] for neigh in space_list]
            
            return space_filtered

    def filterByYear (self, class_, space_list, time_list, columns, extrapolate=False):
        list_years = {year: 0 for year in time_list}
                
        data = list(class_.objects.filter(ID_NEIGHB__in=space_list, COLYEAR__in=time_list).order_by().values(columns[YEARS]).order_by(columns[YEARS]).annotate(count=Count(columns[YEARS])))
        for value in data:
            list_years[value[columns[YEARS]]] = value['count']
            
        return [list_years.keys(), list_years.values()]
    
    def filterByMonth (self, class_, space_list, time_list, columns, extrapolate=False):
        months_per_year = [i for i in range(1, 13)]
        list_months = {f'{year}/{month}': 0 for year in time_list
                                            for month in months_per_year}
        
        data = list(class_.objects.filter(ID_NEIGHB__in=space_list, COLYEAR__in=time_list).order_by().values(columns[YEARS], columns[MONTHS]).order_by(columns[YEARS], columns[MONTHS]).annotate(count=Count(columns[YEARS])))
        print(data)
        for value in data:
            list_months[f'{value[columns[YEARS]]}/{value[columns[MONTHS]]}'] = value['count']
                
        print(list_months)
        return [list_months.keys(), list_months.values()]

    def filterByDays (self, class_, space_list, time_list, columns, extrapolate=False):
        days_for_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        months_per_year = [i for i in range(1, 13)]
        list_days = {f'{year}/{month}/{day}': 0 for year in time_list
                                                for i, month in enumerate(months_per_year) 
                                                for day in range(1, days_for_month[i]+1)}
                
        data = list(class_.objects.filter(ID_NEIGHB__in=space_list, COLYEAR__in=time_list).order_by().values(columns[YEARS], columns[MONTHS], columns[DAYS]).order_by(columns[YEARS], columns[MONTHS], columns[DAYS]).annotate(count=Count(columns[YEARS])))
        for value in data:
            list_days[f'{value[columns[YEARS]]}/{value[columns[MONTHS]]}/{value[columns[DAYS]]}'] = value['count']
                
        return [list_days.keys(), list_days.values()]
    
    def filterByHours (self, class_, space_list, time_list, columns, extrapolate=False):
        list_hours = {hour: 0 for hour in list(range(0, 24))}
                
        data = list(class_.objects.filter(ID_NEIGHB__in=space_list, COLYEAR__in=time_list).order_by().values(columns[HOURS]).order_by(columns[HOURS]).annotate(count=Count(columns[HOURS])))
        for value in data:
            list_hours[value[columns[HOURS]]] = value['count']
                    
        return [list_hours.keys(), list_hours.values()]
    
    def filterByDom (self, class_, space_list, time_list, columns, dom_list, dom):
        list_values = {dom_: 0 for dom_ in dom_list.keys()}
        
        labels = dom_list.values()
        data = list(class_.objects.filter(ID_NEIGHB__in=space_list, COLYEAR__in=time_list).order_by().values(columns[dom]).order_by(columns[dom]).annotate(count=Count(columns[dom])))
        for value in data:
            list_values[value[columns[dom]]] = value['count']
            
        return [dom_list.values(), list_values.values()]
    
    def filterByRange (self, class_, columns, col, extrapolate=False):
        max = class_.objects.aggregate(Max(columns[col]))[f"{columns[col]}__max"]
        min = class_.objects.aggregate(Min(columns[col]))[f"{columns[col]}__min"]
        range_list = np.linspace(max, min, 10)[::-1]
        
        list_values = {
            f'{round(value, 2)}-{round(range_list[i+1], 2)}': class_.objects.filter(**{f"{columns[col]}__range":(value, range_list[i+1])}).aggregate(count=Count(columns[col]))['count']
            for i, value, in enumerate(range_list[:-1])
            }
            
        return [list_values.keys(), list_values.values()]

    def filterByNeightborhood (self, class_, space_list, time_list, columns, extrapolate=False):
        neigh_values = list(Neightborhood.objects.all().filter(ID_NEIGHB__in=space_list).values("ID_NEIGHB", "NAME", "AREA"))     
        
        list_neigh = dict()
        for neigh in neigh_values:
            if neigh['NAME'] != 'NA':
                list_neigh[neigh['ID_NEIGHB']] = {
                    'count': 0,
                    'name': neigh['NAME'].replace("_", " "),
                    'area': neigh['AREA'],
                    'extrapolation': 0
                }

        list_neigh['OTHERS'] = {
            'count': 0,
            'name': 'OTHERS',
            'area': sum(neigh['AREA'] for neigh in neigh_values if neigh['NAME'] == 'NA'),
            'extrapolation': 0
        }
        
        if class_ is TrafficCollision:        
            data = list(class_.objects.filter(ID_NEIGHB__in=space_list, COLYEAR__in=time_list).order_by().values(columns[NEIGHTBORHOOD]).annotate(count=Count(columns[NEIGHTBORHOOD])))
        else:
            data = list(class_.objects.filter(ID_NEIGHB__in=space_list).order_by().values(columns[NEIGHTBORHOOD]).annotate(count=Count(columns[NEIGHTBORHOOD]), area=Sum('TPAREA'), sum=Sum('TPABUND')))
        
        for value in data:
            try:
                list_neigh[value[columns[NEIGHTBORHOOD]]]['count'] = value['count']
                
                if extrapolate:
                    list_neigh[value[columns[NEIGHTBORHOOD]]]['extrapolation'] = int((list_neigh[value[columns[NEIGHTBORHOOD]]]['area'] * value['sum']) /(value['area'] * 0.0001))
            except:
                list_neigh['OTHERS']['count'] += value['count']
                
                if extrapolate:
                    list_neigh['OTHERS']['extrapolation'] = int((list_neigh['OTHERS']['area'] * value['sum']) /(value['area'] * 0.0001))
        
        
        neigh_data = dict()                   
        for neigh in list_neigh.keys():
            if list_neigh[neigh]['count'] > 0:
                try:
                    if extrapolate:
                        neigh_data[list_neigh[neigh]['name']] += list_neigh[neigh]['extrapolation']
                    else:
                        neigh_data[list_neigh[neigh]['name']] += list_neigh[neigh]['count']
                except:
                    if extrapolate:
                        neigh_data[list_neigh[neigh]['name']] = list_neigh[neigh]['extrapolation']
                    else:
                        neigh_data[list_neigh[neigh]['name']] = list_neigh[neigh]['count']
        
        neigh_data = dict(sorted(neigh_data.items(), key=lambda item: item[1], reverse=True))
        return [neigh_data.keys(), neigh_data.values()]

    def filterByLocality (self, class_, space_list, time_list, columns, extrapolate=False):
        list_neigh = list(Neightborhood.objects.all().filter(ID_NEIGHB__in=space_list).values("ID_NEIGHB", "LOCALITY", "AREA"))
        loc_ids = set([neigh['LOCALITY'] for neigh in list_neigh])
        loc_names = {loc["ID_LOCALITY"]: loc['NAME'] for loc in list(Locality_bar.objects.all().filter(ID_LOCALITY__in=loc_ids).values("ID_LOCALITY", "NAME"))}
        
        list_loc = dict()
        for neigh in list_neigh:
            list_loc[neigh["ID_NEIGHB"]] = {
                'count': 0,
                'locality': loc_names[neigh["LOCALITY"]],
                'area': neigh["AREA"],
                'extrapolation': 0
            }
            
        if class_ is TrafficCollision:
            data = list(class_.objects.filter(ID_NEIGHB__in=space_list, COLYEAR__in=time_list).order_by().values(columns[NEIGHTBORHOOD]).annotate(count=Count(columns[NEIGHTBORHOOD])))
        else: 
            data = list(class_.objects.filter(ID_NEIGHB__in=space_list).order_by().values(columns[NEIGHTBORHOOD]).annotate(count=Count(columns[NEIGHTBORHOOD]), area=Sum('TPAREA'), sum=Sum('TPABUND')))
            
        for value in data:
            list_loc[value[columns[NEIGHTBORHOOD]]]['count'] += value['count']
                
            if extrapolate:
                list_loc[value[columns[NEIGHTBORHOOD]]]['extrapolation'] += int((list_loc[value[columns[NEIGHTBORHOOD]]]['area'] * value['sum']) /(value['area'] * 0.0001))

        loc_data = dict()  
        for neigh in list_loc.keys():
            if list_loc[neigh]['count'] > 0:
                try:
                    if extrapolate:
                        loc_data[list_loc[neigh]['locality']] += list_loc[neigh]['extrapolation']
                    else:
                        loc_data[list_loc[neigh]['locality']] += list_loc[neigh]['count']
                except:
                    if extrapolate:
                        loc_data[list_loc[neigh]['locality']] = list_loc[neigh]['extrapolation']
                    else:
                        loc_data[list_loc[neigh]['locality']] = list_loc[neigh]['count']

        loc_data = dict(sorted(loc_data.items(), key=lambda item: item[1], reverse=True))
        return [loc_data.keys(), loc_data.values()]
  
    def filterByMunicipality (self, class_, space_list, time_list, columns, extrapolate=False):
        list_neigh = list(Neightborhood.objects.all().filter(ID_NEIGHB__in=space_list).values("ID_NEIGHB", "LOCALITY", "AREA"))
        neigh_by_loc = {neigh["ID_NEIGHB"]: neigh["LOCALITY"] for neigh in list_neigh}
        loc_by_mun = {neigh["ID_LOCALITY"]: neigh["MUNICIPALITY"] for neigh in list(Locality_bar.objects.all().filter(ID_LOCALITY__in=set(neigh_by_loc.values())).values("ID_LOCALITY", "MUNICIPALITY"))}
        mun_by_neigh = {neigh: loc_by_mun[neigh_by_loc[neigh]] for neigh in neigh_by_loc.keys()}
        
        list_mun = dict()
        for neigh in list_neigh:
            list_mun[neigh["ID_NEIGHB"]] = {
                'count': 0,
                'municipality': mun_by_neigh[neigh["ID_NEIGHB"]],
                'area': neigh["AREA"],
                'extrapolation': 0
            }
            
        if class_ is TrafficCollision:
            data = list(class_.objects.filter(ID_NEIGHB__in=space_list, COLYEAR__in=time_list).order_by().values(columns[NEIGHTBORHOOD]).annotate(count=Count(columns[NEIGHTBORHOOD])))
        else: 
            data = list(class_.objects.filter(ID_NEIGHB__in=space_list).order_by().values(columns[NEIGHTBORHOOD]).annotate(count=Count(columns[NEIGHTBORHOOD]), area=Sum('TPAREA'), sum=Sum('TPABUND')))
            
        for value in data:
            list_mun[value[columns[NEIGHTBORHOOD]]]['count'] += value['count']
                
            if extrapolate:
                list_mun[value[columns[NEIGHTBORHOOD]]]['extrapolation'] += int((list_mun[value[columns[NEIGHTBORHOOD]]]['area'] * value['sum']) /(value['area'] * 0.0001))

        data = 0
        for neigh in list_mun.keys():
            if list_mun[neigh]['count'] > 0:
                if extrapolate:
                    data += list_mun[neigh]['extrapolation']
                else:
                    data += list_mun[neigh]['count']

        return ["Barranquilla", data]
    
    def filterByNeighborhoodArea (self, class_, space_list, time_list, columns, extrapolate=False):
        neigh_values = list(Neightborhood.objects.all().filter(ID_NEIGHB__in=space_list).values("ID_NEIGHB", "NAME", "AREA"))     
        
        list_neigh = dict()
        for neigh in neigh_values:
            if neigh['NAME'] != 'NA':
                list_neigh[neigh['ID_NEIGHB']] = {
                    'count': 0,
                    'name': neigh['NAME'].replace("_", " "),
                    'area': neigh['AREA'],
                    'extrapolation': 0
                }

        list_neigh['OTHERS'] = {
            'count': 0,
            'name': 'OTHERS',
            'area': sum(neigh['AREA'] for neigh in neigh_values if neigh['NAME'] == 'NA'),
            'extrapolation': 0
        }
        
        if class_ is TrafficCollision:        
            data = list(class_.objects.filter(ID_NEIGHB__in=space_list, COLYEAR__in=time_list).order_by().values(columns[NEIGHTBORHOOD]).annotate(count=Count(columns[NEIGHTBORHOOD])))
        else:
            data = list(class_.objects.filter(ID_NEIGHB__in=space_list).order_by().values(columns[NEIGHTBORHOOD]).annotate(count=Count(columns[NEIGHTBORHOOD]), area=Sum('TPAREA'), sum=Sum('TPABUND')))
        
        for value in data:
            try:
                list_neigh[value[columns[NEIGHTBORHOOD]]]['count'] = value['count']/list_neigh[value[columns[NEIGHTBORHOOD]]]['area']
                
                if extrapolate:
                    list_neigh[value[columns[NEIGHTBORHOOD]]]['extrapolation'] = (int((list_neigh[value[columns[NEIGHTBORHOOD]]]['area'] * value['sum']) /(value['area'] * 0.0001)))/list_neigh[value[columns[NEIGHTBORHOOD]]]['area']
            except:
                list_neigh['OTHERS']['count'] += value['count']/list_neigh['OTHERS']['area']
                
                if extrapolate:
                    list_neigh['OTHERS']['extrapolation'] = (int((list_neigh['OTHERS']['area'] * value['sum']) /(value['area'] * 0.0001)))/list_neigh['OTHERS']['area']
          
        neigh_data = dict()                   
        for neigh in list_neigh.keys():
            if list_neigh[neigh]['count'] > 0:
                try:
                    if extrapolate:
                        neigh_data[list_neigh[neigh]['name']] += list_neigh[neigh]['extrapolation']
                    else:
                        neigh_data[list_neigh[neigh]['name']] += list_neigh[neigh]['count']
                except:
                    if extrapolate:
                        neigh_data[list_neigh[neigh]['name']] = list_neigh[neigh]['extrapolation']
                    else:
                        neigh_data[list_neigh[neigh]['name']] = list_neigh[neigh]['count']

        
        neigh_data = dict(sorted(neigh_data.items(), key=lambda item: item[1], reverse=True))
        return [neigh_data.keys(), neigh_data.values()]
    
    def filterByLocalityArea (self, class_, space_list, time_list, columns, extrapolate=False):
        list_neigh = list(Neightborhood.objects.all().filter(ID_NEIGHB__in=space_list).values("ID_NEIGHB", "LOCALITY", "AREA"))
        loc_ids = set([neigh['LOCALITY'] for neigh in list_neigh])
        
        list_locs = list(Locality_bar.objects.all().filter(ID_LOCALITY__in=loc_ids).values("ID_LOCALITY", "NAME", "AREA"))
        loc_names = {loc["ID_LOCALITY"]: loc['NAME'] for loc in list_locs}
        loc_area = {loc["NAME"]: loc["AREA"] for loc in list_locs}
        
        list_loc = dict()
        for neigh in list_neigh:
            list_loc[neigh["ID_NEIGHB"]] = {
                'count': 0,
                'locality': loc_names[neigh["LOCALITY"]],
                'area': neigh["AREA"],
                'extrapolation': 0
            }
            
        if class_ is TrafficCollision:
            data = list(class_.objects.filter(ID_NEIGHB__in=space_list, COLYEAR__in=time_list).order_by().values(columns[NEIGHTBORHOOD]).annotate(count=Count(columns[NEIGHTBORHOOD])))
        else: 
            data = list(class_.objects.filter(ID_NEIGHB__in=space_list).order_by().values(columns[NEIGHTBORHOOD]).annotate(count=Count(columns[NEIGHTBORHOOD]), area=Sum('TPAREA'), sum=Sum('TPABUND')))
            
        for value in data:
            list_loc[value[columns[NEIGHTBORHOOD]]]['count'] += value['count']
                
            if extrapolate:
                list_loc[value[columns[NEIGHTBORHOOD]]]['extrapolation'] += int((list_loc[value[columns[NEIGHTBORHOOD]]]['area'] * value['sum']) /(value['area'] * 0.0001))

        loc_data = dict()
        for neigh in list_loc.keys():
            if list_loc[neigh]['count'] > 0:
                try:
                    if extrapolate:
                        loc_data[list_loc[neigh]['locality']] += list_loc[neigh]['extrapolation'] / loc_area[list_loc[neigh]['locality']]
                    else:
                        loc_data[list_loc[neigh]['locality']] += list_loc[neigh]['count'] / loc_area[list_loc[neigh]['locality']]
                except:
                    if extrapolate:
                        loc_data[list_loc[neigh]['locality']] = list_loc[neigh]['extrapolation'] / loc_area[list_loc[neigh]['locality']]
                    else:
                        loc_data[list_loc[neigh]['locality']] = list_loc[neigh]['count'] / loc_area[list_loc[neigh]['locality']]

        loc_data = dict(sorted(loc_data.items(), key=lambda item: item[1], reverse=True))
        return [loc_data.keys(), loc_data.values()]
    
    def filterByMunicipalityArea (self, class_, space_list, time_list, columns, extrapolate=False):
        list_neigh = list(Neightborhood.objects.all().filter(ID_NEIGHB__in=space_list).values("ID_NEIGHB", "LOCALITY", "AREA"))
        neigh_by_loc = {neigh["ID_NEIGHB"]: neigh["LOCALITY"] for neigh in list_neigh}
        loc_by_mun = {neigh["ID_LOCALITY"]: neigh["MUNICIPALITY"] for neigh in list(Locality_bar.objects.all().filter(ID_LOCALITY__in=set(neigh_by_loc.values())).values("ID_LOCALITY", "MUNICIPALITY"))}
        mun_by_neigh = {neigh: loc_by_mun[neigh_by_loc[neigh]] for neigh in neigh_by_loc.keys()}
        
        mun_area = {mun["ID_MUN"]: mun["AREA"] for mun in list(Municipality.objects.all().values("ID_MUN", "AREA"))}
        
        list_mun = dict()
        for neigh in list_neigh:
            list_mun[neigh["ID_NEIGHB"]] = {
                'count': 0,
                'municipality': mun_by_neigh[neigh["ID_NEIGHB"]],
                'area': neigh["AREA"],
                'extrapolation': 0
            }
            
        if class_ is TrafficCollision:
            data = list(class_.objects.filter(ID_NEIGHB__in=space_list, COLYEAR__in=time_list).order_by().values(columns[NEIGHTBORHOOD]).annotate(count=Count(columns[NEIGHTBORHOOD])))
        else: 
            data = list(class_.objects.filter(ID_NEIGHB__in=space_list).order_by().values(columns[NEIGHTBORHOOD]).annotate(count=Count(columns[NEIGHTBORHOOD]), area=Sum('TPAREA'), sum=Sum('TPABUND')))
            
        for value in data:
            list_mun[value[columns[NEIGHTBORHOOD]]]['count'] += value['count']
                
            if extrapolate:
                list_mun[value[columns[NEIGHTBORHOOD]]]['extrapolation'] += int((list_mun[value[columns[NEIGHTBORHOOD]]]['area'] * value['sum']) /(value['area'] * 0.0001))

        data = 0
        for neigh in list_mun.keys():
            if list_mun[neigh]['count'] > 0:
                if extrapolate:
                    data += list_mun[neigh]['extrapolation'] / mun_area[list_mun[neigh]['municipality']]
                else:
                    data += list_mun[neigh]['count'] / mun_area[list_mun[neigh]['municipality']]

        return ["Barranquilla", data]
    
    def meanByYear (self, class_, space_list, time_list, columns):
        list_years = self.filterByYear(class_, space_list, time_list, columns)
            
        for year in time_list:
            if (year%4 == 0):
                list_years[year] = list_years[year]/366
            else:
                list_years[year] = list_years[year]/365
            
        return list_years
            
    def meanByMonth (self, class_, space_list, time_list, columns):
        days_for_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        months_per_year = [i for i in range(1, 13)]
        
        list_months = self.filterByMonth(class_, space_list, time_list, columns)
        
        list_months = {f'{year}/{month}': list_months[f'{year}/{month}']/days_for_month[i]  for year in time_list
                                                                                            for i, month in enumerate(months_per_year)}
        
        return list_months
    
    def filterByLocYear (self, class_, space_list, time_list, columns, extrapolate=False):
        list_neigh = list(Neightborhood.objects.all().filter(ID_NEIGHB__in=space_list).values("ID_NEIGHB", "LOCALITY", "AREA"))   
        loc_ids = set([neigh['LOCALITY'] for neigh in list_neigh])
        loc_names = {loc["ID_LOCALITY"]: loc['NAME'] for loc in list(Locality_bar.objects.all().filter(ID_LOCALITY__in=loc_ids).values("ID_LOCALITY", "NAME"))}
        
        list_loc = dict()
        for neigh in list_neigh:
            list_loc[neigh["ID_NEIGHB"]] = {
                'count': 0,
                'locality': loc_names[neigh["LOCALITY"]],
                'area': neigh["AREA"],
                'data': {year: 0 for year in time_list}
            }
        
        data = list(class_.objects.filter(ID_NEIGHB__in=space_list, COLYEAR__in=time_list).order_by().values(columns[NEIGHTBORHOOD], columns[YEARS]).order_by(columns[YEARS]).annotate(count=Count(columns[YEARS])))
        for value in data:
            list_loc[value[columns[NEIGHTBORHOOD]]]['data'][ value[columns[YEARS]]] = value['count']
        
        loc_data = dict()  
        for neigh in list_loc.keys():
            if sum(list_loc[neigh]['data'].values()) > 0:
                if (list_loc[neigh]['locality'] not in loc_data.keys()):
                    loc_data[list_loc[neigh]['locality']] = [0 for i in list_loc[neigh]['data']]
                
                loc_data[list_loc[neigh]['locality']] = [sum(i) for i in zip(loc_data[list_loc[neigh]['locality']], list_loc[neigh]['data'].values())] 

        labels, data_list = [], []
        for loc in loc_data.keys():
            data_count = loc_data[loc]
            if (sum(data_count) > 0):
                labels.append(loc)
                data_list.append(data_count)
        
        return [labels, time_list, data_list]
    
    def filterByLocMonth (self, class_, space_list, time_list, columns, extrapolate=False):
        months_per_year = [i for i in range(1, 13)]
        list_neigh = list(Neightborhood.objects.all().filter(ID_NEIGHB__in=space_list).values("ID_NEIGHB", "LOCALITY", "AREA"))   
        loc_ids = set([neigh['LOCALITY'] for neigh in list_neigh])
        loc_names = {loc["ID_LOCALITY"]: loc['NAME'] for loc in list(Locality_bar.objects.all().filter(ID_LOCALITY__in=loc_ids).values("ID_LOCALITY", "NAME"))}
        
        list_loc = dict()
        for neigh in list_neigh:
            list_loc[neigh["ID_NEIGHB"]] = {
                'count': 0,
                'locality': loc_names[neigh["LOCALITY"]],
                'area': neigh["AREA"],
                'data': {f'{year}/{month}': 0 for year in time_list
                                              for month in months_per_year}
            }
        
        data = list(class_.objects.filter(ID_NEIGHB__in=space_list, COLYEAR__in=time_list).order_by().values(columns[NEIGHTBORHOOD], columns[YEARS], columns[MONTHS]).order_by(columns[YEARS], columns[MONTHS]).annotate(count=Count(columns[YEARS])))
        for value in data:
            list_loc[value[columns[NEIGHTBORHOOD]]]['data'][f'{value[columns[YEARS]]}/{value[columns[MONTHS]]}'] = value['count']
        
        loc_data = dict()  
        for neigh in list_loc.keys():
            if sum(list_loc[neigh]['data'].values()) > 0:
                if (list_loc[neigh]['locality'] not in loc_data.keys()):
                    loc_data[list_loc[neigh]['locality']] = [0 for i in list_loc[neigh]['data']]
                
                loc_data[list_loc[neigh]['locality']] = [sum(i) for i in zip(loc_data[list_loc[neigh]['locality']], list_loc[neigh]['data'].values())] 

        labels, data_list = [], []
        for loc in loc_data.keys():
            data_count = loc_data[loc]
            if (sum(data_count) > 0):
                labels.append(loc)
                data_list.append(data_count)
        
        return [labels, list_loc[neigh]['data'].keys(), data_list]
    
    def filterByNeighYear (self, class_, space_list, time_list, columns, extrapolate=False):
        neigh_values = list(Neightborhood.objects.all().filter(ID_NEIGHB__in=space_list).values("ID_NEIGHB", "NAME", "AREA"))   
        
        list_neigh = dict()
        for neigh in neigh_values:
            if neigh['NAME'] != 'NA':
                list_neigh[neigh['ID_NEIGHB']] = {
                    'count': 0,
                    'name': neigh['NAME'].replace("_", " "),
                    'area': neigh['AREA'],
                    'data': {year: 0 for year in time_list}
                }

        list_neigh['OTHERS'] = {
            'count': 0,
            'name': 'OTHERS',
            'area': sum(neigh['AREA'] for neigh in neigh_values if neigh['NAME'] == 'NA'),
            'data': {year: 0 for year in time_list}
        }
        
        data = list(class_.objects.filter(ID_NEIGHB__in=space_list, COLYEAR__in=time_list).order_by().values(columns[NEIGHTBORHOOD], columns[YEARS]).order_by(columns[YEARS]).annotate(count=Count(columns[YEARS])))
        for value in data:
            try:
                list_neigh[value[columns[NEIGHTBORHOOD]]]['data'][value[columns[YEARS]]] = value['count']
            except:
                list_neigh['OTHERS']['data'][value[columns[YEARS]]] += value['count']
        
        labels, data_list = [], []
        for neigh in list_neigh.keys():
            data_count = list(list_neigh[neigh]['data'].values())
            if (sum(data_count) > 0):
                labels.append(list_neigh[neigh]['name'])
                data_list.append(data_count)
        
        return [labels, list_neigh['OTHERS']['data'].keys(), data_list]
    
    def filterByNeighMonth (self, class_, space_list, time_list, columns, extrapolate=False):
        months_per_year = [i for i in range(1, 13)]
        neigh_values = list(Neightborhood.objects.all().filter(ID_NEIGHB__in=space_list).values("ID_NEIGHB", "NAME", "AREA"))     
        
        list_neigh = dict()
        for neigh in neigh_values:
            if neigh['NAME'] != 'NA':
                list_neigh[neigh['ID_NEIGHB']] = {
                    'count': 0,
                    'name': neigh['NAME'].replace("_", " "),
                    'area': neigh['AREA'],
                    'data': {f'{year}/{month}': 0 for year in time_list
                                                  for month in months_per_year}
                }

        list_neigh['OTHERS'] = {
            'count': 0,
            'name': 'OTHERS',
            'area': sum(neigh['AREA'] for neigh in neigh_values if neigh['NAME'] == 'NA'),
            'data': {f'{year}/{month}': 0 for year in time_list
                                          for month in months_per_year}
        }
        
        data = list(class_.objects.filter(ID_NEIGHB__in=space_list, COLYEAR__in=time_list).order_by().values(columns[NEIGHTBORHOOD], columns[YEARS], columns[MONTHS]).order_by(columns[YEARS], columns[MONTHS]).annotate(count=Count(columns[YEARS])))
        for value in data:
            try:
                list_neigh[value[columns[NEIGHTBORHOOD]]]['data'][f'{value[columns[YEARS]]}/{value[columns[MONTHS]]}'] = value['count']
            except:
                list_neigh['OTHERS']['data'][f'{value[columns[YEARS]]}/{value[columns[MONTHS]]}'] += value['count']
        
        labels, data_list = [], []
        for neigh in list_neigh.keys():
            data_count = list(list_neigh[neigh]['data'].values())
            if (sum(data_count) > 0):
                labels.append(list_neigh[neigh]['name'])
                data_list.append(data_count)
        
        return [labels, list_neigh['OTHERS']['data'].keys(), data_list]
    
    
# Colección de ViewSets para [TrafficCollision] 
class TrafficCollisionViewSet (viewsets.ModelViewSet):
    queryset = TrafficCollision.objects.all()
    serializer_class = TrafficCollisionSerializer
    
class TrafficCollisionPointViewSet (viewsets.ModelViewSet):
    queryset = TrafficCollision.objects.all()
    serializer_class = TrafficCollisionPointSerializer


'''
[TrafficCollision] Count Query
QueryParams:
- filter: one of (YY, MM, DD, HH, municipality, locality, neightborhood, etc)
- time: (First [YEAR], Last [YEAR])
- space: (List of [Neightborhood])
'''
class TrafficCollisionCountViewSet (viewsets.ModelViewSet, EscalaFilter):
    queryset = TrafficCollision.objects.all()
    serializer_class = TrafficCollisionSerializer
    
    def searchByFilter (self, class_, space_list, time_list, columns, DOMAINS, params):
        if 'filter' in params:
            query_filter = params.get('filter')
            
            if MUNBYYEAR in query_filter:
                chart = [BAR, LINE]
                return self.filterByYear(class_, space_list, time_list, columns) + [chart]
            elif MUNBYMONTH in query_filter:
                chart = [BAR, LINE]
                return self.filterByMonth(class_, space_list, time_list, columns) + [chart]
            elif DAYS in query_filter:
                chart = [BAR, LINE]
                return self.filterByDays(class_, space_list, time_list, columns) + [chart]
            elif HOURS in query_filter:
                chart = [BAR, LINE]
                return self.filterByHours(class_, space_list, time_list, columns) + [chart]
            elif MUNICIPALITY in query_filter:
                chart = [BAR, PIE]
                return self.filterByMunicipality(class_, space_list, time_list, columns) + [chart]
            elif LOCALITY in query_filter:
                chart = [BAR, PIE]
                return self.filterByLocality(class_, space_list, time_list, columns) + [chart]
            elif NEIGHBYMONTH in query_filter:
                chart = [LINE]
                return self.filterByNeighMonth(class_, space_list, time_list, columns) + [chart]
            elif NEIGHTBORHOOD in query_filter:
                chart = [BAR, PIE]
                return self.filterByNeightborhood(class_, space_list, time_list, columns) + [chart]
            elif ZONE in query_filter:
                chart = [BAR, PIE]
                return self.filterByDom(class_, space_list, time_list, columns, DOMAINS[columns[ZONE]], ZONE) + [chart]
            elif AREA in query_filter:
                chart = [BAR, PIE]
                return self.filterByDom(class_, space_list, time_list, columns, DOMAINS[columns[AREA]], AREA) + [chart]
            elif SEVERITY in query_filter:
                chart = [PIE]
                return self.filterByDom(class_, space_list, time_list, columns, DOMAINS[columns[SEVERITY]], SEVERITY) + [chart]
            elif TYPE in query_filter:
                chart = [DOUGHNUT]
                return self.filterByDom(class_, space_list, time_list, columns, DOMAINS[columns[TYPE]], TYPE) + [chart]
            elif OBJ in query_filter:
                chart = [DOUGHNUT]
                return self.filterByDom(class_, space_list, time_list, columns, DOMAINS[columns[OBJ]], OBJ) + [chart]
            elif OBJTYP in query_filter:
                chart = [DOUGHNUT]
                return self.filterByDom(class_, space_list, time_list, columns, DOMAINS[columns[OBJTYP]], OBJTYP) + [chart]
            
            else:
                return [], [], []
        else:
            return [], [], []
    
    def list (self, request, *args, **kwargs):
        params = self.request.query_params
        
        COLUMNS = {
            YEARS: "COLYEAR",
            MONTHS: "COLMONTH",
            DAYS: "COLDAY",
            HOURS: "COLHOUR",
            NEIGHTBORHOOD: "ID_NEIGHB",
            ZONE: "COLZONE",
            AREA: "COLAREA",
            SEVERITY: "COLSEV",
            TYPE: "COLTYP",
            OBJ: "COLOBJ",
            OBJTYP: "COLOBJTYP",
        }

        DOMAINS = {
            COLUMNS[ZONE]: {
                1: 'Hospital',
                2: 'Military',
                3: 'Private',
                4: 'School',
                5: 'Sports',
                6: 'Tourist',
                7: 'Not reported'
            },
            COLUMNS[AREA]: {
                1: 'Rural',
                2: 'Urban'
            },
            COLUMNS[SEVERITY]: {
                1: 'Fatal',
                2: 'Injured',
                3: 'Unharmed',
                4: 'Not reported'
            },
            COLUMNS[TYPE]: {
                1: 'Crash',
                2: 'Fire',
                3: 'Occupant fall',
                4: 'Pedestrian collision',
                5: 'Rollover',
                6: 'Other'
            },
            COLUMNS[OBJ]: {
                1: 'Fixed object',
                2: 'Moving object',
                3: 'Vehicle',
                4: 'Not reported'
            },
            COLUMNS[OBJTYP]: {
                1: 'Building',
                2: 'Guardrail',
                3: 'Parked vehicle',
                4: 'Pole',
                5: 'Sing',
                6: 'Traffic light',
                7: 'Tree',
                8: 'Wall',
                9: 'Other',
                10: 'Not reported'
            }
        }
        
        label = "Traffic Collision"
        time_list = self.timeFilter(TrafficCollision, COLUMNS[YEARS], params)
        space_list = self.spaceFilter(TrafficCollision, COLUMNS[NEIGHTBORHOOD], params)
        print(space_list)
        
        labels, data_list, charts = self.searchByFilter(TrafficCollision, space_list, time_list, COLUMNS, DOMAINS, params)

        dataset = {'label': label, 'data': data_list}
        response = {
            'labels': labels, 
            'datasets': dataset, 
            'chart': charts
            }
        
        return Response(response)


class TrafficCollisionTSCountViewSet (viewsets.ModelViewSet, EscalaFilter):
    queryset = TrafficCollision.objects.all()
    serializer_class = TrafficCollisionSerializer
    
    def searchByFilter (self, class_, space_list, time_list, columns, DOMAINS, params):
        if 'filter' in params:
            query_filter = params.get('filter')
            if MUNBYYEAR in query_filter:
                chart = [BAR, LINE]
                return [["Barranquilla"]] + self.filterByYear(class_, space_list, time_list, columns) + [chart]
            elif MUNBYMONTH in query_filter:
                chart = [BAR, LINE]
                return [["Barranquilla"]] + self.filterByMonth(class_, space_list, time_list, columns) + [chart]
            elif NEIGHBYYEAR in query_filter:
                chart = [LINE]
                return self.filterByNeighYear(class_, space_list, time_list, columns) + [chart]  
            elif NEIGHBYMONTH in query_filter:
                chart = [LINE]
                return self.filterByNeighMonth(class_, space_list, time_list, columns) + [chart]  
            elif LOCBYYEAR in query_filter:
                chart = [LINE]
                return self.filterByLocYear(class_, space_list, time_list, columns) + [chart]  
            elif LOCBYMONTH in query_filter:
                chart = [LINE]
                return self.filterByLocMonth(class_, space_list, time_list, columns) + [chart]    
            else:
                return [], [], [], []
        else:
            return [], [], [], []
    
    def list (self, request, *args, **kwargs):
        params = self.request.query_params
        
        COLUMNS = {
            YEARS: "COLYEAR",
            MONTHS: "COLMONTH",
            DAYS: "COLDAY",
            HOURS: "COLHOUR",
            NEIGHTBORHOOD: "ID_NEIGHB",
            ZONE: "COLZONE",
            AREA: "COLAREA",
            SEVERITY: "COLSEV",
            TYPE: "COLTYP",
            OBJ: "COLOBJ",
            OBJTYP: "COLOBJTYP",
        }

        DOMAINS = {
            COLUMNS[ZONE]: {
                1: 'Hospital',
                2: 'Military',
                3: 'Private',
                4: 'School',
                5: 'Sports',
                6: 'Tourist',
                7: 'Not reported'
            },
            COLUMNS[AREA]: {
                1: 'Rural',
                2: 'Urban'
            },
            COLUMNS[SEVERITY]: {
                1: 'Fatal',
                2: 'Injured',
                3: 'Unharmed',
                4: 'Not reported'
            },
            COLUMNS[TYPE]: {
                1: 'Crash',
                2: 'Fire',
                3: 'Occupant fall',
                4: 'Pedestrian collision',
                5: 'Rollover',
                6: 'Other'
            },
            COLUMNS[OBJ]: {
                1: 'Fixed object',
                2: 'Moving object',
                3: 'Vehicle',
                4: 'Not reported'
            },
            COLUMNS[OBJTYP]: {
                1: 'Building',
                2: 'Guardrail',
                3: 'Parked vehicle',
                4: 'Pole',
                5: 'Sing',
                6: 'Traffic light',
                7: 'Tree',
                8: 'Wall',
                9: 'Other',
                10: 'Not reported'
            }
        }
        
        label = "Traffic Collision"
        time_list = self.timeFilter(TrafficCollision, COLUMNS[YEARS], params)
        space_list = self.spaceFilter(TrafficCollision, COLUMNS[NEIGHTBORHOOD], params)
        
        label_list, labels, data_list, charts = self.searchByFilter(TrafficCollision, space_list, time_list, COLUMNS, DOMAINS, params)
        
        if (len(label_list) == 1):
            data_list = [data_list]

        dataset = [{'label': label, 'data': data_list[i]} for i, label in enumerate(label_list)]
        response = {
            'labels': labels, 
            'datasets': dataset, 
            'chart': charts
            }
        
        return Response(response)

'''
[TrafficCollision] Area Count Query
QueryParams:
- filter: one of (municipality, locality, neightborhood)
- time: (First [YEAR], Last [YEAR])
- space: (List of [Neightborhood])
'''
class TrafficCollisionAreaCountViewSet (viewsets.ModelViewSet, EscalaFilter):
    queryset = TrafficCollision.objects.all()
    serializer_class = TrafficCollisionSerializer
    
    def searchByFilter (self, class_, space_list, time_list, columns, params):
        if 'filter' in params:
            query_filter = params.get('filter')
            
            if MUNICIPALITY in query_filter:
                chart = [BAR]
                return self.filterByMunicipalityArea(class_, space_list, time_list, columns) + [chart]
            elif LOCALITY in query_filter:
                chart = [BAR]
                return self.filterByLocalityArea(class_, space_list, time_list, columns) + [chart]
            elif NEIGHTBORHOOD in query_filter:
                chart = [BAR]
                return self.filterByNeighborhoodArea(class_, space_list, time_list, columns) + [chart]  
            else:
                return [], [], []
        else:
            return [], [], []
    
    def list (self, request, *args, **kwargs):
        params = self.request.query_params
        
        COLUMNS = {
            YEARS: "COLYEAR",
            MONTHS: "COLMONTH",
            DAYS: "COLDAY",
            HOURS: "COLHOUR",
            NEIGHTBORHOOD: "ID_NEIGHB",
        }

        label = "Traffic Collision/Hectare"
        time_list = self.timeFilter(TrafficCollision, COLUMNS[YEARS], params)
        space_list = self.spaceFilter(TrafficCollision, COLUMNS[NEIGHTBORHOOD], params)
        
        labels, data_list, charts = self.searchByFilter(TrafficCollision, space_list, time_list, COLUMNS, params)

        dataset = {'label': label, 'data': data_list}
        response = {
            'labels': labels, 
            'datasets': dataset, 
            'chart': charts
            }
        
        return Response(response)


# Colección de ViewSets para [TreePlot] 
class TreePlotViewSet (viewsets.ModelViewSet):
    queryset = TreePlot.objects.all()
    serializer_class = TreePlotSerializer
    
class TreePlotPointViewSet (viewsets.ModelViewSet):
    queryset = TreePlot.objects.all()
    serializer_class = TreePlotPointSerializer

'''
[TreePlot] Count Query
QueryParams:
- filter: one of (area_range, avg_diameter, avg_height, etc)
- space: (List of [Neightborhood])
'''
class TreePlotCountViewSet (viewsets.ModelViewSet, EscalaFilter):
    queryset = TreePlot.objects.all()
    serializer_class = TreePlotSerializer
    
    def searchByFilter (self, class_, space_list, columns, params):
        if 'filter' in params:
            query_filter = params.get('filter')
            
            if MUNICIPALITY in query_filter:
                chart = [BAR, PIE]
                return self.filterByMunicipality(class_, space_list, [], columns, extrapolate=True) + [chart]
            elif LOCALITY in query_filter:
                chart = [BAR, PIE]
                return self.filterByLocality(class_, space_list, [], columns, extrapolate=True) + [chart]
            elif NEIGHTBORHOOD in query_filter:
                chart = [BAR, PIE]
                return self.filterByNeightborhood(class_, space_list, [], columns, extrapolate=True) + [chart]
            elif AREA_RANGE in query_filter:
                chart = [BAR, PIE]
                return self.filterByRange(class_, columns, AREA_RANGE) + [chart]
            elif DIAMETER in query_filter:
                chart = [BAR, PIE]
                return self.filterByRange(class_, columns, DIAMETER) + [chart]
            elif HEIGHT in query_filter:
                chart = [BAR, PIE]
                return self.filterByRange(class_, columns, HEIGHT) + [chart]
            elif BASAL in query_filter:
                chart = [BAR, PIE]
                return self.filterByRange(class_, columns, BASAL) + [chart]
            elif CAREA in query_filter:
                chart = [BAR, PIE]
                return self.filterByRange(class_, columns, CAREA) + [chart]
            elif CAPLOT in query_filter:
                chart = [BAR, PIE]
                return self.filterByRange(class_, columns, CAPLOT) + [chart]
            elif CCV in query_filter:
                chart = [BAR, PIE]
                return self.filterByRange(class_, columns, CCV) + [chart]            
            else:
                return [], [], []
        else:
            return [], [], []
    
    def list (self, request, *args, **kwargs):
        params = self.request.query_params
        
        COLUMNS = {
            NEIGHTBORHOOD: "ID_NEIGHB",
            AREA_RANGE: "TPAREA",
            DIAMETER: "TPDBH",
            HEIGHT: "TPHEIG",
            BASAL: "TPBAS",
            CAREA: "TPCAREA",
            CAPLOT: "TPCAPLOT",
            CCV: "TPCCV"
        }

        label = "Tree Plot"
        space_list = self.spaceFilter(TreePlot, COLUMNS[NEIGHTBORHOOD], params)
        
        labels, data_list, charts = self.searchByFilter(TreePlot, space_list, COLUMNS, params)

        dataset = {'label': label, 'data': data_list}
        response = {
            'labels': labels, 
            'datasets': dataset, 
            'chart': charts
            }
        
        return Response(response)

'''
[TreePlot] Area Count Query
QueryParams:
- filter: one of (municipality, locality, neightborhood)
- time: (First [YEAR], Last [YEAR])
- space: (List of [Neightborhood])
'''
class TreePlotAreaCountViewSet (viewsets.ModelViewSet, EscalaFilter):
    queryset = TreePlot.objects.all()
    serializer_class = TreePlotSerializer
    
    def searchByFilter (self, class_, space_list, columns, params):
        if 'filter' in params:
            query_filter = params.get('filter')
            
            if MUNICIPALITY in query_filter:
                chart = [BAR]
                return self.filterByMunicipalityArea(class_, space_list, [], columns, extrapolate=True) + [chart]
            elif LOCALITY in query_filter:
                chart = [BAR]
                return self.filterByLocalityArea(class_, space_list, [], columns, extrapolate=True) + [chart]
            elif NEIGHTBORHOOD in query_filter:
                chart = [BAR]
                return self.filterByNeighborhoodArea(class_, space_list, [], columns, extrapolate=True) + [chart]  
            else:
                return [], [], []
        else:
            return [], [], []
    
    def list (self, request, *args, **kwargs):
        params = self.request.query_params
        
        COLUMNS = {
            NEIGHTBORHOOD: "ID_NEIGHB",
        }

        label = "Tree Plot/Hectare"
        space_list = self.spaceFilter(TreePlot, COLUMNS[NEIGHTBORHOOD], params)
        
        labels, data_list, charts = self.searchByFilter(TreePlot, space_list, COLUMNS, params)

        dataset = {'label': label, 'data': data_list}
        response = {
            'labels': labels, 
            'datasets': dataset, 
            'chart': charts
            }
        
        return Response(response)

# Colección de ViewSets para [Neightborhood]
class NeightborhoodViewSet (viewsets.ModelViewSet):
    queryset = Neightborhood.objects.all()
    serializer_class = NeightborhoodSerializer
 
# Colección de ViewSets para [Locality_bar] 
class Locality_barViewSet (viewsets.ModelViewSet):
    queryset = Locality_bar.objects.all()
    serializer_class = Locality_barSerializer

# Colección de ViewSets para [UPZ] 
class UPZViewSet (viewsets.ModelViewSet):
    queryset = UPZ.objects.all()
    serializer_class = UPZSerializer

# Colección de ViewSets para [ZAT] 
class ZATViewSet (viewsets.ModelViewSet):
    queryset = ZAT.objects.all()
    serializer_class = ZATSerializer

# Colección de ViewSets para [UrbanPerimeter] 
class UrbanPerimeterViewSet (viewsets.ModelViewSet):
    queryset = UrbanPerimeter.objects.all()
    serializer_class = UrbanPerimeterSerializer

# Colección de ViewSets para [Municipality] 
class MunicipalityViewSet (viewsets.ModelViewSet):
    queryset = Municipality.objects.all()
    serializer_class = MunicipalitySerializer
    
# Colección de ViewSets para [AirTemperature] 
class AirTemperatureViewSet (viewsets.ModelViewSet):
    queryset = AirTemperature.objects.all()
    serializer_class = AirTemperatureSerializer

# Colección de ViewSets para [Rainfall] 
class RainfallViewSet (viewsets.ModelViewSet):
    queryset = Rainfall.objects.all()
    serializer_class = RainfallSerializer

# Colección de ViewSets para [LandSurfaceTemperature] 
class LandSurfaceTemperatureViewSet (viewsets.ModelViewSet):
    queryset = LandSurfaceTemperature.objects.all()
    serializer_class = LandSurfaceTemperatureSerializer
    
    def list (self, request):
        params = self.request.query_params
        
        if 'YY' in params:
            queryset = LandSurfaceTemperature.objects.filter(YEAR=params.get("YY"))
        elif 'ID' in params:
            queryset = LandSurfaceTemperature.objects.filter(ID_LST=params.get("ID"))
        else:
            queryset = LandSurfaceTemperature.objects.all()
        
        serializer = LandSurfaceTemperatureSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data[0])

class LandSurfaceTemperatureMunMeanViewSet (viewsets.ModelViewSet, EscalaFilter):
    serializer_class = LandSurfaceTemperatureSerializer
    
    def list (self, request):        
        COLUMNS = {
            YEARS: "YEAR"
        }
        
        params = self.request.query_params
        time_list = self.timeFilter(LandSurfaceTemperature, COLUMNS[YEARS], params)
        
        data = list(LandSurfaceTemperature.objects.filter(YEAR__in=time_list).order_by(COLUMNS[YEARS]).values("RASTER", COLUMNS[YEARS]))

        means_list = dict()
        std_list = dict()
        for value in data:
            if (value[COLUMNS[YEARS]] > 1900):
                raster = GDALRaster(value['RASTER'])
                raster_data = raster.bands[0].statistics()
                mean = raster_data[2]
                std = raster_data[3]
                
                means_list[value[COLUMNS[YEARS]]] = mean
                std_list[value[COLUMNS[YEARS]]] = std
                
                     
        mun_mean = round(sum(list(means_list.values())) / len(means_list.keys()), 3)
        mun_std = round(math.sqrt(sum([std**2 for std in std_list.values()])), 3)
        
        dataset = {'label': "Barranquilla", 'data': [mun_mean, mun_std]}
        response = {
            'labels': ['mean', 'std'], 
            'datasets': dataset, 
            'chart': [LINE, BAR]
            }
        
        return Response(response)

class LandSurfaceTemperatureMeanViewSet (viewsets.ModelViewSet, EscalaFilter):
    serializer_class = LandSurfaceTemperatureSerializer
    
    def list (self, request):        
        COLUMNS = {
            YEARS: "YEAR"
        }
        
        params = self.request.query_params
        time_list = self.timeFilter(LandSurfaceTemperature, COLUMNS[YEARS], params)
        
        data = list(LandSurfaceTemperature.objects.filter(YEAR__in=time_list).order_by(COLUMNS[YEARS]).values("RASTER", COLUMNS[YEARS]))

        means_list = dict()
        std_list = dict()
        for value in data:
            if (value[COLUMNS[YEARS]] > 1900):
                raster = GDALRaster(value['RASTER'])
                raster_data = raster.bands[0].statistics()
                mean = round(raster_data[2], 3)
                std = round(raster_data[3], 3)
                
                means_list[value[COLUMNS[YEARS]]] = mean
                std_list[value[COLUMNS[YEARS]]] = std
        
        dataset = [{'label': "Means", 'data': means_list.values()},
                   {'label': "Standard Deviation", 'data': std_list.values()}]
        response = {
            'labels': means_list.keys(), 
            'datasets': dataset, 
            'chart': [LINE, BAR]
            }
        
        return Response(response)
    
# Colección de ViewSets para [NDVI] 
class NDVIViewSet (viewsets.ModelViewSet):
    serializer_class = NDVISerializer
    
    def list (self, request):
        params = self.request.query_params
        
        if 'YY' in params:
            queryset = NDVI.objects.filter(YEAR=params.get("YY"))
        elif 'ID' in params:
            queryset = NDVI.objects.filter(ID_NDVI=params.get("ID"))
        else:
            queryset = NDVI.objects.all()
        
        #print(NDVI.objects.all().values("ID_NDVI", "RASTER"))
        serializer = NDVISerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data[0])

class NDVIMunMeanViewSet (viewsets.ModelViewSet, EscalaFilter):
    serializer_class = NDVISerializer
    
    def list (self, request):        
        COLUMNS = {
            YEARS: "YEAR"
        }
        
        params = self.request.query_params
        time_list = self.timeFilter(NDVI, COLUMNS[YEARS], params)
        
        data = list(NDVI.objects.filter(YEAR__in=time_list).order_by(COLUMNS[YEARS]).values("RASTER", COLUMNS[YEARS]))

        means_list = dict()
        std_list = dict()
        for value in data:
            if (value[COLUMNS[YEARS]] > 1900):
                raster = GDALRaster(value['RASTER'])
                raster_data = raster.bands[0].statistics()
                mean = raster_data[2]
                std = raster_data[3]
                
                means_list[value[COLUMNS[YEARS]]] = mean
                std_list[value[COLUMNS[YEARS]]] = std
        
        mun_mean = round(sum(list(means_list.values())) / len(means_list.keys()), 3)
        mun_std = round(math.sqrt(sum([std**2 for std in std_list.values()])), 3)
        
        dataset = {'label': "Barranquilla", 'data': [mun_mean, mun_std]}
        response = {
            'labels': ['mean', 'std'], 
            'datasets': dataset, 
            'chart': [LINE, BAR]
            }
        
        return Response(response)

class NDVIMeanViewSet (viewsets.ModelViewSet, EscalaFilter):
    serializer_class = NDVISerializer
    
    def list (self, request):        
        COLUMNS = {
            YEARS: "YEAR"
        }
        
        params = self.request.query_params
        time_list = self.timeFilter(NDVI, COLUMNS[YEARS], params)
        
        data = list(NDVI.objects.filter(YEAR__in=time_list).order_by(COLUMNS[YEARS]).values("RASTER", COLUMNS[YEARS]))

        means_list = dict()
        std_list = dict()
        for value in data:
            if (value[COLUMNS[YEARS]] > 1900):
                raster = GDALRaster(value['RASTER'])
                raster_data = raster.bands[0].statistics()
                mean = round(raster_data[2], 3)
                std = round(raster_data[3], 3)
                
                means_list[value[COLUMNS[YEARS]]] = mean
                std_list[value[COLUMNS[YEARS]]] = std
        
        dataset = [{'label': "NDVI Means", 'data': means_list.values()},
                   {'label': "NDVI Std", 'data': std_list.values()}]
        response = {
            'labels': means_list.keys(), 
            'datasets': dataset, 
            'chart': [LINE, BAR]
            }
        
        return Response(response)

class NDVITestViewSet (viewsets.ModelViewSet):
    serializer_class = NDVITestSerializer
    
    def list (self, request):
        params = self.request.query_params
        
        if 'YY' in params:
            queryset = NDVI.objects.filter(YEAR=params.get("YY"))
        elif 'ID' in params:
            queryset = NDVI.objects.filter(ID_NDVI=params.get("ID"))
        else:
            queryset = NDVI.objects.all()
        
        serializer = NDVITestSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data[0])
