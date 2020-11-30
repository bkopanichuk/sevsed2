import logging

from django.db.models import signals

from apps.contracts.models.contract_model import  Contract,   ContractProducts, ContractSubscription
from apps.contracts.models.register_accrual_model import RegisterAccrual
from apps.contracts.models.register_payment_model import RegisterPayment
from apps.contracts.models.register_act_model import RegisterAct
from apps.contracts.models.contract_finance_model import ContractFinance
from apps.contracts.services.create_stage_property import CreateStageProperty

logger = logging.getLogger(__name__)


def create_act(sender, instance, created, **kwargs):
    instance.contract.refresh_balance()


def post_delete_act(sender, instance: RegisterAct, **kwargs):
    if instance.contract:
        instance.contract.refresh_balance()


def create_update_payment(sender, instance, created, **kwargs):
    instance.contract.refresh_balance()


def delete_payment(sender, instance, **kwargs):
    instance.contract.refresh_balance()


def create_update_accrual(sender, instance, created, **kwargs):
    instance.contract.refresh_balance()


def create_update_ContractXXX(sender, instance, created, **kwargs):
    instance.contract.one_time_service = False

    instance.contract.set_price_from_details()


def create_update_ContractProduct(sender, instance, created, **kwargs):
    if not instance.contract.contractsubscription_set.all().exists():
        instance.contract.one_time_service = True
    else:
        instance.contract.one_time_service = False

    instance.contract.set_contract_product_price()


def delete_ContractXXX(sender, instance, **kwargs):
    if not instance.contract.contractsubscription_set.all().exists():
        instance.contract.one_time_service = True
    else:
        instance.contract.one_time_service = False

    instance.contract.set_price_from_details()


def save_stage_property(sender, instance, created, **kwargs):
    logger.warning('CreateStageProperty')
    if created:
        service = CreateStageProperty(instance)
        service.run()


def save_finance(sender, instance, created, **kwargs):
    finance, created = ContractFinance.objects.get_or_create(contract=instance, author=instance.author,
                                                             organization=instance.organization)
    finance.set_finance_values()
    finance.save()


def init_signals():
    logger.info('-------------CONTRACT SIGNALS INIT------------')
    signals.post_save.connect(receiver=save_finance, sender=Contract)
    signals.post_save.connect(receiver=save_stage_property, sender=Contract)
    signals.post_save.connect(receiver=create_update_accrual, sender=RegisterAccrual)
    signals.post_save.connect(receiver=create_update_payment, sender=RegisterPayment)
    signals.post_delete.connect(receiver=delete_payment, sender=RegisterPayment)
    signals.post_save.connect(receiver=create_act, sender=RegisterAccrual)
    signals.post_delete.connect(receiver=post_delete_act, sender=RegisterAct)
    signals.post_save.connect(receiver=create_update_ContractXXX, sender=ContractSubscription)
    signals.post_save.connect(receiver=create_update_ContractProduct, sender=ContractProducts)
    signals.post_delete.connect(receiver=delete_ContractXXX, sender=ContractSubscription)
    signals.post_delete.connect(receiver=delete_ContractXXX, sender=ContractProducts)
