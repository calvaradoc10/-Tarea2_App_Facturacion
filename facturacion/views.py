from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError, Count, Q
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404

from .forms import MarcaForm, ProductoForm, CategoriaForm, ClienteForm, PerfilForm
from .models import Marca, Producto, Categoria, Cliente, Perfil


# =====================================================================
# MARCAS · Vistas Basadas en Funciones (VBF)
# =====================================================================


@login_required
def marca_lista(request):                                  # READ: muestra todas las marcas
    q = request.GET.get("q", "")                            # 1. Leemos el buscador: /facturacion/marcas/?q=sam (si no hay, queda "")
    marcas = Marca.objects.all()                          # 2. Pedimos todas las marcas a la base de datos

    if q:                                                  # 3. Si el usuario escribió algo en el buscador...
        marcas = marcas.filter(nombre__icontains=q)        #    ...dejamos solo las que contienen ese texto

    contexto = {                                           # 4. Datos que enviamos al template
        "titulo": "Marcas",                                #    → {{ titulo }}
        "marcas": marcas,                                  #    → {% for marca in marcas %}
        "q": q,                                            #    → para que el buscador no se borre
    }
    return render(request, "facturacion/marca_lista.html", contexto)   # 5. Mostramos la página


@login_required
def marca_crear(request):                                  # CREATE: crear una marca nueva

    if request.method == "POST":                           # ¿El usuario presionó "Guardar"? (llegó por POST)
        form = MarcaForm(request.POST)                     # 1. Llenamos el formulario con lo que escribió
        if form.is_valid():                                # 2. ¿Los datos están bien? (obligatorios, únicos, clean_nombre)
            marca = form.save()                            # 3. Guardamos en la base de datos (save devuelve la marca)
            messages.success(request, f"Marca «{marca.nombre}» creada correctamente.")   # 4. Mensaje verde
            return redirect("facturacion:marca_lista")     # 5. Vamos a la lista. Así, si recarga, no se guarda dos veces

        # Si NO es válido, no entra al if: baja hasta el render y muestra el formulario CON errores

    else:                                                  # Si llegó por GET (solo abrió la página)...
        form = MarcaForm()                                 # ...creamos un formulario vacío

    contexto = {                                           # Datos para el template
        "titulo": "Nueva marca",                           # Título de la página
        "form": form,                                      # El formulario (vacío o con errores)
        "boton": "Guardar",                                # Texto del botón
    }
    return render(request, "facturacion/marca_form.html", contexto)


@login_required
def marca_editar(request, pk):                             # UPDATE. pk llega desde la URL: /marcas/editar/3/ → pk=3
    marca = get_object_or_404(Marca, pk=pk)

    #marca = Marca.objects.get(id=pk)             # 1. Buscamos la marca. Si no existe → página 404

    if request.method == "POST":                           # 2. ¿Presionó "Actualizar"?
        form = MarcaForm(request.POST, instance=marca)     #    Datos nuevos + la marca que vamos a cambiar
        if form.is_valid():                                #    ¿Están bien?
            form.save()                                    #    Actualiza (UPDATE), no crea una nueva
            messages.success(request, f"Marca «{marca.nombre}» actualizada.")
            return redirect("facturacion:marca_lista")     #    Volvemos a la lista

    else:                                                  # 3. Llegó por GET...
        form = MarcaForm(instance=marca)                   #    ...formulario lleno con los datos actuales

    contexto = {
        "titulo": f"Editar marca: {marca.nombre}",
        "form": form,
        "boton": "Actualizar",
    }
    return render(request, "facturacion/marca_form.html", contexto)   # ¡El mismo template de crear!


@login_required
def marca_eliminar(request, pk):                           # DELETE
        if not request.user.is_staff:
            messages.error(request, "No tienes permisos para eliminar marcas.")
            return redirect("facturacion:marca_lista")
        marca = get_object_or_404(Marca, pk=pk)                # Buscamos la marca o mostramos 404

        if request.method == "POST":                           # ¿Presionó "Sí, eliminar"?
           try:                                               # Intentamos borrar...
            nombre = marca.nombre                          # Guardamos el nombre para el mensaje
            marca.delete()                                 # DELETE en la base de datos
            messages.success(request, f"Marca «{nombre}» eliminada.")

           except ProtectedError:                             # ...si tiene productos, PROTECT no deja borrarla
            messages.error(request, f"No se puede eliminar «{marca.nombre}» porque tiene productos. Desactívala en su lugar.")

        return redirect("facturacion:marca_lista")         # En los dos casos volvemos a la lista

        # Si llegó por GET: mostramos la pregunta "¿Seguro?"
        contexto = {"titulo": "Eliminar marca", "marca": marca}
        return render(request, "facturacion/marca_eliminar.html", contexto)


# =====================================================
# PRODUCTOS - LISTADO Y BÚSQUEDA
# =====================================================


