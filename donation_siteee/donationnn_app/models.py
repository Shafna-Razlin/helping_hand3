from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

# Custom User Model (if not using Django's built-in User model)
class Donor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    age = models.IntegerField()

    def __str__(self):
        return self.user.username

class Organization(models.Model):
    picture = models.ImageField(upload_to='organization_pictures/', blank=True, null=True)  
    org_name = models.CharField(max_length=255, verbose_name="Organization Name")
    org_id = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    location = models.CharField(max_length=100)
    category = models.CharField(max_length=50)

    def __str__(self):
        return self.org_name

# donationnn_app/models.py
from django.db import models

class Item(models.Model):
    CATEGORY_CHOICES = [
        ('household_essentials', 'Household Essentials'),
        ('clothing', 'Clothing'),
        ('footwear', 'Footwear'),
        ('grains', 'Grains'),
        ('pulses', 'Pulses'),
        ('mobility_aids', 'Mobility Aids'),
        ('educational_supplies', 'Educational Supplies'),
    ]

    item_name = models.CharField(max_length=255)
    item_category = models.CharField(max_length=50, choices=CATEGORY_CHOICES,default='grains')
    description = models.TextField(blank=True, null=True)
    item_picture = models.ImageField(upload_to='item_pictures/', blank=True, null=True)  # Ensure this matches the form
    quantity_needed = models.PositiveIntegerField(default=1)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='items')

    def __str__(self):
        return self.item_name

class Donation(models.Model):
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='donations')
    quantity = models.IntegerField()
    donation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.username} donated {self.quantity} of {self.item.name}"
    
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('donor', 'Donor'),
        ('org_rep', 'Organization Representative'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='donor')