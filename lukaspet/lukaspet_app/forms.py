from django import forms
from .models import Producto, Categoria, Marca, Contacto
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class ContactoForm(forms.ModelForm):
    class Meta:
        model=Contacto
        fields='__all__'

from django.core.exceptions import ValidationError
import re

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        label='Nombre',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Ingresa tu nombre'})
    )
    last_name = forms.CharField(
        label='Apellidos',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Ingresa tus apellidos'})
    )
    username = forms.CharField(
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={'placeholder': 'Elige un nombre de usuario'})
    )
    email = forms.EmailField(
        label='Correo electrónico',
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'ejemplo@correo.com'})
    )
    phone = forms.CharField(
        label='Teléfono',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': '+56 9 XXXX XXXX'})
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingresa tu contraseña'})
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirma tu contraseña'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6'),
                Column('last_name', css_class='form-group col-md-6'),
            ),
            'username',
            'email',
            'phone',
            'password1',
            'password2',
            Submit('submit', 'Registrarse', css_class='btn btn-primary w-100 mt-3')
        )

        # Personalizar mensajes de ayuda
        self.fields['password1'].help_text = """
        Tu contraseña debe cumplir con lo siguiente:
        • Tener al menos 8 caracteres
        • No puede ser similar a tu información personal
        • No puede ser una contraseña común
        • No puede ser completamente numérica
        """

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', first_name):
            raise ValidationError('El nombre solo puede contener letras y espacios.')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', last_name):
            raise ValidationError('El apellido solo puede contener letras y espacios.')
        return last_name

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={'placeholder': 'Ingresa tu nombre de usuario'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingresa tu contraseña'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password',
            Submit('submit', 'Iniciar Sesión', css_class='btn btn-primary w-100 mt-3')
        )
    
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'marca',
                 'categoria', 'imagen', 'sku']
        labels = {
            'nombre': 'Nombre del Producto',
            'descripcion': 'Descripción',
            'precio': 'Precio (CLP)',
            'stock': 'Stock Disponible',
            'marca': 'Marca',
            'categoria': 'Categoría',
            'imagen': 'Imagen del Producto',
            'sku': 'SKU'
        }
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'precio': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'min': 0, 'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
        }

class SeguimientoPedidoForm(forms.Form):
    numero_pedido = forms.IntegerField(
        label='Número de Pedido',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Ingrese el número de su pedido'
        })
    )