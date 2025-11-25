from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Proveedor
from usuarios.views import registrar_actividad


@login_required
def listar_proveedores_view(request):
    """Lista todos los proveedores"""
    proveedores = Proveedor.objects.filter(activo=True).order_by('nombre')
    
    context = {
        'proveedores': proveedores,
    }
    return render(request, 'proveedores/listar.html', context)


@login_required
def crear_proveedor_view(request):
    """Crear nuevo proveedor"""
    if not request.user.puede_gestionar_inventario():
        messages.error(request, '❌ No tienes permisos.')
        return redirect('proveedores:listar')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        nit = request.POST.get('nit', '')
        contacto = request.POST.get('contacto', '')
        telefono = request.POST.get('telefono', '')
        email = request.POST.get('email', '')
        direccion = request.POST.get('direccion', '')
        ciudad = request.POST.get('ciudad', '')
        calificacion = request.POST.get('calificacion', 3)
        notas = request.POST.get('notas', '')
        
        if nombre:
            Proveedor.objects.create(
                nombre=nombre,
                nit=nit,
                contacto=contacto,
                telefono=telefono,
                email=email,
                direccion=direccion,
                ciudad=ciudad,
                calificacion=calificacion,
                notas=notas
            )
            
            registrar_actividad(
                request.user,
                'CREAR',
                f'Creó el proveedor {nombre}',
                request
            )
            
            messages.success(request, f'✅ Proveedor {nombre} creado.')
            return redirect('proveedores:listar')
        else:
            messages.error(request, '❌ El nombre es obligatorio.')
    
    return render(request, 'proveedores/crear.html')


@login_required
def ver_proveedor_view(request, proveedor_id):
    """Ver detalles del proveedor"""
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    productos = proveedor.productos.filter(activo=True)[:10]
    
    context = {
        'proveedor': proveedor,
        'productos': productos,
    }
    return render(request, 'proveedores/ver.html', context)


@login_required
def editar_proveedor_view(request, proveedor_id):
    """Editar proveedor"""
    if not request.user.puede_gestionar_inventario():
        messages.error(request, '❌ No tienes permisos.')
        return redirect('proveedores:listar')
    
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    
    if request.method == 'POST':
        proveedor.nombre = request.POST.get('nombre')
        proveedor.nit = request.POST.get('nit', '')
        proveedor.contacto = request.POST.get('contacto', '')
        proveedor.telefono = request.POST.get('telefono', '')
        proveedor.email = request.POST.get('email', '')
        proveedor.direccion = request.POST.get('direccion', '')
        proveedor.ciudad = request.POST.get('ciudad', '')
        proveedor.calificacion = request.POST.get('calificacion', 3)
        proveedor.notas = request.POST.get('notas', '')
        proveedor.save()
        
        registrar_actividad(
            request.user,
            'EDITAR',
            f'Editó el proveedor {proveedor.nombre}',
            request
        )
        
        messages.success(request, f'✅ Proveedor actualizado.')
        return redirect('proveedores:listar')
    
    context = {'proveedor': proveedor}
    return render(request, 'proveedores/editar.html', context)


@login_required
def eliminar_proveedor_view(request, proveedor_id):
    """Desactivar proveedor"""
    if not request.user.puede_eliminar():
        messages.error(request, '❌ No tienes permisos.')
        return redirect('proveedores:listar')
    
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    
    if request.method == 'POST':
        proveedor.activo = False
        proveedor.save()
        
        registrar_actividad(
            request.user,
            'ELIMINAR',
            f'Desactivó el proveedor {proveedor.nombre}',
            request
        )
        
        messages.success(request, f'✅ Proveedor desactivado.')
        return redirect('proveedores:listar')
    
    context = {'proveedor': proveedor}
    return render(request, 'proveedores/eliminar.html', context)