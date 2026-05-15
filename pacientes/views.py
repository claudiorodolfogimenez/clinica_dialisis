from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Paciente


@login_required
def lista_pacientes(request):

    pacientes = Paciente.objects.all().order_by(
        "apellido",
        "nombre"
    )

    return render(
        request,
        "pacientes/lista_pacientes.html",
        {
            "pacientes": pacientes
        }
    )


@login_required
def editar_paciente(request, paciente_id=None):

    paciente = None

    if paciente_id:
        paciente = get_object_or_404(
            Paciente,
            id=paciente_id
        )

    if request.method == "POST":

        if not paciente:
            paciente = Paciente()

        paciente.nombre = request.POST.get("nombre")
        paciente.apellido = request.POST.get("apellido")
        paciente.dni = request.POST.get("dni")

        paciente.fecha_nacimiento = (
            request.POST.get("fecha_nacimiento") or None
        )

        paciente.telefono = request.POST.get("telefono")
        paciente.direccion = request.POST.get("direccion")
        paciente.obra_social = request.POST.get("obra_social")
        paciente.numero_afiliado = request.POST.get("numero_afiliado")

        paciente.fecha_ingreso_dialisis = (
            request.POST.get("fecha_ingreso_dialisis") or None
        )

        paciente.etiologia = request.POST.get("etiologia")
        paciente.diagnostico = request.POST.get("diagnostico")
        paciente.acceso_vascular = request.POST.get("acceso_vascular")
        paciente.medico_tratante = request.POST.get("medico_tratante")
        paciente.observaciones = request.POST.get("observaciones")
        paciente.activo = request.POST.get("activo") == "1"
        paciente.save()

        return redirect("lista_pacientes")

    return render(
        request,
        "pacientes/editar_paciente.html",
        {
            "paciente": paciente
        }
    )
