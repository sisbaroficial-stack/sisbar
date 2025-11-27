from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Usuario, HistorialActividad
from .forms import (
    RegistroUsuarioForm, 
    LoginForm, 
    PerfilUsuarioForm, 
    CambiarPasswordForm,
    AprobarUsuarioForm
)
from .emails import enviar_email_registro, enviar_email_aprobacion, enviar_email_alerta_admin


def get_client_ip(request):
    """Obtiene la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def registrar_actividad(usuario, tipo, descripcion, request=None):
    """Registra una actividad del usuario"""
    ip = get_client_ip(request) if request else None
    HistorialActividad.objects.create(
        usuario=usuario,
        tipo=tipo,
        descripcion=descripcion,
        ip_address=ip
    )


def registro_view(request):
    """
    Vista de registro de nuevos usuarios
    Los usuarios quedan pendientes de aprobación
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            # Crear usuario pero no aprobado
            usuario = form.save(commit=False)
            usuario.aprobado = False
            usuario.is_active = True  # Activo pero no aprobado
            usuario.save()
            
            # Registrar actividad
            registrar_actividad(
                usuario, 
                'CREAR', 
                f'Usuario {usuario.username} se registró en el sistema',
                request
            )
            
            # Enviar correos
            enviar_email_registro(usuario)
            enviar_email_alerta_admin(usuario)
            
            messages.success(
                request, 
                '✅ ¡Registro exitoso! Recibirás un correo cuando tu cuenta sea aprobada.'
            )
            return redirect('usuarios:login')
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})


def login_view(request):
    """
    Vista de inicio de sesión
    Verifica que el usuario esté aprobado
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Registrar actividad
            registrar_actividad(
                user,
                'LOGIN',
                f'{user.username} inició sesión',
                request
            )
            
            messages.success(request, f'¡Bienvenido, {user.first_name}!')
            
            # Redirigir según el rol
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard:home')
    else:
        form = LoginForm()
    
    return render(request, 'usuarios/login.html', {'form': form})


@login_required
def logout_view(request):
    """Vista de cierre de sesión"""
    # Registrar actividad antes de cerrar sesión
    registrar_actividad(
        request.user,
        'LOGOUT',
        f'{request.user.username} cerró sesión',
        request
    )
    
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('index')


@login_required
def perfil_view(request):
    """Vista del perfil del usuario"""
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            
            registrar_actividad(
                request.user,
                'EDITAR',
                'Usuario actualizó su perfil',
                request
            )
            
            messages.success(request, '✅ Perfil actualizado correctamente.')
            return redirect('usuarios:perfil')
    else:
        form = PerfilUsuarioForm(instance=request.user)
    
    # Obtener últimas actividades del usuario
    actividades = HistorialActividad.objects.filter(
        usuario=request.user
    ).order_by('-fecha')[:10]
    
    context = {
        'form': form,
        'actividades': actividades
    }
    return render(request, 'usuarios/perfil.html', context)


@login_required
def cambiar_password_view(request):
    """Vista para cambiar contraseña"""
    if request.method == 'POST':
        form = CambiarPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            
            registrar_actividad(
                request.user,
                'EDITAR',
                'Usuario cambió su contraseña',
                request
            )
            
            messages.success(request, '✅ Contraseña cambiada exitosamente.')
            return redirect('usuarios:perfil')
    else:
        form = CambiarPasswordForm(request.user)
    
    return render(request, 'usuarios/cambiar_password.html', {'form': form})


def es_admin(user):
    """Verifica si el usuario es administrador"""
    return user.rol in ['SUPER_ADMIN', 'ADMIN']


@login_required
@user_passes_test(es_admin)
def gestionar_usuarios_view(request):
    """
    Vista para que administradores gestionen usuarios
    Solo accesible por SUPER_ADMIN y ADMIN
    """
    # Filtros
    filtro = request.GET.get('filtro', 'todos')
    busqueda = request.GET.get('q', '')
    
    usuarios = Usuario.objects.all()
    
    # Aplicar filtros
    if filtro == 'pendientes':
        usuarios = usuarios.filter(aprobado=False)
    elif filtro == 'aprobados':
        usuarios = usuarios.filter(aprobado=True)
    elif filtro == 'activos':
        usuarios = usuarios.filter(is_active=True)
    elif filtro == 'inactivos':
        usuarios = usuarios.filter(is_active=False)
    
    # Búsqueda
    if busqueda:
        usuarios = usuarios.filter(
            Q(username__icontains=busqueda) |
            Q(first_name__icontains=busqueda) |
            Q(last_name__icontains=busqueda) |
            Q(email__icontains=busqueda) |
            Q(documento__icontains=busqueda)
        )
    
    usuarios = usuarios.order_by('-date_joined')
    
    # Estadísticas
    stats = {
        'total': Usuario.objects.count(),
        'pendientes': Usuario.objects.filter(aprobado=False).count(),
        'aprobados': Usuario.objects.filter(aprobado=True).count(),
        'activos': Usuario.objects.filter(is_active=True).count(),
    }
    
    context = {
        'usuarios': usuarios,
        'stats': stats,
        'filtro': filtro,
        'busqueda': busqueda
    }
    return render(request, 'usuarios/gestionar_usuarios.html', context)


@login_required
@user_passes_test(es_admin)
def aprobar_usuario_view(request, usuario_id):
    """
    Vista para aprobar un usuario
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    if request.method == 'POST':
        form = AprobarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario = form.save(commit=False)
            if usuario.aprobado and not usuario.fecha_aprobacion:
                usuario.fecha_aprobacion = timezone.now()
                usuario.aprobado_por = request.user
            usuario.save()
            
            # Enviar correo de aprobación
            if usuario.aprobado:
                enviar_email_aprobacion(usuario, request.user)
                
                registrar_actividad(
                    request.user,
                    'EDITAR',
                    f'Aprobó la cuenta de {usuario.username}',
                    request
                )
                
                messages.success(
                    request, 
                    f'✅ Usuario {usuario.username} aprobado correctamente.'
                )
            else:
                messages.info(request, f'Usuario {usuario.username} actualizado.')
            
            return redirect('usuarios:gestionar_usuarios')
    else:
        form = AprobarUsuarioForm(instance=usuario)
    
    context = {
        'form': form,
        'usuario_obj': usuario
    }
    return render(request, 'usuarios/aprobar_usuario.html', context)


