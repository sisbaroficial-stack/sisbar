from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from inventario.models import Producto
from categorias.models import Categoria
from movimientos.models import Movimiento, AlertaInventario
from usuarios.models import HistorialActividad, Usuario


@login_required
def home_view(request):
    """
    Dashboard principal con estadísticas en tiempo real
    """
    
    # Estadísticas de productos
    total_productos = Producto.objects.filter(activo=True).count()
    productos_disponibles = Producto.objects.filter(activo=True, estado='DISPONIBLE').count()
    productos_por_agotar = Producto.objects.filter(activo=True, estado='POR_AGOTAR').count()
    productos_agotados = Producto.objects.filter(activo=True, estado='AGOTADO').count()
    
    # Valor total del inventario
    valor_total = Producto.objects.filter(activo=True).aggregate(
        total=Sum('precio_compra')
    )['total'] or 0
    
    # Productos por categoría
    productos_por_categoria = Categoria.objects.filter(activa=True).annotate(
        total=Count('productos', filter=Q(productos__activo=True))
    ).order_by('-total')[:5]
    
    # Productos con stock bajo
    productos_stock_bajo = Producto.objects.filter(
        activo=True,
        cantidad__lte=5
    ).order_by('cantidad')[:5]
    
    # Últimos movimientos (últimos 7 días)
    hace_7_dias = timezone.now() - timedelta(days=7)
    ultimos_movimientos = Movimiento.objects.filter(
        fecha__gte=hace_7_dias
    ).select_related('producto', 'usuario').order_by('-fecha')[:10]
    
    # Actividad reciente del usuario
    actividad_reciente = HistorialActividad.objects.filter(
        usuario=request.user
    ).order_by('-fecha')[:5]
    
    # Alertas pendientes
    alertas_pendientes = AlertaInventario.objects.filter(
        resuelta=False
    ).select_related('producto').order_by('-fecha_generada')[:5]
    
    # Movimientos de hoy
    hoy = timezone.now().date()
    movimientos_hoy = Movimiento.objects.filter(
        fecha__date=hoy
    ).count()
    
    # Productos más movidos (últimos 30 días)
    hace_30_dias = timezone.now() - timedelta(days=30)
    productos_mas_movidos = Producto.objects.filter(
        activo=True,
        movimientos__fecha__gte=hace_30_dias
    ).annotate(
        total_movimientos=Count('movimientos')
    ).order_by('-total_movimientos')[:5]
    
    # Datos para gráfica de categorías (formato JSON para Chart.js)
    categorias_labels = []
    categorias_data = []
    categorias_colors = []
    
    for cat in productos_por_categoria:
        categorias_labels.append(f"{cat.icono} {cat.nombre}")
        categorias_data.append(cat.total)
        categorias_colors.append(cat.color)
    
    # Estadísticas de usuarios (solo para admins)
    stats_usuarios = None
    if request.user.puede_aprobar():
        stats_usuarios = {
            'total': Usuario.objects.count(),
            'activos': Usuario.objects.filter(is_active=True).count(),
            'pendientes': Usuario.objects.filter(aprobado=False).count(),
        }
    
    context = {
        # Estadísticas principales
        'total_productos': total_productos,
        'productos_disponibles': productos_disponibles,
        'productos_por_agotar': productos_por_agotar,
        'productos_agotados': productos_agotados,
        'valor_total': valor_total,
        'movimientos_hoy': movimientos_hoy,
        
        # Listas
        'productos_por_categoria': productos_por_categoria,
        'productos_stock_bajo': productos_stock_bajo,
        'ultimos_movimientos': ultimos_movimientos,
        'actividad_reciente': actividad_reciente,
        'alertas_pendientes': alertas_pendientes,
        'productos_mas_movidos': productos_mas_movidos,
        
        # Datos para gráficas
        'categorias_labels': categorias_labels,
        'categorias_data': categorias_data,
        'categorias_colors': categorias_colors,
        
        # Estadísticas de usuarios
        'stats_usuarios': stats_usuarios,
    }
    
    return render(request, 'dashboard/home.html', context)
