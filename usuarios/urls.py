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




   








    # Gestión avanzada de usuarios (solo admins)
    path('editar-completo/<int:usuario_id>/', views.editar_usuario_completo_view, name='editar_usuario_completo'),
    path('resetear-password/<int:usuario_id>/', views.resetear_password_view, name='resetear_password'),
    path('eliminar-usuario/<int:usuario_id>/', views.eliminar_usuario_view, name='eliminar_usuario'),
]