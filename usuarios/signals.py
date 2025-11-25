from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Usuario
from .emails import enviar_email_registro, enviar_email_aprobacion, enviar_email_alerta_admin


@receiver(post_save, sender=Usuario)
def gestionar_correos_usuario(sender, instance, created, **kwargs):

    if created:
        # Usuario registrado
        enviar_email_registro(instance)

        # Notificación a administradores
        enviar_email_alerta_admin(instance)

    else:
        # Usuario aprobado
        if instance.aprobado and not instance.notificado_aprobacion:

            aprobador = instance.aprobado_por

            # Si ningún aprobador fue asignado, escoger un superusuario
            if aprobador is None:
                User = get_user_model()
                aprobador = User.objects.filter(is_superuser=True).first()

            # Enviar correo
            enviar_email_aprobacion(instance, aprobador)

            # Marcar que ya se envió
            instance.notificado_aprobacion = True

            # Importante: evitar que el post_save genere loop infinito
            Usuario.objects.filter(pk=instance.pk).update(
                notificado_aprobacion=True
            )
