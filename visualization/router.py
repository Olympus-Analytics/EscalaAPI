from rest_framework import routers

from .viewsets import HomicidesDateViewSet, HomicidesViewSet, TrafficCollisionViewSet, NeightborhoodViewSet, Locality_barViewSet, UPZViewSet, ZATViewSet, UrbanPerimeterViewSet, MunicipalityViewSet, TreePlotViewSet, AirTemperatureViewSet, RainfallViewSet, LandSurfaceTemperatureViewSet, NDVIViewSet

from .viewsets import TrafficColissionPerYearViewSet, TrafficColissionPerMonthViewSet, TrafficColissionPerDaysViewSet, TrafficColissionPerHourViewSet
from .viewsets import TrafficCollisionObjectViewSet, TrafficCollisionObjectTypeViewSet
from .viewsets import TrafficCollisionAreaViewSet, TrafficCollisionZoneViewSet
from .viewsets import TrafficCollisionVictimsNumberYearViewSet, TrafficCollisionVictimsNumberMonthViewSet
from .viewsets import TrafficCollisionObjectViewSet, TrafficCollisionRoadViewSet, TrafficCollisionSeverityViewSet, TrafficCollisionViewSet

from .viewsets import TreePlotAreaViewSet, TreePlotBasalViewSet, TreePlotCanopyViewSet, TreePlotDiameterViewSet, TreePlotHeightViewSet, TreePlotPointViewSet, TreePlotRecordsViewSet, TreePlotViewSet

app_name = "visualization"

router = routers.DefaultRouter()

# TABLES
router.register("homicides", HomicidesViewSet, basename='homicides_data')
router.register("homicides_date", HomicidesDateViewSet, basename='homicides_date_data')

# GEOGRAPHIC LAYERS
router.register("traffic_collisions", TrafficCollisionViewSet, basename='traffic_collisions_data')
router.register("traffic_collisions_year", TrafficColissionPerYearViewSet, basename='traffic_collisions_year')
router.register("traffic_collisions_month", TrafficColissionPerMonthViewSet, basename='traffic_collisions_month')
router.register("traffic_collisions_day", TrafficColissionPerDaysViewSet, basename='traffic_collisions_day')
router.register("traffic_collisions_hour", TrafficColissionPerHourViewSet, basename='traffic_collisions_hour')

router.register("traffic_collisions_object", TrafficCollisionObjectViewSet, basename='traffic_collisions_object')
router.register("traffic_collisions_object_type", TrafficCollisionObjectTypeViewSet, basename='traffic_collisions_object_type')

router.register("traffic_collisions_area", TrafficCollisionAreaViewSet, basename='traffic_collisions_area')
router.register("traffic_collisions_zone", TrafficCollisionZoneViewSet, basename='traffic_collisions_zone')

router.register("traffic_collisions_victims_year", TrafficCollisionVictimsNumberYearViewSet, basename='traffic_collisions_victims_year')
router.register("traffic_collisions_victims_month", TrafficCollisionVictimsNumberMonthViewSet, basename='traffic_collisions_victims_month')

router.register("traffic_collisions_road", TrafficCollisionRoadViewSet, basename='traffic_collisions_road')
router.register("traffic_collisions_severity", TrafficCollisionSeverityViewSet, basename='traffic_collisions_severity')


router.register("neightborhood", NeightborhoodViewSet, basename='neightborhood_data')
router.register("locality_bar", Locality_barViewSet, basename='locality_bar_data')
router.register("upz", UPZViewSet, basename='upz_data')
router.register("zat", ZATViewSet, basename='zat_data')
router.register("urban_perimeter", UrbanPerimeterViewSet, basename='urban_perimeter_data')
router.register("municipality", MunicipalityViewSet, basename='municipality_data')

router.register("tree_plot", TreePlotViewSet, basename='tree_plot_data')
router.register("tree_plot_area", TreePlotAreaViewSet, basename='tree_plot_area')
router.register("tree_plot_basal", TreePlotBasalViewSet, basename='tree_plot_basal')
router.register("tree_plot_canopy", TreePlotCanopyViewSet, basename='tree_plot_canopy')
router.register("tree_plot_diameter", TreePlotDiameterViewSet, basename='tree_plot_diameter')
router.register("tree_plot_height", TreePlotHeightViewSet, basename='tree_plot_height')
router.register("tree_plot_point", TreePlotPointViewSet, basename='tree_plot_point')
router.register("tree_plot_records", TreePlotRecordsViewSet, basename='tree_plot_records')

# RASTERS
router.register("air_temperature", AirTemperatureViewSet, basename='air_temperature_data')
router.register("rainfall", RainfallViewSet, basename='rainfall_data')
router.register("landsurface_temperature", LandSurfaceTemperatureViewSet, basename='landsurface_temperature_data')
router.register("ndvi", NDVIViewSet, basename='ndvi_data')




