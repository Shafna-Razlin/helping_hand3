from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User  # Import the default User model
from .models import Organization, Item, Donor, CustomUser # Import your custom models

admin.site.register(CustomUser, UserAdmin)

# Register your custom User model (Donor)
@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address', 'age')
    search_fields = ('user__username', 'phone', 'address')
    list_filter = ('age',)

# Register other models
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('org_name', 'org_id', 'email', 'location', 'category')
    search_fields = ('org_name', 'org_id', 'email')
    list_filter = ('category', 'location')

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('item_name','item_category','organization', 'quantity_needed')
    search_fields = ('item_name', 'organization__org_name')  #
    list_filter = ('organization','item_category')