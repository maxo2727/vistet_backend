from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Clothe, Comment, Outfit, Store, User
from .serializers import (
    BulkCreateClotheSerializer,
    ClotheSerializer,
    CommentSerializer,
    CreateClotheFromScrapedDataSerializer,
    OutfitSerializer,
    StoreSerializer,
    UserSerializer,
)


class ClotheListCreateView(generics.ListCreateAPIView):
    """
    GET /api/clothe/all - List all clothes
    POST /api/clothe/ - Create a new clothe
    """

    queryset = Clothe.objects.all().order_by("-created_at")
    serializer_class = ClotheSerializer

    def get_queryset(self):
        """Filter by query parameters if provided"""
        queryset = super().get_queryset()

        # Optional filters
        clothe_type = self.request.query_params.get("type", None)
        if clothe_type:
            queryset = queryset.filter(type=clothe_type)

        vendor = self.request.query_params.get("vendor", None)
        if vendor:
            queryset = queryset.filter(vendor__icontains=vendor)

        return queryset


class ClotheDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/clothe/{id} - Retrieve a specific clothe
    PUT /api/clothe/{id} - Update a specific clothe
    DELETE /api/clothe/{id} - Delete a specific clothe
    """

    queryset = Clothe.objects.all()
    serializer_class = ClotheSerializer
    lookup_field = "id"


@api_view(["POST"])
def create_clothe_from_scraped_data(request):
    """
    POST /api/clothe/from-scraped/ - Create clothe from scraped Shopify data

    Expected payload format:
    {
        "id": 7731842056254,
        "gid": "gid://shopify/Product/7731842056254",
        "vendor": "REHAB CLO.",
        "type": "Shorts",
        "title": "Jorts Ultra Baggy Black",
        "variants": [
            {
                "id": 41543583727678,
                "price": 3799000,
                "name": "Jorts Ultra Baggy Black - S/28US",
                "public_title": "S/28US",
                "sku": null
            },
            ...
        ],
        "image_url": "https://example.com/image.jpg"
    }
    """
    serializer = CreateClotheFromScrapedDataSerializer(data=request.data)
    if serializer.is_valid():
        clothe = serializer.save()
        response_serializer = ClotheSerializer(clothe)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def bulk_create_clothes_from_scraped_data(request):
    """
    POST /api/clothe/bulk-from-scraped/ - Bulk create clothes from scraped Shopify data

    Expected payload format:
    {
        "products": [
            {
                "id": 7731842056254,
                "gid": "gid://shopify/Product/7731842056254",
                "vendor": "REHAB CLO.",
                "type": "Shorts",
                "title": "Jorts Ultra Baggy Black",
                "variants": [...],
                "image_url": "https://example.com/image.jpg"
            },
            ...
        ]
    }
    """
    serializer = BulkCreateClotheSerializer(data=request.data)
    if serializer.is_valid():
        result = serializer.save()
        return Response(
            {
                "message": f'Successfully processed {result["total_created"] + result["total_updated"]} products',
                "created": result["total_created"],
                "updated": result["total_updated"],
                "created_items": ClotheSerializer(result["created"], many=True).data,
                "updated_items": ClotheSerializer(result["updated"], many=True).data,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def clothe_statistics(request):
    """
    GET /api/clothe/stats - Get statistics about clothes in the database
    """
    total_clothes = Clothe.objects.count()
    clothes_by_type = {}
    clothes_by_vendor = {}

    # Count by type
    for clothe_type in Clothe.ClothingType.choices:
        count = Clothe.objects.filter(type=clothe_type[0]).count()
        if count > 0:
            clothes_by_type[clothe_type[1]] = count

    # Count by vendor (top 10)
    vendors = Clothe.objects.values_list("vendor", flat=True).distinct()
    for vendor in vendors:
        if vendor:
            count = Clothe.objects.filter(vendor=vendor).count()
            clothes_by_vendor[vendor] = count

    # Sort vendors by count
    clothes_by_vendor = dict(
        sorted(clothes_by_vendor.items(), key=lambda x: x[1], reverse=True)[:10]
    )

    return Response(
        {
            "total_clothes": total_clothes,
            "clothes_by_type": clothes_by_type,
            "clothes_by_vendor": clothes_by_vendor,
            "scraped_from_shopify": Clothe.objects.filter(
                shopify_id__isnull=False
            ).count(),
        }
    )


# Legacy function-based views for simpler usage
@api_view(["GET"])
def get_all_clothes(request):
    """
    GET /api/clothe/all - Alternative endpoint to get all clothes
    """
    clothes = Clothe.objects.all().order_by("-created_at")
    serializer = ClotheSerializer(clothes, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_clothe_by_id(request, clothe_id):
    """
    GET /api/clothe/{id} - Alternative endpoint to get clothe by ID
    """
    clothe = get_object_or_404(Clothe, id=clothe_id)
    serializer = ClotheSerializer(clothe)
    return Response(serializer.data)


# User Views
class UserListCreateView(generics.ListCreateAPIView):
    """
    GET /api/user/all - List all users
    POST /api/user/ - Create a new user
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/user/{id} - Retrieve a specific user
    PUT /api/user/{id} - Update a specific user
    DELETE /api/user/{id} - Delete a specific user
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "id"


