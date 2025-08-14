"""
Configuración de emails para el sistema de aerolínea.

Este módulo configura el sistema de envío de emails con:
- Templates HTML personalizados
- Configuración de SMTP
- Funciones helper para envío
"""

import logging
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils.translation import gettext as _


logger = logging.getLogger(__name__)


class EmailService:
    """
    Servicio para envío de emails del sistema de aerolínea.
    
    Proporciona métodos para enviar diferentes tipos de emails:
    - Confirmación de reserva
    - Recordatorio de vuelo
    - Cambios de estado
    - Notificaciones administrativas
    """
    
    @staticmethod
    def send_reservation_confirmation(reservation, user):
        """
        Envía email de confirmación de reserva.
        
        Args:
            reservation: Objeto Reserva
            user: Usuario que realizó la reserva
        """
        try:
            subject = _('Confirmación de Reserva - Vuelo {}').format(
                reservation.vuelo.codigo_vuelo
            )
            
            # Renderizar template HTML
            html_content = render_to_string('emails/reservation_confirmation.html', {
                'reservation': reservation,
                'user': user,
                'vuelo': reservation.vuelo,
                'pasajero': reservation.pasajero,
                'asiento': reservation.asiento
            })
            
            # Versión texto plano
            text_content = strip_tags(html_content)
            
            # Crear email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            
            email.attach_alternative(html_content, "text/html")
            
            # Enviar email
            email.send()
            
            logger.info(
                f"Email de confirmación enviado a {user.email} "
                f"para reserva {reservation.codigo_reserva}"
            )
            
            return True
            
        except Exception as e:
            logger.error(
                f"Error enviando email de confirmación a {user.email}: {str(e)}"
            )
            return False
    
    @staticmethod
    def send_flight_reminder(reservation, user):
        """
        Envía email de recordatorio de vuelo.
        
        Args:
            reservation: Objeto Reserva
            user: Usuario que realizó la reserva
        """
        try:
            subject = _('Recordatorio de Vuelo - {} → {}').format(
                reservation.vuelo.origen,
                reservation.vuelo.destino
            )
            
            # Renderizar template HTML
            html_content = render_to_string('emails/flight_reminder.html', {
                'reservation': reservation,
                'user': user,
                'vuelo': reservation.vuelo,
                'pasajero': reservation.pasajero,
                'asiento': reservation.asiento
            })
            
            # Versión texto plano
            text_content = strip_tags(html_content)
            
            # Crear email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            
            email.attach_alternative(html_content, "text/html")
            
            # Enviar email
            email.send()
            
            logger.info(
                f"Email de recordatorio enviado a {user.email} "
                f"para vuelo {reservation.vuelo.codigo_vuelo}"
            )
            
            return True
            
        except Exception as e:
            logger.error(
                f"Error enviando email de recordatorio a {user.email}: {str(e)}"
            )
            return False
    
    @staticmethod
    def send_flight_status_change(vuelo, old_status, new_status, users):
        """
        Envía email de cambio de estado de vuelo.
        
        Args:
            vuelo: Objeto Vuelo
            old_status: Estado anterior
            new_status: Nuevo estado
            users: Lista de usuarios a notificar
        """
        try:
            subject = _('Cambio de Estado - Vuelo {}').format(vuelo.codigo_vuelo)
            
            # Renderizar template HTML
            html_content = render_to_string('emails/flight_status_change.html', {
                'vuelo': vuelo,
                'old_status': old_status,
                'new_status': new_status
            })
            
            # Versión texto plano
            text_content = strip_tags(html_content)
            
            # Enviar a todos los usuarios
            for user in users:
                try:
                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=text_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[user.email]
                    )
                    
                    email.attach_alternative(html_content, "text/html")
                    email.send()
                    
                    logger.info(
                        f"Email de cambio de estado enviado a {user.email} "
                        f"para vuelo {vuelo.codigo_vuelo}"
                    )
                    
                except Exception as e:
                    logger.error(
                        f"Error enviando email a {user.email}: {str(e)}"
                    )
            
            return True
            
        except Exception as e:
            logger.error(
                f"Error enviando emails de cambio de estado: {str(e)}"
            )
            return False
    
    @staticmethod
    def send_welcome_email(user):
        """
        Envía email de bienvenida a nuevos usuarios.
        
        Args:
            user: Usuario recién registrado
        """
        try:
            subject = _('¡Bienvenido a {}!').format(settings.SITE_NAME)
            
            # Renderizar template HTML
            html_content = render_to_string('emails/welcome.html', {
                'user': user,
                'site_name': settings.SITE_NAME
            })
            
            # Versión texto plano
            text_content = strip_tags(html_content)
            
            # Crear email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            
            email.attach_alternative(html_content, "text/html")
            
            # Enviar email
            email.send()
            
            logger.info(f"Email de bienvenida enviado a {user.email}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email de bienvenida a {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_password_reset(user, reset_url):
        """
        Envía email de restablecimiento de contraseña.
        
        Args:
            user: Usuario que solicitó el restablecimiento
            reset_url: URL para restablecer la contraseña
        """
        try:
            subject = _('Restablecimiento de Contraseña')
            
            # Renderizar template HTML
            html_content = render_to_string('emails/password_reset.html', {
                'user': user,
                'reset_url': reset_url,
                'site_name': settings.SITE_NAME
            })
            
            # Versión texto plano
            text_content = strip_tags(html_content)
            
            # Crear email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            
            email.attach_alternative(html_content, "text/html")
            
            # Enviar email
            email.send()
            
            logger.info(f"Email de restablecimiento enviado a {user.email}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email de restablecimiento a {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_admin_notification(subject, message, admin_emails):
        """
        Envía notificación administrativa.
        
        Args:
            subject: Asunto del email
            message: Mensaje del email
            admin_emails: Lista de emails de administradores
        """
        try:
            # Renderizar template HTML
            html_content = render_to_string('emails/admin_notification.html', {
                'subject': subject,
                'message': message,
                'site_name': settings.SITE_NAME
            })
            
            # Versión texto plano
            text_content = strip_tags(html_content)
            
            # Enviar a todos los administradores
            for admin_email in admin_emails:
                try:
                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=text_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[admin_email]
                    )
                    
                    email.attach_alternative(html_content, "text/html")
                    email.send()
                    
                    logger.info(f"Notificación administrativa enviada a {admin_email}")
                    
                except Exception as e:
                    logger.error(f"Error enviando notificación a {admin_email}: {str(e)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando notificaciones administrativas: {str(e)}")
            return False


def send_simple_email(subject, message, recipient_list, html_message=None):
    """
    Función helper para envío de emails simples.
    
    Args:
        subject: Asunto del email
        message: Mensaje del email
        recipient_list: Lista de destinatarios
        html_message: Mensaje HTML (opcional)
    
    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message
        )
        
        logger.info(f"Email simple enviado a {recipient_list}")
        return True
        
    except Exception as e:
        logger.error(f"Error enviando email simple: {str(e)}")
        return False


def send_bulk_email(subject, message, recipient_list, html_message=None):
    """
    Función helper para envío masivo de emails.
    
    Args:
        subject: Asunto del email
        message: Mensaje del email
        recipient_list: Lista de destinatarios
        html_message: Mensaje HTML (opcional)
    
    Returns:
        int: Número de emails enviados exitosamente
    """
    success_count = 0
    
    for recipient in recipient_list:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                html_message=html_message
            )
            
            success_count += 1
            logger.info(f"Email masivo enviado a {recipient}")
            
        except Exception as e:
            logger.error(f"Error enviando email masivo a {recipient}: {str(e)}")
    
    logger.info(f"Envio masivo completado: {success_count}/{len(recipient_list)} emails enviados")
    return success_count 