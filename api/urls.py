from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Class-based views (recommended)
    path('clothe/', views.ClotheListCreateView.as_view(), name='clothe-list-create'),
    path('clothe/<int:pk>/', views.ClotheDetailView.as_view(), name='clothe-detail'),
    
    # Function-based views for specific use cases
    path('clothe/all/', views.get_all_clothes, name='clothe-list'),
    path('clothe/stats/', views.clothe_statistics, name='clothe-stats'),
    path('clothe/from-scraped/', views.create_clothe_from_scraped_data, name='clothe-from-scraped'),
    path('clothe/bulk-from-scraped/', views.bulk_create_clothes_from_scraped_data, name='clothe-bulk-from-scraped'),
    
    # Alternative endpoint for getting clothe by ID
    path('clothe/get/<int:clothe_id>/', views.get_clothe_by_id, name='clothe-by-id'),
] 