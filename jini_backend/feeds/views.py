from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from .models import Feed
from django.db.models import F, Prefetch
from django.db.models.aggregates import Count
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, api_view, permission_classes
from categories.models import Category
from reviews.models import Review
from reviews.serializers import ReviewSerializer
from replies.models import Reply
from replies.serializers import ReplySerializer
from . import serializers
from .permissions import IsWriterorReadOnly, FeedOrReviewOwnerOnly
from .pagination import CustomPagination
from .filters import FeedFilter
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter


User = get_user_model()


class FeedViewSet(viewsets.ModelViewSet):
    queryset = (
        Feed.objects.annotate(
            nickname=F("writer__nickname"),
            profile=F("writer__profileImg"),
            kind=F("category__kind"),
            likes_count=Count("like_users"),
        )
        .select_related("writer", "category")
        .only("writer", "category", "like_users", "title", "content", "is_secret")
        .prefetch_related(
            Prefetch(
                "reviews",
                queryset=Review.objects.annotate(
                    nickname=F("writer__nickname"),
                    profile=F("writer__profileImg"),
                ),
                to_attr="reviews_review",
            ),
            "like_users",
        )
    )
    filterset_class = FeedFilter
    pagination_class = CustomPagination
    order_by = ["-created_at"]

    def get_permissions(self):
        permission_classes = []
        if self.action in ["list", "retreive", "create"]:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ["destroy", "update", "partial_update"]:
            self.permission_classes = [IsWriterorReadOnly]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ["retrieve", "delete", "partial_update", "update"]:
            return serializers.FeedDetailSerializer
        else:
            return serializers.FeedSerializer

    @extend_schema(
        tags=["피드 리스트"],
        description="피드 리스트",
        responses=serializers.FeedSerializer,
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=["피드 리스트"],
        description="피드 저장",
        responses=serializers.FeedSerializer,
        examples=[
            OpenApiExample(
                response_only=True,
                summary="피드 저장",
                name="Feeds",
                value={
                    "category": "place",
                    "title": "제목",
                    "comment": "내용",
                    "is_secret": "true or false",
                },
            ),
        ],
    )
    def create(self, request):
        category_val = request.data.get("category")
        category = Category.objects.get(kind=category_val)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        feed_data = serializer.save(writer=request.user, category=category)
        return Response(serializers.FeedSerializer(feed_data).data)

    @extend_schema(
        tags=["피드 자세히 보기"],
        description="피드 자세히 보기",
        responses=serializers.FeedSerializer,
    )
    def retrieve(self, request, *args, **kwargs):
        feed = self.get_object()
        serializer = self.get_serializer(feed)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = (
        Review.objects.annotate(
            nickname=F("writer__nickname"),
            profile=F("writer__profileImg"),
            reply_count=Count("replies"),
        )
        .select_related("writer", "feed")
        .prefetch_related(
            Prefetch(
                "replies",
                queryset=Reply.objects.annotate(
                    nickname=F("writer__nickname"),
                    profile=F("writer__profileImg"),
                ).all(),
                to_attr="review_replies",
            ),
        )
        .all()
    )

    def get_serializer_class(self):
        if self.action == "post_reply":
            return ReplySerializer
        else:
            return ReviewSerializer

    def get_permissions(self):
        permission_classes = []
        if self.action in ["list", "create"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsWriterorReadOnly]
        return super().get_permissions()

    def get_feed_object(self, *args, **kwargs):
        queryset = (
            Feed.objects.select_related("writer").prefetch_related("reviews").all()
        )
        lookup_url_kwarg = "feed_pk"
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_review_object(self, *args, **kwargs):
        queryset = self.get_queryset()
        lookup_url_kwarg = "pk"
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    @extend_schema(
        tags=["리뷰 리스트"],
        description="리뷰 리스트",
        responses=serializers.ReviewSerializer,
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return Response(ReviewSerializer(queryset, many=True).data)

    @extend_schema(
        tags=["리뷰 자세히 보기"],
        description="리뷰 자세히 보기",
        responses=serializers.ReviewSerializer,
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_review_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        tags=["리뷰 저장"],
        description="리뷰 저장",
        responses=serializers.ReviewSerializer,
        examples=[
            OpenApiExample(
                response_only=True,
                summary="리뷰 저장",
                name="Reviews",
                value={"comment": "내용"},
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        feed = self.get_feed_object()
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not feed.reviews.filter(writer=request.user).exists():
            review_data = serializer.save(
                writer=request.user,
                feed=feed,
            )
            return Response(ReviewSerializer(review_data).data)
        else:
            raise ParseError("이미 리뷰를 작성했습니다.")

    @extend_schema(
        tags=["대댓글 저장"],
        description="대댓글 저장",
        responses=ReplySerializer,
        examples=[
            OpenApiExample(
                response_only=True,
                summary="대댓글 저장",
                name="Reply",
                value={"comment": "내용"},
            ),
        ],
    )
    @action(methods=["post"], detail=True, permission_classes=[FeedOrReviewOwnerOnly])
    def post_reply(self, request, **kwargs):
        review = self.get_review_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reply = serializer.save(
            writer=request.user,
            review=review,
        )
        return Response(ReplySerializer(reply).data)


@extend_schema(
    tags=["대댓글 수정/삭제"],
    description="대댓글 수정/삭제",
    responses=ReplySerializer,
    examples=[
        OpenApiExample(
            response_only=True,
            summary="대댓글 저장",
            name="Reply",
            value={"comment": "내용"},
        ),
    ],
)
@api_view(["PUT", "DELETE"])
@permission_classes([FeedOrReviewOwnerOnly])
def updel_reply(request, reply_pk):
    if request.method == "PUT":
        reply = Reply.objects.get(pk=reply_pk)
        serializer = ReplySerializer(reply, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    if request.method == "DELETE":
        reply = Reply.objects.get(pk=reply_pk)
        reply.delete()
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def likes(request, feed_pk):
    if request.user.is_authenticated:
        feed = Feed.objects.get(pk=feed_pk)

        if feed.like_users.filter(pk=request.user.pk).exists():
            feed.like_users.remove(request.user)
        else:
            feed.like_users.add(request.user)
        return Response({"message": "ok"}, status=status.HTTP_200_OK)
