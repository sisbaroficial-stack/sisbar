from django.urls import path
from . import views

app_name = 'categorias'

urlpatterns = [
    path('', views.listar_categorias_view, name='listar'),
    path('crear/', views.crear_categoria_view, name='crear'),
    path('editar/<int:categoria_id>/', views.editar_categoria_view, name='editar'),
    path('eliminar/<int:categoria_id>/', views.eliminar_categoria_view, name='eliminar'),
    path('subcategoria/crear/<int:categoria_id>/', views.crear_subcategoria_view, name='crear_subcategoria'),
]