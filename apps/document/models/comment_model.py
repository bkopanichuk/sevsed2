from django.db import models
from apps.l_core.models import CoreBase,CoreUser


class Comment(CoreBase):
    document = models.ForeignKey('BaseDocument', on_delete=models.SET_NULL, null=True, blank=True,related_name='comments' )
    task_executor = models.ForeignKey('TaskExecutor', related_name="comments", on_delete=models.SET_NULL, null=True,
                                      blank=True)
    task = models.ForeignKey('Task', on_delete=models.SET_NULL, null=True, blank=True,related_name="comments")
    description = models.CharField(verbose_name="Коментар", max_length=500)
    to_user = models.ForeignKey(CoreUser,verbose_name="Для користувача",null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Кометар'
        verbose_name_plural = 'Коментарі'

    def __str__(self):
        return f'{self.author}'
