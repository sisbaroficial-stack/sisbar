from django.contrib import admin
from .models import Categoria, Subcategoria

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """
    Panel de administración para Categorías
    """
    list_display = ('icono', 'nombre', 'slug', 'color', 'activa', 'total_productos', 'fecha_creacion')
    list_filter = ('activa', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')
    prepopulated_fields = {'slug': ('nombre',)}
    readonly_fields = ('fecha_creacion',)
    ordering = ('nombre',)
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('nombre', 'slug', 'icono', 'color')
        }),
        ('Detalles', {
            'fields': ('descripcion', 'activa')
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activar_categorias', 'desactivar_categorias']
    
    def activar_categorias(self, request, queryset):
        count = queryset.update(activa=True)
        self.message_user(request, f'{count} categoría(s) activada(s).')
    activar_categorias.short_description = "✅ Activar categorías"
    
    def desactivar_categorias(self, request, queryset):
        count = queryset.update(activa=False)
        self.message_user(request, f'{count} categoría(s) desactivada(s).')
    desactivar_categorias.short_description = "🚫 Desactivar categorías"


@admin.register(Subcategoria)
class SubcategoriaAdmin(admin.ModelAdmin):
    """
    Panel de administración para Subcategorías
    """
    list_display = ('nombre', 'categoria', 'slug', 'activa', 'total_productos', 'fecha_creacion')
    list_filter = ('activa', 'categoria', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion', 'categoria__nombre')
    prepopulated_fields = {'slug': ('nombre',)}
    readonly_fields = ('fecha_creacion',)
    ordering = ('categoria', 'nombre')
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('categoria', 'nombre', 'slug')
        }),
        ('Detalles', {
            'fields': ('descripcion', 'activa')
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )