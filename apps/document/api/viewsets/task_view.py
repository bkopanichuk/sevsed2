from __future__ import unicode_literals

from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.document.api.srializers.document_serializer import DocumentSerializer
from apps.document.api.srializers.task_serializer import TaskSerializer, FlowSerializer, TaskExecutorSerializer, \
    TaskExecutorFinishSerializer, TaskExecutorFinishApproveSerializer, TaskApproveSerializer
from apps.document.models.document_model import ON_CONTROL,BaseDocument
from apps.document.models.document_constants import INNER

from apps.document.models.task_model import Task, Flow, TaskExecutor, RUNNING, SUCCESS, EXECUTE, \
    APPROVE, TASK, RETRY
from apps.document.services.task_service import FinishExecution, ApproveTask, FinishApprove, RejectApprove, RetryTask
from apps.l_core.api.base.serializers import BaseOrganizationViewSetMixing


class TaskSerializerViewSet(BaseOrganizationViewSetMixing):
    queryset = Task.objects.filter(goal=EXECUTE)
    serializer_class = TaskSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)



    @swagger_auto_schema(method='patch', request_body=TaskApproveSerializer(),
                         responses={200: TaskSerializer(many=False)})
    @action(detail=True, methods=['patch'])
    def approve_task(self, request, pk=None):
        """Підтвердити виконання завдання, після підтвердження завдання буде зняте з контролю.
        Підтвердити виконання завдання може лише контролер"""
        task = Task.objects.get(pk=pk)
        ser = TaskApproveSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        flow = ApproveTask(task, user=request.user, data=ser.validated_data)
        res = flow.run()
        task_result_serializer = TaskSerializer(res, context={'request': request})
        return Response(task_result_serializer.data)

    @swagger_auto_schema(method='patch', request_body=TaskApproveSerializer(),
                         responses={200: TaskSerializer(many=False)})
    @action(detail=True, methods=['patch'])
    def retry_task(self, request, pk=None):
        """Повернути завдання на доопрацювання. """
        task = Task.objects.get(pk=pk)
        ser = TaskApproveSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        flow = RetryTask(task, user=request.user, data=ser.validated_data)
        res = flow.run()
        task_result_serializer = TaskSerializer(res, context={'request': request})
        return Response(task_result_serializer.data)


