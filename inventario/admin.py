from django.contrib import admin
from django.utils.html import format_html
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """
    Panel de administración para Productos
    """
    list_display = (
        'codigo', 
        'nombre', 
        'categoria', 
        'subcategoria',
        'cantidad_display',
        'estado_display',
        'precio_compra',
        'proveedor',
        'activo'
    )
    
    list_filter = (
        'estado',
        'activo',
        'categoria',
        'subcategoria',
        'proveedor',
        'fecha_creacion'
    )
    
    search_fields = (
        'codigo',
        'codigo_barras',
        'nombre',
        'descripcion',
        'categoria__nombre',
        'proveedor__nombre'
    )
    
    readonly_fields = (
        'estado',
        'creado_por',
        'fecha_creacion',
        'ultima_actualizacion',
        'ultima_salida'
    )
    
    ordering = ('-fecha_creacion',)
    
    date_hierarchy = 'fecha_creacion'
    
    fieldsets = (
        ('Identificación', {
            'fields': ('codigo', 'codigo_barras', 'nombre')
        }),
        ('Descripción', {
            'fields': ('descripcion', 'imagen')
        }),
        ('Categorización', {
            'fields': ('categoria', 'subcategoria')
        }),
        ('Inventario', {
            'fields': (
                'cantidad',
                'cantidad_minima',
                'unidad_medida',
                'ubicacion'
            )
        }),
        ('Precio', {
            'fields': ('precio_compra',)
        }),
        ('Proveedor', {
            'fields': ('proveedor',)
        }),
        ('Estado', {
            'fields': ('estado', 'activo')
        }),
        ('Auditoría', {
            'fields': (
                'creado_por',
                'fecha_creacion',
                'ultima_actualizacion',
                'ultima_salida'
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'activar_productos',
        'desactivar_productos',
        'marcar_disponible',
        'exportar_excel'
    ]
    
    def cantidad_display(self, obj):
        """Muestra la cantidad con color según el estado"""
        if obj.cantidad == 0:
            color = 'red'
        elif obj.cantidad <= obj.cantidad_minima:
            color = 'orange'
        else:
            color = 'green'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.cantidad
        )
    cantidad_display.short_description = 'Cantidad'
    
    def estado_display(self, obj):
        """Muestra el estado con emoji"""
        return f"{obj.get_estado_icono()} {obj.get_estado_display()}"
    estado_display.short_description = 'Estado'
    
    def save_model(self, request, obj, form, change):
        """Guarda el usuario que creó el producto"""
        if not change:  # Si es un nuevo producto
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)
    
    def activar_productos(self, request, queryset):
        count = queryset.update(activo=True)
        self.message_user(request, f'{count} producto(s) activado(s).')
    activar_productos.short_description = "✅ Activar productos"
    
    def desactivar_productos(self, request, queryset):
        count = queryset.update(activo=False)
        self.message_user(request, f'{count} producto(s) desactivado(s).')
    desactivar_productos.short_description = "🚫 Desactivar productos"
    
    def marcar_disponible(self, request, queryset):
        count = queryset.update(estado='DISPONIBLE')
        self.message_user(request, f'{count} producto(s) marcado(s) como disponible.')
    marcar_disponible.short_description = "🟢 Marcar como disponible"