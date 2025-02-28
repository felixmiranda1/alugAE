from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import Landlord, AdoptionCode

@receiver(post_save, sender=Landlord)
def create_adoption_code(sender, instance, created, **kwargs):
    if created and isinstance(instance, Landlord):  # Garante que é Landlord e não CustomUser
        AdoptionCode.objects.create(landlord=instance)
