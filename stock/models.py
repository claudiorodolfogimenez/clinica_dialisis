from django.db import models


class Insumo(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    stock_actual = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=0)
    unidad = models.CharField(max_length=30, default="unidad")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    @property
    def stock_bajo(self):
        """Retorna True si el stock actual está en o por debajo del mínimo."""
        return self.stock_actual <= self.stock_minimo


class MovimientoStock(models.Model):
    TIPO_CHOICES = [
        ("ingreso", "Ingreso"),
        ("egreso", "Egreso"),
    ]

    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cantidad = models.IntegerField()
    motivo = models.CharField(max_length=200, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.insumo} - {self.tipo} - {self.cantidad}"

    def save(self, *args, **kwargs):
        """Al guardar un movimiento, actualiza el stock_actual del insumo."""
        if self.tipo == "ingreso":
            self.insumo.stock_actual += self.cantidad
        elif self.tipo == "egreso":
            self.insumo.stock_actual -= self.cantidad
        self.insumo.save()
        super().save(*args, **kwargs)