# Store Views
class StoreListCreateView(generics.ListCreateAPIView):
    """
    GET /api/store/all - List all stores
    POST /api/store/ - Create a new store
    """

    queryset = Store.objects.all().order_by("-created_at")
    serializer_class = StoreSerializer


class StoreDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/store/{id} - Retrieve a specific store
    PUT /api/store/{id} - Update a specific store
    DELETE /api/store/{id} - Delete a specific store
    """

    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    lookup_field = "id"


# Outfit Views
class OutfitListCreateView(generics.ListCreateAPIView):
    """
    GET /api/outfit/all - List all outfits
    POST /api/outfit/ - Create a new outfit
    """

    queryset = Outfit.objects.all().order_by("-created_at")
    serializer_class = OutfitSerializer

    def get_queryset(self):
        """Filter by query parameters if provided"""
        queryset = super().get_queryset()

        # Optional filters
        user_id = self.request.query_params.get("user", None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        rating = self.request.query_params.get("rating", None)
        if rating:
            queryset = queryset.filter(rating__gte=rating)

        return queryset


class OutfitDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/outfit/{id} - Retrieve a specific outfit
    PUT /api/outfit/{id} - Update a specific outfit
    DELETE /api/outfit/{id} - Delete a specific outfit
    """

    queryset = Outfit.objects.all()
    serializer_class = OutfitSerializer
    lookup_field = "id"


