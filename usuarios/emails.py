from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from .models import Usuario


def enviar_email_registro(usuario):
    """
    Envía un correo de confirmación de registro al usuario
    Informa que debe esperar aprobación
    """
    asunto = '✅ Registro Exitoso en SISBAR - Pendiente de Aprobación'
    
    mensaje_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .content {{
                padding: 40px 30px;
                color: #333;
            }}
            .info-box {{
                background-color: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin: 20px 0;
            }}
            .footer {{
                background-color: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #666;
                font-size: 14px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background-color: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛒 SISBAR </h1>
                <p>Sistema de Inventario Empresarial</p>
            </div>
            
            <div class="content">
                <h2>¡Hola {usuario.first_name}!</h2>
                
                <p>Tu registro en SISBAR ha sido exitoso. 🎉</p>
                
                <div class="info-box">
                    <strong>📋 Datos de tu cuenta:</strong><br>
                    <strong>Usuario:</strong> {usuario.username}<br>
                    <strong>Correo:</strong> {usuario.email}<br>
                    <strong>Rol solicitado:</strong> {usuario.get_rol_display()}<br>
                    <strong>Documento:</strong> {usuario.documento}
                </div>
                
                <p><strong>⏳ Estado:</strong> Pendiente de aprobación</p>
                
                <p>Un administrador revisará tu solicitud pronto. Recibirás un correo cuando tu cuenta sea aprobada.</p>
                
                <p>Mientras tanto, no podrás iniciar sesión hasta que tu cuenta sea activada.</p>
            </div>
            
            <div class="footer">
                <p>Este es un correo automático, por favor no responder.</p>
                <p><strong>SISBAR </strong> - Sistema de Inventario</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    mensaje_texto = strip_tags(mensaje_html)
    
    try:
        email = EmailMultiAlternatives(
            asunto,
            mensaje_texto,
            settings.DEFAULT_FROM_EMAIL,
            [usuario.email]
        )
        email.attach_alternative(mensaje_html, "text/html")
        email.send()
        return True
    except Exception as e:
        print(f"Error al enviar correo de registro: {e}")
        return False


def enviar_email_aprobacion(usuario, aprobado_por):
    """
    Envía un correo cuando un administrador aprueba la cuenta
    """
    asunto = '✅ Tu cuenta en SISBAR ha sido aprobada'
    
    mensaje_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .content {{
                padding: 40px 30px;
                color: #333;
            }}
            .success-box {{
                background-color: #d1fae5;
                border-left: 4px solid #10b981;
                padding: 20px;
                margin: 20px 0;
                border-radius: 5px;
            }}
            .button {{
                display: inline-block;
                padding: 15px 40px;
                background-color: #10b981;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
                font-weight: bold;
            }}
            .footer {{
                background-color: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #666;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✅ ¡Cuenta Aprobada!</h1>
            </div>
            
            <div class="content">
                <h2>¡Excelentes noticias, {usuario.first_name}!</h2>
                
                <div class="success-box">
                    <h3 style="margin-top: 0;">🎉 Tu cuenta ha sido aprobada</h3>
                    <p><strong>Rol asignado:</strong> {usuario.get_rol_display()}</p>
                    <p><strong>Aprobado por:</strong> {aprobado_por.get_full_name()}</p>
                </div>
                
                <p>Ya puedes iniciar sesión en SISBAR y comenzar a trabajar.</p>
                
                <div style="text-align: center;">
                    <a href="http://127.0.0.1:8000/usuarios/login/" class="button">
                        Iniciar Sesión Ahora
                    </a>
                </div>
                
                <p><strong>Tus credenciales:</strong></p>
                <ul>
                    <li><strong>Usuario:</strong> {usuario.username}</li>
                    <li><strong>Contraseña:</strong> La que elegiste al registrarte</li>
                </ul>
                
                <p>Si tienes alguna pregunta, contacta al administrador.</p>
            </div>
            
            <div class="footer">
                <p>Este es un correo automático, por favor no responder.</p>
                <p><strong>SISBAR </strong> - Sistema de Inventario</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    mensaje_texto = strip_tags(mensaje_html)
    
    try:
        email = EmailMultiAlternatives(
            asunto,
            mensaje_texto,
            settings.DEFAULT_FROM_EMAIL,
            [usuario.email]
        )
        email.attach_alternative(mensaje_html, "text/html")
        email.send()
        return True
    except Exception as e:
        print(f"Error al enviar correo de aprobación: {e}")
        return False

def enviar_email_alerta_admin(usuario):
    """
    Notifica a los administradores cuando hay un nuevo registro
    """
    asunto = '🔔 Nuevo usuario pendiente de aprobación - SISBAR'
    
    # Obtener todos los administradores
    admins = Usuario.objects.filter(
        rol__in=['SUPER_ADMIN', 'ADMIN'],
        is_active=True,
        aprobado=True
    )
    
    emails_admins = [admin.email for admin in admins if admin.email]
    
    if not emails_admins:
        return False
    
    mensaje_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .content {{
                padding: 40px 30px;
                color: #333;
            }}
            .alert-box {{
                background-color: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 20px;
                margin: 20px 0;
                border-radius: 5px;
            }}
            .button {{
                display: inline-block;
                padding: 15px 40px;
                background-color: #f59e0b;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
                font-weight: bold;
            }}
            .footer {{
                background-color: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #666;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔔 Nueva Solicitud de Registro</h1>
            </div>
            
            <div class="content">
                <h2>Atención Administrador</h2>
                
                <p>Un nuevo usuario se ha registrado y está esperando aprobación:</p>
                
                <div class="alert-box">
                    <strong>📋 Información del usuario:</strong><br><br>
                    <strong>Nombre:</strong> {usuario.get_full_name()}<br>
                    <strong>Usuario:</strong> {usuario.username}<br>
                    <strong>Correo:</strong> {usuario.email}<br>
                    <strong>Documento:</strong> {usuario.documento}<br>
                    <strong>Teléfono:</strong> {usuario.telefono or 'No proporcionado'}<br>
                    <strong>Rol solicitado:</strong> {usuario.get_rol_display()}
                </div>
                
                <p>Por favor, revisa la solicitud y aprueba o rechaza la cuenta desde el panel de administración.</p>
                
                <div style="text-align: center;">
                    <a href="http://127.0.0.1:8000/admin/usuarios/usuario/{usuario.id}/change/" class="button">
                        Revisar Solicitud
                    </a>
                </div>
            </div>
            
            <div class="footer">
                <p>Este es un correo automático, por favor no responder.</p>
                <p><strong>SISBAR </strong> - Sistema de Inventario</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    mensaje_texto = strip_tags(mensaje_html)
    
    try:
        email = EmailMultiAlternatives(
            asunto,
            mensaje_texto,
            settings.DEFAULT_FROM_EMAIL,
            emails_admins
        )
        email.attach_alternative(mensaje_html, "text/html")
        email.send()
        return True
    except Exception as e:
        print(f"Error al enviar correo a administradores: {e}")
        return False
    

def enviar_email_cambio_password(usuario):
    asunto = '🔐 Contraseña Cambiada - SISBAR'

    mensaje_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .content {{
                padding: 40px 30px;
                color: #333;
            }}
            .info-box {{
                background-color: #eff6ff;
                border-left: 4px solid #3b82f6;
                padding: 20px;
                margin: 20px 0;
                border-radius: 5px;
            }}
            .footer {{
                background-color: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #666;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Contraseña Actualizada</h1>
            </div>
            
            <div class="content">
                <h2>Hola {usuario.first_name},</h2>

                <p>Tu contraseña fue cambiada correctamente.</p>

                <div class="info-box">
                    <strong>🕒 Fecha del cambio:</strong><br>
                    El cambio fue realizado desde tu cuenta.<br><br>

                    Si <strong>tú no realizaste este cambio</strong>, contacta al administrador inmediatamente.
                </div>
            </div>
            
            <div class="footer">
                <p>Este es un correo automático, por favor no responder.</p>
                <p><strong>SISBAR</strong> - Sistema de Inventario</p>
            </div>
        </div>
    </body>
    </html>
    """

    mensaje_texto = strip_tags(mensaje_html)

    email = EmailMultiAlternatives(
        asunto,
        mensaje_texto,
        settings.DEFAULT_FROM_EMAIL,
        [usuario.email]
    )
    email.attach_alternative(mensaje_html, "text/html")
    email.send()

    