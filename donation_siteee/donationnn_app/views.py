from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Organization, Item, Donation
from .forms import UserRegistrationForm, OrganizationForm, DonationForm, ItemForm

@login_required
def dashboard(request):
    context = {}
    
    if request.user.is_authenticated and request.user.role == 'org_rep':
        # Check if the user has an organization
        user_organization = Organization.objects.filter(email=request.user.email).first()
        context['user_has_organization'] = user_organization is not None
        context['user_organization'] = user_organization
    return render(request, 'donationnn_app/dashboard.html', context)

from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
@login_required
def donate(request):
    if request.user.role != 'donor':
        return redirect('dashboard')

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity'))
        
        # Get the item and organization
        item = get_object_or_404(Item, id=item_id)
        organization = item.organization

        # Check if the donation quantity is valid
        if quantity > 0 and quantity <= item.quantity_needed:
            # Record the donation
            Donation.objects.create(donor=request.user, item=item, quantity=quantity)
            
            # Update the item's quantity needed
            item.quantity_needed -= quantity

            # If quantity needed reaches 0, delete the item
            if item.quantity_needed == 0:
                item.delete()
                messages.success(request, f'Thank you for donating {quantity} of {item.item_name} to {organization.org_name}! The item has been fully donated and removed from the list.')
            else:
                item.save()
                messages.success(request, f'Thank you for donating {quantity} of {item.item_name} to {organization.org_name}!')

            # Send confirmation email to the donor
            try:
                send_mail(
                    subject="Donation Confirmation - Helping Hand",
                    message=f"Thank you for donating {quantity} of {item.item_name} to {organization.org_name}!",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[request.user.email],  # Send email to the donor
                    fail_silently=False,
                )
                logger.info("Email sent to donor successfully!")
            except Exception as e:
                logger.error(f"Failed to send email to donor: {e}")
                messages.error(request, "Failed to send confirmation email to donor. Please contact support.")

            # Send notification email to the organization owner
            try:
                send_mail(
                    subject="New Donation Received - Helping Hand",
                    message=f"A new donation has been received for your organization '{organization.org_name}'. "
                            f"Donor: {request.user.username}\n"
                            f"Item: {item.item_name}\n"
                            f"Quantity: {quantity}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[organization.email],  # Send email to the organization owner
                    fail_silently=False,
                )
                logger.info("Email sent to organization owner successfully!")
            except Exception as e:
                logger.error(f"Failed to send email to organization owner: {e}")
                messages.error(request, "Failed to send notification email to organization owner. Please contact support.")

            return redirect('donate')
        else:
            messages.error(request, 'Invalid donation quantity. Please try again.')

    # Fetch all organizations
    organizations = Organization.objects.all()

    # Handle category-based search
    category = request.GET.get('category')
    org_id = request.GET.get('org_id')

    if org_id:
        # Get the specific organization
        organization = get_object_or_404(Organization, id=org_id)
        # Filter items by category if a category is selected
        if category:
            items = organization.items.filter(item_category=category)
        else:
            items = organization.items.all()
        
        # Add the filtered items to the organization object
        organization.filtered_items = items
        organizations = [organization]
    else:
        # If no organization is selected, show all organizations with all items
        for organization in organizations:
            organization.filtered_items = organization.items.all()

    return render(request, 'donationnn_app/donate.html', {
        'organizations': organizations,
        'category': category,
    })

from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

