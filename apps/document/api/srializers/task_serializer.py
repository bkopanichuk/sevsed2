from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator
from drf_writable_nested.serializers import WritableNestedModelSerializer


from apps.l_core.models import CoreUser
from apps.document.api.srializers.comment_serializer import CommentSerializer
from apps.document.models.task_model import Task, TaskExecutor, Flow, FlowApprove, EXECUTOR_ROLE, EXECUTION_TYPE,TASK_GOAL


class SimpleTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id','task_status','__str__','controller_comment','approve_type']

class TaskExecutorSerializer(serializers.ModelSerializer):
    #comments = CommentSerializer(many=False, required=False, label="Коментар")
    executor = serializers.PrimaryKeyRelatedField(label='Виконавець', queryset=CoreUser.objects.all(), required=True)
    executor_role = serializers.ChoiceField(label='Роль виконавця', required=True, choices=EXECUTOR_ROLE)
    document = serializers.SerializerMethodField(method_name='get_document')
    task = SimpleTaskSerializer(many=False,read_only=True)

    class Meta:
        model = TaskExecutor
        fields = ['id', 'executor', 'executor_role', 'detail', 'result', '__str__', 'date_add','end_date', 'status', 'task',
                  'document', 'approve_method', 'sign_info','sign_file', 'end_date','result_file', 'result_document','unique_uuid']
        read_only_fields = ['sign_file','document',]

        #read_only_fields = ['comments']

    def get_document(self, obj):
        return obj.task.document.__str__()

    # def get_task_repr(self, obj):
    #     return obj.task.__str__()
    # # validators = [
    #     UniqueTogetherValidator(
    #         queryset=TaskExecutor.objects.all().distinct('task','executor', 'executor_role'),
    #         fields=['executor', 'executor_role']
    #     )
    # ]


class TaskExecutorFinishSerializer(serializers.ModelSerializer):
    result = serializers.CharField(label='Результат виконання', required=False)
    result_file = serializers.FileField(label='Результат виконання(файл)', required=False)
    #comment = CommentSerializer(many=False, required=False, label="Коментар")

    class Meta:
        model = TaskExecutor
        fields = ['id', 'result', 'result_file']


class TaskExecutorFinishApproveSerializer(serializers.ModelSerializer):
    sign = serializers.CharField(label='Цифровий підпис', required=False)
    sign_file = serializers.FileField(label='Цифровий підпис(файл)', required=False)
    result = serializers.CharField(label='Коментар', required=False,allow_null=True)

    class Meta:
        model = TaskExecutor
        fields = ['id', 'sign','result','sign_file']


class TaskApproveSerializer(serializers.Serializer):
    controller_comment = serializers.CharField(label='Коментар контролера', required=True)
    class Meta:
        model = TaskExecutor
        fields = ['controller_comment']





class TaskSerializer(WritableNestedModelSerializer):
    task_executors = TaskExecutorSerializer(many=True, required=True)
    task_author = serializers.SerializerMethodField(method_name='get_task_author')
    format_date_add = serializers.SerializerMethodField(method_name='get_format_date_add')
    #comments = CommentSerializer(many=False, required=False, label="Коментар")

    class Meta:
        model = Task
        fields = ['id', 'format_date_add','task_type', 'title', '__str__', 'flow', 'document', 'parent_task', 'parent_node',
                  'task_status', 'task_executors', 'is_completed', 'end_date', 'execute_date', 'controller',
                  'author_is_controller', 'approve_type','goal','controller_comment','task_author','unique_uuid']
        read_only_fields = ['execute_date', 'is_completed']

    def validate_executors(self, attrs):
        executors = attrs.get('task_executors')
        if not executors:
            raise ValidationError({'task_executors': 'У резолюції має бути хоча б один виконавець'})

    def validate(self, attrs):
        self.validate_executors(attrs)
        return super(TaskSerializer, self).validate(attrs)

    def get_task_author(self, obj):
        return obj.author.__str__()

    def get_format_date_add(self, obj):
        return obj.date_add.strftime("%Y-%m-%d")


class FlowApproveSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlowApprove
        fields = ['id', 'approver', '__str__', 'status','unique_uuid']


class FlowSerializer(serializers.ModelSerializer):
    ## Має називатисть так само, як поле "related_name"
    approvers = FlowApproveSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Flow
        fields = ['id', 'status', 'approvers', 'tasks', 'execution_type','goal','unique_uuid']
        read_only_fields = [ 'approvers', 'tasks']


class CreateFlowSerializer(serializers.Serializer):
    execution_type = serializers.ChoiceField(choices=EXECUTION_TYPE, required=True)
    goal = serializers.ChoiceField(choices=TASK_GOAL, required=False)