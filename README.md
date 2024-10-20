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
    - /traffic_collisions_count/
        QueryParams:
        - filter: one of the next list
                    - YY: years
                    - MM: months
                    - DD: days
                    - HH: hours
                    - municipalily: count for municipality
                    - locality: count for locality
                    - neighborhood: count for neighborhood
                    - zone
                    - area
                    - severity
                    - type
                    - object
                    - object_type
        - time: (First [YEAR], Last [YEAR])
        - space: (List of [Neighborhood]) #Each Neighborhood must be inside quotes "[Neighborhood]"
    - /traffic_collisions_area_count/
        QueryParams:
        - filter: one of the next list
                    - municipalily: count for municipality
                    - locality: count for locality
                    - neighborhood: count for neighborhood
        - time: (First [YEAR], Last [YEAR])
        - space: (List of [Neighborhood]) #Each Neighborhood must be inside quotes "[Neighborhood]"

    
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
                    - neighborhood: count for neighborhood
                    - area_range
                    - avg_diameter: average diameter
                    - avg_height: average height
                    - basal_area
                    - canopy_area
                    - area_covered
                    - canopy_volume
        - space: (List of [Neighborhood]) #Each Neighborhood must be inside quotes "[Neighborhood]"
    - /tree_plot_area_count/
        QueryParams:
        - filter: one of the next list
                    - municipalily: count for municipality
                    - locality: count for locality
                    - neighborhood: count for neighborhood
        - space: (List of [Neighborhood]) #Each Neighborhood must be inside quotes "[Neighborhood]"

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


_____________________________________________________________________________
List of Neighborhoods Available
_____________________________________________________________________________