@login_required
def producto_lista(request):

    # GET: obtener el texto ingresado en el buscador
    q = request.GET.get("q", "")

    # Consultar los productos con sus respectivas marcas
    productos = Producto.objects.select_related("marca").all()

    # Filtrar por nombre si el usuario realizó una búsqueda
    if q:
        productos = productos.filter(nombre__icontains=q)

    # Mostrar 5 productos por página
    paginador = Paginator(productos, 5)

    # Obtener el número de página solicitado
    numero_pagina = request.GET.get("page")

    # Obtener los productos correspondientes a esa página
    page_obj = paginador.get_page(numero_pagina)

    # Información que enviaremos al HTML
    contexto = {
        "titulo": "Listado de productos",
        "page_obj": page_obj,
        "q": q,
    }

    # Mostrar la página de productos
    return render(
        request,
        "facturacion/producto_lista.html",
        contexto
    )


# =====================================================
# PRODUCTOS - REGISTRAR UN NUEVO PRODUCTO
# =====================================================


@login_required
def producto_crear(request):                               # CREATE: crear un producto nuevo

    if request.method == "POST":                           # ¿Presionó "Guardar"? (llegó por POST)
        form = ProductoForm(request.POST)                  # 1. Llenamos el formulario con lo que envió
        if form.is_valid():                                # 2. ¿Todo bien? (obligatorios, marca existe, clean_precio...)
            producto = form.save()                         # 3. INSERT del producto + INSERT de sus categorías (N:M)
            messages.success(request, f"Producto «{producto.nombre}» creado.")
            return redirect("facturacion:producto_lista")  # 4. A la lista (Post/Redirect/Get)

        # Si NO es válido, baja hasta el render y muestra el formulario CON errores

    else:                                                  # Llegó por GET (abrió la página)...
        form = ProductoForm()                              # ...formulario vacío

    contexto = {
        "titulo": "Nuevo producto",
        "form": form,                                      # Vacío (GET) o con datos y errores (POST inválido)
        "boton": "Guardar",
    }
    return render(request, "facturacion/producto_form.html", contexto)


@login_required
def producto_editar(request, pk):                          # UPDATE. pk viene de la URL: /productos/editar/7/ → pk=7
    producto = get_object_or_404(Producto, pk=pk)          # 1. Buscamos el producto. Si no existe → página 404

    if request.method == "POST":                           # 2. ¿Presionó "Actualizar"?
        form = ProductoForm(request.POST, instance=producto)   # Datos nuevos + el producto que vamos a cambiar
        if form.is_valid():
            form.save()                                    # UPDATE del producto y reemplaza sus categorías por las marcadas
            messages.success(request, f"Producto «{producto.nombre}» actualizado.")
            return redirect("facturacion:producto_lista")

        messages.error(request, "Revisa los campos marcados en rojo.")   # Solo llega aquí si NO es válido

    else:                                                  # 3. Llegó por GET...
        form = ProductoForm(instance=producto)             #    ...formulario LLENO con los datos actuales (y sus casillas marcadas)

    contexto = {
        "titulo": f"Editar producto: {producto.nombre}",
        "form": form,
        "boton": "Actualizar",
    }
    return render(request, "facturacion/producto_form.html", contexto)   # El mismo template de crear


@login_required
def producto_detalle(request, pk):                         # READ (uno): la ficha de un producto
    producto = get_object_or_404(Producto, pk=pk)          # Buscamos el producto número pk o mostramos 404
    contexto = {"producto": producto}                      # Solo necesitamos enviar el producto
    return render(request, "facturacion/producto_detalle.html", contexto)

    # Esta vista solo atiende GET: no tiene formulario, así que no pregunta por request.method


@login_required
def producto_eliminar(request, pk):                        # DELETE
    if not request.user.is_staff:
       messages.error(request, "No tienes permisos para eliminar productos.")
       return redirect("facturacion:producto_lista")
    producto = get_object_or_404(Producto, pk=pk)          # Buscamos el producto o mostramos 404

    if request.method == "POST":                           # ¿Presionó "Sí, eliminar"?
        nombre = producto.nombre                           # Guardamos el nombre para el mensaje
        producto.delete()                                  # DELETE del producto y de sus filas en la tabla intermedia
        messages.success(request, f"Producto «{nombre}» eliminado.")   # (la marca y las categorías NO se borran)
        return redirect("facturacion:producto_lista")

    # Llegó por GET: mostramos la pregunta "¿Seguro?"
    contexto = {"titulo": "Eliminar producto", "producto": producto}
    return render(request, "facturacion/producto_eliminar.html", contexto)


# =====================================================================
# UNIDAD 5 · CATEGORÍAS · Vistas Basadas en Funciones (VBF)
# =====================================================================
@login_required
def categoria_lista(request):                              # READ · GET: lista y buscador
    q = request.GET.get("q", "").strip()                    # GET: texto buscado en ?q=...
    categorias = Categoria.objects.annotate(num_productos=Count("productos"))
    if q:
        categorias = categorias.filter(nombre__icontains=q)
    contexto = {"titulo": "Categorías", "categorias": categorias, "q": q}
    return render(request, "facturacion/categoria_lista.html", contexto)


