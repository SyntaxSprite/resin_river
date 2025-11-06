"""
Email utility functions for sending order-related emails
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def send_order_confirmation_email(order):
    """
    Send order confirmation email to customer
    """
    try:
        # Get recipient email
        if order.user:
            recipient_email = order.user.email
        elif order.guest_email:
            recipient_email = order.guest_email
        else:
            recipient_email = order.contact_email_phone if '@' in order.contact_email_phone else None
        
        if not recipient_email:
            return False
        
        # Prepare context
        context = {
            'order': order,
            'site_name': getattr(settings, 'SITE_NAME', 'Resin River'),
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }
        
        # Render email templates
        subject = f'Order Confirmation - Order #{order.order_number}'
        html_message = render_to_string('resin_apps/emails/order_confirmation.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        
        return True
    except Exception as e:
        print(f"Error sending order confirmation email: {e}")
        return False


def send_order_status_update_email(order, status_change):
    """
    Send email when order status changes (e.g., shipped, delivered)
    """
    try:
        # Get recipient email
        if order.user:
            recipient_email = order.user.email
        elif order.guest_email:
            recipient_email = order.guest_email
        else:
            recipient_email = order.contact_email_phone if '@' in order.contact_email_phone else None
        
        if not recipient_email:
            return False
        
        # Prepare context
        context = {
            'order': order,
            'status_change': status_change,
            'site_name': getattr(settings, 'SITE_NAME', 'Resin River'),
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }
        
        # Render email templates
        subject = f'Order Update - Order #{order.order_number}'
        html_message = render_to_string('resin_apps/emails/order_status_update.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        
        return True
    except Exception as e:
        print(f"Error sending order status update email: {e}")
        return False


def send_payment_confirmation_email(order):
    """
    Send payment confirmation email
    """
    try:
        # Get recipient email
        if order.user:
            recipient_email = order.user.email
        elif order.guest_email:
            recipient_email = order.guest_email
        else:
            recipient_email = order.contact_email_phone if '@' in order.contact_email_phone else None
        
        if not recipient_email:
            return False
        
        # Prepare context
        context = {
            'order': order,
            'site_name': getattr(settings, 'SITE_NAME', 'Resin River'),
            'site_url': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        }
        
        # Render email templates
        subject = f'Payment Confirmed - Order #{order.order_number}'
        html_message = render_to_string('resin_apps/emails/payment_confirmation.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        
        return True
    except Exception as e:
        print(f"Error sending payment confirmation email: {e}")
        return False

