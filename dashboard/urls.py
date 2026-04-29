from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("sala/", views.sala, name="sala"),
    path("turno/", views.turno, name="turno"),
    path("iniciar/<int:sesion_id>/", views.iniciar_sesion, name="iniciar_sesion"),
    path("finalizar/<int:sesion_id>/", views.finalizar_sesion, name="finalizar_sesion"),
    path("signos/<int:sesion_id>/", views.editar_signos, name="editar_signos"),
    path("paciente/nuevo/", views.crear_paciente_basico, name="crear_paciente_basico"),

    path("login/", auth_views.LoginView.as_view(template_name="dashboard/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/login/"), name="logout"),
]