@login_required
def categoria_crear(request):                              # CREATE · GET formulario / POST guarda
    if request.method == "POST":                           # POST: valida y guarda la categoría nueva.
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f"Categoría «{categoria.nombre}» creada correctamente.")
            return redirect("facturacion:categoria_lista")
    else:                                                  # GET: formulario vacío.
        form = CategoriaForm()
    contexto = {"titulo": "Nueva categoría", "form": form, "boton": "Guardar"}
    return render(request, "facturacion/categoria_form.html", contexto)


@login_required
def categoria_editar(request, pk):                          # UPDATE · GET muestra / POST actualiza
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == "POST":                           # POST: modifica esta categoría (instance).
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f"Categoría «{categoria.nombre}» actualizada.")
            return redirect("facturacion:categoria_lista")
    else:                                                  # GET: formulario con sus datos actuales.
        form = CategoriaForm(instance=categoria)
    contexto = {"titulo": f"Editar categoría: {categoria.nombre}", "form": form, "boton": "Actualizar"}
    return render(request, "facturacion/categoria_form.html", contexto)


@login_required
def categoria_eliminar(request, pk):                        # DELETE · GET confirma / POST elimina
    categoria = get_object_or_404(Categoria, pk=pk)
    cantidad = categoria.productos.count()                 # N productos relacionados antes de eliminar.
    if request.method == "POST":                           # POST: borra solo categoría y relaciones N:M.
        nombre = categoria.nombre
        categoria.delete()                                 # Los productos siguen existiendo.
        messages.success(request, f"Categoría «{nombre}» eliminada.")
        return redirect("facturacion:categoria_lista")
    # GET: solo se muestra la confirmación; todavía no se borra nada.
    contexto = {"titulo": "Eliminar categoría", "categoria": categoria, "cantidad": cantidad}
    return render(request, "facturacion/categoria_eliminar.html", contexto)


# =====================================================================
# UNIDAD 5 · CLIENTES · CRUD con buscador y paginación
# =====================================================================
@login_required
def cliente_lista(request):                                # READ · GET lista, búsqueda y página
    q = request.GET.get("q", "").strip()                    # GET: busca por apellido O cédula.
    clientes = Cliente.objects.all()
    if q:
        clientes = clientes.filter(Q(apellidos__icontains=q) | Q(cedula__icontains=q))
    paginador = Paginator(clientes, 5)                     # Solo cinco clientes por página.
    page_obj = paginador.get_page(request.GET.get("page"))
    contexto = {"titulo": "Clientes", "page_obj": page_obj, "q": q}
    return render(request, "facturacion/cliente_lista.html", contexto)


@login_required
def cliente_crear(request):                                # CREATE · GET muestra / POST guarda
    if request.method == "POST":                           # POST: revisa cédula y demás campos.
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f"Cliente «{cliente}» registrado correctamente.")
            return redirect("facturacion:cliente_lista")  # PRG evita repetir al presionar F5.
    else:                                                  # GET: formulario vacío.
        form = ClienteForm()
    contexto = {"titulo": "Nuevo cliente", "form": form, "boton": "Guardar"}
    return render(request, "facturacion/cliente_form.html", contexto)


@login_required
def cliente_editar(request, pk):                            # UPDATE · GET muestra / POST actualiza
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == "POST":                           # POST: guarda cambios en el mismo cliente.
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, f"Cliente «{cliente}» actualizado.")
            return redirect("facturacion:cliente_lista")
    else:                                                  # GET: formulario relleno.
        form = ClienteForm(instance=cliente)
    contexto = {"titulo": f"Editar cliente: {cliente}", "form": form, "boton": "Actualizar"}
    return render(request, "facturacion/cliente_form.html", contexto)


@login_required
def cliente_eliminar(request, pk):                          # DELETE · GET pregunta / POST borra
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == "POST":                           # POST: eliminación confirmada.
        nombre = str(cliente)
        cliente.delete()
        messages.success(request, f"Cliente «{nombre}» eliminado.")
        return redirect("facturacion:cliente_lista")
    # GET: aún no elimina; solo muestra el aviso.
    contexto = {"titulo": "Eliminar cliente", "cliente": cliente}
    return render(request, "facturacion/cliente_eliminar.html", contexto)


# =====================================================================
# UNIDAD 5 · MI PERFIL · relación 1:1 con el usuario conectado
# =====================================================================
@login_required
def mi_perfil(request):                                    # GET edita / POST guarda sin pk
    # El usuario solo puede editar SU perfil, nunca elegir un usuario por la URL.
    perfil, creado = Perfil.objects.get_or_create(usuario=request.user)
    if request.method == "POST":                           # POST: guarda la información personal.
        form = PerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu perfil se actualizó correctamente.")
            return redirect("facturacion:mi_perfil")      # Evita nuevo envío con F5.
    else:                                                  # GET: muestra datos ya guardados.
        form = PerfilForm(instance=perfil)
    contexto = {"titulo": "Mi perfil", "form": form, "boton": "Guardar cambios"}
    return render(request, "facturacion/mi_perfil.html", contexto)