class ApproveTaskSerializerViewSet(BaseOrganizationViewSetMixing):
    queryset = Task.objects.filter(goal=APPROVE)
    serializer_class = TaskSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)

    @swagger_auto_schema(method='get',
                         responses={200: TaskSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def my_control(self, request, ):
        self.queryset = Task.objects.filter(controller=request.user, goal=APPROVE, task_status__in=[SUCCESS])
        return self.list(request)

    # @swagger_auto_schema(method='patch', responses={200: TaskSerializer(many=False)})
    # @action(detail=True, methods=['patch'])
    # def approve_task(self, request, pk=None):
    #     task = Task.objects.get(pk=pk)
    #     flow = ApproveTask(task, user=request.user)
    #     res = flow.run()
    #     task_result_serializer = TaskSerializer(res, context={'request': request})
    #     return Response(task_result_serializer.data)


class TaskExecutorSerializerViewSet(BaseOrganizationViewSetMixing):
    queryset = TaskExecutor.objects.all()
    serializer_class = TaskExecutorSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    ordering_fields = '__all__'
    ordering = ['date_add']

    @swagger_auto_schema(method='get',
                         responses={200: TaskExecutorSerializer(many=False)})
    @action(detail=False, methods=['get'])
    def my_execution_tasks(self, request, ):
        self.queryset = TaskExecutor.objects.filter(executor=request.user, task__goal=EXECUTE,
                                                    task__task_type=TASK,
                                                    task__task_status__in=[RUNNING, RETRY])
        return self.list(request)

    @swagger_auto_schema(method='get',
                         responses={200: TaskExecutorSerializer(many=False)})
    @action(detail=False, methods=['get'])
    def my_approve_tasks(self, request, ):
        self.queryset = TaskExecutor.objects.filter(executor__id=request.user.id,
                                                    task__task_type=APPROVE, task__task_status__in=[RUNNING])
        return self.list(request)

    @swagger_auto_schema(method='get',
                         responses={200: TaskExecutorSerializer(many=False)})
    @action(detail=False, methods=['get'])
    def my_approve_tasks_inner(self, request, ):
        self.queryset = TaskExecutor.objects.filter(executor__id=request.user.id,
                                                    task__task__document_document_cast=INNER,
                                                    task__task_type=APPROVE, task__task_status__in=[RUNNING])
        return self.list(request)

    @swagger_auto_schema(method='patch', responses={200: TaskExecutorSerializer(many=False)})
    @action(detail=True, methods=['patch'])
    def start_execution(self, request, pk=None):
        task_executor = TaskExecutor.objects.get(pk=pk)
        task_executor.status = RUNNING
        task_executor.save()
        task_executor_serializer = TaskExecutorSerializer(task_executor, context={'request': request})
        return Response(task_executor_serializer.data)

    @swagger_auto_schema(method='get', responses={200: DocumentSerializer(many=False)})
    @action(detail=True, methods=['get'])
    def get_document(self, request, pk=None):
        document = TaskExecutor.objects.get(pk=pk).task.document
        document_serializer = DocumentSerializer(document, context={'request': request})
        return Response(document_serializer.data)

    @swagger_auto_schema(method='patch', request_body=TaskExecutorFinishSerializer(),
                         responses={200: TaskExecutorSerializer(many=False)})
    @action(detail=True, methods=['patch'])
    def finish_execution(self, request, pk=None):
        """Викононати завдання. Відправляється виконавцем завдання"""
        task_executor = TaskExecutor.objects.get(pk=pk)
        task_executor_serializer = TaskExecutorFinishSerializer(data=request.data)
        task_executor_serializer.is_valid(raise_exception=True)
        flow = FinishExecution(task_executor, data=task_executor_serializer.validated_data, user=request.user)
        res = flow.run()
        task_executor_result_serializer = TaskExecutorSerializer(res, context={'request': request})
        return Response(task_executor_result_serializer.data)

    @swagger_auto_schema(method='patch', request_body=TaskExecutorFinishSerializer(),
                         responses={200: TaskExecutorSerializer(many=False)})
    @action(detail=True, methods=['patch'])
    def finish_approve(self, request, pk=None):

        task_executor = TaskExecutor.objects.get(pk=pk)
        task_executor_serializer = TaskExecutorFinishApproveSerializer(data=request.data)
        task_executor_serializer.is_valid(raise_exception=True)
        flow = FinishApprove(task_executor, data=task_executor_serializer.validated_data, user=request.user)
        res = flow.run()
        task_executor_result_serializer = TaskExecutorSerializer(res, context={'request': request})
        return Response(task_executor_result_serializer.data)

    @swagger_auto_schema(method='patch', request_body=TaskExecutorFinishSerializer(),
                         responses={200: TaskExecutorSerializer(many=False)})
    @action(detail=True, methods=['patch'])
    def reject_approve(self, request, pk=None):
        task_executor = TaskExecutor.objects.get(pk=pk)
        task_executor_serializer = TaskExecutorFinishApproveSerializer(data=request.data)
        task_executor_serializer.is_valid(raise_exception=True)
        flow = RejectApprove(task_executor, data=task_executor_serializer.validated_data, user=request.user)
        res = flow.run()
        task_executor_result_serializer = TaskExecutorSerializer(res, context={'request': request})
        return Response(task_executor_result_serializer.data)


class FlowSerializerViewSet(BaseOrganizationViewSetMixing):
    queryset = Flow.objects.filter(goal=EXECUTE)
    serializer_class = FlowSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)


class ApproveFlowSerializerViewSet(BaseOrganizationViewSetMixing):
    queryset = Flow.objects.filter(goal=APPROVE)
    serializer_class = FlowSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)


class DocumentFlowView(APIView):
    @swagger_auto_schema(responses={200: FlowSerializer(many=True)})
    def get(self, request, document_id):
        q = Flow.objects.filter(goal=EXECUTE, document__id=document_id)
        serializer = FlowSerializer(q, many=True, context={'request': request})
        return Response(serializer.data)

class DocumentResolutionView(APIView):
    @swagger_auto_schema(responses={200: FlowSerializer(many=True)})
    def get(self, request, document_id):
        q = Flow.objects.filter(goal=EXECUTE, document__id=document_id)
        serializer = FlowSerializer(q, many=True, context={'request': request})
        return Response(serializer.data)

class DocumentConciderationView(APIView):
    @swagger_auto_schema(responses={200: FlowSerializer(many=True)})
    def get(self, request, document_id):
        q = Flow.objects.filter(goal=APPROVE, document__id=document_id)
        serializer = FlowSerializer(q, many=True, context={'request': request})
        return Response(serializer.data)


class ApproveDocumentFlowView(APIView):
    @swagger_auto_schema(responses={200: FlowSerializer(many=True)})
    def get(self, request, document_id):
        q = Flow.objects.filter(goal=APPROVE, document__id=document_id)
        serializer = FlowSerializer(q, many=True, context={'request': request})
        return Response(serializer.data)
