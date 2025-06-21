from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Clothe
from .serializers import ClotheSerializer, CreateClotheFromScrapedDataSerializer, BulkCreateClotheSerializer


class ClotheListCreateView(generics.ListCreateAPIView):
    """
    GET /api/clothe/all - List all clothes
    POST /api/clothe/ - Create a new clothe
    """
    queryset = Clothe.objects.all().order_by('-created_at')
    serializer_class = ClotheSerializer
    
    def get_queryset(self):
        """Filter by query parameters if provided"""
        queryset = super().get_queryset()
        
        # Optional filters
        clothe_type = self.request.query_params.get('type', None)
        if clothe_type:
            queryset = queryset.filter(type=clothe_type)
        
        vendor = self.request.query_params.get('vendor', None)
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


@api_view(['POST'])
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


@api_view(['POST'])
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
        return Response({
            'message': f'Successfully processed {result["total_created"] + result["total_updated"]} products',
            'created': result['total_created'],
            'updated': result['total_updated'],
            'created_items': ClotheSerializer(result['created'], many=True).data,
            'updated_items': ClotheSerializer(result['updated'], many=True).data,
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
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
    vendors = Clothe.objects.values_list('vendor', flat=True).distinct()
    for vendor in vendors:
        if vendor:
            count = Clothe.objects.filter(vendor=vendor).count()
            clothes_by_vendor[vendor] = count
    
    # Sort vendors by count
    clothes_by_vendor = dict(sorted(clothes_by_vendor.items(), key=lambda x: x[1], reverse=True)[:10])
    
    return Response({
        'total_clothes': total_clothes,
        'clothes_by_type': clothes_by_type,
        'clothes_by_vendor': clothes_by_vendor,
        'scraped_from_shopify': Clothe.objects.filter(shopify_id__isnull=False).count(),
    })


# Legacy function-based views for simpler usage
@api_view(['GET'])
def get_all_clothes(request):
    """
    GET /api/clothe/all - Alternative endpoint to get all clothes
    """
    clothes = Clothe.objects.all().order_by('-created_at')
    serializer = ClotheSerializer(clothes, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_clothe_by_id(request, clothe_id):
    """
    GET /api/clothe/{id} - Alternative endpoint to get clothe by ID
    """
    clothe = get_object_or_404(Clothe, id=clothe_id)
    serializer = ClotheSerializer(clothe)
    return Response(serializer.data)
