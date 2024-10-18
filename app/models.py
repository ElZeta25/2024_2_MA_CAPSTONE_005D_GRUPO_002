from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Marca(models.Model):
    nombre=models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre= models.CharField(max_length=50)
    precio=models.IntegerField()
    descripcion=models.TextField()
    marca=models.ForeignKey(Marca,on_delete=models.PROTECT)
    imagen=models.ImageField(upload_to="Productos",null=True)

    def __str__(self):
        return self.nombre


#Inicio carrito
class Carrito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Carrito de {self.usuario}"

class ElementoCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    def subtotal(self):
        return self.cantidad * self.producto.precio
    
#FIn Carrito

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