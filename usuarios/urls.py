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
]