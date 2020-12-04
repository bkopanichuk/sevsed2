import os
import shutil
from django.conf import settings
from pathlib import Path

from apps.dict_register.models import TemplateDocument, get_upload_template_path

MEDIA_ROOT = settings.MEDIA_ROOT
import logging

logger = logging.getLogger(__name__)


class CreateInitialTemplates():
    def __init__(self, organization):
        self.organization = organization

    def run(self):
        self.create_initial_templates()

    def create_initial_templates(self):
        self.create_base_foulder()
        self.create_initial_act()
        self.create_initial_invoice()

    def create_base_foulder(self):
        base_dir = os.path.join(MEDIA_ROOT, get_upload_template_path(self.organization, ''))
        logger.warning(base_dir)
        Path(base_dir).mkdir(parents=True, exist_ok=True)

    def create_initial_act(self):
        act_default_template = os.path.join(MEDIA_ROOT, 'default_doc_templates', 'act.docx')
        related_template_path = get_upload_template_path(self.organization, 'act.docx')
        act_template_path = os.path.join(MEDIA_ROOT, related_template_path)
        shutil.copy2(act_default_template, act_template_path)
        TemplateDocument.objects.create(protected=True, organization=self.organization,
                                        template_file=related_template_path,
                                        related_model_name='registeract', name='Шаблон акту')

    def create_initial_invoice(self):
        act_default_template = os.path.join(MEDIA_ROOT, 'default_doc_templates', 'invoice.docx')
        related_template_path = get_upload_template_path(self.organization, 'invoice.docx')
        act_template_path = os.path.join(MEDIA_ROOT, related_template_path)
        shutil.copy2(act_default_template, act_template_path)
        TemplateDocument.objects.create(protected=True, organization=self.organization,
                                        template_file=related_template_path,
                                        related_model_name='registerinvoice', name='Шаблон рахунку')
