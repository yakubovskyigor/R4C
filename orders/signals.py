from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from robots.models import Robot
from django.core.mail import send_mail


@receiver(post_save, sender=Robot)
def notify_available_robot(instance, **kwargs):
    orders = Order.objects.filter(robot_serial=instance.serial)
    if orders.exists():
        subject = "Робот доступен!"
        message = 'Добрый день! Недавно вы интересовались нашим роботом модели {}, версии {}. \n' \
                  'Этот робот теперь в наличии. Если вам подходит этот вариант - пожалуйста, свяжитесь с нами.'\
                   .format(instance.model, instance.version)
        from_email = "igorby8881@gmail.com"  # Замените на вашу электронную почту
        recipient_list = [order.customer.email for order in orders]
        send_mail(subject, message, from_email, recipient_list)
