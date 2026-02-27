from django.db import transaction
from rest_framework import serializers
from .models import Product, Category, ProductImage, ProductVariant

# ============================================
# CATEGORY RELATED SERIALIZERS
# ============================================
class CategoryMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=("id", "name")

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=["id", "name", "description", "products_count", "image"]

# ============================================
# PRODUCT RELATED SERIALIZERS
# ============================================
class ProductSerializer(serializers.ModelSerializer):
    category = CategoryMiniSerializer(read_only=True)
    images = serializers.SerializerMethodField()
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
            "meta_description",
            "images",
        ]
        read_only_fields=["id"]

    def get_images(self, obj):
        request = self.context.get('request')

        return [request.build_absolute_uri(img.image.url) for img in obj.images.all()]

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
            "quantity",
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

        with transaction.atomic():
            product = Product.objects.create(**validated_data)

            for image in images:
                ProductImage.objects.create(product=product, image=image)

        return product

# ============================================
# PRODUCT VARIANT RELATED SERIALIZERS
# ============================================
class ProductVariantBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProductVariant
        fields=["name", "sku", "price", "quantity", "size", "color", "material", "is_active", "images"]

class ProductVariantAddSerializer(ProductVariantBaseSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    @transaction.atomic
    def create(self, validated_data):
        product_id = validated_data.pop("product_id", None)
        images = validated_data.pop("images", None)

        print(product_id)
        product = Product.objects.get(id=product_id)

        if product:
            new_prod_variant = ProductVariant.create(product=product, **validated_data)

            for image in images:
                ProductImage.objects.create(product_variant=new_prod_variant, image=image)

