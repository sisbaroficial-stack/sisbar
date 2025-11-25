from django.urls import path
from . import views

app_name = 'movimientos'

urlpatterns = [
    path('', views.listar_movimientos_view, name='listar'),
    path('alertas/', views.listar_alertas_view, name='alertas'),
]