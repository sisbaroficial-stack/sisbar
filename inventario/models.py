from django.db import models
from django.core.validators import MinValueValidator
from categorias.models import Categoria, Subcategoria
from proveedores.models import Proveedor
from usuarios.models import Usuario
import uuid

class Producto(models.Model):
    """
    Modelo principal de productos en inventario
    """
    
    UNIDADES_MEDIDA = (
        ('UNIDAD', 'Unidad'),
        ('DOCENA', 'Docena'),
        ('CAJA', 'Caja'),
        ('PAQUETE', 'Paquete'),
        ('KILO', 'Kilogramo'),
        ('GRAMO', 'Gramo'),
        ('LITRO', 'Litro'),
        ('METRO', 'Metro'),
        ('PAR', 'Par'),
        ('JUEGO', 'Juego'),
    )
    
    ESTADOS = (
        ('DISPONIBLE', '🟢 Disponible'),
        ('POR_AGOTAR', '🟡 Por Agotarse'),
        ('AGOTADO', '🔴 Agotado'),
    )
    
    # Identificación
    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código / Referencia',
        help_text='Código único del producto (puede ser SKU o código de barras)'
    )
    
    codigo_barras = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Código de Barras',
        help_text='Código de barras para escaneo'
    )
    
    # Información básica
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre del Producto'
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    # Categorización
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='productos',
        verbose_name='Categoría'
    )
    
    subcategoria = models.ForeignKey(
        Subcategoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos',
        verbose_name='Subcategoría'
    )
    
    # Inventario
    cantidad = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Cantidad en Stock'
    )
    
    cantidad_minima = models.IntegerField(
        default=5,
        validators=[MinValueValidator(0)],
        verbose_name='Cantidad Mínima',
        help_text='Alerta cuando llegue a este nivel'
    )
    
    unidad_medida = models.CharField(
        max_length=20,
        choices=UNIDADES_MEDIDA,
        default='UNIDAD',
        verbose_name='Unidad de Medida'
    )
    
    # Precios (solo control interno)
    precio_compra = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Precio de Compra',
        help_text='Precio al que se compra el producto'
    )
    
    # Proveedor
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos',
        verbose_name='Proveedor'
    )
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='DISPONIBLE',
        verbose_name='Estado del Producto'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Producto Activo',
        help_text='Desactivar en lugar de eliminar'
    )
    
    # Imagen
    imagen = models.ImageField(
        upload_to='productos/',
        blank=True,
        null=True,
        verbose_name='Imagen del Producto'
    )
    
    # Ubicación
    ubicacion = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Ubicación en Bodega',
        help_text='Estante, pasillo, zona, etc.'
    )
    
    # Auditoría
    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='productos_creados',
        verbose_name='Creado Por'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    ultima_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    ultima_salida = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Última Salida'
    )
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['codigo_barras']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def save(self, *args, **kwargs):
        # Actualizar estado automáticamente basado en cantidad
        if self.cantidad == 0:
            self.estado = 'AGOTADO'
        elif self.cantidad <= self.cantidad_minima:
            self.estado = 'POR_AGOTAR'
        else:
            self.estado = 'DISPONIBLE'
        
        super().save(*args, **kwargs)
    
    def descontar_cantidad(self, cantidad, usuario=None):
        """
        Descuenta cantidad del producto
        """
        if cantidad > self.cantidad:
            raise ValueError(f"No hay suficiente stock. Disponible: {self.cantidad}")
        
        self.cantidad -= cantidad
        self.save()
        
        # Registrar el movimiento
        from movimientos.models import Movimiento
        Movimiento.objects.create(
            producto=self,
            tipo='SALIDA',
            cantidad=cantidad,
            usuario=usuario,
            cantidad_anterior=self.cantidad + cantidad,
            cantidad_nueva=self.cantidad
        )
    
    def agregar_cantidad(self, cantidad, usuario=None):
        """
        Agrega cantidad al producto
        """
        cantidad_anterior = self.cantidad
        self.cantidad += cantidad
        self.save()
        
        # Registrar el movimiento
        from movimientos.models import Movimiento
        Movimiento.objects.create(
            producto=self,
            tipo='ENTRADA',
            cantidad=cantidad,
            usuario=usuario,
            cantidad_anterior=cantidad_anterior,
            cantidad_nueva=self.cantidad
        )
    
    def get_estado_color(self):
        """Retorna el color según el estado"""
        colores = {
            'DISPONIBLE': 'success',
            'POR_AGOTAR': 'warning',
            'AGOTADO': 'danger'
        }
        return colores.get(self.estado, 'secondary')
    
    def get_estado_icono(self):
        """Retorna el icono según el estado"""
        iconos = {
            'DISPONIBLE': '🟢',
            'POR_AGOTAR': '🟡',
            'AGOTADO': '🔴'
        }
        return iconos.get(self.estado, '⚪')