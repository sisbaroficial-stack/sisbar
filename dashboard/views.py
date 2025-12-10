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
    Dashboard optimizado con consultas más eficientes
    """
    # Estadísticas de productos
    productos_activos = Producto.objects.filter(activo=True)

    total_productos = productos_activos.count()
    productos_disponibles = productos_activos.filter(estado='DISPONIBLE').count()
    productos_por_agotar = productos_activos.filter(estado='POR_AGOTAR').count()
    productos_agotados = productos_activos.filter(estado='AGOTADO').count()

    valor_total = productos_activos.aggregate(total=Sum('precio_compra'))['total'] or 0

    # Productos por categoría (solo top 5)
    productos_por_categoria = (
        Categoria.objects.filter(activa=True)
        .annotate(total=Count('productos', filter=Q(productos__activo=True)))
        .order_by('-total')[:5]
    )

    # Productos con stock bajo (solo top 5)
    productos_stock_bajo = productos_activos.filter(cantidad__lte=5).only('nombre', 'cantidad')[:5]

    # Últimos movimientos (últimos 7 días, solo lo necesario)
    hace_7_dias = timezone.now() - timedelta(days=7)
    ultimos_movimientos = (
        Movimiento.objects.filter(fecha__gte=hace_7_dias)
        .select_related('producto', 'usuario')
        .only('producto__nombre', 'usuario__username', 'fecha')[:10]
    )

    # Actividad reciente del usuario
    actividad_reciente = (
        HistorialActividad.objects.filter(usuario=request.user)
        .only('accion', 'fecha')[:5]
    )

    # Alertas pendientes (solo top 5)
    alertas_pendientes = (
        AlertaInventario.objects.filter(resuelta=False)
        .select_related('producto')
        .only('producto__nombre', 'mensaje', 'fecha_generada')[:5]
    )

    # Movimientos de hoy (solo conteo)
    hoy = timezone.now().date()
    movimientos_hoy = Movimiento.objects.filter(fecha__date=hoy).count()

    # Productos más movidos últimos 30 días (solo top 5)
    hace_30_dias = timezone.now() - timedelta(days=30)
    productos_mas_movidos = (
        productos_activos.filter(movimientos__fecha__gte=hace_30_dias)
        .annotate(total_movimientos=Count('movimientos'))
        .only('nombre')[:5]
    )

    # Datos para gráficas
    categorias_labels = [f"{cat.icono} {cat.nombre}" for cat in productos_por_categoria]
    categorias_data = [cat.total for cat in productos_por_categoria]
    categorias_colors = [cat.color for cat in productos_por_categoria]

    # Estadísticas de usuarios (solo admins)
    stats_usuarios = None
    if request.user.puede_aprobar():
        stats_usuarios = {
            'total': Usuario.objects.count(),
            'activos': Usuario.objects.filter(is_active=True).count(),
            'pendientes': Usuario.objects.filter(aprobado=False).count(),
        }

    context = {
        'total_productos': total_productos,
        'productos_disponibles': productos_disponibles,
        'productos_por_agotar': productos_por_agotar,
        'productos_agotados': productos_agotados,
        'valor_total': valor_total,
        'movimientos_hoy': movimientos_hoy,
        'productos_por_categoria': productos_por_categoria,
        'productos_stock_bajo': productos_stock_bajo,
        'ultimos_movimientos': ultimos_movimientos,
        'actividad_reciente': actividad_reciente,
        'alertas_pendientes': alertas_pendientes,
        'productos_mas_movidos': productos_mas_movidos,
        'categorias_labels': categorias_labels,
        'categorias_data': categorias_data,
        'categorias_colors': categorias_colors,
        'stats_usuarios': stats_usuarios,
    }

    return render(request, 'dashboard/home.html', context)
