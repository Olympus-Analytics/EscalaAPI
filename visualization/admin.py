from django.contrib import admin
from .models import Homicides, TrafficCollision, Neightborhood, Locality_bar, UPZ, ZAT, UrbanPerimeter, Municipality, TreePlot

# Register your models here.
admin.site.register(Homicides)
admin.site.register(TrafficCollision)
admin.site.register(Neightborhood)
admin.site.register(Locality_bar)
admin.site.register(UPZ)
admin.site.register(ZAT)
admin.site.register(UrbanPerimeter)
admin.site.register(Municipality)
admin.site.register(TreePlot)