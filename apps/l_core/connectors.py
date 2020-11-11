from django.db.models import signals

from crm_module.models import Contact
from .models import CoreUser


def create_update_CoreUser(sender, instance: CoreUser, created, **kwargs):
    params = dict(first_name=instance.first_name, last_name=instance.last_name, related_user=instance,
                  email=instance.email)
    if Contact.objects.filter(related_user=instance).count() > 0:
        Contact.objects.filter(related_user=instance).update(**params)
    else:
        Contact.objects.create(**params)


signals.post_save.connect(receiver=create_update_CoreUser, sender=CoreUser)
