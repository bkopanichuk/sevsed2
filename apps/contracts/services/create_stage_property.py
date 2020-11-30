from apps.contracts.models.stage_propperty_model import StageProperty
from apps.l_core.models import CoreOrganization


class CreateStageProperty:
    def __init__(self, contract):
        self.contract = contract

    def run(self):
        self.create_stage_property()

    def create_stage_property(self):
        contractor: CoreOrganization = self.contract.contractor
        StageProperty.objects.create(contract=self.contract,
                             author=self.contract.author,
                             organization=self.contract.organization,
                             name=contractor.name,
                             full_name=contractor.full_name,
                             address=contractor.address,
                             edrpou=contractor.edrpou,
                             mfo=contractor.mfo,
                             phone=contractor.phone,
                             fax=contractor.fax,
                             email=contractor.email,
                             site=contractor.site,
                             register_date=contractor.register_date,
                             work_reason=contractor.work_reason,
                             sert_name=contractor.sert_name,
                             settlement_account=contractor.settlement_account,
                             bank=contractor.bank,
                             bank_name=contractor.bank_name,
                             ipn=contractor.ipn,
                             taxation_method=contractor.taxation_method,
                             certificate_number=contractor.certificate_number,
                             main_unit=contractor.main_unit,
                             main_unit_state=contractor.main_unit_state,
                             main_activity_text=contractor.main_activity_text,
                             statute_copy=contractor.statute_copy,
                             )
