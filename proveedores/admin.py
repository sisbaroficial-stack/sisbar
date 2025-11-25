from django.contrib import admin
from .models import Proveedor

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    """
    Panel de administración para Proveedores
    """
    list_display = ('nombre', 'nit', 'contacto', 'telefono', 'email', 'estrellas', 'activo', 'total_productos')
    list_filter = ('calificacion', 'activo', 'pais', 'ciudad', 'fecha_registro')
    search_fields = ('nombre', 'nit', 'contacto', 'email', 'telefono')
    readonly_fields = ('fecha_registro', 'ultima_actualizacion')
    ordering = ('nombre',)
    
    fieldsets = (
        ('Información del Proveedor', {
            'fields': ('nombre', 'nit')
        }),
        ('Contacto', {
            'fields': ('contacto', 'telefono', 'email', 'sitio_web')
        }),
        ('Ubicación', {
            'fields': ('direccion', 'ciudad', 'pais')
        }),
        ('Calificación', {
            'fields': ('calificacion', 'notas')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Información del Sistema', {
            'fields': ('fecha_registro', 'ultima_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activar_proveedores', 'desactivar_proveedores']
    
    def activar_proveedores(self, request, queryset):
        count = queryset.update(activo=True)
        self.message_user(request, f'{count} proveedor(es) activado(s).')
    activar_proveedores.short_description = "✅ Activar proveedores"
    
    def desactivar_proveedores(self, request, queryset):
        count = queryset.update(activo=False)
        self.message_user(request, f'{count} proveedor(es) desactivado(s).')
    desactivar_proveedores.short_description = "🚫 Desactivar proveedores"