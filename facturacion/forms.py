from django import forms                         # Herramientas de formularios de Django
from .models import Marca, Producto, Categoria, Cliente, Perfil  # Modelos de la tienda

class MarcaForm(forms.ModelForm):                # ModelForm: formulario construido desde un modelo

    class Meta:                                  # Configuración del formulario
        model = Marca                            # ¿De qué modelo sale? De Marca
        fields = ["nombre", "pais_origen", "activo"]   # ¿Qué campos muestra y en qué orden?
        labels = {                               # Cambia el texto de la etiqueta de un campo
            "nombre": "Nombre de la marca",
        }
        widgets = {                              # widgets: CÓMO se dibuja cada campo en HTML
            # TextInput = <input type="text">. attrs agrega atributos HTML: aquí la clase de Bootstrap
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Samsung"}),
            "pais_origen": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Corea del Sur"}),
            # CheckboxInput = <input type="checkbox">. form-check-input es la clase de Bootstrap para casillas
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
   
    def clean_nombre(self):                      # Validación propia del campo "nombre" (clean_ + nombre del campo)
        nombre = self.cleaned_data["nombre"].strip()   # cleaned_data: los datos ya revisados. strip quita espacios
        if len(nombre) < 2:                      # Si tiene menos de 2 letras...
            raise forms.ValidationError("El nombre debe tener al menos 2 letras.")  # ...error en rojo bajo el campo
        return nombre.title()                    # Si está bien, lo devolvemos con la Primera Letra Mayúscula


# =====================================================
# FORMULARIO DE PRODUCTOS
# =====================================================

class ProductoForm(forms.ModelForm):

    class Meta:
        model = Producto

        fields = [
            "nombre",
            "descripcion",
            "marca",
            "categorias",
            "precio",
            "stock",
            "activo",
        ]

        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej: Laptop Pro 14"
            }),

            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),

            "marca": forms.Select(attrs={
                "class": "form-select"
            }),

            "categorias": forms.CheckboxSelectMultiple(attrs={
                "class": "form-check-input"
            }),

            "precio": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0"
            }),

            "stock": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0"
            }),

            "activo": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Mostrar solamente las marcas activas
        self.fields["marca"].queryset = Marca.objects.filter(
            activo=True
        )

        self.fields["marca"].empty_label = "— Elige una marca —"

    def clean_precio(self):
        precio = self.cleaned_data["precio"]

        if precio <= 0:
            raise forms.ValidationError(
                "El precio debe ser mayor que 0."
            )

        return precio


# =====================================================
# UNIDAD 5 · FORMULARIO DE CATEGORÍAS
# =====================================================
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion", "activo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Ofertas"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()  # Quita espacios a ambos lados.
        if len(nombre) < 3:
            raise forms.ValidationError("El nombre debe tener al menos 3 letras.")
        return nombre.title()  # «  ofertas  » se guarda como «Ofertas».


# =====================================================
# UNIDAD 5 · FORMULARIO DE CLIENTES
# =====================================================
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["cedula", "nombres", "apellidos", "email", "telefono", "direccion"]
        widgets = {
            "cedula": forms.TextInput(attrs={"class": "form-control", "placeholder": "10 dígitos"}),
            "nombres": forms.TextInput(attrs={"class": "form-control"}),
            "apellidos": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_cedula(self):
        cedula = self.cleaned_data["cedula"].strip()
        if len(cedula) != 10:
            raise forms.ValidationError("La cédula debe tener exactamente 10 dígitos.")
        if not cedula.isdigit():
            raise forms.ValidationError("La cédula debe contener solo números.")
        return cedula  # unique=True en el modelo revisa que no exista otra igual.


# =====================================================
# UNIDAD 5 · FORMULARIO MI PERFIL (sin usuario)
# =====================================================
class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ["cedula", "telefono", "direccion", "cargo"]
        widgets = {
            "cedula": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "cargo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Vendedor"}),
        }
