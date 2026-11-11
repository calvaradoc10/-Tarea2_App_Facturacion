from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import CategoriaForm, ClienteForm
from .models import Categoria, Cliente, Marca, Producto, Perfil


class Unidad5Tests(TestCase):
    """Comprueba los puntos 5.3, 5.4 y el reto 5.5 de la guía."""

    def setUp(self):
        self.usuario = User.objects.create_user(username="alumno", password="ClaveSegura123!")
        self.client.force_login(self.usuario)

    def test_categoria_normaliza_nombre_y_rechaza_repetido(self):
        form = CategoriaForm({"nombre": "  ofertas  ", "descripcion": "", "activo": "on"})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertEqual(Categoria.objects.get().nombre, "Ofertas")
        self.assertFalse(CategoriaForm({"nombre": "Ofertas"}).is_valid())
        self.assertFalse(CategoriaForm({"nombre": "ab"}).is_valid())

    def test_categoria_eliminar_solo_en_post_preserva_productos(self):
        categoria = Categoria.objects.create(nombre="Ofertas")
        marca = Marca.objects.create(nombre="Demo")
        producto = Producto.objects.create(nombre="Artículo", marca=marca, precio="10.00")
        producto.categorias.add(categoria)
        url = reverse("facturacion:categoria_eliminar", args=[categoria.pk])
        self.assertContains(self.client.get(url), "Se quitará de 1 producto")
        self.assertTrue(Categoria.objects.filter(pk=categoria.pk).exists())
        self.assertRedirects(self.client.post(url), reverse("facturacion:categoria_lista"))
        self.assertTrue(Producto.objects.filter(pk=producto.pk).exists())

    def test_cliente_validacion_y_paginacion_con_busqueda(self):
        datos = {"nombres": "Ana", "apellidos": "Pérez", "cedula": "12345"}
        self.assertIn("10 dígitos", str(ClienteForm(datos).errors))
        datos["cedula"] = "12345abcde"
        self.assertIn("solo números", str(ClienteForm(datos).errors))
        for n in range(7):
            Cliente.objects.create(cedula=f"09000000{n:02d}", nombres="Ana", apellidos="Prueba")
        respuesta = self.client.get(reverse("facturacion:cliente_lista"), {"q": "Prueba", "page": 2})
        self.assertContains(respuesta, "Página 2 de 2")
        self.assertEqual(len(respuesta.context["page_obj"]), 2)
        self.assertContains(self.client.get(reverse("facturacion:cliente_lista"), {"q": "0900000001"}), "0900000001")

    def test_cliente_crear_editar_y_eliminar(self):
        datos = {"cedula": "0912345678", "nombres": "Ana", "apellidos": "Pérez"}
        self.assertRedirects(self.client.post(reverse("facturacion:cliente_crear"), datos), reverse("facturacion:cliente_lista"))
        cliente = Cliente.objects.get(cedula="0912345678")
        self.assertFalse(ClienteForm(datos).is_valid())  # Cédula repetida.
        datos["nombres"] = "María"
        self.assertRedirects(self.client.post(reverse("facturacion:cliente_editar", args=[cliente.pk]), datos), reverse("facturacion:cliente_lista"))
        cliente.refresh_from_db()
        self.assertEqual(cliente.nombres, "María")
        url = reverse("facturacion:cliente_eliminar", args=[cliente.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(Cliente.objects.filter(pk=cliente.pk).exists())
        self.assertRedirects(self.client.post(url), reverse("facturacion:cliente_lista"))

    def test_perfil_pertenece_al_usuario_actual(self):
        url = reverse("facturacion:mi_perfil")
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertRedirects(self.client.post(url, {"cedula": "0912345678", "cargo": "Vendedor"}), url)
        self.assertEqual(Perfil.objects.get(usuario=self.usuario).cargo, "Vendedor")

    def test_todas_las_paginas_requieren_login(self):
        self.client.logout()
        for nombre in ("categoria_lista", "categoria_crear", "cliente_lista", "cliente_crear", "mi_perfil"):
            self.assertEqual(self.client.get(reverse(f"facturacion:{nombre}")).status_code, 302)

# Create your tests here.
