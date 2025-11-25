from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Mantener redirección al login
    path('', views.index_view, name='index'),

    # Página index
    path('index/', views.index_view, name='index'),

    # Apps
    path('usuarios/', include('usuarios.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('inventario/', include('inventario.urls')),
    path('categorias/', include('categorias.urls')),
    path('proveedores/', include('proveedores.urls')),
    path('movimientos/', include('movimientos.urls')),
    path('reportes/', include('reportes.urls')),
]

# Media & Static
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin style
admin.site.site_header = "🛒 SISBAR  - Administración"
admin.site.site_title = "SISBAR Admin"
admin.site.index_title = "Panel de Administración"
