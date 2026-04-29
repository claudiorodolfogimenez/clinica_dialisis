from django.contrib import admin

from .models import (
    Puesto,
    SesionDialisis,
    PlanillaEnfermeria,
    PlanillaHemodialisis,
    ControlHorarioHemodialisis,
)


@admin.register(Puesto)
class PuestoAdmin(admin.ModelAdmin):
    list_display = ("numero", "activo")
    list_filter = ("activo",)
    search_fields = ("numero",)


@admin.register(SesionDialisis)
class SesionDialisisAdmin(admin.ModelAdmin):
    list_display = (
        "paciente",
        "fecha",
        "turno",
        "puesto",
        "estado",
        "finalizada",
    )
    list_filter = ("fecha", "turno", "estado", "finalizada")
    search_fields = (
        "paciente__apellido",
        "paciente__nombre",
        "paciente__dni",
    )
    date_hierarchy = "fecha"


@admin.register(PlanillaEnfermeria)
class PlanillaEnfermeriaAdmin(admin.ModelAdmin):
    list_display = (
        "sesion",
        "firma_medico",
        "firma_enfermero",
        "firma_paciente",
        "creada_en",
    )
    search_fields = (
        "sesion__paciente__apellido",
        "sesion__paciente__nombre",
        "sesion__paciente__dni",
    )
    list_filter = ("creada_en",)


class ControlHorarioHemodialisisInline(admin.TabularInline):
    model = ControlHorarioHemodialisis
    extra = 4
    fields = (
        "hora",
        "ta",
        "ultrafiltracion",
        "presion_venosa",
        "qb",
        "heparina_hora",
        "observacion",
    )


@admin.register(PlanillaHemodialisis)
class PlanillaHemodialisisAdmin(admin.ModelAdmin):
    list_display = (
        "sesion",
        "acceso_vascular",
        "dializador",
        "peso_seco",
        "qb",
    )
    search_fields = (
        "sesion__paciente__apellido",
        "sesion__paciente__nombre",
        "sesion__paciente__dni",
    )
    inlines = [ControlHorarioHemodialisisInline]


@admin.register(ControlHorarioHemodialisis)
class ControlHorarioHemodialisisAdmin(admin.ModelAdmin):
    list_display = (
        "planilla",
        "hora",
        "ta",
        "ultrafiltracion",
        "presion_venosa",
        "qb",
        "heparina_hora",
    )
    search_fields = (
        "planilla__sesion__paciente__apellido",
        "planilla__sesion__paciente__nombre",
        "planilla__sesion__paciente__dni",
    )