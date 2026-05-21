from django.db import models

# Create your models here.
class Estudiante(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    grado = models.CharField(max_length=20)
    acudiente = models.CharField(max_length=100, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nombre

    @property
    def total_ftl(self):
        return self.reportes.filter(tipo='ftl').count()

    @property
    def total_ftg(self):
        return self.reportes.filter(tipo='ftg').count()

    @property
    def total_ftgr(self):
        return self.reportes.filter(tipo='ftgr').count()

    @property
    def total_inas(self):
        return self.reportes.filter(tipo='inas').count()

class Reporte(models.Model):
    TIPO_CHOICES = [
        ('ftl', 'Falta leve'),
        ('ftg', 'Falta grave'),
        ('ftgr', 'Falta gravísima'),
        ('inas', 'Inasistencia'),
    ]
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='reportes')
    tipo = models.CharField(max_length=5, choices=TIPO_CHOICES)
    descripcion = models.TextField()
    fecha = models.DateField()

    def __str__(self):
        return f"{self.tipo} - {self.estudiante.nombre}"