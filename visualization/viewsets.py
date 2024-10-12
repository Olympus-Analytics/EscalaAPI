from rest_framework.response import Response
from django.db.models import Sum, Count, Max, Min

from .models import TrafficCollision, Neightborhood, Locality_bar, UPZ, ZAT, UrbanPerimeter, Municipality, TreePlot, AirTemperature, Rainfall, LandSurfaceTemperature, NDVI

from rest_framework import viewsets
import re
import numpy as np


from .serializer import TrafficCollisionSerializer, TrafficCollisionPointSerializer
from .serializer import TreePlotSerializer, TreePlotPointSerializer

from .serializer import AirTemperatureSerializer, RainfallSerializer, LandSurfaceTemperatureSerializer, NDVISerializer

from .serializer import TrafficCollisionSerializer, NeightborhoodSerializer, Locality_barSerializer, UPZSerializer, ZATSerializer, UrbanPerimeterSerializer, MunicipalitySerializer, TreePlotSerializer, AirTemperatureSerializer, RainfallSerializer, LandSurfaceTemperatureSerializer, NDVISerializer

#Chart Domains
BAR = 'bar'
LINE = 'line'
PIE = 'pie'
DOUGHNUT = 'doughnut'

# Filters List
YEARS = "YY"
MONTHS = "MM"
DAYS = "DD"
HOURS = "HH"
MUNICIPALITY = "municipality"
LOCALITY = "locality"
NEIGHTBORHOOD = "neightborhood"

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
            pass
        else:
            pass

    def filterByYear (self, class_, time_list, columns):
        list_years = {year: 0 for year in time_list}
                
        data = list(class_.objects.filter(COLYEAR__in=time_list).order_by().values(columns[YEARS]).order_by(columns[YEARS]).annotate(count=Count(columns[YEARS])))
        for value in data:
            list_years[value[columns[YEARS]]] = value['count']
            
        return [list_years.keys(), list_years.values()]
    
    def filterByMonth (self, class_, time_list, columns):
        months_per_year = [i for i in range(1, 13)]
        list_months = {f'{year}/{month}': 0 for year in time_list
                                            for month in months_per_year}
        
        data = list(class_.objects.filter(COLYEAR__in=time_list).order_by().values(columns[YEARS], columns[MONTHS]).order_by(columns[YEARS], columns[MONTHS]).annotate(count=Count(columns[YEARS])))
        for value in data:
            list_months[f'{value[columns[YEARS]]}/{value[columns[MONTHS]]}/'] = value['count']
                
        return [list_months.keys(), list_months.values()]

    def filterByDays (self, class_, time_list, columns):
        days_for_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        months_per_year = [i for i in range(1, 13)]
        list_days = {f'{year}/{month}/{day}': 0 for year in time_list
                                                for i, month in enumerate(months_per_year) 
                                                for day in range(1, days_for_month[i]+1)}
                
        data = list(class_.objects.filter(COLYEAR__in=time_list).order_by().values(columns[YEARS], columns[MONTHS], columns[DAYS]).order_by(columns[YEARS], columns[MONTHS], columns[DAYS]).annotate(count=Count(columns[YEARS])))
        for value in data:
            list_days[f'{value[columns[YEARS]]}/{value[columns[MONTHS]]}/{value[columns[DAYS]]}'] = value['count']
                
        return [list_days.keys(), list_days.values()]
    
    def filterByHours (self, class_, time_list, columns):
        list_hours = {hour: 0 for hour in list(range(0, 24))}
                
        data = list(class_.objects.filter(COLYEAR__in=time_list).order_by().values(columns[HOURS]).order_by(columns[HOURS]).annotate(count=Count(columns[HOURS])))
        for value in data:
            list_hours[value[columns[HOURS]]] = value['count']
                    
        return [list_hours.keys(), list_hours.values()]
    
    def filterByDom (self, class_, time_list, columns, dom_list, dom):
        list_values = {dom_: 0 for dom_ in dom_list.keys()}
        
        labels = dom_list.values()
        data = list(class_.objects.filter(COLYEAR__in=time_list).order_by().values(columns[dom]).order_by(columns[dom]).annotate(count=Count(columns[dom])))
        for value in data:
            list_values[value[columns[dom]]] = value['count']
            
        return [dom_list.values(), list_values.values()]
    
    def filterByRange (self, class_, columns, col):
        max = class_.objects.aggregate(Max(columns[col]))[f"{columns[col]}__max"]
        min = class_.objects.aggregate(Min(columns[col]))[f"{columns[col]}__min"]
        range_list = np.linspace(max, min, 10)[::-1]
        print(range_list)
        
        list_values = {
            f'{round(value, 2)}-{round(range_list[i+1], 2)}': class_.objects.filter(**{f"{columns[col]}__range":(value, range_list[i+1])}).aggregate(count=Count(columns[col]))['count']
            for i, value, in enumerate(range_list[:-1])
            }
        print(list_values)
            
        return [list_values.keys(), list_values.values()]


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
    
    def searchByFilter (self, class_, time_list, columns, DOMAINS, params):
        if 'filter' in params:
            query_filter = params.get('filter')
            
            if YEARS in query_filter:
                chart = [BAR, LINE]
                return self.filterByYear(class_, time_list, columns) + [chart]
            elif MONTHS in query_filter:
                chart = [BAR, LINE]
                return self.filterByMonth(class_, time_list, columns) + [chart]
            elif DAYS in query_filter:
                chart = [BAR, LINE]
                return self.filterByDays(class_, time_list, columns) + [chart]
            elif HOURS in query_filter:
                chart = [BAR, LINE]
                return self.filterByHours(class_, time_list, columns) + [chart]
            elif MUNICIPALITY in query_filter:
                chart = [BAR, PIE]
                return [[], []] + [chart]
            elif LOCALITY in query_filter:
                chart = [BAR, PIE]
                return [[], []] + [chart]
            elif NEIGHTBORHOOD in query_filter:
                chart = [BAR, PIE]
                return [[], []] + [chart]
            elif ZONE in query_filter:
                chart = [BAR, PIE]
                return self.filterByDom(class_, time_list, columns, DOMAINS[columns[ZONE]], ZONE) + [chart]
            elif AREA in query_filter:
                chart = [BAR, PIE]
                return self.filterByDom(class_, time_list, columns, DOMAINS[columns[AREA]], AREA) + [chart]
            elif SEVERITY in query_filter:
                chart = [PIE]
                return self.filterByDom(class_, time_list, columns, DOMAINS[columns[SEVERITY]], SEVERITY) + [chart]
            elif TYPE in query_filter:
                chart = [DOUGHNUT]
                return self.filterByDom(class_, time_list, columns, DOMAINS[columns[TYPE]], TYPE) + [chart]
            elif OBJ in query_filter:
                chart = [DOUGHNUT]
                return self.filterByDom(class_, time_list, columns, DOMAINS[columns[OBJ]], OBJ) + [chart]
            elif OBJTYP in query_filter:
                chart = [DOUGHNUT]
                return self.filterByDom(class_, time_list, columns, DOMAINS[columns[OBJTYP]], OBJTYP) + [chart]
            
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
            NEIGHTBORHOOD: "COLNEIGH",
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
        
        labels, data_list, charts = self.searchByFilter(TrafficCollision, time_list, COLUMNS, DOMAINS, params)

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
    
    def searchByFilter (self, class_, columns, params):
        if 'filter' in params:
            query_filter = params.get('filter')
            
            if MUNICIPALITY in query_filter:
                chart = [BAR, PIE]
                return [], [] + chart
            elif LOCALITY in query_filter:
                chart = [BAR, PIE]
                return [], [] + chart
            elif NEIGHTBORHOOD in query_filter:
                chart = [BAR, PIE]
                return [], [] + chart
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
            NEIGHTBORHOOD: "TPNEIGH",
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
        
        labels, data_list, charts = self.searchByFilter(TreePlot, COLUMNS, params)

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

# Colección de ViewSets para [NDVI] 
class NDVIViewSet (viewsets.ModelViewSet):
    queryset = NDVI.objects.all()
    serializer_class = NDVISerializer


