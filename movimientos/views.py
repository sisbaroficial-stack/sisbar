from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Movimiento, AlertaInventario
from datetime import timedelta
from django.utils import timezone


@login_required
def listar_movimientos_view(request):
    """Lista todos los movimientos"""
    # Filtro por período
    dias = int(request.GET.get('dias', 7))
    fecha_desde = timezone.now() - timedelta(days=dias)
    
    movimientos = Movimiento.objects.filter(
        fecha__gte=fecha_desde
    ).select_related('producto', 'usuario').order_by('-fecha')
    
    context = {
        'movimientos': movimientos,
        'dias': dias,
    }
    return render(request, 'movimientos/listar.html', context)


@login_required
def listar_alertas_view(request):
    """Lista todas las alertas"""
    alertas = AlertaInventario.objects.filter(
        resuelta=False
    ).select_related('producto').order_by('-fecha_generada')
    
    context = {
        'alertas': alertas,
    }
    return render(request, 'movimientos/alertas.html', context)