from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    # Documentation
    path("docs/", views.api_documentation_view, name="api-docs"),
    # Clothe endpoints
    path("clothe/", views.ClotheListCreateView.as_view(), name="clothe-list-create"),
    path("clothe/<int:id>/", views.ClotheDetailView.as_view(), name="clothe-detail"),
    path(
        "clothe/all/", views.ClotheListCreateView.as_view(), name="clothe-list"
    ),
    path("clothe/stats/", views.clothe_statistics, name="clothe-stats"),
    path(
        "clothe/from-scraped/",
        views.create_clothe_from_scraped_data,
        name="clothe-from-scraped",
    ),
    path(
        "clothe/bulk-from-scraped/",
        views.bulk_create_clothes_from_scraped_data,
        name="clothe-bulk-from-scraped",
    ),
    # User endpoints
    path("user/", views.UserListCreateView.as_view(), name="user-list-create"),
    path("user/<int:id>/", views.UserDetailView.as_view(), name="user-detail"),
    path(
        "user/all/", views.UserListCreateView.as_view(), name="user-list"
    ),
    # Store endpoints
    path("store/", views.StoreListCreateView.as_view(), name="store-list-create"),
    path("store/<int:id>/", views.StoreDetailView.as_view(), name="store-detail"),
    path(
        "store/all/", views.StoreListCreateView.as_view(), name="store-list"
    ),
    # Outfit endpoints
    path("outfit/", views.OutfitListCreateView.as_view(), name="outfit-list-create"),
    path("outfit/<int:id>/", views.OutfitDetailView.as_view(), name="outfit-detail"),
    path(
        "outfit/all/", views.OutfitListCreateView.as_view(), name="outfit-list"
    ),
    # Comment endpoints
    path("comment/", views.CommentListCreateView.as_view(), name="comment-list-create"),
    path("comment/<int:id>/", views.CommentDetailView.as_view(), name="comment-detail"),
    path(
        "comment/all/", views.CommentListCreateView.as_view(), name="comment-list"
    ),
]
