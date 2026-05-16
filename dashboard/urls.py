from django.urls import path
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from . import views

urlpatterns = [
    # 👉 Dashboard
    path("dashboard/", views.inicio, name="inicio"),

    # 👉 Redirección principal (login o acceso directo)
    path("", views.home, name="home"),

    # 👉 Turnos (pantalla principal)
    path("turno/", views.turno, name="turno"),

    path("sala/", views.sala, name="sala"),

    path("iniciar/<int:sesion_id>/", views.iniciar_sesion, name="iniciar_sesion"),
    path("finalizar/<int:sesion_id>/", views.finalizar_sesion, name="finalizar_sesion"),
    path("signos/<int:sesion_id>/", views.editar_signos, name="editar_signos"),
    path("historial/<int:paciente_id>/", views.historial_paciente, name="historial_paciente"),

    path(
        "historial-mensual/<int:paciente_id>/",
        views.historial_mensual,
        name="historial_mensual"
    ),

    path("paciente/nuevo/", views.crear_paciente_basico, name="crear_paciente_basico"),

    # Auth
    path("login/", auth_views.LoginView.as_view(template_name="dashboard/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/login/"), name="logout"),
]






