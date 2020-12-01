from __future__ import unicode_literals

from rest_framework import serializers

from apps.document.models.comment_model import Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', '__str__', 'document', 'task', 'task_executor', 'description', 'date_add', 'author']
