from rest_framework.response import Response
from django.db.models import Sum

from .models import Homicides, TrafficCollision, Neightborhood, Locality_bar, UPZ, ZAT, UrbanPerimeter, Municipality, TreePlot, AirTemperature, Rainfall, LandSurfaceTemperature, NDVI

from rest_framework import viewsets


from .serializer import TrafficCollisionSerializer, TrafficCollisionDateSerializer, TrafficCollisionObjectSerializer, TrafficCollisionPlaceSerializer, TrafficCollisionRoadSerializer, TrafficCollisionSeveritySerializer, TrafficCollisionVictimsNumberSerializer
from .serializer import TreePlotAreaSerializer, TrafficCollisionVictimsNumberSerializer, TreePlotBasalSerializer, TreePlotRecordsSerializer, TreePlotCanopySerializer, TreePlotDiameterSerializer, TreePlotHeightSerializer, TreePlotPointSerializer, TreePlotSerializer

from .serializer import AirTemperatureSerializer, RainfallSerializer, LandSurfaceTemperatureSerializer, NDVISerializer

from .serializer import HomicidesSerializer, HomicidesDateSerializer, TrafficCollisionSerializer, NeightborhoodSerializer, Locality_barSerializer, UPZSerializer, ZATSerializer, UrbanPerimeterSerializer, MunicipalitySerializer, TreePlotSerializer, AirTemperatureSerializer, RainfallSerializer, LandSurfaceTemperatureSerializer, NDVISerializer

