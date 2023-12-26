from django.contrib import admin
from core.models import Player, Endpoint
# Register your models here.
class PlayerAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    pass

class EndpointAdmin(admin.ModelAdmin):
    search_fields = ["page"]
    pass

admin.site.register(Player, PlayerAdmin)
admin.site.register(Endpoint, EndpointAdmin)