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

    pacientes_activos = Paciente.objects.filter(activo=True).count()
    sesiones_hoy = SesionDialisis.objects.filter(fecha=hoy).count()

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
        SesionDialisis.objects.select_related("paciente", "puesto")
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
    return render(request, "dashboard/inicio.html", context)


@login_required
def sala(request):
    return redirect("/turno/")


@login_required
def turno(request):
    turno_actual = request.GET.get("turno", "manana")

    fecha_get = request.GET.get("fecha")

    if fecha_get:
        try:
            hoy = datetime.strptime(fecha_get, "%Y-%m-%d").date()
        except ValueError:
            hoy = date.today()
    else:
        hoy = date.today()

    medicos = User.objects.filter(
        username__icontains="medico"
    ).order_by("first_name", "last_name", "username")

    if request.method == "POST":
        paciente_id = request.POST.get("paciente")
        puesto_id = request.POST.get("puesto")
        medico_id = request.POST.get("medico")

        

        medico = ""
        if medico_id:
            medico_user = User.objects.filter(id=medico_id).first()
            if medico_user:
                medico = nombre_usuario(medico_user)
                

        enfermero = nombre_usuario(request.user)

        if paciente_id:
            puesto = None

            if puesto_id:
                puesto = Puesto.objects.filter(id=puesto_id).first()

            sesion_existente = SesionDialisis.objects.filter(
                paciente_id=paciente_id,
                fecha=hoy,
                turno=turno_actual,
                finalizada=False,
            ).first()

            if sesion_existente:
                sesion_existente.estado = "activa"
                sesion_existente.finalizada = False
                sesion_existente.puesto = puesto
                sesion_existente.medico_asignado = medico
                sesion_existente.enfermero_asignado = enfermero
                sesion_existente.save()
            else:
                SesionDialisis.objects.create(
                    paciente_id=paciente_id,
                    puesto=puesto,
                    fecha=hoy,
                    turno=turno_actual,
                    estado="activa",
                    finalizada=False,
                    medico_asignado=medico,
                    enfermero_asignado=enfermero,
                )

        return redirect(f"/turno/?turno={turno_actual}&fecha={hoy}")

    pacientes = Paciente.objects.filter(activo=True).order_by("apellido", "nombre")
    puestos = Puesto.objects.filter(activo=True).order_by("numero")

    sesiones = list(
        SesionDialisis.objects.filter(
            fecha=hoy,
            turno=turno_actual,
        ).select_related("paciente", "puesto")
    )

    for s in sesiones:
        try:
            s.planilla = s.planillahemodialisis

            if s.planilla.hora_inicio and s.planilla.hora_fin:
                h_inicio = datetime.strptime(s.planilla.hora_inicio, "%H:%M")
                h_fin = datetime.strptime(s.planilla.hora_fin, "%H:%M")
                diferencia = h_fin - h_inicio
                horas = diferencia.seconds // 3600
                minutos = (diferencia.seconds % 3600) // 60
                s.duracion = f"{horas}h {minutos}m"
            else:
                s.duracion = None

        except Exception:
            s.planilla = None
            s.duracion = None

    sesiones_activas = [
        s for s in sesiones if s.estado == "activa" and not s.finalizada
    ]

    sesiones_finalizadas = [
        s for s in sesiones if s.finalizada
    ]

    context = {
        "hoy": hoy,
        "turno_actual": turno_actual,
        "pacientes": pacientes,
        "puestos": puestos,
        "medicos": medicos,
        "sesiones_activas": sesiones_activas,
        "sesiones_finalizadas": sesiones_finalizadas,
        "sesiones_pendientes": [],
    }

    context.update(contexto_roles(request))





    return render(request, "dashboard/turno.html", context)


@login_required
def iniciar_sesion(request, sesion_id):
    sesion = get_object_or_404(SesionDialisis, id=sesion_id)
    sesion.estado = "activa"
    sesion.finalizada = False
    sesion.save()

    return redirect(f"/signos/{sesion.id}/")


@login_required
def finalizar_sesion(request, sesion_id):
    sesion = get_object_or_404(SesionDialisis, id=sesion_id)
    sesion.estado = "finalizada"
    sesion.finalizada = True
    sesion.save()

    return redirect(f"/turno/?turno={sesion.turno}&fecha={sesion.fecha}")


