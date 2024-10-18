from django.urls import path
from . import views
from .views import home,contacto,galeria,sobrenosotros,tienda,registro,agregar_producto,listar_producto,modificar_producto,eliminar_producto,agregar_al_carrito,ver_carrito

urlpatterns = [
    path('', home, name="home"),
    path('sobrenosotros/',sobrenosotros,name="sobrenosotros"),
    path('contacto/',contacto,name="contacto"),
    path('galeria/',galeria,name="galeria"),
    path('agregar-producto/',agregar_producto,name="agregar_producto"),
    path('listar-productos/',listar_producto,name="listar_producto"),
    path('modificar-producto/<id>/',modificar_producto,name="modificar_producto"),
    path('eliminar-producto/<id>/',eliminar_producto,name="eliminar_producto"),
    path('tienda/',tienda,name="tienda"),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('registro/',registro,name="registro"),
]