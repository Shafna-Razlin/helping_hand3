from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User  # Import the User model
from .models import Organization, Item, Donation
from .models import CustomUser

class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, widget=forms.Select)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'password1', 'password2']

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = '__all__'  # This includes all fields from the model

class DonationForm(forms.Form):
    item = forms.ModelChoiceField(queryset=Item.objects.all(), widget=forms.HiddenInput())
    quantity = forms.IntegerField(min_value=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item'].widget.attrs.update({'class': 'form-control'})
        self.fields['quantity'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Quantity'})


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['item_category','item_name','item_picture', 'description', 'quantity_needed']