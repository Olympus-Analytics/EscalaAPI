from rest_framework import routers

from .viewsets import NeightborhoodViewSet, Locality_barViewSet, UPZViewSet, ZATViewSet, UrbanPerimeterViewSet, MunicipalityViewSet, TreePlotViewSet, AirTemperatureViewSet, RainfallViewSet, LandSurfaceTemperatureViewSet, NDVIViewSet

from .viewsets import TrafficCollisionViewSet, TrafficCollisionPointViewSet, TrafficCollisionCountViewSet
from .viewsets import TreePlotViewSet, TreePlotPointViewSet, TreePlotCountViewSet

app_name = "visualization"

router = routers.DefaultRouter()


# GEOGRAPHIC LAYERS
# [TrafficCollision] EndPoints
router.register("traffic_collisions", TrafficCollisionViewSet, basename='traffic_collisions_data')
router.register("traffic_collisions_point", TrafficCollisionPointViewSet, basename='traffic_collisions_point')
router.register("traffic_collisions_count", TrafficCollisionCountViewSet, basename='traffic_collisions_count')

# [TreePlot] EndPoints
router.register("tree_plot", TreePlotViewSet, basename='tree_plot_data')
router.register("tree_plot_point", TreePlotPointViewSet, basename='tree_plot_point')
router.register("tree_plot_count", TreePlotCountViewSet, basename='tree_plot_count')

# Spatial Filters EndPoints
router.register("neightborhood", NeightborhoodViewSet, basename='neightborhood_data')
router.register("locality_bar", Locality_barViewSet, basename='locality_bar_data')
router.register("upz", UPZViewSet, basename='upz_data')
router.register("zat", ZATViewSet, basename='zat_data')
router.register("urban_perimeter", UrbanPerimeterViewSet, basename='urban_perimeter_data')
router.register("municipality", MunicipalityViewSet, basename='municipality_data')

# Rasters EndPoints
router.register("air_temperature", AirTemperatureViewSet, basename='air_temperature_data')
router.register("rainfall", RainfallViewSet, basename='rainfall_data')
router.register("landsurface_temperature", LandSurfaceTemperatureViewSet, basename='landsurface_temperature_data')
router.register("ndvi", NDVIViewSet, basename='ndvi_data')