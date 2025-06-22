from rest_framework import serializers

from .models import Clothe, Comment, Outfit, Store, User


class ClotheSerializer(serializers.ModelSerializer):
    """
    Serializer for Clothe model with automatic variant processing
    """

    price_range = serializers.SerializerMethodField()
    available_sizes = serializers.SerializerMethodField()

    class Meta:
        model = Clothe
        fields = [
            "id",
            "name",
            "type",
            "image",
            "shopify_id",
            "gid",
            "vendor",
            "base_price",
            "variants",
            "user",
            "store",
            "created_at",
            "updated_at",
            "price_range",
            "available_sizes",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "price_range",
            "available_sizes",
        ]

    def get_price_range(self, obj):
        """Get price range from variants"""
        min_price, max_price = obj.get_price_range()
        if min_price == max_price:
            return {"price": float(min_price) if min_price else None}
        return {
            "min_price": float(min_price) if min_price else None,
            "max_price": float(max_price) if max_price else None,
        }

    def get_available_sizes(self, obj):
        """Get available sizes from variants"""
        return obj.get_available_sizes()


class CreateClotheFromScrapedDataSerializer(serializers.Serializer):
    """
    Serializer for creating clothe objects from scraped Shopify data
    """

    id = serializers.IntegerField(help_text="Shopify product ID")
    gid = serializers.CharField(help_text="Shopify Global ID")
    vendor = serializers.CharField(help_text="Product vendor/brand")
    type = serializers.CharField(help_text="Product type")
    title = serializers.CharField(help_text="Product name/title")
    variants = serializers.ListField(
        child=serializers.DictField(), help_text="Product variants array"
    )
    image_url = serializers.URLField(
        required=False, allow_blank=True, help_text="Product image URL"
    )

    def create(self, validated_data):
        """
        Create a Clothe object from scraped Shopify data
        """
        # Map Shopify types to our ClothingType choices
        type_mapping = {
            "Shorts": Clothe.ClothingType.SHORTS,
            "Pantalón": Clothe.ClothingType.PANTS,
            "Polera": Clothe.ClothingType.POLERA,
            "Accesorio": Clothe.ClothingType.ACCESSORIES,
        }

        rehabclo_store, created = Store.objects.get_or_create(
            name="Rehabclo",
            defaults={
                "description": "Rehabclo",
                "contact_number": "+569000000000",
                "site_url": "https://rehabclo.cl",
            },
        )

        # Get the first variant price as base price (converted from centavos to pesos)
        base_price = None
        if validated_data["variants"]:
            first_variant_price = validated_data["variants"][0].get("price", 0)
            base_price = first_variant_price / 100  # Convert from centavos to pesos

        clothe_data = {
            "name": validated_data["title"],
            "type": type_mapping.get(validated_data["type"], Clothe.ClothingType.OTHER),
            "image": validated_data.get("image_url", ""),
            "shopify_id": validated_data["id"],
            "gid": validated_data["gid"],
            "vendor": validated_data["vendor"],
            "base_price": base_price,
            "variants": validated_data["variants"],
            "store": rehabclo_store,
        }

        # Check if clothe already exists by name (primary) or shopify_id (secondary)
        clothe, created = Clothe.objects.update_or_create(
            name=validated_data["title"], defaults=clothe_data
        )

        return clothe


class BulkCreateClotheSerializer(serializers.Serializer):
    """
    Serializer for bulk creating clothes from scraped data
    """

    products = CreateClotheFromScrapedDataSerializer(many=True)

    def create(self, validated_data):
        """
        Bulk create clothe objects from scraped Shopify data
        """
        created_clothes = []
        updated_clothes = []

        for product_data in validated_data["products"]:
            serializer = CreateClotheFromScrapedDataSerializer(data=product_data)
            if serializer.is_valid():
                clothe = serializer.save()
                if hasattr(clothe, "_created") and clothe._created:
                    created_clothes.append(clothe)
                else:
                    updated_clothes.append(clothe)

        return {
            "created": created_clothes,
            "updated": updated_clothes,
            "total_created": len(created_clothes),
            "total_updated": len(updated_clothes),
        }


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "description",
            "contact_number",
            "date_joined",
            "last_login",
            "is_active",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]
        extra_kwargs = {"password": {"write_only": True}}


class StoreSerializer(serializers.ModelSerializer):
    """
    Serializer for Store model
    """

    class Meta:
        model = Store
        fields = [
            "id",
            "name",
            "description",
            "contact_number",
            "site_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OutfitSerializer(serializers.ModelSerializer):
    """
    Serializer for Outfit model
    """

    user_name = serializers.CharField(source="user.name", read_only=True)
    components_count = serializers.SerializerMethodField()

    class Meta:
        model = Outfit
        fields = [
            "id",
            "user",
            "user_name",
            "name",
            "rating",
            "components",
            "components_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "user_name",
            "components_count",
        ]

    def get_components_count(self, obj):
        """Get the number of clothing items in this outfit"""
        return obj.components.count()


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model
    """

    user_name = serializers.CharField(source="user.name", read_only=True)
    outfit_name = serializers.CharField(source="outfit.name", read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "user_name",
            "outfit",
            "outfit_name",
            "title",
            "message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "user_name",
            "outfit_name",
        ]
