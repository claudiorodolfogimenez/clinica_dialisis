from django.urls import path
from . import views

urlpatterns = [
    path("", views.lista_pacientes, name="lista_pacientes"),
    path("nuevo/", views.editar_paciente, name="nuevo_paciente"),
    path("<int:paciente_id>/", views.editar_paciente, name="editar_paciente"),
    
]