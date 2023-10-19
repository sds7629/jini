from rest_framework import serializers
from .models import Feed
from django.db.models import Count
from reviews.serializers import ReviewSerializer
from categories.serializers import CategorySerializer


class PostFeedSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Feed
        exclude = (
            "writer",
            "like_users",
        )


class GetFeedSerializer(serializers.ModelSerializer):
    writer = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_like = serializers.SerializerMethodField()

    class Meta:
        model = Feed
        exclude = ("like_users",)

    def get_writer(self, obj):
        return {"nickname": obj.feed_nickname, "profile": obj.feed_profile}

    def get_category(self, obj):
        return obj.kind

    def get_review_count(self, obj):
        return len(obj.reviews_review)

    def get_likes_count(self, obj):
        return obj.likes_count

    def get_is_like(self, obj):
        try:
            request = self.context["request"]
            return obj.like_users.filter(pk=request.user.pk).exists()
            # return obj.objects.filter(like_users__user__id=request.user.pk).exists()
        except:
            return False


class FeedDetailSerializer(serializers.ModelSerializer):
    feed_writer = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    is_like = serializers.SerializerMethodField()

    class Meta:
        model = Feed
        exclude = ("like_users",)

    def get_is_owner(self, obj):
        request = self.context["request"]
        return obj.writer == request.user

    def get_feed_writer(self, obj):
        feed_writer = {
            "nickname": obj.feed_nickname,
            "profileImg": obj.feed_profile,
        }
        return feed_writer

    def get_category(self, obj):
        return obj.kind

    def get_likes(self, obj):
        return obj.likes_count

    def get_is_like(self, obj):
        request = self.context["request"]
        return obj.like_users.filter(pk=request.user.pk).exists()

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


class TestSerializer(serializers.ModelSerializer):
    # writer = serializers.SerializerMethodField()
    # category = serializers.SerializerMethodField()
    # review_count = serializers.SerializerMethodField()
    # likes_count = serializers.SerializerMethodField()
    # # is_like = serializers.SerializerMethodField()

    # class Meta:
    #     model = Feed
    #     exclude = ("like_users",)

    # def get_writer(self, obj):
    #     return {"nickname": obj.feed_nickname, "profile": obj.feed_profile}

    # def get_category(self, obj):
    #     return obj.kind

    # def get_review_count(self, obj):
    #     return len(obj.reviews_review)

    # def get_likes_count(self, obj):
    #     return obj.likes_count

    # def get_is_like(self, obj):
    #     try:
    #         request = self.context["request"]
    #         return obj.like_users.filter(pk=request.user.pk).exists()
    #     except:
    #         return False
    def to_representation(self, instance):
        repr = {
            "pk": instance.pk,
            "writer": {
                "nickname": instance.feed_nickname,
                "profile": instance.feed_profile,
            },
            "category": instance.kind,
            "review_count": len(instance.reviews_review),
            "get_review_count": instance.likes_count,
            "title": instance.title,
            "content": instance.content,
            "file": instance.file,
            "is_secret": instance.is_secret,
        }
        if self.context["request"].user in instance.like_confirm:
            repr["is_like"] = True
        else:
            repr["is_like"] = False
        return repr
        # return {
        #     "pk": instance.pk,
        #     "writer": {
        #         "nickname": instance.feed_nickname,
        #         "profile": instance.feed_profile,
        #     },
        #     "category": instance.kind,
        #     "review_count": len(instance.reviews_review),
        #     "get_review_count": instance.likes_count,
        #     # "is_like": instance.like_users.filter(
        #     #     pk=self.context["request"].user.pk
        #     # ).exists(),
        #     # "is_like": instance.filter(
        #     #     like_users__pk=self.context["request"].user.pk
        #     # ).exists(),
        #     "title": instance.title,
        #     "content": instance.content,
        #     "file": instance.file,
        #     "is_secret": instance.is_secret,
        # }

    class Meta:
        model = Feed
        exclude = ("like_users",)
