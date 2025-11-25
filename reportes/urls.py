
from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.reportes_home_view, name='home'),
    path('exportar/productos/excel/', views.exportar_productos_excel, name='exportar_productos_excel'),
    path('exportar/productos/pdf/', views.exportar_productos_pdf, name='exportar_productos_pdf'),
    path('exportar/movimientos/excel/', views.exportar_movimientos_excel, name='exportar_movimientos_excel'),
]