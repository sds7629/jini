from rest_framework import serializers
from .models import Feed
from reviews.serializers import ReviewSerializer


class FeedSerializer(serializers.ModelSerializer):
    writer = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Feed
        exclude = ("like_users",)

    def get_writer(self, obj):
        return {"nickname": obj.nickname, "profile": obj.profile}

    def get_category(self, obj):
        return obj.kind


class FeedDetailSerializer(serializers.ModelSerializer):
    writer = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = Feed
        exclude = ("like_users",)

    def get_is_owner(self, obj):
        request = self.context["request"]
        return obj.writer == request.user

    def get_writer(self, obj):
        return obj.nickname

    def get_category(self, obj):
        return obj.kind

    def get_likes(self, obj):
        return obj.likes_count

    def get_reviews(self, obj):
        reviews = []
        for review in obj.reviews_review:
            reviews.append(
                {
                    "id": review.pk,
                    "writer": review.nickname,
                    "profile": review.profile,
                    "content": review.content,
                    "created": review.created_at,
                }
            )
        return reviews