# Comment Views
class CommentListCreateView(generics.ListCreateAPIView):
    """
    GET /api/comment/all - List all comments
    POST /api/comment/ - Create a new comment
    """

    queryset = Comment.objects.all().order_by("-created_at")
    serializer_class = CommentSerializer

    def get_queryset(self):
        """Filter by query parameters if provided"""
        queryset = super().get_queryset()

        # Optional filters
        outfit_id = self.request.query_params.get("outfit", None)
        if outfit_id:
            queryset = queryset.filter(outfit_id=outfit_id)

        user_id = self.request.query_params.get("user", None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/comment/{id} - Retrieve a specific comment
    PUT /api/comment/{id} - Update a specific comment
    DELETE /api/comment/{id} - Delete a specific comment
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    lookup_field = "id"


def api_documentation_view(request):
    """
    GET /api/docs/ - API Documentation page
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>VisteT API Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-left: 4px solid #007cba; }
            .method { font-weight: bold; color: #007cba; }
            .url { font-family: monospace; background: #e8e8e8; padding: 2px 5px; }
            .description { margin: 8px 0; }
            .example { background: #f0f0f0; padding: 10px; border-radius: 4px; font-family: monospace; white-space: pre-wrap; overflow-x: auto; }
            h1 { color: #333; }
            h2 { color: #007cba; border-bottom: 2px solid #007cba; padding-bottom: 5px; }
        </style>
    </head>
    <body>
        <h1>🎯 VisteT API Documentation</h1>
        <p>Complete API reference for the VisteT clothing management system.</p>

        <h2>👤 User Endpoints</h2>

        <div class="endpoint">
            <div class="method">GET</div>
            <div class="url">/api/user/all/</div>
            <div class="description">Get all users</div>
            <div class="example">curl http://localhost:8000/api/user/all/</div>
        </div>

        <div class="endpoint">
            <div class="method">POST</div>
            <div class="url">/api/user/</div>
            <div class="description">Create a new user</div>
            <div class="example">curl -X POST http://localhost:8000/api/user/ -H "Content-Type: application/json" -d '{"email": "user@example.com", "name": "John Doe", "description": "Fashion enthusiast"}'</div>
        </div>

        <div class="endpoint">
            <div class="method">GET</div>
            <div class="url">/api/user/{id}/</div>
            <div class="description">Get specific user by ID</div>
            <div class="example">curl http://localhost:8000/api/user/1/</div>
        </div>

        <div class="endpoint">
            <div class="method">PUT</div>
            <div class="url">/api/user/{id}/</div>
            <div class="description">Update specific user</div>
            <div class="example">curl -X PUT http://localhost:8000/api/user/1/ -H "Content-Type: application/json" -d '{"name": "Updated Name"}'</div>
        </div>

        <div class="endpoint">
            <div class="method">DELETE</div>
            <div class="url">/api/user/{id}/</div>
            <div class="description">Delete specific user</div>
            <div class="example">curl -X DELETE http://localhost:8000/api/user/1/</div>
        </div>

        <h2>🏪 Store Endpoints</h2>

        <div class="endpoint">
            <div class="method">GET</div>
            <div class="url">/api/store/all/</div>
            <div class="description">Get all stores</div>
            <div class="example">curl http://localhost:8000/api/store/all/</div>
        </div>

        <div class="endpoint">
            <div class="method">POST</div>
            <div class="url">/api/store/</div>
            <div class="description">Create a new store</div>
            <div class="example">curl -X POST http://localhost:8000/api/store/ -H "Content-Type: application/json" -d '{"name": "Fashion Store", "description": "Quality clothing", "contact_number": "+569 1234 5678"}'</div>
        </div>

        <div class="endpoint">
            <div class="method">GET</div>
            <div class="url">/api/store/{id}/</div>
            <div class="description">Get specific store by ID</div>
            <div class="example">curl http://localhost:8000/api/store/1/</div>
        </div>

        <div class="endpoint">
            <div class="method">PUT</div>
            <div class="url">/api/store/{id}/</div>
            <div class="description">Update specific store</div>
            <div class="example">curl -X PUT http://localhost:8000/api/store/1/ -H "Content-Type: application/json" -d '{"name": "Updated Store Name"}'</div>
        </div>

        <div class="endpoint">
            <div class="method">DELETE</div>
            <div class="url">/api/store/{id}/</div>
            <div class="description">Delete specific store</div>
            <div class="example">curl -X DELETE http://localhost:8000/api/store/1/</div>
        </div>

        <h2>👔 Outfit Endpoints</h2>

        <div class="endpoint">
            <div class="method">GET</div>
            <div class="url">/api/outfit/all/</div>
            <div class="description">Get all outfits with optional filters</div>
            <div class="example">curl http://localhost:8000/api/outfit/all/?user=1&rating=5</div>
        </div>

        <div class="endpoint">
            <div class="method">POST</div>
            <div class="url">/api/outfit/</div>
            <div class="description">Create a new outfit</div>
            <div class="example">curl -X POST http://localhost:8000/api/outfit/ -H "Content-Type: application/json" -d '{"user": 1, "name": "Summer Look", "rating": 5, "components": [1, 2, 3]}'</div>
        </div>

        <div class="endpoint">
            <div class="method">GET</div>
            <div class="url">/api/outfit/{id}/</div>
            <div class="description">Get specific outfit by ID</div>
            <div class="example">curl http://localhost:8000/api/outfit/1/</div>
        </div>

        <div class="endpoint">
            <div class="method">PUT</div>
            <div class="url">/api/outfit/{id}/</div>
            <div class="description">Update specific outfit</div>
            <div class="example">curl -X PUT http://localhost:8000/api/outfit/1/ -H "Content-Type: application/json" -d '{"name": "Updated Outfit Name"}'</div>
        </div>

        <div class="endpoint">
            <div class="method">DELETE</div>
            <div class="url">/api/outfit/{id}/</div>
            <div class="description">Delete specific outfit</div>
            <div class="example">curl -X DELETE http://localhost:8000/api/outfit/1/</div>
        </div>

        <h2>💬 Comment Endpoints</h2>

        <div class="endpoint">
            <div class="method">GET</div>
            <div class="url">/api/comment/all/</div>
            <div class="description">Get all comments with optional filters</div>
            <div class="example">curl http://localhost:8000/api/comment/all/?outfit=1&user=2</div>
        </div>

        <div class="endpoint">
            <div class="method">POST</div>
            <div class="url">/api/comment/</div>
            <div class="description">Create a new comment</div>
            <div class="example">curl -X POST http://localhost:8000/api/comment/ -H "Content-Type: application/json" -d '{"user": 1, "outfit": 1, "title": "Great outfit!", "message": "I love this combination!"}'</div>
        </div>

        <div class="endpoint">
            <div class="method">GET</div>
            <div class="url">/api/comment/{id}/</div>
            <div class="description">Get specific comment by ID</div>
            <div class="example">curl http://localhost:8000/api/comment/1/</div>
        </div>

        <div class="endpoint">
            <div class="method">PUT</div>
            <div class="url">/api/comment/{id}/</div>
            <div class="description">Update specific comment</div>
            <div class="example">curl -X PUT http://localhost:8000/api/comment/1/ -H "Content-Type: application/json" -d '{"title": "Updated Comment Title"}'</div>
        </div>

        <div class="endpoint">
            <div class="method">DELETE</div>
            <div class="url">/api/comment/{id}/</div>
            <div class="description">Delete specific comment</div>
            <div class="example">curl -X DELETE http://localhost:8000/api/comment/1/</div>
        </div>

        <h2>👕 Clothe Endpoints</h2>

        <div class="endpoint">
            <div class="method">GET</div>
            <div class="url">/api/clothe/all/</div>
            <div class="description">Get all clothing items with pagination (20 items per page)</div>
            <div class="example">curl http://localhost:8000/api/clothe/all/</div>
        </div>

        <div class="endpoint">
            <div class="method">POST</div>
            <div class="url">/api/clothe/</div>
            <div class="description">Create a new clothing item manually</div>
            <div class="example">curl -X POST http://localhost:8000/api/clothe/ -H "Content-Type: application/json" -d '{"name": "Cool Shirt", "type": "SHIRT", "image": "http://example.com/image.jpg"}'</div>
        </div>

        <div class="endpoint">
            <div class="method">GET</div>
            <div class="url">/api/clothe/{id}/</div>
            <div class="description">Get specific clothing item by ID</div>
            <div class="example">curl http://localhost:8000/api/clothe/1/</div>
        </div>

        <div class="endpoint">
            <div class="method">PUT</div>
            <div class="url">/api/clothe/{id}/</div>
            <div class="description">Update specific clothing item</div>
            <div class="example">curl -X PUT http://localhost:8000/api/clothe/1/ -H "Content-Type: application/json" -d '{"name": "Updated Name"}'</div>
        </div>

        <div class="endpoint">
            <div class="method">DELETE</div>
            <div class="url">/api/clothe/{id}/</div>
            <div class="description">Delete specific clothing item</div>
            <div class="example">curl -X DELETE http://localhost:8000/api/clothe/1/</div>
        </div>

        <div class="endpoint">
            <div class="method">POST</div>
            <div class="url">/api/clothe/from-scraped/</div>
            <div class="description">Create clothing item from scraped Shopify data</div>
            <div class="example">curl -X POST http://localhost:8000/api/clothe/from-scraped/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": 7731842056254,
    "gid": "gid://shopify/Product/7731842056254",
    "vendor": "REHAB CLO.",
    "type": "Shorts",
    "title": "Jorts Ultra Baggy Black",
    "variants": [
      {
        "id": 41543583727678,
        "price": 3799000,
        "name": "Jorts Ultra Baggy Black - S/28US",
        "public_title": "S/28US",
        "sku": null
      }
    ],
    "image_url": "https://example.com/image.jpg"
  }'</div>
        </div>

        <div class="endpoint">
            <div class="method">POST</div>
            <div class="url">/api/clothe/bulk-from-scraped/</div>
            <div class="description">Bulk create clothing items from scraped data</div>
            <div class="example">curl -X POST http://localhost:8000/api/clothe/bulk-from-scraped/ \
  -H "Content-Type: application/json" \
  -d '{
    "products": [
      {
        "id": 7731842056254,
        "gid": "gid://shopify/Product/7731842056254",
        "vendor": "REHAB CLO.",
        "type": "Shorts",
        "title": "Jorts Ultra Baggy Black",
        "variants": [
          {
            "id": 41543583727678,
            "price": 3799000,
            "name": "Jorts Ultra Baggy Black - S/28US",
            "public_title": "S/28US",
            "sku": null
          }
        ],
        "image_url": "https://example.com/image.jpg"
      }
    ]
  }'</div>
        </div>

        <div class="endpoint">
            <div class="method">GET</div>
            <div class="url">/api/clothe/stats/</div>
            <div class="description">Get database statistics (total items, by type, by vendor)</div>
            <div class="example">curl http://localhost:8000/api/clothe/stats/</div>
        </div>

        <h2>🔍 Query Parameters</h2>
        <div class="endpoint">
            <div class="description">Filter clothing items by type or vendor:</div>
            <div class="example">GET /api/clothe/all/?type=SHORTS&vendor=REHAB</div>
        </div>

        <h2>📊 Response Format</h2>
        <div class="endpoint">
            <div class="description">All clothing items include computed fields:</div>
            <div class="example">{
  "id": 1,
  "name": "Jorts Ultra Baggy Black",
  "type": "SHORTS",
  "vendor": "REHAB CLO.",
  "base_price": "37990.00",
  "variants": [
    {
      "id": 41543583727678,
      "price": 3799000,
      "name": "Jorts Ultra Baggy Black - S/28US",
      "public_title": "S/28US",
      "sku": null
    },
    {
      "id": 41543583760446,
      "price": 3799000,
      "name": "Jorts Ultra Baggy Black - M/31US",
      "public_title": "M/31US",
      "sku": null
    }
  ],
  "price_range": {
    "price": 37990.0
  },
  "available_sizes": [
    "S/28US",
    "M/31US",
    "L/34US"
  ],
  "user": null,
  "store": 1,
  "created_at": "2025-06-21T23:38:22.979697Z",
  "updated_at": "2025-06-22T00:00:04.984363Z"
}</div>
        </div>

        <h2>🕷️ Scraper Integration</h2>
        <p>The spider automatically runs and saves data to these endpoints:</p>
        <div class="endpoint">
            <div class="description">Run scraper manually:</div>
            <div class="example">cd vistet_backend/scraper/vistet_scraper && scrapy crawl details_spider</div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)
