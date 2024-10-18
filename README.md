# Escala
Plataforma de visualización de datos para el proyecto de investigación conjunta entre la Universidad del Norte con la Universidad de Drexel (ESCALA)

SUPERUSER
Username: olympus
Email: administrativo@olympus-analytics.dev
Password: 123456789

<EndPoints List>
_____________________________________________________________________________
  TrafficCollisions
_____________________________________________________________________________
    - /traffic_collisions/
    - /traffic_collisions_point/
        QueryParams:
        - filter: one of the next list
                    - YY: years
                    - MM: months
                    - DD: days
                    - HH: hours
                    - municipalily: count for municipality
                    - locality: count for locality
                    - neightborhood: count for neightborhood
                    - zone
                    - area
                    - severity
                    - type
                    - object
                    - object_type
        - time: (First [YEAR], Last [YEAR])
        - space: (List of [Neightborhood])
    - /traffic_collisions_count/
    
_____________________________________________________________________________
  TreePlot
_____________________________________________________________________________
    - /tree_plot/
    - /tree_plot_point/
    - /tree_plot_count/
        QueryParams:
        - filter: one of the next list
                    - municipalily: count for municipality
                    - locality: count for locality
                    - neightborhood: count for neightborhood
                    - area_range
                    - avg_diameter: average diameter
                    - avg_height: average height
                    - basal_area
                    - canopy_area
                    - area_covered
                    - canopy_volume
        - space: (List of [Neightborhood])

_____________________________________________________________________________
  Spatial Filters
_____________________________________________________________________________
    - /neightborhood/
    - /locality_bar/
    - /upz/
    - /zat/
    - /urban_perimeter/
    - /municipality/

_____________________________________________________________________________
  Rasters
_____________________________________________________________________________
    - /ndvi/
        QueryParams:
        - YY: [YEAR]
        - ID: [ID]
    - /landsurface_temperature/
        QueryParams:
        - YY: [YEAR]
        - ID: [ID]



DATABASE CREDENTIALS:
Platform: Aiven
Username: Olympus Analytics
Email: administrativo@olympus-analytics.dev
Password: .YYXNj3M@uvdeD.
