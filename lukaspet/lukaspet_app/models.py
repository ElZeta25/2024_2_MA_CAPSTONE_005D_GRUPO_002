from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.contrib.auth.models import User
from django.db.models import Sum, F

# Create your models here.
class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    
    class Meta:
        verbose_name_plural = "Categorías"
    
    def __str__(self):
        return self.nombre
    
class Marca(models.Model):
    nombre = models.CharField(max_length=50)
    
    def __str__(self):
        return self.nombre
    
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Precio en pesos chilenos (CLP)"
    )
    stock = models.PositiveIntegerField(default=0)
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    imagen = models.ImageField(upload_to="productos/")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    sku = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
    def __str__(self):
        return self.nombre

    @property
    def precio_formato_clp(self):
        return f"${{:,}}".format(self.precio).replace(',', '.')
    
opciones_consultas=[
    [0,"Consulta"],
    [1,"Reclamo"],
    [2,"Sugerencia"],
    [3,"Felicitaciones"]
]

class Contacto(models.Model):
    nombre=models.CharField(max_length=50)
    apellido_paterno=models.CharField(max_length=50)
    apellido_materno=models.CharField(max_length=50)
    rut=models.CharField(max_length=9)
    direccion=models.CharField(max_length=30)
    correo=models.EmailField()
    tipo_consulta=models.IntegerField(choices=opciones_consultas)
    mensaje=models.TextField()
    avisos=models.BooleanField()

    def __str__(self):
        return self.nombre
class CarritoCompra(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    completado = models.BooleanField(default=False)

    def __str__(self):
        return f"Carrito de {self.usuario.username}"

    @property
    def total(self):
        return self.items.aggregate(
            total=Sum(F('cantidad') * F('producto__precio'))
        )['total'] or 0

    @property
    def cantidad_total(self):
        return self.items.aggregate(
            total=Sum('cantidad')
        )['total'] or 0
    
class ItemCarrito(models.Model):
    carrito = models.ForeignKey(CarritoCompra, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['carrito', 'producto']

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    @property
    def subtotal(self):
        return self.cantidad * self.producto.precio

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado')
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    comuna = models.CharField(max_length=255, null=True, blank=True)
    carrito = models.OneToOneField(CarritoCompra, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    numero_seguimiento = models.CharField(max_length=100, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"Pedido {self.id} - {self.usuario.username}"