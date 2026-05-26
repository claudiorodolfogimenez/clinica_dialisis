from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Paciente
from sesiones.models import SesionDialisis


def usuario_en_grupo(user, nombre_grupo):
    return user.groups.filter(name=nombre_grupo).exists()


@login_required
def lista_pacientes(request):
    hoy = date.today()

    try:
        mes = int(request.GET.get("mes", hoy.month))
    except ValueError:
        mes = hoy.month

    try:
        anio = int(request.GET.get("anio", hoy.year))
    except ValueError:
        anio = hoy.year

    sesiones_mes = (
        SesionDialisis.objects
        .filter(
            fecha__month=mes,
            fecha__year=anio
        )
        .select_related("paciente")
        .order_by("-fecha", "-id")
    )

    pacientes = []
    vistos = set()

    for sesion in sesiones_mes:
        if sesion.paciente.id not in vistos:
            sesion.paciente.fecha_ultima_atencion = sesion.fecha
            pacientes.append(sesion.paciente)
            vistos.add(sesion.paciente.id)

    meses = [
        (1, "Enero"),
        (2, "Febrero"),
        (3, "Marzo"),
        (4, "Abril"),
        (5, "Mayo"),
        (6, "Junio"),
        (7, "Julio"),
        (8, "Agosto"),
        (9, "Septiembre"),
        (10, "Octubre"),
        (11, "Noviembre"),
        (12, "Diciembre"),
    ]

    return render(
        request,
        "pacientes/lista_pacientes.html",
        {
            "pacientes": pacientes,
            "mes": mes,
            "anio": anio,
            "meses": meses,
            "es_administracion": usuario_en_grupo(request.user, "Administracion"),
            "es_superadmin": request.user.is_superuser,
        }
    )


@login_required
def editar_paciente(request, paciente_id=None):
    paciente = None

    if paciente_id:
        paciente = get_object_or_404(Paciente, id=paciente_id)

    if request.method == "POST":
        if not paciente:
            paciente = Paciente()

        paciente.nombre = request.POST.get("nombre")
        paciente.apellido = request.POST.get("apellido")
        paciente.dni = request.POST.get("dni")

        paciente.fecha_nacimiento = request.POST.get("fecha_nacimiento") or None
        paciente.telefono = request.POST.get("telefono")
        paciente.direccion = request.POST.get("direccion")
        paciente.obra_social = request.POST.get("obra_social")
        paciente.numero_afiliado = request.POST.get("numero_afiliado")
        paciente.fecha_ingreso_dialisis = request.POST.get("fecha_ingreso_dialisis") or None
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
