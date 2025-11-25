from django.urls import path
from . import views

app_name = 'proveedores'

urlpatterns = [
    path('', views.listar_proveedores_view, name='listar'),
    path('crear/', views.crear_proveedor_view, name='crear'),
    path('ver/<int:proveedor_id>/', views.ver_proveedor_view, name='ver'),
    path('editar/<int:proveedor_id>/', views.editar_proveedor_view, name='editar'),
    path('eliminar/<int:proveedor_id>/', views.eliminar_proveedor_view, name='eliminar'),
]