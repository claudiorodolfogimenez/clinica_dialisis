from django.db import models
from pacientes.models import Paciente


class Puesto(models.Model):
    numero = models.PositiveIntegerField(unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Puesto {self.numero}"


class SesionDialisis(models.Model):
    TURNO_CHOICES = [
        ("manana", "Mañana"),
        ("tarde", "Tarde"),
        ("noche", "Noche"),
    ]

    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("activa", "En sesión"),
        ("finalizada", "Finalizada"),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    puesto = models.ForeignKey(Puesto, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateField()
    turno = models.CharField(max_length=10, choices=TURNO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="pendiente")

    peso_pre = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    peso_post = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ta_inicial = models.CharField(max_length=20, blank=True)
    ta_final = models.CharField(max_length=20, blank=True)

    medicacion = models.TextField(blank=True)
    incidencias = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)

    finalizada = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "turno"]

    def __str__(self):
        return f"{self.paciente} - {self.fecha} - {self.turno}"


class PlanillaEnfermeria(models.Model):
    sesion = models.OneToOneField(SesionDialisis, on_delete=models.CASCADE)

    indicaciones_medicas = models.TextField(blank=True)
    eritropoyetina = models.CharField(max_length=100, blank=True)
    hierro = models.CharField(max_length=100, blank=True)
    vacunacion = models.CharField(max_length=100, blank=True)
    antibiotico = models.CharField(max_length=100, blank=True)
    paracetamol = models.CharField(max_length=100, blank=True)
    otro = models.CharField(max_length=100, blank=True)

    medicacion_entregada = models.TextField(blank=True)
    evolucion_enfermeria = models.TextField(blank=True)

    firma_medico = models.CharField(max_length=100, blank=True)
    firma_enfermero = models.CharField(max_length=100, blank=True)
    firma_paciente = models.CharField(max_length=100, blank=True)

    creada_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Planilla enfermería - {self.sesion}"


class PlanillaHemodialisis(models.Model):
    sesion = models.OneToOneField(SesionDialisis, on_delete=models.CASCADE)

    acceso_vascular = models.CharField(max_length=100, blank=True)
    dializador = models.CharField(max_length=100, blank=True)
    concentrado = models.CharField(max_length=100, blank=True)
    agujas = models.CharField(max_length=100, blank=True)
    talla = models.CharField(max_length=50, blank=True)
    peso_seco = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    td = models.CharField(max_length=50, blank=True)
    qb = models.CharField(max_length=50, blank=True)
    qd = models.CharField(max_length=50, blank=True)
    na = models.CharField(max_length=50, blank=True)

    peso_pre = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    peso_post = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    uf_prescripta = models.CharField(max_length=50, blank=True)
    temperatura_inicial = models.CharField(max_length=50, blank=True)
    frecuencia_cardiaca_inicial = models.CharField(max_length=50, blank=True)
    ta_inicial = models.CharField(max_length=50, blank=True)
    heparina_inicial = models.CharField(max_length=100, blank=True)
    hora_inicio = models.CharField(max_length=50, blank=True)

    temperatura_final = models.CharField(max_length=50, blank=True)
    ta_egreso = models.CharField(max_length=50, blank=True)
    frecuencia_cardiaca_final = models.CharField(max_length=50, blank=True)
    uf_final = models.CharField(max_length=50, blank=True)
    hora_fin = models.CharField(max_length=50, blank=True)
    atb = models.CharField(max_length=100, blank=True)

    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Hemodiálisis - {self.sesion}"


class ControlHorarioHemodialisis(models.Model):
    planilla = models.ForeignKey(
        PlanillaHemodialisis,
        on_delete=models.CASCADE,
        related_name="controles"
    )

    hora = models.PositiveIntegerField()

    ta = models.CharField(max_length=20, blank=True)
    ultrafiltracion = models.CharField(max_length=20, blank=True)
    presion_venosa = models.CharField(max_length=20, blank=True)
    qb = models.CharField(max_length=20, blank=True)
    heparina_hora = models.CharField(max_length=50, blank=True)
    observacion = models.TextField(blank=True)

    class Meta:
        ordering = ["hora"]

    def __str__(self):
        return f"Hora {self.hora} - {self.planilla}"
