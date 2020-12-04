import os
from datetime import datetime
import logging

import docxtpl
from babel.dates import format_datetime
from django.db import models
from django.utils.crypto import get_random_string
from django.conf import settings
from num2words import num2words

from apps.dict_register.models import TemplateDocument
from apps.contracts.models.stage_propperty_model import StageProperty
from apps.contracts.models.contract_product_model import AccrualProducts, AccrualSubscription
from apps.l_core.models import CoreBase
from apps.l_core.utilits.converter import LibreOfficeConverter
from apps.l_core.utilits.month import LOCAL_MONTH

MEDIA_ROOT = settings.MEDIA_ROOT



logger = logging.getLogger(__name__)



class RegisterAct(CoreBase):
    number_act = models.TextField(verbose_name="Номер акту")
    contract = models.ForeignKey('contracts.Contract', on_delete=models.CASCADE, verbose_name="Договір")
    accrual = models.ForeignKey('contracts.RegisterAccrual', null=True, blank=True, editable=False,
                                on_delete=models.CASCADE, verbose_name="Нарахування")
    date_formation_act = models.DateField(verbose_name="Дата формування акту")
    date_sending_act = models.DateField(verbose_name="Дата відправлення акту", null=True)
    is_send_successful = models.BooleanField(verbose_name="Акт успішно відправлено?", null=True)
    date_return_act = models.DateField(verbose_name="Дата повернення акту", null=True, )
    copy_act = models.FileField(null=True, upload_to='uploads/docx_act/%Y/%m/%d/', verbose_name="Копія акту(DOCX)")
    copy_act_pdf = models.FileField(null=True, upload_to='uploads/pdf_act/%Y/%m/%d/', verbose_name="Копія акту(PDF)")
    sign_act_from_contractor = models.TextField(null=True, verbose_name="Цифровий підпис контрагента",
                                                help_text="Підписант може накласти цифровий підпис на копію акту в пдф")
    copy_act_from_contractor = models.FileField(null=True, upload_to='uploads/pdf_act_stamp/%Y/%m/%d/',
                                                verbose_name="Копія акту підписана контрагентом",
                                                help_text="Повинна містити скановану копію з штампом організації підписанта")

    class Meta:
        verbose_name_plural = u'Акти'
        verbose_name = u'Акт'

    def save(self, *args, **kwargs):
        super(RegisterAct, self).save(*args, **kwargs)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u'{}'.format(self.number_act or '-')

    ## TODO Видалити generate_acts, його неможливо икористовувати в мультипаспортному режимі
    @classmethod
    def generate_acts(cls, regenerate_all=None):
        template_obj = TemplateDocument.objects.get(related_model_name='registeract')
        docx_template = template_obj.template_file.path
        doc = docxtpl.DocxTemplate(docx_template)
        res = []
        if regenerate_all:
            acts = cls.objects.all()
        else:
            acts = cls.objects.filter(copy_act__exact=None)
        for act in acts:
            act_docx_file = act.generate_docx_act(doc=doc)
            act.copy_act.name = act_docx_file
            act_pdf_file = act.convert_docx_to_pdf()
            act.copy_act_pdf.name = act_pdf_file
            act.save()
            res.append(str(act))

        return res

    def generate_act_docs(self):
        act_docx_file = self.generate_docx_act()
        self.copy_act.name = act_docx_file
        ##act_pdf_file = self.convert_docx_to_pdf()
        ##self.copy_act_pdf.name = act_pdf_file
        self.save()

        return {'copy_act': self.copy_act.name}  # , 'copy_act_pdf': self.copy_act_pdf.name}

    def generate_docx_act(self, doc=None):
        """ Return *.docx path from MEDIA_ROOT """
        logger.debug(' start function "generate_docx_act"')
        if not doc:
            template_obj = TemplateDocument.objects.get(related_model_name='registeract',
                                                        organization_id=self.organization.id)
            docx_template = template_obj.template_file.path
            doc = docxtpl.DocxTemplate(docx_template)

        upload_to = datetime.today().strftime('uploads/docx_act/%Y/%m/%d/')
        base_dir = os.path.join(MEDIA_ROOT, upload_to)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        filename = get_random_string(length=32) + '.docx'
        out_path = os.path.join(base_dir, filename)

        ret = os.path.join(upload_to, filename)

        data = self.get_act_data()
        logger.debug(' end function "generate_docx_act"')
        doc.render(data)
        doc.save(out_path)
        return ret

    def get_act_data(self):
        logger.debug('start function "get_act_data"')
        data = {}
        contract = self.contract
        data['number_contract'] = str(contract.number_contract)
        local_contract_date = format_datetime(contract.start_date, "«d» MMMM Y", locale='uk_UA')
        data['local_contract_date'] = local_contract_date
        data['subject_contract'] = contract.subject_contract
        data['price_contract_by_month'] = float(self.accrual.size_accrual or 0.00)
        price_contract_by_month_locale = num2words(self.accrual.size_accrual + 0.00, lang='uk', to='currency',
                                                   currency='UAH')
        data['price_contract_by_month_locale'] = price_contract_by_month_locale

        pdv = round(self.accrual.size_accrual / 120 * 20, 2)  ## розмір пдв
        data['pdv'] = pdv
        pdv_locale = num2words(pdv + 0.00, lang='uk', to='currency',
                               currency='UAH')
        data['pdv_locale'] = pdv_locale
        data['price'] = round(self.accrual.size_accrual - pdv, 2)
        data['price_locale'] = num2words(data['price'] + 0.00, lang='uk', to='currency',
                                         currency='UAH')

        data['act_date_locale'] = format_datetime(self.date_formation_act, "«d» MMMM Y", locale='uk_UA')

        local_month_name = LOCAL_MONTH[self.date_formation_act.month]

        data['spatial_date'] = '{} {}'.format(local_month_name, self.date_formation_act.year)

        stage_property_q = StageProperty.objects.filter(contract=contract)
        if stage_property_q.count() > 0:
            stage_property = stage_property_q[0]
            stage_property_data = {'name': stage_property.name,
                                   'address': stage_property.address,
                                   'bank_name': stage_property.bank_name,
                                   'settlement_account': stage_property.settlement_account,
                                   'certificate_number': stage_property.certificate_number,
                                   'mfo': stage_property.mfo,
                                   'edrpou': stage_property.edrpou,
                                   'phone': stage_property.phone
                                   }

        else:
            stage_property_data = None

        data['stage_property_data'] = stage_property_data
        details_1 = AccrualProducts.objects.filter(accrual=self.accrual).values('product', 'product__name', 'count',
                                                                                'price', 'pdv', 'total_price',
                                                                                'total_price_pdv')
        details_2 = AccrualSubscription.objects.filter(accrual=self.accrual).values('product', 'product__name', 'count',
                                                                                    'price', 'pdv', 'total_price',
                                                                                    'total_price_pdv', 'start_period',
                                                                                    'end_period')
        data['details'] = list(details_1) + list(details_2)
        logger.debug(' end function "get_act_data"')
        return data

    def convert_docx_to_pdf(self, save=None):
        """ Return *.pdf path from MEDIA_ROOT """
        upload_to = datetime.today().strftime('uploads/pdf_act/%Y/%m/%d/')
        source = self.copy_act.path
        # print('source:',source)
        out_path = os.path.join(MEDIA_ROOT, upload_to)
        filename = os.path.basename(source).replace('.docx', '.pdf')
        ret = os.path.join(upload_to, filename)
        # print('ret:', ret)
        out_file = os.path.join(out_path, filename)
        # print('out_file:', out_file)
        LibreOfficeConverter.convert_to_pdf(source, out_file)
        if save:
            self.copy_act_pdf.name = ret
            self.save()
        return ret

    def send_act(self):
        ##TODO
        ##1. Отримати пошту контрагента
        ##2. Сформувати акт (generate_act)
        ##3. Перегнати акт з docx в pdf
        ##3. Відправити акт по пошті
        ##4. Якщо відправлено успішно змінюємо статус акту
        pass