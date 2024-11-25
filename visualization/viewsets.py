from rest_framework.response import Response
from django.db.models import Sum, Count, Max, Min

from rest_framework import viewsets
import re, math
import numpy as np

from django.contrib.gis.gdal.raster.source import GDALRaster
from django.db import connection

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

    def filterByYear (self, class_, space_list, time_list, columns, statistics=False):
        list_years = {year: 0 for year in time_list}
          
        mun_area = sum([mun["AREA"] for mun in list(Municipality.objects.all().values("ID_MUN", "AREA"))])      
        data = list(class_.objects.filter(ID_NEIGHB__in=space_list, COLYEAR__in=time_list).order_by().values(columns[YEARS], columns[MONTHS]).order_by(columns[YEARS]).annotate(count=Count(columns[YEARS])))
        
        for value in data:
            if statistics:
                list_years[value[columns[YEARS]]] = round(value['count']/mun_area, 4)
            else:
                list_years[value[columns[YEARS]]] = value['count']
        
        if statistics:
            std_list = {year: 0 for year in time_list}
            month_count = {year: 0 for year in time_list}
            for value in data:
                year_mean = list_years[value[columns[YEARS]]]
                std_list[value[columns[YEARS]]] += (year_mean - value['count']/mun_area) ** 2
                month_count[value[columns[YEARS]]] += 1
            
            upper_std = []
            lower_std = []
            for year in list_years.keys():
                std_list[year] = np.sqrt(std_list[year]/month_count[year])
                upper_std.append(round(list_years[year] + std_list[year], 3))
                lower_std.append(round(list_years[year] - std_list[year], 3))
                
            return [list_years.keys(), [list_years.values(), upper_std, lower_std]]
        else:
            return [list_years.keys(), list_years.values()]
    
    def filterByMonth (self, class_, space_list, time_list, columns, statistics=False):
        months_per_year = [i for i in range(1, 13)]
        list_months = {f'{year}/{month}': 0 for year in time_list
                                            for month in months_per_year}
        
        mun_area = sum([mun["AREA"] for mun in list(Municipality.objects.all().values("ID_MUN", "AREA"))])
        data = list(class_.objects.filter(ID_NEIGHB__in=space_list, COLYEAR__in=time_list).order_by().values(columns[YEARS], columns[MONTHS]).order_by(columns[YEARS], columns[MONTHS]).annotate(count=Count(columns[YEARS])))
        for value in data:
            if statistics:
                list_months[f'{value[columns[YEARS]]}/{value[columns[MONTHS]]}'] = round(value['count']/mun_area, 4)
            else:
                list_months[f'{value[columns[YEARS]]}/{value[columns[MONTHS]]}'] = value['count']
                
        return [list(list_months.keys())[:-8], list(list_months.values())[:-8]]

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

        list_neigh['OTHER'] = {
            'count': 0,
            'name': 'OTHER',
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
                list_neigh['OTHER']['count'] += value['count']
                
                if extrapolate:
                    list_neigh['OTHER']['extrapolation'] = int((list_neigh['OTHER']['area'] * value['sum']) /(value['area'] * 0.0001))
        
        
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

        list_neigh['OTHER'] = {
            'count': 0,
            'name': 'OTHER',
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
                list_neigh['OTHER']['count'] += value['count']/list_neigh['OTHER']['area']
                
                if extrapolate:
                    list_neigh['OTHER']['extrapolation'] = (int((list_neigh['OTHER']['area'] * value['sum']) /(value['area'] * 0.0001)))/list_neigh['OTHER']['area']
          
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

        print(mun_area)
        tot_area = sum([list_mun[neigh]['area'] for neigh in list_mun.keys()])
        print(tot_area)

        mean = 0
        for neigh in list_mun.keys():
            if list_mun[neigh]['count'] > 0:
                if extrapolate:
                    mean += list_mun[neigh]['extrapolation']
                else:
                    mean += list_mun[neigh]['count']
        mean = round(mean/tot_area, 1)
                    
        std = 0
        for neigh in list_mun.keys():
            if list_mun[neigh]['count'] > 0:
                if extrapolate:
                    std += (list_mun[neigh]['extrapolation']/list_mun[neigh]['area'] - mean)**2 / tot_area
                else:
                    std += (list_mun[neigh]['count']/list_mun[neigh]['area'] - mean)**2 / tot_area
        std = round(np.sqrt(std), 1)

        return [['mean', 'std'], [mean, std]]
    
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
    
    def filterByLocYear (self, class_, space_list, time_list, columns, statistics=False):
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
        loc_area = dict()
        for neigh in list_loc.keys():
            if sum(list_loc[neigh]['data'].values()) > 0:
                if (list_loc[neigh]['locality'] not in loc_data.keys()):
                    loc_data[list_loc[neigh]['locality']] = [0 for i in list_loc[neigh]['data']]
                    loc_area[list_loc[neigh]['locality']] = 0
                
                loc_data[list_loc[neigh]['locality']] = [sum(i) for i in zip(loc_data[list_loc[neigh]['locality']], list_loc[neigh]['data'].values())] 
                loc_area[list_loc[neigh]['locality']] += list_loc[neigh]['area']

        labels, data_list = [], []
        for loc in loc_data.keys():
            data_count = loc_data[loc]
            area = loc_area[loc]
            if (sum(data_count) > 0):
                if statistics:
                    labels.append(loc)
                    data_list.append([data/area for data in data_count])
                else:
                    labels.append(loc)
                    data_list.append(data_count)
        
        return [labels, time_list, data_list]
    
    def filterByLocMonth (self, class_, space_list, time_list, columns, statistics=False):
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
        loc_area = dict()
        for neigh in list_loc.keys():
            if sum(list_loc[neigh]['data'].values()) > 0:
                if (list_loc[neigh]['locality'] not in loc_data.keys()):
                    loc_data[list_loc[neigh]['locality']] = [0 for i in list_loc[neigh]['data']]
                    loc_area[list_loc[neigh]['locality']] = 0
                
                loc_data[list_loc[neigh]['locality']] = [sum(i) for i in zip(loc_data[list_loc[neigh]['locality']], list_loc[neigh]['data'].values())] 
                loc_area[list_loc[neigh]['locality']] += list_loc[neigh]['area']

        
        
        labels, data_list = [], []
        for loc in loc_data.keys():
            data_count = loc_data[loc]
            area = loc_area[loc]
            if (sum(data_count) > 0):
                if statistics:
                    labels.append(loc)
                    data_list.append([data/area for data in data_count][:-8])
                else:
                    labels.append(loc)
                    data_list.append(data_count[:-8])
        
        return [labels, list(list_loc[neigh]['data'].keys())[:-8], data_list]
    
    def filterByNeighYear (self, class_, space_list, time_list, columns, statistics=False):
        neigh_values = list(Neightborhood.objects.all().filter(ID_NEIGHB__in=space_list).values("ID_NEIGHB", "NAME", "AREA"))   
        
        list_neigh = dict()
        for neigh in neigh_values:
            if neigh['NAME'] != 'NA':
                list_neigh[neigh['ID_NEIGHB']] = {
                    'count': 0,
                    'name': neigh['NAME'].replace("_", " "),
                    'area': neigh['AREA'],
                    'total': 0,
                    'data': {year: 0 for year in time_list}
                }

        list_neigh['OTHER'] = {
            'count': 0,
            'name': 'OTHER',
            'area': sum(neigh['AREA'] for neigh in neigh_values if neigh['NAME'] == 'NA'),
            'total': 0,
            'data': {year: 0 for year in time_list}
        }
        
        data = list(class_.objects.filter(ID_NEIGHB__in=space_list, COLYEAR__in=time_list).order_by().values(columns[NEIGHTBORHOOD], columns[YEARS]).order_by(columns[YEARS]).annotate(count=Count(columns[YEARS])))
        for value in data:
            try:
                if statistics:
                    list_neigh[value[columns[NEIGHTBORHOOD]]]['data'][value[columns[YEARS]]] = value['count'] / list_neigh[value[columns[NEIGHTBORHOOD]]]['area']
                    list_neigh[value[columns[NEIGHTBORHOOD]]]['total'] += value['count'] / list_neigh[value[columns[NEIGHTBORHOOD]]]['area']
                else:
                    list_neigh[value[columns[NEIGHTBORHOOD]]]['data'][value[columns[YEARS]]] = value['count']
                    list_neigh[value[columns[NEIGHTBORHOOD]]]['total'] += value['count'] 
            except:
                if statistics:
                    list_neigh['OTHER']['data'][value[columns[YEARS]]] += value['count'] / list_neigh['OTHER']['area']
                    list_neigh['OTHER']['total'] += value['count'] / list_neigh['OTHER']['area']
                else:
                    list_neigh['OTHER']['data'][value[columns[YEARS]]] += value['count']
                    list_neigh['OTHER']['total'] += value['count']
        
        list_neigh = dict(sorted(list_neigh.items(), key=lambda item: item[1]['total'], reverse=True))
        
        labels, data_list = [], []
        for neigh in list(list_neigh.keys())[:10]:
            data_count = list(list_neigh[neigh]['data'].values())
            if (sum(data_count) > 0):
                labels.append(list_neigh[neigh]['name'])
                data_list.append(data_count)
        
        return [labels, list_neigh['OTHER']['data'].keys(), data_list]
    
    def filterByNeighMonth (self, class_, space_list, time_list, columns, statistics=False):
        months_per_year = [i for i in range(1, 13)]
        neigh_values = list(Neightborhood.objects.all().filter(ID_NEIGHB__in=space_list).values("ID_NEIGHB", "NAME", "AREA"))     
        
        list_neigh = dict()
        for neigh in neigh_values:
            if neigh['NAME'] != 'NA':
                list_neigh[neigh['ID_NEIGHB']] = {
                    'count': 0,
                    'name': neigh['NAME'].replace("_", " "),
                    'area': neigh['AREA'],
                    'total': 0,
                    'data': {f'{year}/{month}': 0 for year in time_list
                                                  for month in months_per_year}
                }

        list_neigh['OTHER'] = {
            'count': 0,
            'name': 'OTHER',
            'area': sum(neigh['AREA'] for neigh in neigh_values if neigh['NAME'] == 'NA'),
            'total': 0,
            'data': {f'{year}/{month}': 0 for year in time_list
                                          for month in months_per_year}
        }
        
        data = list(class_.objects.filter(ID_NEIGHB__in=space_list, COLYEAR__in=time_list).order_by().values(columns[NEIGHTBORHOOD], columns[YEARS], columns[MONTHS]).order_by(columns[YEARS], columns[MONTHS]).annotate(count=Count(columns[YEARS])))
        for value in data:
            try:
                if statistics:
                    list_neigh[value[columns[NEIGHTBORHOOD]]]['data'][f'{value[columns[YEARS]]}/{value[columns[MONTHS]]}'] = value['count'] / list_neigh[value[columns[NEIGHTBORHOOD]]]['area']
                    list_neigh[value[columns[NEIGHTBORHOOD]]]['total'] += value['count'] / list_neigh[value[columns[NEIGHTBORHOOD]]]['area']
                else:
                    list_neigh[value[columns[NEIGHTBORHOOD]]]['data'][f'{value[columns[YEARS]]}/{value[columns[MONTHS]]}'] = value['count']
                    list_neigh[value[columns[NEIGHTBORHOOD]]]['total'] += value['count'] 
            except:
                if statistics:
                    list_neigh['OTHER']['data'][f'{value[columns[YEARS]]}/{value[columns[MONTHS]]}'] += value['count'] / list_neigh['OTHER']['area']
                    list_neigh['OTHER']['total'] += value['count'] / list_neigh['OTHER']['area']
                else:
                    list_neigh['OTHER']['data'][f'{value[columns[YEARS]]}/{value[columns[MONTHS]]}'] += value['count']
                    list_neigh['OTHER']['total'] += value['count']
        
        
        list_neigh = dict(sorted(list_neigh.items(), key=lambda item: item[1]['total'], reverse=True))
        
        labels, data_list = [], []
        for neigh in list(list_neigh.keys())[:10]:
            data_count = list(list_neigh[neigh]['data'].values())[:-8]
            if (sum(data_count) > 0):
                labels.append(list_neigh[neigh]['name'])
                data_list.append(data_count)
        
        months_list = list(list_neigh['OTHER']['data'].keys())[:-8]
        return [labels, months_list, data_list]
    
    def getRasterLocalityMean (self, class_name, id_column, locality_id, raster_ids):
        with connection.cursor() as cursor:
                    raster_ids_str = ', '.join([f"'{raster_id}'" for raster_id in raster_ids])
        
                    cursor.execute(f'''      
                        SELECT 
                            subquery."{id_column}", 
                            AVG((pvc).value) AS mean_value
                        FROM (
                            SELECT 
                                ST_ValueCount(
                                    ST_Clip(nv."RASTER", 1, ST_Transform(lb."POLY", ST_SRID(nv."RASTER")), true)
                                ) AS pvc,
                                nv."{id_column}"
                            FROM visualization_{class_name} nv, visualization_locality_bar lb
                            WHERE lb."ID_LOCALITY" = %s 
                            AND nv."{id_column}" IN ({raster_ids_str})
                        ) AS subquery
                        WHERE (pvc).value IS NOT NULL
                        AND (pvc).value != 'NaN'
                        AND (pvc).value < 100
                        AND (pvc).value > -100
                        GROUP BY subquery."{id_column}";
                    ''', [locality_id])
                    results = cursor.fetchall()
                    return results
                
        return 0
    
    def getRasterNeighMean (self, class_name, id_column, neigh_id, raster_ids):
        with connection.cursor() as cursor:
                    raster_ids_str = ', '.join([f"'{raster_id}'" for raster_id in raster_ids])
        
                    cursor.execute(f'''      
                        SELECT 
                            subquery."{id_column}", 
                            AVG((pvc).value) AS mean_value
                        FROM (
                            SELECT 
                                ST_ValueCount(
                                    ST_Clip(nv."RASTER", 1, ST_Transform(lb."POLY", ST_SRID(nv."RASTER")), true)
                                ) AS pvc,
                                nv."{id_column}"
                            FROM visualization_{class_name} nv, visualization_neightborhood lb
                            WHERE lb."ID_NEIGHB" = %s 
                            AND nv."{id_column}" IN ({raster_ids_str})
                        ) AS subquery
                        WHERE (pvc).value IS NOT NULL
                        AND (pvc).value != 'NaN'
                        AND (pvc).value < 100
                        AND (pvc).value > -100
                        GROUP BY subquery."{id_column}";
                    ''', [neigh_id])
                    results = cursor.fetchall()
                    return results
                
        return 0
    
# Colección de ViewSets para [TrafficCollision] 
class TrafficCollisionViewSet (viewsets.ModelViewSet):
    queryset = TrafficCollision.objects.all()
    serializer_class = TrafficCollisionSerializer
    
class TrafficCollisionPointViewSet (viewsets.ModelViewSet):
    serializer_class = TrafficCollisionPointSerializer
    
    def list (self, request):
        params = self.request.query_params
        
        if 'YY' in params:
            queryset = TrafficCollision.objects.filter(COLYEAR=params.get("YY"))
        
        serializer = TrafficCollisionPointSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


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

'''
[TrafficCollision] Mean Query
QueryParams:
- filter: one of (municipality_YY, municipality_MM, locality_YY, locality_MM, neighborhood_YY, neighborhood_MM)
- time: (First [YEAR], Last [YEAR])
- space: (List of [Neightborhood])
'''
class TrafficCollisionTSMeanViewSet (viewsets.ModelViewSet, EscalaFilter):
    queryset = TrafficCollision.objects.all()
    serializer_class = TrafficCollisionSerializer
    
    def searchByFilter (self, class_, space_list, time_list, columns, DOMAINS, params):
        if 'filter' in params:
            query_filter = params.get('filter')
            if MUNBYYEAR in query_filter:
                chart = [BAR, LINE]
                return [['Means', 'Upper Std', 'Lower Std']] + self.filterByYear(class_, space_list, time_list, columns, statistics=True) + [chart]
            elif MUNBYMONTH in query_filter:
                chart = [BAR, LINE]
                return [['Barranquilla']] + self.filterByMonth(class_, space_list, time_list, columns, statistics=True) + [chart]
            elif NEIGHBYYEAR in query_filter:
                chart = [LINE]
                return self.filterByNeighYear(class_, space_list, time_list, columns, statistics=True) + [chart]  
            elif NEIGHBYMONTH in query_filter:
                chart = [LINE]
                return self.filterByNeighMonth(class_, space_list, time_list, columns, statistics=True) + [chart]  
            elif LOCBYYEAR in query_filter:
                chart = [LINE]
                return self.filterByLocYear(class_, space_list, time_list, columns, statistics=True) + [chart]  
            elif LOCBYMONTH in query_filter:
                chart = [LINE]
                return self.filterByLocMonth(class_, space_list, time_list, columns, statistics=True) + [chart]    
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
[TrafficCollision] Count Query
QueryParams:
- filter: one of (municipality_YY, municipality_MM, locality_YY, locality_MM, neighborhood_YY, neighborhood_MM)
- time: (First [YEAR], Last [YEAR])
- space: (List of [Neightborhood])
'''
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
    
    def list (self, request, *args, **kwargs):
        params = self.request.query_params
        
        COLUMNS = {
            YEARS: "COLYEAR",
            MONTHS: "COLMONTH",
            DAYS: "COLDAY",
            HOURS: "COLHOUR",
            NEIGHTBORHOOD: "ID_NEIGHB",
        }

        label = "Barranquilla"
        time_list = self.timeFilter(TrafficCollision, COLUMNS[YEARS], params)
        space_list = self.spaceFilter(TrafficCollision, COLUMNS[NEIGHTBORHOOD], params)
        
        labels, data_list, charts = self.filterByMunicipalityArea(TrafficCollision, space_list, time_list, COLUMNS) + [BAR]

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

        label = "Tree Count"
        space_list = self.spaceFilter(TreePlot, COLUMNS[NEIGHTBORHOOD], params)
        
        labels, data_list, charts = self.searchByFilter(TreePlot, space_list, COLUMNS, params)

        dataset = {'label': label, 'data': data_list}
        response = {
            'labels': labels, 
            'datasets': dataset, 
            'chart': charts
            }
        
        return Response(response)


class TreePlotMunMeanViewSet (viewsets.ModelViewSet, EscalaFilter):
    queryset = TreePlot.objects.all()
    serializer_class = TreePlotSerializer
    
    def list (self, request, *args, **kwargs):
        params = self.request.query_params
        
        COLUMNS = {
            NEIGHTBORHOOD: "ID_NEIGHB",
        }

        label = "Barranquilla"
        space_list = self.spaceFilter(TreePlot, COLUMNS[NEIGHTBORHOOD], params)
        
        labels, data_list, charts = self.filterByMunicipalityArea(TreePlot, space_list, [], COLUMNS, extrapolate=True) + [BAR]

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
            
            if LOCALITY in query_filter:
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

        label = "Tree/Hectare"
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
                
                     
        mun_mean = round(sum(list(means_list.values())) / len(means_list.keys()), 1)
        mun_std = round(math.sqrt(sum([std**2 for std in std_list.values()])), 1)
        
        dataset = {'label': "Barranquilla", 'data': [mun_mean, mun_std]}
        response = {
            'labels': ['mean', 'std'], 
            'datasets': dataset, 
            'chart': [LINE, BAR]
            }
        
        return Response(response)

class LandSurfaceTemperatureMeanViewSet (viewsets.ModelViewSet, EscalaFilter):
    serializer_class = LandSurfaceTemperatureSerializer
    
    def searchByFilter (self, time_list, space_list, columns, params):
        if 'filter' in params:
            query_filter = params.get('filter')
            time_list = [year for year in time_list if year > 1900]
            
            if MUNICIPALITY in query_filter:
                data = list(LandSurfaceTemperature.objects.filter(YEAR__in=time_list).order_by(columns[YEARS]).values("RASTER", columns[YEARS]))

                means_list = dict()
                std_list = dict()
                for value in data:
                    if (value[columns[YEARS]] > 1900):
                        raster = GDALRaster(value['RASTER'])
                        raster_data = raster.bands[0].statistics()
                        mean = round(raster_data[2], 3)
                        std = round(raster_data[3], 3)
                        
                        means_list[value[columns[YEARS]]] = mean
                        std_list[value[columns[YEARS]]] = std
                
                up_std = []
                low_std = []
                std = list(std_list.values())
                for i, mean in enumerate(means_list.values()):
                    up_std.append(round(mean+std[i], 3))
                    low_std.append(round(mean-std[i], 3))
                
                dataset = [{'label': "LST Means", 'data': means_list.values()},
                            {'label': "LST upper Std", 'data': up_std},
                            {'label': "LST lower Std", 'data': low_std}]
                
                return dataset, means_list.keys()
            elif LOCALITY in query_filter:
                data = list(LandSurfaceTemperature.objects.filter(YEAR__in=time_list).order_by(columns[YEARS]).values("ID_LST", columns[YEARS]))
                print("LOCALITY")
                list_neigh = list(Neightborhood.objects.all().filter(ID_NEIGHB__in=space_list).values("ID_NEIGHB", "LOCALITY", "AREA"))   
                loc_ids = set([neigh['LOCALITY'] for neigh in list_neigh])
                loc_names = {loc["ID_LOCALITY"]: loc['NAME'] for loc in list(Locality_bar.objects.all().filter(ID_LOCALITY__in=loc_ids).values("ID_LOCALITY", "NAME"))}
                
                list_loc = dict()
                for loc in loc_names.keys():
                    list_loc[loc] = {
                        "name": loc_names[loc],
                        "data": {year: 0 for year in time_list} 
                    }               
                
                raster_ids = [raster['ID_LST'] for raster in data if raster[columns[YEARS]] > 1000]
                
                for loc in list_loc.keys():
                    mean = self.getRasterLocalityMean("landsurfacetemperature", "ID_LST", loc, raster_ids)
                    
                    for data in mean:
                        year = int(data[0].split("_")[1])
                        list_loc[loc]['data'][year] = round(data[1], 3)
                                    
                labels = time_list                
                datasets = [
                    {
                        'label': list_loc[loc]['name'],
                        'dataset': list(list_loc[loc]['data'].values())   
                    } for loc in list_loc.keys()
                ]
                
                return datasets, labels
            elif NEIGHTBORHOOD in query_filter:
                data = list(LandSurfaceTemperature.objects.filter(YEAR__in=time_list).order_by(columns[YEARS]).values("ID_LST", columns[YEARS]))
                space_list = ['NBAR177', 'NBAR187', 'NBAR167', 'NBAR186', 'NBAR014', 'NBAR188', 'NBAR150', 'NBAR164', 'NBAR180', 'NBAR189']
                list_neigh = {neigh['ID_NEIGHB']: neigh['NAME'] for neigh in Neightborhood.objects.all().filter(ID_NEIGHB__in=space_list).values("ID_NEIGHB", "NAME")}
                
                list_neighborhood = dict()
                for neigh in list_neigh.keys():
                    list_neighborhood[neigh] = {
                        "name": list_neigh[neigh],
                        "data": {year: 0 for year in time_list},
                        "sum": 0
                    }               
                
                raster_ids = [raster['ID_LST'] for raster in data if raster[columns[YEARS]] > 1000]
                
                for neigh in list_neighborhood.keys():
                    mean = self.getRasterNeighMean("landsurfacetemperature", "ID_LST", neigh, raster_ids)
                    
                    for data in mean:
                        if (list_neighborhood[neigh]['name'] == 'NA'):
                            continue
                        
                        year = int(data[0].split("_")[1])
                        list_neighborhood[neigh]['data'][year] = round(data[1], 3)
                    list_neighborhood[neigh]['sum'] = sum(list_neighborhood[neigh]['data'].values())
                
                list_neighborhood = dict(sorted(list_neighborhood.items(), key=lambda item: item[1]['sum'], reverse=True))
                                    
                labels = time_list                
                datasets = [
                    {
                        'label': list_neighborhood[neigh]['name'],
                        'dataset': list(list_neighborhood[neigh]['data'].values()) 
                    } for neigh in list_neighborhood.keys()
                ]
                
                return datasets, labels
            else:
                return [], ""
        else:
                return [], ""
            
    def list (self, request):        
        COLUMNS = {
            YEARS: "YEAR"
        }
        
        params = self.request.query_params
        time_list = self.timeFilter(NDVI, COLUMNS[YEARS], params)
        space_list = space_list = self.spaceFilter(TreePlot, 'ID_NEIGHB', params)
        
        dataset, labels = self.searchByFilter(time_list, space_list, COLUMNS, params)
        
        response = {
            'labels': labels, 
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
                print(raster_data)
                mean = raster_data[2]
                std = raster_data[3]
                
                means_list[value[COLUMNS[YEARS]]] = mean
                std_list[value[COLUMNS[YEARS]]] = std
        
        mun_mean = round(sum(list(means_list.values())) / len(means_list.keys()), 1)
        mun_std = round(math.sqrt(sum([std**2 for std in std_list.values()])), 1)
        
        dataset = {'label': "Barranquilla", 'data': [mun_mean, mun_std]}
        response = {
            'labels': ['mean', 'std'], 
            'datasets': dataset, 
            'chart': [LINE, BAR]
            }
        
        return Response(response)

class NDVIMeanViewSet (viewsets.ModelViewSet, EscalaFilter):
    serializer_class = NDVISerializer
    
    def searchByFilter (self, time_list, space_list, columns, params):
        if 'filter' in params:
            query_filter = params.get('filter')
            time_list = [year for year in time_list if year > 1900]
            
            if MUNICIPALITY in query_filter:
                data = list(NDVI.objects.filter(YEAR__in=time_list).order_by(columns[YEARS]).values("RASTER", columns[YEARS]))

                means_list = dict()
                std_list = dict()
                for value in data:
                    if (value[columns[YEARS]] > 1900):
                        raster = GDALRaster(value['RASTER'])
                        raster_data = raster.bands[0].statistics()
                        mean = round(raster_data[2], 3)
                        std = round(raster_data[3], 3)
                        
                        means_list[value[columns[YEARS]]] = mean
                        std_list[value[columns[YEARS]]] = std
                        
                up_std = []
                low_std = []
                std = list(std_list.values())
                for i, mean in enumerate(means_list.values()):
                    up_std.append(round(mean+std[i],3))
                    low_std.append(round(mean-std[i], 3))
                
                dataset = [{'label': "NDVI Means", 'data': means_list.values()},
                        {'label': "NDVI Upper Std", 'data': up_std},
                        {'label': "NDVI Lower Std", 'data': low_std}]
                
                return dataset, means_list.keys()
            elif LOCALITY in query_filter:
                data = list(NDVI.objects.filter(YEAR__in=time_list).order_by(columns[YEARS]).values("ID_NDVI", columns[YEARS]))
                print("LOCALITY")
                list_neigh = list(Neightborhood.objects.all().filter(ID_NEIGHB__in=space_list).values("ID_NEIGHB", "LOCALITY", "AREA"))   
                loc_ids = set([neigh['LOCALITY'] for neigh in list_neigh])
                loc_names = {loc["ID_LOCALITY"]: loc['NAME'] for loc in list(Locality_bar.objects.all().filter(ID_LOCALITY__in=loc_ids).values("ID_LOCALITY", "NAME"))}
                
                list_loc = dict()
                for loc in loc_names.keys():
                    list_loc[loc] = {
                        "name": loc_names[loc],
                        "data": {year: 0 for year in time_list} 
                    }               
                
                raster_ids = [raster['ID_NDVI'] for raster in data if raster[columns[YEARS]] > 1000]
                
                for loc in list_loc.keys():
                    mean = self.getRasterLocalityMean("ndvi", "ID_NDVI", loc, raster_ids)
                    
                    for data in mean:
                        year = int(data[0].split("_")[1])
                        list_loc[loc]['data'][year] = round(data[1], 3)

                labels = time_list
                datasets = [
                    {
                        'label': list_loc[loc]['name'],
                        'data': list(list_loc[loc]['data'].values())   
                    } for loc in list_loc.keys()
                ]
                
                return datasets, labels
            elif NEIGHTBORHOOD in query_filter:
                data = list(NDVI.objects.filter(YEAR__in=time_list).order_by(columns[YEARS]).values("ID_NDVI", columns[YEARS]))
                space_list = ['NBAR083', 'NBAR138', 'NBAR159', 'NBAR146', 'NBAR151', 'NBAR147', 'NBAR119', 'NBAR126', 'NBAR012', 'NBAR130']
                list_neigh = {neigh['ID_NEIGHB']: neigh['NAME'] for neigh in Neightborhood.objects.all().filter(ID_NEIGHB__in=space_list).values("ID_NEIGHB", "NAME")}
                
                list_neighborhood = dict()
                for neigh in list_neigh.keys():
                    list_neighborhood[neigh] = {
                        "name": list_neigh[neigh],
                        "data": {year: 0 for year in time_list},
                        "sum": 0
                    }               
                
                raster_ids = [raster['ID_NDVI'] for raster in data if raster[columns[YEARS]] > 1000]
                
                for neigh in list_neighborhood.keys():
                    mean = self.getRasterNeighMean("ndvi", "ID_NDVI", neigh, raster_ids)
                    
                    for data in mean:
                        if (list_neighborhood[neigh]['name'] == 'NA'):
                            continue
                        
                        year = int(data[0].split("_")[1])
                        list_neighborhood[neigh]['data'][year] = round(data[1], 3)
                    list_neighborhood[neigh]['sum'] = round(sum(list_neighborhood[neigh]['data'].values()), 3)
                
                list_neighborhood = dict(sorted(list_neighborhood.items(), key=lambda item: item[1]['sum'], reverse=True))
            
                                    
                labels = time_list                
                datasets = [
                    {
                        'label': list_neighborhood[neigh]['name'],
                        'data': list(list_neighborhood[neigh]['data'].values()) 
                    } for neigh in list_neighborhood.keys()
                ]
                
                return datasets, labels
            else:
                return [], ""
        else:
                return [], ""
    
    def list (self, request):
        COLUMNS = {
            YEARS: "YEAR"
        }
        
        params = self.request.query_params
        time_list = self.timeFilter(NDVI, COLUMNS[YEARS], params)
        space_list = space_list = self.spaceFilter(TreePlot, 'ID_NEIGHB', params)
        
        dataset, labels = self.searchByFilter(time_list, space_list, COLUMNS, params)
        
        response = {
            'labels': labels, 
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
