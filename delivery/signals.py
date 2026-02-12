from django.db.models.signals import post_save
from django.dispatch import receiver

from delivery.models import Delivery, DeliveryStatusHistory


@receiver(post_save, sender=Delivery)
def create_delivery_status_history(sender, instance, created, **kwargs):
    """
    Delivery status o'zgarganda avtomatik history yaratadi.
    
    TZ 6.8: "Buyurtma holatlaridagi barcha o'zgarishlar tarixda saqlanadi"
    """
    
    # Faqat status o'zgargan bo'lsa
    if hasattr(instance, '_status_changed') and instance._status_changed:
        DeliveryStatusHistory.objects.create(
            delivery=instance,
            old_status=instance._old_status,
            new_status=instance.status,
            changed_by=getattr(instance, '_changed_by', None)
        )
        
        # Cleanup temporary attributes
        delattr(instance, '_status_changed')
        delattr(instance, '_old_status')