@login_required
def add_organization(request):
    if request.user.role != 'org_rep':
        return redirect('dashboard')

    if request.method == 'POST':
        org_form = OrganizationForm(request.POST, request.FILES)
        item_form = ItemForm(request.POST, request.FILES)

        if org_form.is_valid() and item_form.is_valid():
            # Save the organization
            organization = org_form.save(commit=False)
            organization.email = request.user.email
            organization.save()

            # Save the item
            item = item_form.save(commit=False)
            item.organization = organization
            item.save()

            # Send an email to the donor (or organization representative)
            try:
                send_mail(
                    subject="New Organization Added - Helping Hand",
                    message=f"Thank you for adding a new organization: {organization.org_name}. "
                            f"Your item '{item.item_name}' has also been added successfully.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[request.user.email],  # Send email to the donor's email
                    fail_silently=False,
                )
                messages.success(request, 'Organization and item added successfully! An email has been sent to your address.')
            except Exception as e:
                logger.error(f"Failed to send email: {e}")
                messages.error(request, 'Organization and item added successfully, but the email could not be sent.')

            return redirect('organization_detail', org_id=organization.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        org_form = OrganizationForm()
        item_form = ItemForm()

    return render(request, 'donationnn_app/add_organization.html', {
        'org_form': org_form,
        'item_form': item_form,
    })

@login_required
def organization_detail(request, org_id):
    organization = get_object_or_404(Organization, id=org_id)
    items = organization.items.all()  # Get all items for this organization

    # Handle category-based search
    category = request.GET.get('category')
    if category:
        items = items.filter(item_category=category)  # Use item_category for filtering

    if request.method == 'POST':
        # Handle item addition
        if 'add_item' in request.POST:
            form = ItemForm(request.POST, request.FILES)
            if form.is_valid():
                item = form.save(commit=False)
                item.organization = organization
                item.save()
                return redirect('organization_detail', org_id=org_id)
        # Handle donation form
        elif 'donate' in request.POST:
            donation_form = DonationForm(request.POST)
            if donation_form.is_valid():
                item = donation_form.cleaned_data['item']
                quantity = donation_form.cleaned_data['quantity']
                # Update item quantities
                item.quantity_donated += quantity
                item.save()
                # Record the donation
                Donation.objects.create(donor=request.user, item=item, quantity=quantity)
                return redirect('donation_success')
    else:
        form = ItemForm()  # Form for adding items
        donation_form = DonationForm()  # Form for donations

    return render(request, 'donationnn_app/organization.html', {
        'organization': organization,
        'items': items,
        'form': form,
        'donation_form': donation_form,
        'category': category,  # Pass the selected category to the template
    })

@login_required
def donation_success(request):
    return render(request, 'donationnn_app/donation_success.html')

def home(request):
    return render(request, 'donationnn_app/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page after registration
    else:
        form = UserRegistrationForm()
    return render(request, 'donationnn_app/register.html', {'form': form})

def organization_list(request):
    organizations = Organization.objects.all()
    return render(request, 'donationnn_app/organization_list.html', {'organizations': organizations})

# views.py
@login_required
def add_item(request, org_id):
    organization = get_object_or_404(Organization, id=org_id)
    if request.user.role != 'org_rep':
        return redirect('dashboard')  # Only organization reps can add items

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.organization = organization
            item.save()
            return redirect('organization_detail', org_id=org_id)
    else:
        form = ItemForm()

    return render(request, 'donationnn_app/add_item.html', {'form': form, 'organization': organization})

@login_required
def update_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.user.role != 'org_rep':
        return redirect('dashboard')  # Only organization reps can update items
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('organization_detail', org_id=item.organization.id)
    else:
        form = ItemForm(instance=item)
    return render(request, 'donationnn_app/update_item.html', {'form': form, 'item': item})

@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.user.role != 'org_rep':
        return redirect('dashboard')  # Only organization reps can delete items
    org_id = item.organization.id
    item.delete()
    return redirect('organization_detail', org_id=org_id)

@login_required
def add_new_organization(request):
    if request.user.role != 'org_rep':
        return redirect('dashboard')  # Only org_rep users can access this page

    if request.method == 'POST':
        form = OrganizationForm(request.POST, request.FILES)
        if form.is_valid():
            organization = form.save(commit=False)
            organization.email = request.user.email  # Link organization to the user's email
            organization.save()
            return redirect('organization_detail', org_id=organization.id)
    else:
        form = OrganizationForm()

    return render(request, 'donationnn_app/add_new_organization.html', {'form': form})
@login_required
def manage_organization(request, organization_id):
    organization = get_object_or_404(Organization, id=organization_id)
    
    # Ensure the logged-in user owns this organization
    if organization.email != request.user.email:
        messages.error(request, 'You do not have permission to manage this organization.')
        return redirect('dashboard')

    # Fetch all items for the organization
    items = organization.items.all()

    # Initialize forms
    org_form = OrganizationForm(instance=organization)  # Form for updating organization
    item_form = ItemForm()  # Form for adding new items

    if request.method == 'POST':
        print("POST data:", request.POST)  # Debug: Print POST data

        # Handle organization update
        if 'update_organization' in request.POST:
            org_form = OrganizationForm(request.POST, request.FILES, instance=organization)
            if org_form.is_valid():
                org_form.save()
                messages.success(request, 'Organization updated successfully!')
                return redirect('manage_organization', organization_id=organization.id)
            else:
                messages.error(request, 'Please correct the errors below.')

        # Handle adding a new item
        elif 'add_item' in request.POST:
            item_form = ItemForm(request.POST, request.FILES)
            if item_form.is_valid():
                item = item_form.save(commit=False)
                item.organization = organization
                item.save()
                messages.success(request, 'Item added successfully!')
                return redirect('manage_organization', organization_id=organization.id)
            else:
                messages.error(request, 'Please correct the errors below.')

        # Handle updating an existing item
        elif 'update_item' in request.POST:
            print("Updating item...")  # Debug: Check if this block is reached
            item_id = request.POST.get('item_id')
            print("Item ID:", item_id)  # Debug: Print the item ID
            item = get_object_or_404(Item, id=item_id, organization=organization)
            item_form = ItemForm(request.POST, request.FILES, instance=item)
            if item_form.is_valid():
                item_form.save()
                messages.success(request, 'Item updated successfully!')
                return redirect('manage_organization', organization_id=organization.id)
            else:
                print("Form Errors:", item_form.errors)  # Debug: Print form errors
                messages.error(request, 'Please correct the errors below.')

        # Handle deleting an item
        elif 'delete_item' in request.POST:
            item_id = request.POST.get('item_id')
            item = get_object_or_404(Item, id=item_id, organization=organization)
            item.delete()
            messages.success(request, 'Item deleted successfully!')
            return redirect('manage_organization', organization_id=organization.id)

    return render(request, 'donationnn_app/manage_organization.html', {
        'organization': organization,
        'items': items,
        'org_form': org_form,
        'item_form': item_form,
    })

@login_required
def delete_organization(request, organization_id):
    organization = get_object_or_404(Organization, id=organization_id)
    
    # Ensure the logged-in user owns this organization
    if organization.email != request.user.email:
        messages.error(request, 'You do not have permission to delete this organization.')
        return redirect('dashboard')
    
    # Delete the organization
    organization.delete()
    messages.success(request, 'Organization deleted successfully!')
    return redirect('dashboard')

from django.contrib.auth import authenticate, login, logout
from django.views import View
class UserLogoutView(View):
    def get(self,request):
        logout(request)
        messages.success(request,"Logout Success")
        return redirect('login')