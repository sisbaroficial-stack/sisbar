from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, HistorialActividad

@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """
    Configuración del panel de administración para Usuario
    """
    list_display = ('username', 'email', 'get_full_name', 'rol', 'aprobado', 'is_active', 'date_joined')
    list_filter = ('rol', 'aprobado', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'documento')
    ordering = ('-date_joined',)
    
    fieldsets = (
        ('Información de Acceso', {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'telefono', 'documento', 'foto_perfil')
        }),
        ('Rol y Permisos', {
            'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Aprobación', {
            'fields': ('aprobado', 'fecha_aprobacion', 'aprobado_por')
        }),
        ('Preferencias', {
            'fields': ('modo_oscuro',)
        }),
        ('Fechas Importantes', {
            'fields': ('date_joined', 'last_login', 'ultima_actividad')
        }),
    )
    
    add_fieldsets = (
        ('Crear Nuevo Usuario', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'rol'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'ultima_actividad', 'fecha_aprobacion', 'aprobado_por')
    
    actions = ['aprobar_usuarios', 'desactivar_usuarios']
    
    def aprobar_usuarios(self, request, queryset):
        """Acción para aprobar múltiples usuarios"""
        count = 0
        for usuario in queryset.filter(aprobado=False):
            usuario.aprobar_usuario(request.user)
            count += 1
        self.message_user(request, f'{count} usuario(s) aprobado(s) exitosamente.')
    aprobar_usuarios.short_description = "✅ Aprobar usuarios seleccionados"
    
    def desactivar_usuarios(self, request, queryset):
        """Acción para desactivar múltiples usuarios"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} usuario(s) desactivado(s).')
    desactivar_usuarios.short_description = "🚫 Desactivar usuarios seleccionados"


@admin.register(HistorialActividad)
class HistorialActividadAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para Historial de Actividad
    """
    list_display = ('usuario', 'tipo', 'descripcion', 'fecha', 'ip_address')
    list_filter = ('tipo', 'fecha')
    search_fields = ('usuario__username', 'descripcion')
    readonly_fields = ('usuario', 'tipo', 'descripcion', 'fecha', 'ip_address')
    date_hierarchy = 'fecha'
    ordering = ('-fecha',)
    
    def has_add_permission(self, request):
        """No permitir agregar manualmente actividades"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir editar actividades"""
        return False