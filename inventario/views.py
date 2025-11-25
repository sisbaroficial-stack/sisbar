from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Producto
from categorias.models import Categoria, Subcategoria
from proveedores.models import Proveedor
from movimientos.models import Movimiento, AlertaInventario
from usuarios.views import registrar_actividad
from .forms import ProductoForm, DescontarProductoForm


@login_required
def listar_productos_view(request):
    """
    Lista todos los productos con filtros
    """
    # Filtros
    categoria_id = request.GET.get('categoria')
    estado = request.GET.get('estado')
    busqueda = request.GET.get('q', '')
    
    productos = Producto.objects.filter(activo=True).select_related(
        'categoria', 'subcategoria', 'proveedor'
    )
    
    # Aplicar filtros
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if estado:
        productos = productos.filter(estado=estado)
    
    # Búsqueda
    if busqueda:
        productos = productos.filter(
            Q(codigo__icontains=busqueda) |
            Q(codigo_barras__icontains=busqueda) |
            Q(nombre__icontains=busqueda) |
            Q(descripcion__icontains=busqueda)
        )
    
    productos = productos.order_by('-fecha_creacion')
    
    # Obtener categorías para el filtro
    categorias = Categoria.objects.filter(activa=True)
    
    # Estadísticas
    stats = {
        'total': Producto.objects.filter(activo=True).count(),
        'disponibles': Producto.objects.filter(activo=True, estado='DISPONIBLE').count(),
        'por_agotar': Producto.objects.filter(activo=True, estado='POR_AGOTAR').count(),
        'agotados': Producto.objects.filter(activo=True, estado='AGOTADO').count(),
    }
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'stats': stats,
        'categoria_id': categoria_id,
        'estado': estado,
        'busqueda': busqueda
    }
    
    return render(request, 'inventario/listar_productos.html', context)


@login_required
def crear_producto_view(request):
    """
    Crear un nuevo producto
    """
    if not request.user.puede_gestionar_inventario():
        messages.error(request, '❌ No tienes permisos para crear productos.')
        return redirect('inventario:listar_productos')
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.creado_por = request.user
            producto.save()
            
            # Registrar actividad
            registrar_actividad(
                request.user,
                'CREAR',
                f'Creó el producto {producto.codigo} - {producto.nombre}',
                request
            )
            
            messages.success(request, f'✅ Producto {producto.nombre} creado exitosamente.')
            return redirect('inventario:listar_productos')
    else:
        form = ProductoForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Nuevo Producto'
    }
    
    return render(request, 'inventario/form_producto.html', context)


@login_required
def editar_producto_view(request, producto_id):
    """
    Editar un producto existente
    """
    if not request.user.puede_gestionar_inventario():
        messages.error(request, '❌ No tienes permisos para editar productos.')
        return redirect('inventario:listar_productos')
    
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            
            # Registrar actividad
            registrar_actividad(
                request.user,
                'EDITAR',
                f'Editó el producto {producto.codigo} - {producto.nombre}',
                request
            )
            
            messages.success(request, f'✅ Producto {producto.nombre} actualizado exitosamente.')
            return redirect('inventario:listar_productos')
    else:
        form = ProductoForm(instance=producto)
    
    context = {
        'form': form,
        'producto': producto,
        'titulo': 'Editar Producto'
    }
    
    return render(request, 'inventario/form_producto.html', context)


@login_required
def ver_producto_view(request, producto_id):
    """
    Ver detalles de un producto
    """
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Obtener movimientos del producto
    movimientos = producto.movimientos.order_by('-fecha')[:10]
    
    context = {
        'producto': producto,
        'movimientos': movimientos
    }
    
    return render(request, 'inventario/ver_producto.html', context)


@login_required
def eliminar_producto_view(request, producto_id):
    """
    Eliminar (desactivar) un producto
    """
    if not request.user.puede_eliminar():
        messages.error(request, '❌ No tienes permisos para eliminar productos.')
        return redirect('inventario:listar_productos')
    
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        producto.activo = False
        producto.save()
        
        # Registrar actividad
        registrar_actividad(
            request.user,
            'ELIMINAR',
            f'Desactivó el producto {producto.codigo} - {producto.nombre}',
            request
        )
        
        messages.success(request, f'✅ Producto {producto.nombre} desactivado.')
        return redirect('inventario:listar_productos')
    
    context = {'producto': producto}
    return render(request, 'inventario/eliminar_producto.html', context)


@login_required
def descontar_producto_view(request):
    """
    Panel para descontar productos del inventario
    """
    if not request.user.puede_gestionar_inventario():
        messages.error(request, '❌ No tienes permisos para descontar productos.')
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = DescontarProductoForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['codigo']
            cantidad = form.cleaned_data['cantidad']
            motivo = form.cleaned_data['motivo']
            
            try:
                # Buscar producto por código o código de barras
                producto = Producto.objects.get(
                    Q(codigo=codigo) | Q(codigo_barras=codigo),
                    activo=True
                )
                
                # Descontar cantidad
                producto.descontar_cantidad(cantidad, request.user)
                
                # Registrar actividad
                registrar_actividad(
                    request.user,
                    'DESCONTAR',
                    f'Descontó {cantidad} unidades de {producto.nombre}',
                    request
                )
                
                # Generar alertas si es necesario
                AlertaInventario.generar_alertas()
                
                messages.success(
                    request,
                    f'✅ Se descontaron {cantidad} unidades de {producto.nombre}. Stock actual: {producto.cantidad}'
                )
                
                # Limpiar formulario
                form = DescontarProductoForm()
                
            except Producto.DoesNotExist:
                messages.error(request, f'❌ No se encontró un producto con el código: {codigo}')
            except ValueError as e:
                messages.error(request, f'❌ {str(e)}')
            except Exception as e:
                messages.error(request, f'❌ Error al descontar producto: {str(e)}')
    else:
        form = DescontarProductoForm()
    
    # Últimos movimientos
    ultimos_movimientos = Movimiento.objects.filter(
        tipo='SALIDA'
    ).select_related('producto', 'usuario').order_by('-fecha')[:10]
    
    context = {
        'form': form,
        'ultimos_movimientos': ultimos_movimientos
    }
    
    return render(request, 'inventario/descontar_producto.html', context)


@login_required
def buscar_producto_ajax(request):
    """
    Buscar producto por código (AJAX)
    """
    codigo = request.GET.get('codigo', '')
    
    try:
        producto = Producto.objects.get(
            Q(codigo=codigo) | Q(codigo_barras=codigo),
            activo=True
        )
        
        data = {
            'encontrado': True,
            'producto': {
                'id': producto.id,
                'codigo': producto.codigo,
                'nombre': producto.nombre,
                'categoria': producto.categoria.nombre,
                'cantidad': producto.cantidad,
                'unidad_medida': producto.get_unidad_medida_display(),
                'estado': producto.get_estado_display(),
                'estado_color': producto.get_estado_color(),
            }
        }
    except Producto.DoesNotExist:
        data = {
            'encontrado': False,
            'mensaje': 'Producto no encontrado'
        }
    
    return JsonResponse(data)