# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from celery import states
from celery.result import AsyncResult
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

HTTP_102_PROCESSING = 102


class GetTaskResult(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        task = AsyncResult(task_id)
        if task.status in [states.PENDING, states.STARTED, states.RETRY]:
            return Response(status=HTTP_102_PROCESSING)
        if task.status == states.SUCCESS:
            return Response(task.result)
        if task.status == states.FAILURE:
            return Response('Частину даних не вдалось обробити', status=status.HTTP_409_CONFLICT)