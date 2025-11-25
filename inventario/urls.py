from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    # Lista y gestión de productos
    path('', views.listar_productos_view, name='listar_productos'),
    path('crear/', views.crear_producto_view, name='crear_producto'),
    path('editar/<int:producto_id>/', views.editar_producto_view, name='editar_producto'),
    path('ver/<int:producto_id>/', views.ver_producto_view, name='ver_producto'),
    path('eliminar/<int:producto_id>/', views.eliminar_producto_view, name='eliminar_producto'),
    
    # Descontar productos
    path('descontar/', views.descontar_producto_view, name='descontar_producto'),
    
    # AJAX
    path('buscar-ajax/', views.buscar_producto_ajax, name='buscar_producto_ajax'),
]
