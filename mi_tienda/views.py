from django.http import HttpResponse, JsonResponse
from django.contrib import messages                        # Mensajes
from django.contrib.auth import login, logout              # Abrir y cerrar sesión
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm   # NUEVO: UserCreationForm (registro)
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST


def saludo(request):
    return HttpResponse("<h1>¡Hola desde Django!</h1><p>Esto es un HttpResponse.</p>")


def info_peticion(request):
    datos = {
        "metodo": request.method,
        "ruta": request.path,
        "parametros_get": request.GET.dict(),
        "navegador": request.headers.get("User-Agent", ""),
        # NUEVO: request.user dice quién está conectado. Si nadie, decimos "anónimo"
        "usuario": request.user.username if request.user.is_authenticated else "anónimo",
    }
    return JsonResponse(datos)


def home(request):
    nombre = ""
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
    contexto = {
        "titulo": "Mi Tienda",
        "nombre": nombre,
        "productos": ["Laptop", "Mouse", "Teclado"],
    }
    return render(request, "home.html", contexto)

# =====================================================================
# AUTENTICACIÓN · se queda en funciones (VBF), como en la guía anterior
# =====================================================================

def ingresar(request):                                     # LOGIN
    if request.user.is_authenticated:                      # ya inició sesión → al inicio
        return redirect("home")
    siguiente = request.POST.get("next") or request.GET.get("next") or ""   # la página que quería ver
    if request.method == "POST":                           # presionó "Ingresar"
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():                                # usuario y clave correctos
            login(request, form.get_user())                # abre la sesión
            if siguiente and url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()}):
                return redirect(siguiente)
            return redirect("home")
    else:                                                  # GET: formulario vacío
        form = AuthenticationForm(request)
    return render(request, "registration/login.html", {"form": form, "next": siguiente})


@require_POST                                              # cerrar sesión SOLO con POST
def salir(request):                                        # LOGOUT
    logout(request)
    messages.info(request, "Cerraste sesión.")
    return redirect("login")


def registro(request):                                     # CREAR CUENTA
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()                          # crea el usuario con la clave cifrada
            login(request, usuario)
            messages.success(request, f"¡Bienvenido, {usuario.username}!")
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "registration/registro.html", {"form": form})