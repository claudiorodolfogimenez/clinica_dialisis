from django.db import models


class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)

    dni = models.CharField(
        max_length=20,
        unique=True
    )

    fecha_nacimiento = models.DateField(
        null=True,
        blank=True
    )

    telefono = models.CharField(
        max_length=30,
        blank=True
    )

    direccion = models.CharField(
        max_length=200,
        blank=True
    )

    obra_social = models.CharField(
        max_length=100,
        blank=True
    )

    numero_afiliado = models.CharField(
        max_length=100,
        blank=True
    )

    fecha_ingreso_dialisis = models.DateField(
        null=True,
        blank=True
    )

    etiologia = models.TextField(
        blank=True
    )

    diagnostico = models.TextField(
        blank=True
    )

    acceso_vascular = models.CharField(
        max_length=100,
        blank=True
    )

    medico_tratante = models.CharField(
        max_length=100,
        blank=True
    )

    activo = models.BooleanField(
        default=True
    )

    observaciones = models.TextField(
        blank=True
    )

    creado_en = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["apellido", "nombre"]

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"