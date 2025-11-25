from django.db import models
from django.utils.text import slugify

class Categoria(models.Model):
    """
    Categorías principales de productos
    """
    
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre de Categoría'
    )
    
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name='Slug'
    )
    
    icono = models.CharField(
        max_length=50,
        default='📦',
        verbose_name='Icono',
        help_text='Emoji o clase de icono'
    )
    
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    
    color = models.CharField(
        max_length=7,
        default='#3B82F6',
        verbose_name='Color Hexadecimal',
        help_text='Color para identificar la categoría en gráficas'
    )
    
    activa = models.BooleanField(
        default=True,
        verbose_name='Categoría Activa'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.icono} {self.nombre}"
    
    def total_productos(self):
        """Retorna el total de productos en esta categoría"""
        return self.productos.filter(activo=True).count()
    
    def productos_agotados(self):
        """Retorna productos agotados de esta categoría"""
        return self.productos.filter(activo=True, cantidad=0).count()


class Subcategoria(models.Model):
    """
    Subcategorías dentro de cada categoría
    """
    
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='subcategorias',
        verbose_name='Categoría'
    )
    
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre de Subcategoría'
    )
    
    slug = models.SlugField(
        max_length=100,
        blank=True,
        verbose_name='Slug'
    )
    
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    
    activa = models.BooleanField(
        default=True,
        verbose_name='Subcategoría Activa'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    class Meta:
        verbose_name = 'Subcategoría'
        verbose_name_plural = 'Subcategorías'
        ordering = ['categoria', 'nombre']
        unique_together = ['categoria', 'nombre']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.categoria.nombre} > {self.nombre}"
    
    def total_productos(self):
        """Retorna el total de productos en esta subcategoría"""
        return self.productos.filter(activo=True).count()