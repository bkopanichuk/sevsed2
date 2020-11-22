from django.db.models import signals
from ..models import SEVOutgoing#, SEVIncoming
from ..services.sender_service import SendToSEVOVVProcess
#from ..services.download_service import ProcessIncoming

def processing_outgoing(instance, created, update_fields, **kwargs):
    if created:
        service = SendToSEVOVVProcess(outgoing_doc=instance)
        service.run()

# def process_incoming(instance, created, update_fields, **kwargs):
#     print('process_incoming')
#     if created:
#         print('ProcessIncoming')



signals.post_save.connect(receiver=processing_outgoing, sender=SEVOutgoing)
# signals.post_save.connect(receiver=process_incoming, sender=SEVIncoming)