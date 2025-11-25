from django.contrib import admin
from django.utils.html import format_html
from .models import Movimiento, AlertaInventario

@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    """
    Panel de administración para Movimientos
    """
    list_display = (
        'fecha',
        'tipo_display',
        'producto',
        'cantidad',
        'cantidad_anterior',
        'cantidad_nueva',
        'usuario',
        'motivo'
    )
    
    list_filter = (
        'tipo',
        'fecha',
        'usuario',
        'producto__categoria'
    )
    
    search_fields = (
        'producto__nombre',
        'producto__codigo',
        'motivo',
        'observaciones',
        'usuario__username'
    )
    
    readonly_fields = (
        'producto',
        'tipo',
        'cantidad',
        'cantidad_anterior',
        'cantidad_nueva',
        'usuario',
        'fecha'
    )
    
    ordering = ('-fecha',)
    
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('Información del Movimiento', {
            'fields': ('fecha', 'tipo', 'producto')
        }),
        ('Cantidades', {
            'fields': ('cantidad', 'cantidad_anterior', 'cantidad_nueva')
        }),
        ('Detalles', {
            'fields': ('motivo', 'observaciones', 'usuario')
        }),
    )
    
    def tipo_display(self, obj):
        """Muestra el tipo con emoji"""
        return f"{obj.get_tipo_icono()} {obj.get_tipo_display()}"
    tipo_display.short_description = 'Tipo'
    
    def has_add_permission(self, request):
        """No permitir agregar movimientos manualmente desde el admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir editar movimientos"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Solo superusuarios pueden eliminar movimientos"""
        return request.user.is_superuser


@admin.register(AlertaInventario)
class AlertaInventarioAdmin(admin.ModelAdmin):
    """
    Panel de administración para Alertas de Inventario
    """
    list_display = (
        'fecha_generada',
        'tipo_display',
        'producto',
        'mensaje_corto',
        'leida',
        'resuelta'
    )
    
    list_filter = (
        'tipo',
        'leida',
        'resuelta',
        'fecha_generada'
    )
    
    search_fields = (
        'producto__nombre',
        'producto__codigo',
        'mensaje'
    )
    
    readonly_fields = (
        'producto',
        'tipo',
        'mensaje',
        'fecha_generada',
        'fecha_lectura'
    )
    
    ordering = ('-fecha_generada',)
    
    date_hierarchy = 'fecha_generada'
    
    fieldsets = (
        ('Información de la Alerta', {
            'fields': ('fecha_generada', 'tipo', 'producto', 'mensaje')
        }),
        ('Estado', {
            'fields': ('leida', 'fecha_lectura', 'resuelta')
        }),
    )
    
    actions = ['marcar_leidas', 'marcar_resueltas']
    
    def tipo_display(self, obj):
        """Muestra el tipo con emoji"""
        return obj.get_tipo_display()
    tipo_display.short_description = 'Tipo'
    
    def mensaje_corto(self, obj):
        """Muestra un mensaje recortado"""
        return obj.mensaje[:50] + '...' if len(obj.mensaje) > 50 else obj.mensaje
    mensaje_corto.short_description = 'Mensaje'
    
    def marcar_leidas(self, request, queryset):
        from django.utils import timezone
        count = queryset.filter(leida=False).update(
            leida=True,
            fecha_lectura=timezone.now()
        )
        self.message_user(request, f'{count} alerta(s) marcada(s) como leída(s).')
    marcar_leidas.short_description = "👁️ Marcar como leídas"
    
    def marcar_resueltas(self, request, queryset):
        count = queryset.update(resuelta=True)
        self.message_user(request, f'{count} alerta(s) marcada(s) como resuelta(s).')
    marcar_resueltas.short_description = "✅ Marcar como resueltas"
    
    def has_add_permission(self, request):
        """No permitir agregar alertas manualmente"""
        return False