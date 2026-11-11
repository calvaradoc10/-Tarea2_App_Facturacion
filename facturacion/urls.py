from django.urls import path               # path() une una dirección con una vista
from . import views                        # Las vistas de ESTA app (facturacion/views.py)

app_name = "facturacion"                   # "Apellido" de las URLs de esta app. En templates: 'facturacion:marca_lista'

urlpatterns = [
    path("marcas/", views.marca_lista, name="marca_lista"),   # /facturacion/marcas/ → vista marca_lista
    # En los pasos siguientes agregarás aquí crear, editar y eliminar
    path("marcas/crear/", views.marca_crear, name="marca_crear"),   # /facturacion/marcas/crear/
       # <int:pk> captura el número de la URL y se lo pasa a la vista como parámetro pk
    path("marcas/editar/<int:pk>/", views.marca_editar, name="marca_editar"),
    path("marcas/eliminar/<int:pk>/", views.marca_eliminar, name="marca_eliminar"),

    # ========================================
    # RUTAS DE PRODUCTOS
    # ========================================

    path(
        "productos/",
        views.producto_lista,
        name="producto_lista"
    ),   
# ========================================
# CREAR PRODUCTOS
# ========================================

    path(
        "productos/crear/",
        views.producto_crear,
        name="producto_crear"
),
    # ========================================
    # RUTAS DE PRODUCTOS
    # ========================================

    path(
        "productos/",
        views.producto_lista,
        name="producto_lista"
    ),

    path(
        "productos/crear/",
        views.producto_crear,
        name="producto_crear"
    ),

    # Editar un producto existente
    path("productos/editar/<int:pk>/", views.producto_editar, name="producto_editar"),
    # Ver información de un producto
    path("productos/<int:pk>/", views.producto_detalle, name="producto_detalle"),
    # Eliminar producto
    path("productos/eliminar/<int:pk>/", views.producto_eliminar, name="producto_eliminar"),

    # UNIDAD 5 · CATEGORÍAS: lista, creación, edición y confirmación de borrado.
    path("categorias/", views.categoria_lista, name="categoria_lista"),
    path("categorias/crear/", views.categoria_crear, name="categoria_crear"),
    path("categorias/editar/<int:pk>/", views.categoria_editar, name="categoria_editar"),
    path("categorias/eliminar/<int:pk>/", views.categoria_eliminar, name="categoria_eliminar"),

    # UNIDAD 5 · CLIENTES: lista paginada y CRUD por GET/POST.
    path("clientes/", views.cliente_lista, name="cliente_lista"),
    path("clientes/crear/", views.cliente_crear, name="cliente_crear"),
    path("clientes/editar/<int:pk>/", views.cliente_editar, name="cliente_editar"),
    path("clientes/eliminar/<int:pk>/", views.cliente_eliminar, name="cliente_eliminar"),

    # UNIDAD 5 · MI PERFIL: el usuario entra sin indicar ningún pk.
    path("mi-perfil/", views.mi_perfil, name="mi_perfil"),
]
