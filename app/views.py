from django.shortcuts import render,redirect,get_object_or_404
from .models import Producto,Carrito,ElementoCarrito
from .forms import ProductoForm,ContactoForm
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login

# Create your views here.

def home(request):
    productos=Producto.objects.all()
    data={
        'productos':productos
    }
    return render (request, 'app/home.html',data)

def sobrenosotros(request):
    return render(request,'app/sobrenosotros.html')

def contacto(request):
    data={
        'form':ContactoForm()
    }

    if request.method=='POST':
        formulario=ContactoForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            data["mensaje"]="Contacto guardado"
        else:
            data["form"]=formulario
            
    return render(request,'app/contacto.html',data)

def galeria(request):
    return render (request,'app/galeria.html')


def tienda(request):
    productos=Producto.objects.all()     
    data={
        'productos':productos
    }
    return render (request, 'app/tienda.html',data)


def agregar_producto(request):
    data = {
        'form': ProductoForm()
    }
    if request.method == 'POST':
        formulario = ProductoForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            data["mensaje"] = "guardado correctamente"
        else:
            data["form"] = formulario
    return render(request, 'app/producto/agregar.html', data)



def listar_producto(request):
    productos = Producto.objects.all()
    data = {
        'productos': productos
    }
    return render(request, 'app/producto/listar.html', data)

def modificar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    data = {
        'form': ProductoForm(instance=producto)
    }

    if request.method == 'POST':
        formulario = ProductoForm(data=request.POST, instance=producto, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request,"modificado correctamente")
            return redirect(to="listar_producto")
        data["form"] = formulario

    return render(request, 'app/producto/modificar.html', data)

def eliminar_producto(request, id):
    producto=get_object_or_404(Producto,id=id)
    producto.delete()
    return redirect(to="listar_producto")

#Carrito
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    # Si el usuario no está autenticado, guardamos el carrito en la sesión
    if not request.user.is_authenticated:
        carrito = request.session.get('carrito', {})

        if str(producto_id) in carrito:
            carrito[str(producto_id)]['cantidad'] += 1
        else:
            carrito[str(producto_id)] = {
                'producto_id': producto_id,
                'nombre': producto.nombre,
                'precio': str(producto.precio),
                'cantidad': 1,
            }

        request.session['carrito'] = carrito
    else:
        # Código para agregar al carrito en la base de datos para usuarios autenticados
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        item, item_created = ElementoCarrito.objects.get_or_create(carrito=carrito, producto=producto)
        
        if not item_created:
            item.cantidad += 1
            item.save()

    return redirect('ver_carrito')

def ver_carrito(request):
    if request.user.is_authenticated:
        # Usar get_or_create para crear un carrito si no existe
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        items = carrito.elementocarrito_set.all()
        total = sum(item.subtotal() for item in items)
    else:
        # Cargar carrito desde la sesión para usuarios no autenticados
        carrito = request.session.get('carrito', {})
        items = [{'producto': v['nombre'], 'cantidad': v['cantidad'], 'subtotal': float(v['precio']) * v['cantidad']} for v in carrito.values()]
        total = sum(item['subtotal'] for item in items)

    return render(request, 'carrito.html', {'items': items, 'total': total})

#Fin carrito

def registro(request):
    data={
        'form':CustomUserCreationForm()
    }
    if request.method=='POST':
        formulario=CustomUserCreationForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            user=authenticate(username=formulario.cleaned_data["username"],password=formulario.cleaned_data["password1"])
            login(request,user)
            #redirigir al home
            return redirect(to="home")
        data["form"]=formulario
    return render(request,'registration/registro.html',data)

