from django.urls import path, include  # Add 'include' to the import
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('login/', auth_views.LoginView.as_view(template_name='donationnn_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),  # Registration page
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard
    path('donate/', views.donate, name='donate'),  # Donation page
    path('organization/<int:org_id>/', views.organization_detail, name='organization_detail'),  # Organization details
    path('add_organization/', views.add_organization, name='add_organization'),  # Add organization
    path('accounts/', include('django.contrib.auth.urls')),  # Add this line for Django auth URLs
    path('donation_success/', views.donation_success, name='donation_success'),
    path('organization_list/', views.organization_list, name='organization_list'), 
    path('item/<int:item_id>/update/', views.update_item, name='update_item'),
    path('item/<int:item_id>/delete/', views.delete_item, name='delete_item'),
    path('add_new_organization/', views.add_new_organization, name='add_new_organization'),
    path('manage_organization/<int:organization_id>/',views.manage_organization, name='manage_organization'),
    path('delete_organization/<int:organization_id>/', views.delete_organization, name='delete_organization'),
]


