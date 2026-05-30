from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404

from pacientes.models import Paciente

from sesiones.models import (
    SesionDialisis,
    Puesto,
    PlanillaHemodialisis,
    ControlHorarioHemodialisis,
)

try:
    from stock.models import Insumo
except Exception:
    Insumo = None


def decimal_o_none(valor):
    try:
        return Decimal(valor.replace(",", ".")) if valor else None
    except (InvalidOperation, AttributeError):
        return None


def usuario_en_grupo(user, nombre_grupo):
    return user.groups.filter(name=nombre_grupo).exists()


def nombre_usuario(user):
    nombre = user.get_full_name()

    if nombre:
        return nombre

    return user.username


def contexto_roles(request):
    return {
        "es_enfermero": usuario_en_grupo(request.user, "Enfermeros"),
        "es_medico": usuario_en_grupo(request.user, "Medicos"),
        "es_administracion": usuario_en_grupo(request.user, "Administracion"),
        "es_superadmin": request.user.is_superuser,
        "usuario_actual": nombre_usuario(request.user),
    }


@login_required
def inicio(request):

    hoy = date.today()

    pacientes_activos = Paciente.objects.filter(
        activo=True
    ).count()

    sesiones_hoy = SesionDialisis.objects.filter(
        fecha=hoy
    ).count()

    sesiones_activas = SesionDialisis.objects.filter(
        fecha=hoy,
        estado="activa",
        finalizada=False
    ).count()

    sesiones_finalizadas = SesionDialisis.objects.filter(
        fecha=hoy,
        finalizada=True
    ).count()

    stock_alerta = 0
    insumos_alerta = []

    if Insumo:

        insumos_alerta = Insumo.objects.filter(
            activo=True,
            stock_actual__lte=20
        ).order_by("stock_actual")

        stock_alerta = insumos_alerta.count()

    ultimas_sesiones = list(
        SesionDialisis.objects
        .select_related("paciente", "puesto")
        .order_by("-fecha", "-id")[:8]
    )

    for s in ultimas_sesiones:

        try:
            s.planilla = s.planillahemodialisis
        except Exception:
            s.planilla = None

    context = {
        "hoy": hoy,
        "pacientes_activos": pacientes_activos,
        "sesiones_hoy": sesiones_hoy,
        "sesiones_activas": sesiones_activas,
        "sesiones_pendientes": 0,
        "sesiones_finalizadas": sesiones_finalizadas,
        "stock_alerta": stock_alerta,
        "insumos_alerta": insumos_alerta,
        "ultimas_sesiones": ultimas_sesiones,
    }

    context.update(contexto_roles(request))

    return render(
        request,
        "dashboard/inicio.html",
        context
    )


@login_required
def sala(request):
    return redirect("/turno/")


@login_required
def turno(request):

    es_medico = usuario_en_grupo(request.user, "Medicos")

    hoy = date.today()

    turno_actual = request.GET.get("turno", "manana")

    pacientes = Paciente.objects.filter(
        activo=True
    ).order_by("apellido", "nombre")

    sesiones_activas = (
        SesionDialisis.objects
        .filter(
            fecha=hoy,
            finalizada=False
        )
        .select_related(
            "paciente",
            "puesto",
            "medico_asignado",
            "enfermero_asignado"
        )
    )

    for s in sesiones_activas:

        try:
            s.planilla = s.planillahemodialisis
        except Exception:
            s.planilla = None

    sesiones_finalizadas = (
        SesionDialisis.objects
        .filter(
            fecha=hoy,
            finalizada=True
        )
        .select_related(
            "paciente",
            "puesto",
            "medico_asignado",
            "enfermero_asignado"
        )
    )

    for s in sesiones_finalizadas:

        try:
            s.planilla = s.planillahemodialisis
        except Exception:
            s.planilla = None

    puestos = Puesto.objects.all().order_by("numero")

    medicos = User.objects.filter(
        groups__name="Medicos"
    ).order_by("first_name")

    enfermeros = User.objects.filter(
        groups__name="Enfermeros"
    ).order_by("first_name")

    if request.method == "POST":

        if es_medico:
            return redirect("turno")

        paciente_id = request.POST.get("paciente")
        puesto_id = request.POST.get("puesto")
        medico_id = request.POST.get("medico")

        paciente = get_object_or_404(
            Paciente,
            id=paciente_id
        )

        puesto = get_object_or_404(
            Puesto,
            id=puesto_id
        )

        medico = None

        if medico_id:
            medico = User.objects.filter(
                id=medico_id
            ).first()

        enfermero = request.user

        SesionDialisis.objects.create(
            paciente=paciente,
            puesto=puesto,
            medico_asignado=medico,
            enfermero_asignado=enfermero,
            fecha=hoy,
            turno=turno_actual,
            estado="pendiente",
            finalizada=False,
        )

        return redirect("turno")

    context = {
        "hoy": hoy,
        "turno_actual": turno_actual,
        "pacientes": pacientes,
        "puestos": puestos,
        "medicos": medicos,
        "enfermeros": enfermeros,
        "sesiones_activas": sesiones_activas,
        "sesiones_finalizadas": sesiones_finalizadas,
        "sesiones_pendientes": [],
        "es_medico": es_medico,
    }

    context.update(contexto_roles(request))

    return render(
        request,
        "dashboard/turno.html",
        context
    )


