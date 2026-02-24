from django.db import transaction
from rest_framework import serializers
from .models import Product, Category, ProductImage

class CategoryMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=("id", "name")

class ProductSerializer(serializers.ModelSerializer):
    category = CategoryMiniSerializer(read_only=True)
    class Meta:
        model=Product
        fields=[
            "id",
            "name",
            "description",
            "short_description",
            "status",
            "category",
            "slug",
            "sku",
            "price",
            "quantity",
            "weight",
            "weight_unit",
            "meta_title",
            "meta_description"
        ]
        read_only_fields=["id"]

class ProductAddSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model=Product
        fields=[
            "name",
            "category",
            "price",
            "status",
            "sku",
            "weight",
            "weight_unit",
            "short_description",
            "meta_description",
            "description",
            "images"
        ]
    
    def create(self, validated_data):
        images = validated_data.pop("images", [])
        print(validated_data)

        with transaction.atomic():
            product = Product.objects.create(**validated_data)

            for image in images:
                ProductImage.objects.create(category=product, image=image)

        return product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=["id", "name", "description", "products_count", "image"]