['VILLA_CAROLINA', 'VILLA_DEL_CARMEN', '20_DE_JULIO', 
'BELLA_ARENA', 'EL_MILAGRO', 'LOS_LAURELES', 
'VILLA_SAN_CARLOS', 'VILLA_BLANCA', 'LAS_GARDENIAS', 
'LAS_FLORES', 'LAS_DUNAS', 'VILLA_SAN_PEDRO_II', 
'SAN_LUIS', 'LA_MAGDALENA', 'SAN_PEDRO', 
'CORDIALIDAD', 'CALIFORNIA', 'SANTA_HELENA', 
'EL_ROMANCE', 'VILLA_FLOR', 'EL_LIMONCITO', 
'SAN_SALVADOR', 'EL_CAMPITO', 'LOS_CONTINENTES', 
'SIAPE', 'INDUSTRIAL_NORTE', 'SAN_PEDRO_ALEJANDRINO', 
'LA_CHINITA', 'LA_SIERRA', 'CENTRO', 
'INDUSTRIAL_VIA_40', 'LAS_TRES_AVE_MARIAS', 
'LOS_ANGELES_III', 'BOYACA', 'LOS_TRUPILLOS', 
'7_DE_AGOSTO', 'CEVILLAR', 'LA_CEIBA', 'LA_CUMBRE', 
'JOSE_ANTONIO_GALAN', 'LIPAYA', 'EL_PUEBLO', 
'SAN_JOSE', 'MONTES', 'PUMAREJO', 'EL_CARMEN', 
'ATLANTICO', 'LA_PAZ', 'CIUDADELA_DE_LA_SALUD', 
'LOMA_FRESCA', 'LOS_ANGELES_I', 'NUEVO_HORIZONTE', 
'LOS_OLIVOS_I', 'LOS_ANDES', 'LOS_PINOS', 
'CORREGIMIENTO_LA_PLAYA', 'LA_LIBERTAD', 'SANTA_ANA', 
'INDUSTRIAL_VIA_40', 'PALMAS_DEL_RIO', 'POR_FIN', 
'SANTODOMINGO', 'ME_QUEJO', 'CHIQUINQUIRA', 
'NUEVA_GRANADA', 'COLINA_CAMPESTRE', 'EL_SILENCIO', 
'VILLA_DEL_ROSARIO', 'LAS_ESTRELLAS', 'LIMON', 
'MERCEDES_SUR', 'EL_RECREO', 'LAS_MERCEDES', 
'LAS_DELICIAS', 'BERNARDO_HOYOS', 'VILLA_SAN_CARLOS_II', 
'BARRIO_ABAJO', 'LOS_NOGALES', 'CIUDAD_JARDIN', 
'BOSTON', 'SANTA_MONICA', 'SIMON_BOLIVAR', 
'KALAMARY', 'AMERICA', 'LOS_ALPES', 
'LA_FLORESTA', 'VILLATE', 'LA_CONCEPCION', 
'GRANADILLO', 'LA_CAMPINA', 'EL_TABOR', 
'ALTAMIRA', 'VILLA_COUNTRY', 'CIUDADELA_20_DE_JULIO', 
'EL_POBLADO', 'EL_GOLF', 'VILLA_DEL_ESTE', 
'VILLA_SANTOS', 'SOLAIRE_NORTE', 'BUENAVISTA', 
'PARAISO', 'ALTOS_DEL_LIMON', 'LOS_OLIVOS_II', 
'EL_CASTILLO', 'LAS_PALMERAS', 'EL_GOLFO', 
'EL_RUBI', 'EL_EDEN_I', 'EL_EDEN_2000', 
'SAN_MARINO', 'UNIVERSAL', 'PASADENA', 
'CORREGIMIENTO_JUAN_MINA', 'VILLA_SEVILLA', 'PASEO_DE_LA_CASTELLANA', 
'CUCHILLA_DE_VILLATE', 'EL_ROSARIO', 'VILLAS_DE_SAN_PABLO', 
'LA_FLORIDA', 'LAS_COLINAS', 'LOS_JOBOS', 
'BUENA_ESPERANZA', 'EL_VALLE', 'SAN_FRANCISCO', 
'BELLAVISTA', 'LOS_GIRASOLES', 'LAS_CAYENAS', 
'LAS_GRANJAS', '7_DE_ABRIL', 'SANTA_MARIA', 
'SAN_NICOLAS', 'CARRIZAL', 'BUENOS_AIRES', 
'PRIMERO_DE_MAYO', 'SANTO_DOMINGO_DE_GUZMAN', 
'TAYRONA', 'LAS_AMERICAS', 'EL_SANTUARIO', 
'LA_ALBORAYA', 'LA_GLORIA', 'LAS_PALMAS', 
'KENNEDY', 'LA_SIERRITA', 'LOS_ANGELES_II', 
'LA_UNION', 'LA_VICTORIA', 'LAS_NIEVES', 
'LAS_MALVINAS', 'LA_LUZ', 'EL_BOSQUE', 
'LOS_ROSALES', 'EVARISTO_SOURDIS', 'CIUDAD_MODESTO', 
'ALFONSO_LOPEZ', 'SAN_ROQUE', 'LA_ESMERALDA', 
'NUEVA_COLOMBIA', 'SAN_ISIDRO', 'REBOLO', 
'CARLOS_MEISEL', 'LA_MANGA', 'SAN_FELIPE', 
'ZONA_FRANCA', 'LUCERO', 'LA_PRADERA', 
'OLAYA', 'BARLOVENTO', 'BETANIA', 
'MONTECRISTO', 'EL_PORVENIR', 'CAMPO_ALEGRE', 
'MODELO', 'VILLANUEVA', 'COLOMBIA', 
'EL_PRADO', 'MIRAMAR', 'ALTOS_DE_RIOMAR', 
'ALTO_PRADO', 'SAN_VICENTE', 'RIOMAR', 
'ANDALUCIA', 'LAS_TERRAZAS']



DATABASE CREDENTIALS:
Platform: Aiven
Username: Olympus Analytics
Email: administrativo@olympus-analytics.dev
Password: .YYXNj3M@uvdeD.
