from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), 
    path('nosotros', views.nosotros, name='nosotros'),
    path('contacto/',views.contacto,name="contacto"),
    path('productos', views.ListaProductos.as_view(), name='lista-productos'),
    path('productos/crear/', views.CrearProducto.as_view(), name='crear-producto'),
    path('productos/<int:pk>/editar/', views.EditarProducto.as_view(), name='editar-producto'),
    path('productos/<int:pk>/eliminar/', views.eliminar_producto, name='eliminar-producto'),
    path('registro', views.register, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('tienda', views.tienda, name='tienda'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/actualizar/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
]