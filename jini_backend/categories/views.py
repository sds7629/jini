from . import serializers
from .models import Category
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAdminUser
from rest_framework import status


@api_view(["GET", "POST"])
@permission_classes([IsAdminUser])
def CategoryView(request):
    if request.method == "GET":
        category_val = Category.objects.all()
        return Response(serializers.CategorySerializer(category_val, many=True).data)

    if request.method == "POST":
        serializer = serializers.CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category_val = serializer.save()
        return Response(serializers.CategorySerializer(category_val).data)


@api_view(["PUT", "DELETE"])
@permission_classes([IsAdminUser])
def DetailCategoryView(request, *args, **kwargs):
    category = Category.objects.get(name=kwargs["name"])
    if request.method == "PUT":
        serializer = serializers.CategoryDetailSerializer(
            category,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        patch_data = serializer.save()
        return Response(serializers.CategoryDetailSerializer(patch_data).data)

    if request.method == "DELETE":
        category.delete()
        return Response({"message": "삭제완료"}, status=status.HTTP_404_NOT_FOUND)