@login_required
def iniciar_sesion(request, sesion_id):

    sesion = get_object_or_404(
        SesionDialisis,
        id=sesion_id
    )

    sesion.estado = "activa"
    sesion.finalizada = False

    sesion.save()

    return redirect(f"/signos/{sesion.id}/")


@login_required
def finalizar_sesion(request, sesion_id):

    sesion = get_object_or_404(
        SesionDialisis,
        id=sesion_id
    )

    sesion.estado = "finalizada"
    sesion.finalizada = True

    sesion.save()

    return redirect(
        f"/turno/?turno={sesion.turno}&fecha={sesion.fecha}"
    )


@login_required
def editar_signos(request, sesion_id):

    sesion = get_object_or_404(
        SesionDialisis,
        id=sesion_id
    )

    planilla, _ = PlanillaHemodialisis.objects.get_or_create(
        sesion=sesion
    )

    ultima_sesion_anterior = (
        SesionDialisis.objects
        .filter(
            paciente=sesion.paciente,
            finalizada=True
        )
        .exclude(id=sesion.id)
        .order_by("-fecha", "-id")
        .first()
    )

    ultimo_peso = None

    if ultima_sesion_anterior:

        try:
            ultima_planilla = ultima_sesion_anterior.planillahemodialisis
            ultimo_peso = ultima_planilla.peso_post

        except Exception:
            ultimo_peso = ultima_sesion_anterior.peso_post

    controles = []

    for i in range(1, 5):

        control, _ = ControlHorarioHemodialisis.objects.get_or_create(
            planilla=planilla,
            hora=i
        )

        controles.append(control)

    if request.method == "POST":

        peso_pre = decimal_o_none(
            request.POST.get("peso_pre")
        )

        peso_post = decimal_o_none(
            request.POST.get("peso_post")
        )

        peso_seco = decimal_o_none(
            request.POST.get("peso_seco")
        )

        hora_inicio = request.POST.get(
            "hora_inicio",
            ""
        ).strip()

        hora_fin = request.POST.get(
            "hora_fin",
            ""
        ).strip()

        # ===== SESION =====

        sesion.peso_pre = peso_pre
        sesion.peso_post = peso_post

        sesion.ta_inicial = request.POST.get(
            "ta_inicial"
        ) or ""

        sesion.ta_final = request.POST.get(
             "ta_egreso"
        ) or ""

        sesion.save()

        # ===== PLANILLA =====

        planilla.peso_pre = peso_pre
        planilla.peso_post = peso_post
        planilla.peso_seco = peso_seco

        planilla.uf_prescripta = request.POST.get(
            "uf_prescripta"
        ) or None

        planilla.temperatura_inicial = request.POST.get(
            "temperatura_inicial"
        ) or None

        planilla.frecuencia_cardiaca_inicial = request.POST.get(
            "frecuencia_cardiaca_inicial"
        ) or None

        planilla.ta_inicial = request.POST.get(
            "ta_inicial"
        ) or None

        planilla.heparina_inicial = request.POST.get(
            "heparina_inicial"
        ) or None

        planilla.hora_inicio = hora_inicio if hora_inicio else None

        planilla.acceso_vascular = request.POST.get(
            "acceso_vascular"
        ) or None

        planilla.dializador = request.POST.get(
            "dializador"
        ) or None

        planilla.concentrado = request.POST.get(
            "concentrado"
        ) or None

        planilla.agujas = request.POST.get(
            "agujas"
        ) or None

        planilla.talla = request.POST.get(
            "talla"
        ) or None

        planilla.td = request.POST.get("td") or None
        planilla.qb = request.POST.get("qb") or None
        planilla.qd = request.POST.get("qd") or None
        planilla.na = request.POST.get("na") or None

        # ===== CONTROLES =====

        for i in range(1, 5):

            control, _ = ControlHorarioHemodialisis.objects.get_or_create(
                planilla=planilla,
                hora=i
            )

            control.ta = request.POST.get(
                f"control_{i}_ta"
            ) or None

            control.ultrafiltracion = request.POST.get(
                f"control_{i}_uf"
            ) or None

            control.presion_venosa = request.POST.get(
                f"control_{i}_pv"
            ) or None

            control.qb = request.POST.get(
                f"control_{i}_qb"
            ) or None

            control.heparina_hora = request.POST.get(
                f"control_{i}_heparina"
            ) or None

            control.observacion = request.POST.get(
                f"control_{i}_observacion"
            ) or None

            control.save()

        # ===== FINAL =====

        planilla.temperatura_final = request.POST.get(
            "temperatura_final"
        ) or None

        planilla.ta_egreso = request.POST.get(
            "ta_egreso"
        ) or None

        planilla.frecuencia_cardiaca_final = request.POST.get(
            "frecuencia_cardiaca_final"
        ) or None

        planilla.uf_final = request.POST.get(
            "uf_final"
        ) or None

        planilla.hora_fin = hora_fin if hora_fin else None

        planilla.atb = request.POST.get(
            "atb"
        ) or None

        planilla.observaciones_enfermeria = request.POST.get(
            "observaciones_enfermeria"
        ) or None

        if (
            usuario_en_grupo(request.user, "Medicos")
            or request.user.is_superuser
        ):

            planilla.observaciones_medicas = request.POST.get(
                "observaciones_medicas"
            ) or None

        planilla.save()

        return redirect(
            "editar_signos",
            sesion_id=sesion.id
        )

    context = {
        "sesion": sesion,
        "planilla": planilla,
        "controles": controles,
        "ultimo_peso": ultimo_peso,
    }

    context.update(contexto_roles(request))

    return render(
        request,
        "dashboard/editar_signos.html",
        context
    )


