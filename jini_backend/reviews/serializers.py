from django.db.models import Count
from rest_framework import serializers
from .models import Review
from replies.models import Reply
from replies.serializers import ReplySerializer


class ReviewSerializer(serializers.ModelSerializer):
    writer = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = Review
        exclude = ("feed",)

    def get_writer(self, obj):
        return {
            "nickname": obj.nickname,
            "profile": obj.profile,
        }

    def get_replies(self, obj):
        replies = []
        for reply in obj.review_replies:
            replies.append(
                {
                    "id": reply.pk,
                    "writer": reply.nickname,
                    "profile": reply.profile,
                    "content": reply.content,
                    "created_at": reply.created_at,
                }
            )
        return replies

    def get_reply_count(self, obj):
        return obj.reply_count

    # def get_replies(self, obj):
    #     data = []
    #     for reply in obj.review_replies:
    #         data.append({"content": reply.content})
    #     return data
