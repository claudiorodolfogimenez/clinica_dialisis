from django.contrib import admin
from .models import (
    Puesto,
    SesionDialisis,
    PlanillaHemodialisis,
    ControlHorarioHemodialisis
)


class ControlHorarioHemodialisisInline(admin.TabularInline):
    model = ControlHorarioHemodialisis
    extra = 0


@admin.register(PlanillaHemodialisis)
class PlanillaHemodialisisAdmin(admin.ModelAdmin):
    inlines = [ControlHorarioHemodialisisInline]


@admin.register(SesionDialisis)
class SesionDialisisAdmin(admin.ModelAdmin):
    list_display = ("paciente", "fecha", "turno", "estado", "finalizada")


admin.site.register(Puesto)