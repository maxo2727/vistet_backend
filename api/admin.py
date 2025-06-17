from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Store, Clothe, Outfit, Comment

"""
EXPLANATION OF ADMIN FEATURES:
- list_display: Columns shown in the main admin list
- list_filter: Sidebar filters for easy data filtering
- search_fields: Fields that can be searched with the search box
- ordering: Default ordering of records
- fieldsets: Groups fields in the edit form for better organization
- add_fieldsets: Special fieldsets for adding new users
- readonly_fields: These fields can't be edited (auto-generated timestamps)
- get_owner: Custom method to display who owns the clothing item
- filter_horizontal: Creates a nice interface for many-to-many relationships
- get_components_count: Shows how many clothing items are in the outfit
"""

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin configuration
    """
    list_display = ('email', 'name', 'contact_number', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'description', 'contact_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    """
    Store admin configuration
    """
    list_display = ('name', 'contact_number', 'site_url', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Clothe)
class ClotheAdmin(admin.ModelAdmin):
    """
    Clothe admin configuration
    """
    list_display = ('name', 'type', 'get_owner', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('name', 'user__name', 'store__name')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_owner(self, obj):
        if obj.user:
            return f"User: {obj.user.name}"
        elif obj.store:
            return f"Store: {obj.store.name}"
        return "No owner"
    get_owner.short_description = 'Owner'


@admin.register(Outfit)
class OutfitAdmin(admin.ModelAdmin):
    """
    Outfit admin configuration
    """
    list_display = ('name', 'user', 'rating', 'get_components_count', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('name', 'user__name')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('components',)
    
    def get_components_count(self, obj):
        return obj.components.count()
    get_components_count.short_description = 'Components Count'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Comment admin configuration
    """
    list_display = ('title', 'user', 'outfit', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'message', 'user__name', 'outfit__name')
    readonly_fields = ('created_at', 'updated_at')