@login_required
def crear_paciente_basico(request):

    if usuario_en_grupo(request.user, "Medicos"):
        return redirect("/turno/")

    if request.method == "POST":

        apellido = request.POST.get("apellido", "")
        nombre = request.POST.get("nombre", "")
        dni = request.POST.get("dni", "")

        if apellido and nombre:

            Paciente.objects.create(
                apellido=apellido,
                nombre=nombre,
                dni=dni,
                activo=True,
            )

        return redirect("/turno/")

    context = {}

    context.update(contexto_roles(request))

    return render(
        request,
        "dashboard/crear_paciente_basico.html",
        context
    )


@login_required
def historial_paciente(request, paciente_id):

    paciente = get_object_or_404(
        Paciente,
        id=paciente_id
    )

    sesiones = SesionDialisis.objects.filter(
        paciente=paciente
    ).order_by("-fecha", "-id")

    context = {
        "paciente": paciente,
        "sesiones": sesiones,
    }

    context.update(contexto_roles(request))

    return render(
        request,
        "dashboard/historial_paciente.html",
        context
    )


@login_required
def historial_mensual(request, paciente_id):

    paciente = get_object_or_404(
        Paciente,
        id=paciente_id
    )

    hoy = date.today()

    try:
        mes = int(request.GET.get("mes", hoy.month))
    except ValueError:
        mes = hoy.month

    try:
        anio = int(request.GET.get("anio", hoy.year))
    except ValueError:
        anio = hoy.year

    sesiones = (
        SesionDialisis.objects
        .filter(
            paciente=paciente,
            fecha__month=mes,
            fecha__year=anio
        )
        .select_related("paciente", "puesto")
        .order_by("fecha", "id")
    )

    sesiones_con_planilla = []

    for s in sesiones:

        try:
            s.planilla = s.planillahemodialisis
        except Exception:
            s.planilla = None

        controles_por_hora = {}

        if s.planilla:

            for control in s.planilla.controles.all().order_by("hora"):
                controles_por_hora[control.hora] = control

        s.controles_por_hora = controles_por_hora

        sesiones_con_planilla.append(s)

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

    context = {
        "paciente": paciente,
        "sesiones": sesiones_con_planilla,
        "mes": mes,
        "anio": anio,
        "meses": meses,
    }

    context.update(contexto_roles(request))

    return render(
        request,
        "dashboard/historial_mensual.html",
        context
    )


@login_required
def home(request):

    if usuario_en_grupo(request.user, "Administracion"):
        return redirect("lista_pacientes")

    return redirect("turno")