@login_required
@user_passes_test(es_admin)
def toggle_usuario_view(request, usuario_id):
    """
    Activar/desactivar usuario
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    # No permitir que se desactive a sí mismo
    if usuario == request.user:
        messages.error(request, '❌ No puedes desactivar tu propia cuenta.')
        return redirect('usuarios:gestionar_usuarios')
    
    usuario.is_active = not usuario.is_active
    usuario.save()
    
    estado = 'activó' if usuario.is_active else 'desactivó'
    
    registrar_actividad(
        request.user,
        'EDITAR',
        f'{estado.capitalize()} la cuenta de {usuario.username}',
        request
    )
    
    messages.success(
        request, 
        f'✅ Usuario {usuario.username} {estado} correctamente.'
    )
    
    return redirect('usuarios:gestionar_usuarios')





@login_required
@user_passes_test(es_admin)
def editar_usuario_completo_view(request, usuario_id):
    usuario_editar = get_object_or_404(Usuario, id=usuario_id)

    if request.method == 'POST':
        usuario_editar.first_name = request.POST.get('first_name')
        usuario_editar.last_name = request.POST.get('last_name')
        usuario_editar.email = request.POST.get('email')
        usuario_editar.telefono = request.POST.get('telefono', '').strip()

        # Nuevo documento recibido
        nuevo_documento = request.POST.get('documento', '').strip()

        # VALIDACIÓN: revisar si el documento ya existe en otro usuario
        if Usuario.objects.exclude(id=usuario_editar.id).filter(documento=nuevo_documento).exists():
            messages.error(request, "❌ Ya existe un usuario con ese número de documento.")
            return redirect('usuarios:editar_usuario_completo', usuario_id=usuario_editar.id)

        usuario_editar.documento = nuevo_documento
        usuario_editar.rol = request.POST.get('rol')
        usuario_editar.is_active = request.POST.get('is_active') == 'on'

        if not usuario_editar.aprobado and request.POST.get('aprobado') == 'on':
            usuario_editar.aprobar_usuario(request.user)
            enviar_email_aprobacion(usuario_editar, request.user)
        else:
            usuario_editar.aprobado = request.POST.get('aprobado') == 'on'

        usuario_editar.save()

        registrar_actividad(
            request.user,
            'EDITAR',
            f'Editó el usuario {usuario_editar.username}',
            request
        )

        messages.success(request, f'Usuario {usuario_editar.username} actualizado correctamente.')
        return redirect('usuarios:gestionar_usuarios')

    return render(request, 'usuarios/editar_usuario_completo.html', {
        'usuario_editar': usuario_editar,
    })


@login_required
@user_passes_test(es_admin)
def resetear_password_view(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == 'POST':
        nueva_password = request.POST.get('nueva_password', '').strip()
        if nueva_password:
            usuario.set_password(nueva_password)
            usuario.save()

            registrar_actividad(
                request.user,
                'EDITAR',
                f'Reseteó la contraseña de {usuario.username}',
                request
            )

            messages.success(request, f'Contraseña de {usuario.username} reseteada.')
            return redirect('usuarios:gestionar_usuarios')

    return render(request, 'usuarios/resetear_password.html', {
        'usuario': usuario
    })


@login_required
@user_passes_test(es_admin)
def eliminar_usuario_view(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)

    if usuario == request.user:
        messages.error(request, 'No puedes eliminar tu propia cuenta.')
        return redirect('usuarios:gestionar_usuarios')

    if request.method == 'POST':
        usuario.is_active = False
        usuario.save()

        registrar_actividad(
            request.user,
            'ELIMINAR',
            f'Desactivó al usuario {usuario.username}',
            request
        )

        messages.success(request, f'Usuario {usuario.username} desactivado.')
        return redirect('usuarios:gestionar_usuarios')

    return render(request, 'usuarios/eliminar_usuario.html', {
        'usuario': usuario
    })
