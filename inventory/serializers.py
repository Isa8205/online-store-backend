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
    variants = serializers.SerializerMethodField()

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
            "variants",
        ]
        read_only_fields=["id"]

    # Note: Since the ProductVariantGetSerializer will not be available at interpretation time.
    # use this method to wait untill it is loaded then import and get it.
    def get_variants(self, obj):
        from .serializers import ProductVariantGetSerializer
        return ProductVariantGetSerializer(
                obj.variants.all(),
                many=True
            ).data

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
        fields=["name", "sku", "price", "quantity", "size", "color", "material", "image", "is_active"]

class ProductVariantAddSerializer(ProductVariantBaseSerializer):
    product_id = serializers.UUIDField(write_only=True)

    class Meta(ProductVariantBaseSerializer.Meta):
        fields = ProductVariantBaseSerializer.Meta.fields + [
                "product_id"
        ]

    @transaction.atomic
    def create(self, validated_data):
        product_id = validated_data.pop("product_id")

        product = Product.objects.get(id=product_id)

        variant = ProductVariant.objects.create(
            product=product,
            **validated_data
        )

        return variant

class ProductVariantGetSerializer(ProductVariantBaseSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