@login_required
def editar_signos(request, sesion_id):
    sesion = get_object_or_404(SesionDialisis, id=sesion_id)
    planilla, _ = PlanillaHemodialisis.objects.get_or_create(sesion=sesion)

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
        peso_pre = decimal_o_none(request.POST.get("peso_pre"))

        planilla.peso_pre = peso_pre
        sesion.peso_pre = peso_pre

        planilla.uf_prescripta = request.POST.get("uf_prescripta", "")
        planilla.temperatura_inicial = request.POST.get("temperatura_inicial", "")
        planilla.frecuencia_cardiaca_inicial = request.POST.get("frecuencia_cardiaca_inicial", "")
        planilla.ta_inicial = request.POST.get("ta_inicial", "")
        planilla.heparina_inicial = request.POST.get("heparina_inicial", "")
        planilla.hora_inicio = request.POST.get("hora_inicio", "")

        sesion.ta_inicial = request.POST.get("ta_inicial", "")

        planilla.acceso_vascular = request.POST.get("acceso_vascular", "")
        planilla.dializador = request.POST.get("dializador", "")
        planilla.concentrado = request.POST.get("concentrado", "")
        planilla.agujas = request.POST.get("agujas", "")
        planilla.talla = request.POST.get("talla", "")
        planilla.peso_seco = decimal_o_none(request.POST.get("peso_seco"))
        planilla.td = request.POST.get("td", "")
        planilla.qb = request.POST.get("qb", "")
        planilla.qd = request.POST.get("qd", "")
        planilla.na = request.POST.get("na", "")

        for i in range(1, 5):
            control, _ = ControlHorarioHemodialisis.objects.get_or_create(
                planilla=planilla,
                hora=i
            )

            control.ta = request.POST.get(f"control_{i}_ta", "")
            control.ultrafiltracion = request.POST.get(f"control_{i}_uf", "")
            control.presion_venosa = request.POST.get(f"control_{i}_pv", "")
            control.qb = request.POST.get(f"control_{i}_qb", "")
            control.heparina_hora = request.POST.get(f"control_{i}_heparina", "")
            control.observacion = request.POST.get(f"control_{i}_observacion", "")
            control.save()

        peso_post = decimal_o_none(request.POST.get("peso_post"))

        planilla.peso_post = peso_post
        sesion.peso_post = peso_post

        planilla.temperatura_final = request.POST.get("temperatura_final", "")
        planilla.ta_egreso = request.POST.get("ta_egreso", "")
        planilla.frecuencia_cardiaca_final = request.POST.get("frecuencia_cardiaca_final", "")
        planilla.uf_final = request.POST.get("uf_final", "")
        planilla.hora_fin = request.POST.get("hora_fin", "")
        planilla.atb = request.POST.get("atb", "")

        if usuario_en_grupo(request.user, "Enfermeros") or request.user.is_superuser:
            planilla.observaciones_enfermeria = request.POST.get(
                "observaciones_enfermeria", ""
            )

        if usuario_en_grupo(request.user, "Medicos") or request.user.is_superuser:
            planilla.observaciones_medicas = request.POST.get(
                "observaciones_medicas", ""
            )

        sesion.ta_final = request.POST.get("ta_egreso", "")

        sesion.save()
        planilla.save()

        return redirect("editar_signos", sesion_id=sesion.id)

    context = {
        "sesion": sesion,
        "planilla": planilla,
        "controles": controles,
        "ultimo_peso": ultimo_peso,
    }

    context.update(contexto_roles(request))
    return render(request, "dashboard/editar_signos.html", context)


@login_required
def crear_paciente_basico(request):
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
    return render(request, "dashboard/crear_paciente_basico.html", context)


@login_required
def historial_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    sesiones = SesionDialisis.objects.filter(
        paciente=paciente
    ).order_by("-fecha", "-id")

    context = {
        "paciente": paciente,
        "sesiones": sesiones,
    }

    context.update(contexto_roles(request))
    return render(request, "dashboard/historial_paciente.html", context)


@login_required
def historial_mensual(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)

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