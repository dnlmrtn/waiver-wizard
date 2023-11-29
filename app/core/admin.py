from django.contrib import admin
from core.models import Player
# Register your models here.
class PlayerAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    pass


admin.site.register(Player, PlayerAdmin)