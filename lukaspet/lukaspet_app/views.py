from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Categoria, Marca, CarritoCompra, ItemCarrito
from django.db.models import Q
from .forms import UserLoginForm, UserRegistrationForm, ProductoForm, ContactoForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy


def home(request):
    return render(request, 'home.html')

def nosotros(request):
    return render(request, 'nosotros.html')

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
            
    return render(request,'contacto.html',data)


def tienda(request):
    # Obtener todos los productos inicialmente
    productos = Producto.objects.all()
    
    # Filtro por categoría
    categoria = request.GET.get('categoria')
    if categoria:
        productos = productos.filter(categoria__id=categoria)
    
    # Filtro por marca
    marca = request.GET.get('marca')
    if marca:
        productos = productos.filter(marca__id=marca)
    
    # Búsqueda por nombre o SKU
    q = request.GET.get('q')
    if q:
        productos = productos.filter(
            Q(nombre__icontains=q) |
            Q(sku__icontains=q)
        )
    
    # Ordenamiento
    orden = request.GET.get('orden', 'nombre')  # Por defecto ordena por nombre
    if orden:
        if orden == 'nombre':
            productos = productos.order_by('nombre')
        elif orden == '-nombre':
            productos = productos.order_by('-nombre')
        elif orden == 'precio':
            productos = productos.order_by('precio')
        elif orden == '-precio':
            productos = productos.order_by('-precio')
    
    # Paginación
    paginator = Paginator(productos, 12)  # 12 productos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Contexto para el template
    context = {
        'productos': page_obj,
        'categorias': Categoria.objects.all(),
        'marcas': Marca.objects.all(),
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    
    return render(request, 'tienda.html', context)

# Autenticacion
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, '¡Cuenta creada exitosamente! Ya puedes iniciar sesión.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'auth/registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido {user.first_name}!')
                return redirect('home')  # O la página que quieras después del login
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = UserLoginForm()
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, '¡Has cerrado sesión exitosamente!')
    return redirect('login')

# Crud productos
class ListaProductos(ListView):
    model = Producto
    template_name = 'productos/lista-productos.html'
    context_object_name = 'productos'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        context['marcas'] = Marca.objects.all()
        return context

   
    def get_queryset(self):
        queryset = Producto.objects.all().order_by('-fecha_creacion')

        categoria = self.request.GET.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria__id=categoria)

        marca = self.request.GET.get('marca')
        if marca:
            queryset = queryset.filter(marca__id=marca)

        # Para buscar por nombre o SKU
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q) |
                Q(sku__icontains=q)
            )

        return queryset
    
class CrearProducto(LoginRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/crear-producto.html'
    success_url = reverse_lazy('lista-productos')
    
    def form_valid(self, form):
        messages.success(self.request, 'Producto creado exitosamente.')
        return super().form_valid(form)

class EditarProducto(LoginRequiredMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/editar-producto.html'
    success_url = reverse_lazy('lista-productos')
    
    def form_valid(self, form):
        messages.success(self.request, 'Producto actualizado exitosamente.')
        return super().form_valid(form)

def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.delete()
    messages.success(request, "Producto eliminado exitosamente.")
    return redirect('lista-productos')
    
def ver_carrito(request):
    carrito, created = CarritoCompra.objects.get_or_create(
        usuario=request.user,
        completado=False
    )
    context = {
        'carrito': carrito,
        'items': carrito.items.select_related('producto').all()
    }
    return render(request, 'carrito/carrito.html', context)

@login_required
def agregar_al_carrito(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        cantidad = int(request.POST.get('cantidad', 1))
        
        try:
            with transaction.atomic():
                producto = get_object_or_404(Producto, id=producto_id)
                
                # Verificar stock
                if producto.stock < cantidad:
                    return JsonResponse({
                        'error': 'No hay suficiente stock disponible'
                    }, status=400)
                
                carrito, _ = CarritoCompra.objects.get_or_create(
                    usuario=request.user,
                    completado=False
                )
                
                item, created = ItemCarrito.objects.get_or_create(
                    carrito=carrito,
                    producto=producto,
                    defaults={'cantidad': cantidad}
                )
                
                if not created:
                    nueva_cantidad = item.cantidad + cantidad
                    if nueva_cantidad > producto.stock:
                        return JsonResponse({
                            'error': 'No hay suficiente stock disponible'
                        }, status=400)
                    item.cantidad = nueva_cantidad
                    item.save()

                return redirect('ver_carrito')
        except Exception as e:
            return JsonResponse({
                'error': 'Error al agregar al carrito'
            }, status=400)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def actualizar_cantidad(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        cantidad = int(request.POST.get('cantidad', 1))
        
        try:
            with transaction.atomic():
                item = get_object_or_404(
                    ItemCarrito,
                    id=item_id,
                    carrito__usuario=request.user,
                    carrito__completado=False
                )
                
                if cantidad <= 0:
                    item.delete()
                    mensaje = 'Producto eliminado del carrito'
                else:
                    if cantidad > item.producto.stock:
                        return JsonResponse({
                            'error': 'No hay suficiente stock disponible'
                        }, status=400)
                    
                    item.cantidad = cantidad
                    item.save()
                    mensaje = 'Cantidad actualizada'

                carrito = item.carrito
                return JsonResponse({
                    'message': mensaje,
                    'cart_count': carrito.cantidad_total,
                    'cart_total': carrito.total,
                    'item_subtotal': item.subtotal if cantidad > 0 else 0
                })
                
        except Exception as e:
            return JsonResponse({
                'error': 'Error al actualizar cantidad'
            }, status=400)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def eliminar_del_carrito(request, item_id):
    try:
        item = get_object_or_404(
            ItemCarrito,
            id=item_id,
            carrito__usuario=request.user,
            carrito__completado=False
        )
        carrito = item.carrito
        item.delete()
        
        return JsonResponse({
            'message': 'Producto eliminado del carrito',
            'cart_count': carrito.cantidad_total,
            'cart_total': carrito.total
        })
        
    except Exception as e:
        return JsonResponse({
            'error': 'Error al eliminar producto'
        }, status=400)

@login_required
def vaciar_carrito(request):
    if request.method == 'POST':
        try:
            carrito = CarritoCompra.objects.get(
                usuario=request.user,
                completado=False
            )
            carrito.items.all().delete()
            
            return JsonResponse({
                'message': 'Carrito vaciado exitosamente',
                'cart_count': 0,
                'cart_total': 0
            })
            
        except Exception as e:
            return JsonResponse({
                'error': 'Error al vaciar el carrito'
            }, status=400)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

