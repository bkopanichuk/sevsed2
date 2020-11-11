from apps.document.models.document_model import BaseDocument, COMPLETED, ON_CONTROL


class CheckControllers:
    def __init__(self, doc):
        self.document: BaseDocument = doc

    def run(self):
        self.change_status_if_has_controllers()
        return self.document

    def change_status_if_has_controllers(self):
        if self.document.status == COMPLETED:
            if self.document.task_set.filter(controller__isnull=False).exists():
                self.document.status = ON_CONTROL