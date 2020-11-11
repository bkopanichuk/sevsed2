from django.db import models
from apps.document.models.document_model import BaseDocument
from apps.l_core.models import CoreBase

APPROVE = 'APPROVE'
SIGN = 'SIGN'
APPROVE_GOAL = [(APPROVE, "Візування"),
                (SIGN, "На підписання"), ]


class DocumentApproveFlow(CoreBase):
    document = models.ForeignKey(BaseDocument, verbose_name="До документа", on_delete=models.CASCADE, null=True,
                                 blank=True)

    class Meta:
        verbose_name = 'Маршрут погодження'


class DocumentApprove(CoreBase):
    document_approve_flow = models.ForeignKey(DocumentApproveFlow, verbose_name="До документа",
                                              on_delete=models.CASCADE)
    goal = models.CharField(verbose_name="Вид підтвердження", choices=APPROVE_GOAL, max_length=50)
    is_completed = models.BooleanField(verbose_name="Чи виконано", default=False)

    class Meta:
        verbose_name = 'Погодження'


class DocumentApproveExecutors(CoreBase):
    document_approve = models.ForeignKey(DocumentApprove, related_name='document_approve_executors',
                                         on_delete=models.CASCADE)
    sign = models.TextField(null=True)
    is_completed = models.BooleanField(verbose_name="Чи виконано", default=False)
    end_date = models.DateTimeField(verbose_name="Уточнення кінцевого терміну", auto_now_add=True)
    execute_date = models.DateTimeField(verbose_name="Дата фактичного виконання", null=True)
    comment = models.TextField(verbose_name="Коментар", max_length=300, null=True, blank=False)

    class Meta:
        verbose_name = 'Учасник маршруту погодження'
