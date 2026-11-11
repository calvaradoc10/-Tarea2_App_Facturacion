from django.contrib import admin
from django.urls import path, include
from . import views                                    # Nuestras vistas (también ingresar y salir)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("saludo/", views.saludo, name="saludo"),
    path("info/", views.info_peticion, name="info"),

   # ---------- AUTENTICACIÓN: funciones (VBF) ----------
    path("login/", views.ingresar, name="login"),
    path("logout/", views.salir, name="logout"),
    path("registro/", views.registro, name="registro"),


    path("facturacion/", include("facturacion.urls")),
]