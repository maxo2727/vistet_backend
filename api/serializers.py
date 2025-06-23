from rest_framework import serializers

from .models import Clothe, Comment, Outfit, Store, User


class ClotheSerializer(serializers.ModelSerializer):
    """
    Serializer for Clothe model with automatic variant processing
    """

    price_range = serializers.SerializerMethodField()
    available_sizes = serializers.SerializerMethodField()
    image_display_url = serializers.SerializerMethodField()

    class Meta:
        model = Clothe
        fields = [
            "id",
            "name",
            "type",
            "image",
            "image_url",
            "image_display_url",
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
            "image_display_url",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        """
        Remove image and image_url from GET responses, keep only image_display_url
        """
        data = super().to_representation(instance)
        
        # Keep only specific fields for GET responses
        allowed_fields = ['name', 'type', 'image_display_url', 'user', 'store', 'id', 'created_at', 'updated_at']
        filtered_data = {key: value for key, value in data.items() if key in allowed_fields}
        
        return filtered_data

    def validate(self, data):
        """
        Simple validation: require either image or image_url
        """
        # Only validate for create operations or when image fields are being updated
        if not self.instance or 'image' in data or 'image_url' in data:
            image = data.get('image')
            image_url = data.get('image_url')
            
            # For updates, check existing values if fields not provided
            if self.instance:
                existing_image = self.instance.image if not data.get('image') else None
                existing_image_url = self.instance.image_url if not data.get('image_url') else None
                image = image or existing_image
                image_url = image_url or existing_image_url
            
            if not image and not image_url:
                raise serializers.ValidationError(
                    "Either 'image' file or 'image_url' must be provided."
                )

            if "type" in data and data["type"] not in [choice[0] for choice in Clothe.ClothingType.choices]:
                raise serializers.ValidationError(
                    f"Invalid type. Must be one of: {', '.join([choice[0] for choice in Clothe.ClothingType.choices])}"
                )
        
        return data

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

    def get_image_display_url(self, obj):
        """Get the appropriate image URL for display"""
        return obj.get_image_url()


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
        required=False, allow_blank=True, allow_null=True, help_text="Product image URL"
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
            "image": None,  # Explicitly set to None for scraped data
            "image_url": validated_data.get("image_url", ""),
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

    def validate(self, data):
        """
        Validate that user cannot create multiple outfits with the same name
        """
        # Only check for duplicates during creation (not updates)
        if not self.instance:
            user = data.get('user')
            name = data.get('name')
            
            if user and name:
                existing_outfit = Outfit.objects.filter(user=user, name=name).first()
                if existing_outfit:
                    raise serializers.ValidationError(
                        f"You already have an outfit named '{name}'. Please choose a different name."
                    )
        
        return data

    def validate_components(self, value):
        """
        Validate that components contain required clothing types: PANTS/SHORTS, ACCESSORIES, POLERA
        """
        # Handle both cases: list of integers or list of Clothe objects
        if value and hasattr(value[0], 'id'):
            # value contains Clothe objects
            clothes = value
            clothing_ids = [clothe.id for clothe in clothes]
        else:
            # value contains integers
            clothing_ids = value
            clothes = Clothe.objects.filter(id__in=clothing_ids)
            
            # Check if all IDs exist
            if len(clothes) != len(clothing_ids):
                missing_ids = set(clothing_ids) - set(clothes.values_list('id', flat=True))
                raise serializers.ValidationError(
                    f"Clothing items with IDs {list(missing_ids)} do not exist."
                )
        
        # Get the types of the selected clothes
        present_types = set(clothe.type for clothe in clothes)
        
        # Required types for a complete outfit (PANTS OR SHORTS + ACCESSORIES + POLERA)
        has_bottom = (Clothe.ClothingType.PANTS in present_types or 
                     Clothe.ClothingType.SHORTS in present_types)
        has_accessories = Clothe.ClothingType.ACCESSORIES in present_types
        has_polera = Clothe.ClothingType.POLERA in present_types
        
        missing_types = []
        if not has_bottom:
            missing_types.append("Pants or Shorts")
        if not has_accessories:
            missing_types.append("Accessories")
        if not has_polera:
            missing_types.append("Polera")
        
        if missing_types:
            raise serializers.ValidationError(
                f"Outfit must include at least one item of each type: Pants/Shorts, Accessories, Polera. "
                f"Missing: {', '.join(missing_types)}"
            )
        
        return value

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