# Domains
Dom_ZONE = {
    1: 'Hospital',
    2: 'Military',
    3: 'Private',
    4: 'School',
    5: 'Sports',
    6: 'Tourist',
    7: 'Not reported'
}
Dom_AREA = {
    1: 'Rural',
    2: 'Urban'
}
Dom_COLSEV = {
    1: 'Fatal',
    2: 'Injured',
    3: 'Unharmed',
    4: 'Not reported'
}
Dom_COLTYP = {
    1: 'Crash',
    2: 'Fire',
    3: 'Occupant fall',
    4: 'Pedestrian collision',
    5: 'Rollover',
    6: 'Other'
}
Dom_COLOBJ = {
    1: 'Fixed object',
    2: 'Moving object',
    3: 'Vehicle',
    4: 'Not reported'
}
Dom_COLOBJTYP = {
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




# Colección de ViewSets para [Homicides] 
class HomicidesViewSet (viewsets.ModelViewSet):
    queryset = Homicides.objects.all()
    serializer_class = HomicidesSerializer
    
class HomicidesDateViewSet (viewsets.ModelViewSet):
    queryset = Homicides.objects.all()
    serializer_class = HomicidesDateSerializer
    
# Colección de ViewSets para [TrafficCollision] 
class TrafficCollisionViewSet (viewsets.ModelViewSet):
    queryset = TrafficCollision.objects.all()
    serializer_class = TrafficCollisionSerializer

class TrafficColissionPerYearViewSet (viewsets.ModelViewSet):
    def list (self, request):
        # Get Years Registered (Unique Values on Column)
        list_years = TrafficCollision.objects.order_by('COLYEAR').values_list('COLYEAR', flat=True).distinct()
        
        labels = list_years
        data_list = [TrafficCollision.objects.filter(COLYEAR=label).count() for label in labels]
        
        dataset = {'label': 'YEAR', 'data': data_list}
        
        response = {
            'labels': labels, 
            'datasets': dataset, 
            'chart': ['bar', 'line']
            }
        return Response(response)
    
    queryset = TrafficCollision.objects.all()
    serializer_class = TrafficCollisionDateSerializer
    
class TrafficColissionPerMonthViewSet (viewsets.ModelViewSet):
    def list (self, request):
        # Get Years Registered (Unique Values on Column)
        list_years = TrafficCollision.objects.order_by('COLYEAR').values_list('COLYEAR', flat=True).distinct()
        
        # Get list of months per Year
        months_per_year = [i for i in range(1, 13)]
        list_months = {f'{year}/{month}': (month, year) for year in list_years
                                                        for month in months_per_year}
        
        labels = list_months.keys()
        data_list = [TrafficCollision.objects.filter(COLYEAR=list_months[label][1], COLMONTH=list_months[label][0]).count() for label in labels]
        
        dataset = {'label': 'YEAR-MONTH', 'data': data_list}
        
        response = {
            'labels': labels, 
            'datasets': dataset, 
            'chart': ['bar', 'line']
            }
        return Response(response)
    
    queryset = TrafficCollision.objects.all()
    serializer_class = TrafficCollisionDateSerializer

class TrafficColissionPerDaysViewSet (viewsets.ModelViewSet):
    def list (self, request):
        # Get Years Registered (Unique Values on Column)
        list_years = TrafficCollision.objects.order_by('COLYEAR').values_list('COLYEAR', flat=True).distinct()
        
        # Get list of months per Year
        months_per_year = [i for i in range(1, 13)]
        
        # Get list of days per Month
        days_for_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        list_days = {f'{year}/{month}/{day}': (year, month, day) for year in list_years
                                                                 for i, month in enumerate(months_per_year) 
                                                                 for day in range(1, days_for_month[i]+1)}
        
        labels = list_days.keys()
        data_list = [TrafficCollision.objects.filter(COLYEAR=list_days[label][2], COLMONTH=list_days[label][1], COLDAY=list_days[label][0]).count() for label in labels]
        
        dataset = {'label': 'YEAR-MONTH-DAY', 'data': data_list}
        
        response = {
            'labels': labels, 
            'datasets': dataset, 
            'chart': ['bar', 'line']
            }
        return Response(response)
    
    queryset = TrafficCollision.objects.all()
    serializer_class = TrafficCollisionDateSerializer
    
class TrafficColissionPerHourViewSet (viewsets.ModelViewSet):
    def list (self, request):
        # Get list of hours per Day
        list_hours = list(range(1, 25))
        
        labels = list_hours
        data_list = [TrafficCollision.objects.filter(COLHOUR=label).count() for label in labels]
        
        dataset = {'label': 'HOUR', 'data': data_list}
        
        response = {
            'labels': labels, 
            'datasets': dataset, 
            'chart': ['bar', 'line']
            }
        return Response(response)
    
    queryset = TrafficCollision.objects.all()
    serializer_class = TrafficCollisionDateSerializer


class TrafficCollisionObjectViewSet (viewsets.ModelViewSet):    
    def list (self, request):
        list_obj = Dom_COLOBJ.keys()
        
        labels = [Dom_COLOBJ[cod] for cod in list_obj]
        data_list = [TrafficCollision.objects.filter(COLOBJ=label).count() for label in list_obj]
        
        dataset = {'label': 'COLOBJ', 'data': data_list}
        
        response = {
            'labels': labels, 
            'datasets': dataset, 
            'description': 'Object struck during the road traffic collision',
            'chart': ['doughtnut']
            }
        
        return Response(response)
    queryset = TrafficCollision.objects.all()
    serializer_class = TrafficCollisionObjectSerializer
 
class TrafficCollisionObjectTypeViewSet (viewsets.ModelViewSet):    
    def list (self, request):
        list_obj_type = Dom_COLOBJTYP.keys()
        
        labels = [Dom_COLOBJTYP[cod] for cod in list_obj_type]
        data_list = [TrafficCollision.objects.filter(COLOBJTYP=label).count() for label in list_obj_type]
        
        dataset = {'label': 'COLOBJTYP', 'data': data_list}
        
        response = {
            'labels': labels, 
            'datasets': dataset, 
            'description': 'Type of object struck during the road traffic collision',
            'chart': ['doughtnut']
            }
        
        return Response(response)
    queryset = TrafficCollision.objects.all()
    serializer_class = TrafficCollisionObjectSerializer
    

class TrafficCollisionAreaViewSet (viewsets.ModelViewSet):
    def list (self, request):
        list_dom = Dom_AREA.keys()
        
        labels = [Dom_AREA[cod] for cod in list_dom]
        data_list = [TrafficCollision.objects.filter(COLAREA=label).count() for label in list_dom]
        
        dataset = {'label': 'COLAREA', 'data': data_list}
        
        response = {
            'labels': labels, 
            'datasets': dataset, 
            'description': 'Road traffic collision area',
            'chart': ['bar', 'pie']
            }
        
        return Response(response)
    
    queryset = TrafficCollision.objects.all()
    serializer_class = TrafficCollisionPlaceSerializer

class TrafficCollisionZoneViewSet (viewsets.ModelViewSet):
    def list (self, request):
        list_dom = Dom_ZONE.keys()
        
        labels = [Dom_ZONE[cod] for cod in list_dom]
        data_list = [TrafficCollision.objects.filter(COLZONE=label).count() for label in list_dom]
        
        dataset = {'label': 'COLZONE', 'data': data_list}
        
        response = {
            'labels': labels, 
            'datasets': dataset, 
            'description': 'Road traffic collision zone',
            'chart': ['bar', 'pie']
            }
        
        return Response(response)
    
    queryset = TrafficCollision.objects.all()
    serializer_class = TrafficCollisionPlaceSerializer


class TrafficCollisionRoadViewSet (viewsets.ModelViewSet):
    def list (self, request):
        list_dom = Dom_COLTYP.keys()
        
        labels = [Dom_ZONE[cod] for cod in list_dom]
        data_list = [TrafficCollision.objects.filter(COLTYP=label).count() for label in list_dom]
        
        dataset = {'label': 'COLTYP', 'data': data_list}
        
        response = {
            'labels': labels, 
            'datasets': dataset, 
            'description': 'Type of road traffic collision',
            'chart': ['doughtnut']
            }
        
        return Response(response)

    queryset = TrafficCollision.objects.all()
    serializer_class = TrafficCollisionRoadSerializer


class TrafficCollisionSeverityViewSet (viewsets.ModelViewSet):
    def list (self, request):
        list_dom = Dom_COLSEV.keys()
        
        labels = [Dom_COLSEV[cod] for cod in list_dom]
        data_list = [TrafficCollision.objects.filter(COLSEV=label).count() for label in list_dom]
        
        dataset = {'label': 'COLSEV', 'data': data_list}
        
        response = {
            'labels': labels, 
            'datasets': dataset, 
            'description': 'Severity of the road traffic collision victims',
            'chart': ['pie']
            }
        
        return Response(response)
    
    queryset = TrafficCollision.objects.all()
    serializer_class = TrafficCollisionSeveritySerializer


class TrafficCollisionVictimsNumberYearViewSet (viewsets.ModelViewSet):
    def list (self, request):
        # Get Years Registered (Unique Values on Column)
        list_years = TrafficCollision.objects.order_by('COLYEAR').values_list('COLYEAR', flat=True).distinct()
        
        labels = list_years
        data_list = [TrafficCollision.objects.filter(COLYEAR=label).aggregate(Sum('COLVICNUM'))['COLVICNUM__sum'] for label in labels]
        data_list = [0 if data is None else data for data in data_list]
        
        dataset = {'label': 'COLVICNUM by YEAR', 'data': data_list}
        
        response = {
            'labels': labels, 
            'datasets': dataset, 
            'description': 'Number of the road traffic collison victims per year',
            'chart': ['bar', 'line']
            }
        return Response(response)
    
    queryset = TrafficCollision.objects.all()
    serializer_class = TrafficCollisionVictimsNumberSerializer
    
class TrafficCollisionVictimsNumberMonthViewSet (viewsets.ModelViewSet):
    def list (self, request):
        # Get Years Registered (Unique Values on Column)
        list_years = TrafficCollision.objects.order_by('COLYEAR').values_list('COLYEAR', flat=True).distinct()
        
        # Get list of months per Year
        months_per_year = [i for i in range(1, 13)]
        list_months = {f'{year}/{month}': (month, year) for year in list_years
                                                        for month in months_per_year}
        
        labels = list_months.keys()
        data_list = [TrafficCollision.objects.filter(COLYEAR=list_months[label][1], COLMONTH=list_months[label][0]).aggregate(Sum('COLVICNUM'))['COLVICNUM__sum'] for label in labels]
        data_list = [0 if data is None else data for data in data_list]
        
        dataset = {'label': 'COLVICNUM by MONTH', 'data': data_list}
        
        response = {
            'labels': labels, 
            'datasets': dataset,
            'description': 'Number of the road traffic collison victims per month', 
            'chart': ['bar', 'line']
            }
        return Response(response)
    
    queryset = TrafficCollision.objects.all()
    serializer_class = TrafficCollisionVictimsNumberSerializer

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

# Colección de ViewSets para [TreePlot] 
class TreePlotViewSet (viewsets.ModelViewSet):
    queryset = TreePlot.objects.all()
    serializer_class = TreePlotSerializer
    
class TreePlotPointViewSet (viewsets.ModelViewSet):
    queryset = TreePlot.objects.all()
    serializer_class = TreePlotPointSerializer
    
class TreePlotAreaViewSet (viewsets.ModelViewSet):
    queryset = TreePlot.objects.all()
    serializer_class = TreePlotAreaSerializer
    
class TreePlotBasalViewSet (viewsets.ModelViewSet):
    queryset = TreePlot.objects.all()
    serializer_class = TreePlotBasalSerializer
    
class TreePlotRecordsViewSet (viewsets.ModelViewSet):
    queryset = TreePlot.objects.all()
    serializer_class = TreePlotRecordsSerializer
    
class TreePlotCanopyViewSet (viewsets.ModelViewSet):
    queryset = TreePlot.objects.all()
    serializer_class = TreePlotCanopySerializer
    
class TreePlotDiameterViewSet (viewsets.ModelViewSet):
    queryset = TreePlot.objects.all()
    serializer_class = TreePlotDiameterSerializer
    
class TreePlotHeightViewSet (viewsets.ModelViewSet):
    queryset = TreePlot.objects.all()
    serializer_class = TreePlotHeightSerializer
    
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


