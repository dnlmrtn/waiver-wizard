from django.contrib import admin
from core.models import Players
# Register your models here.
class PlayersAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    pass


admin.site.register(Players, PlayersAdmin)