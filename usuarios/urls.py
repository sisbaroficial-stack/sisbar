from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Autenticación
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Perfil
    path('perfil/', views.perfil_view, name='perfil'),
    path('cambiar-password/', views.cambiar_password_view, name='cambiar_password'),
    
    # Gestión de usuarios (solo admins)
    path('gestionar/', views.gestionar_usuarios_view, name='gestionar_usuarios'),
    path('aprobar/<int:usuario_id>/', views.aprobar_usuario_view, name='aprobar_usuario'),
    path('toggle/<int:usuario_id>/', views.toggle_usuario_view, name='toggle_usuario'),
    path("detalle/<int:usuario_id>/", views.detalle_usuario, name="detalle_usuario"),
    # PANEL ELIMINADOS (solo admins)
    path('eliminados/', views.panel_eliminados_view, name='panel_eliminados'),
    # Productos
    path('eliminados/producto/restaurar/<int:producto_id>/', views.restaurar_producto, name='restaurar_producto'),
    path('eliminados/producto/borrar-definitivo/<int:producto_id>/', views.eliminar_producto_definitivo, name='eliminar_producto_definitivo'),
    # Categorías
    path('eliminados/categoria/restaurar/<int:categoria_id>/', views.restaurar_categoria, name='restaurar_categoria'),
    path('eliminados/categoria/borrar-definitivo/<int:categoria_id>/', views.eliminar_categoria_definitivo, name='eliminar_categoria_definitivo'),
    # Proveedores
    path('eliminados/proveedor/restaurar/<int:proveedor_id>/', views.restaurar_proveedor, name='restaurar_proveedor'),
    path('eliminados/proveedor/borrar-definitivo/<int:proveedor_id>/', views.eliminar_proveedor_definitivo, name='eliminar_proveedor_definitivo'),
    # Usuarios
    path('eliminados/usuario/restaurar/<int:usuario_id>/', views.restaurar_usuario, name='restaurar_usuario'),
    path('eliminados/usuario/borrar-definitivo/<int:usuario_id>/', views.eliminar_usuario_definitivo, name='eliminar_usuario_definitivo'),
    # AGREGAR SOLO ESTAS 4 LÍNEAS NUEVAS ABAJO
    path('producto/desactivar/<int:producto_id>/', views.desactivar_producto, name='desactivar_producto'),
    path('categoria/desactivar/<int:categoria_id>/', views.desactivar_categoria, name='desactivar_categoria'),
    path('proveedor/desactivar/<int:proveedor_id>/', views.desactivar_proveedor, name='desactivar_proveedor'),
    path('usuario/desactivar/<int:usuario_id>/', views.desactivar_usuario, name='desactivar_usuario'),
    # Gestión avanzada de usuarios (solo admins)
    path('editar-completo/<int:usuario_id>/', views.editar_usuario_completo_view, name='editar_usuario_completo'),
    path('resetear-password/<int:usuario_id>/', views.resetear_password_view, name='resetear_password'),
    path('eliminar-usuario/<int:usuario_id>/', views.eliminar_usuario_view, name='eliminar_usuario'),
    path('grupos/', views.gestionar_grupos_view, name='gestionar_grupos'),
    path('grupos/crear/', views.crear_grupo_view, name='crear_grupo'),
    path('grupos/editar/<int:grupo_id>/', views.editar_grupo_view, name='editar_grupo'),
    path('grupos/eliminar/<int:grupo_id>/', views.eliminar_grupo_view, name='eliminar_grupo'),
]

