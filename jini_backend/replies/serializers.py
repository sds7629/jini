from rest_framework import serializers
from .models import Reply


class ReplySerializer(serializers.ModelSerializer):
    writer = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = (
            "content",
            "writer",
        )

    def get_writer(self, obj):
        return obj.writer.nickname
