from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from takeout.models import CustomerProfile, VendorProfile, VendorMeal
from django.contrib.auth import authenticate

MAX_UPLOAD_SIZE = 2500000

class CustomerLoginForm(forms.Form):
    username = forms.CharField(max_length=20,
                               widget=forms.TextInput(
                                   attrs={'class': 'validate',
                                          'name': 'username',
                                          'id': 'customer-username'}))
    password = forms.CharField(max_length=200,
                               widget=forms.PasswordInput(
                                   attrs={'class': 'validate',
                                          'name': 'password',
                                          'id': 'customer-password'}))

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username/password")

        return cleaned_data

class VendorLoginForm(forms.Form):
    username = forms.CharField(max_length=20,
                               widget=forms.TextInput(
                                   attrs={'class': 'validate',
                                          'name': 'username',
                                          'id': 'vendor-username'}))
    password = forms.CharField(max_length=200,
                               widget=forms.PasswordInput(
                                   attrs={'class': 'validate',
                                          'name':'password',
                                          'id':'vendor-password'}))

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username/password")

        return cleaned_data

class CustomerRegistrationForm(forms.Form):
    last_name = forms.CharField(max_length=20,
                                widget=forms.TextInput(
                                    attrs={'class': "validate",
                                           'name': "last-name-input",
                                           'id': "last-name"}))
    first_name = forms.CharField(max_length=20,
                                 widget=forms.TextInput(
                                     attrs={'class': "validate",
                                            'name': "first-name-input",
                                            'id': "first-name"}))
    andrewID = forms.CharField(max_length=20, label='Andrew ID',
                               widget=forms.TextInput(
                                   attrs={'class': "validate",
                                          'name': "andrew-id-input",
                                          'id': "andrew-id"}))
    email = forms.CharField(max_length=50,
                            widget=forms.EmailInput(
                                attrs={'class': "validate",
                                       'name': "email-input",
                                       'id': "email"}))
    username = forms.CharField(max_length=20,
                               widget=forms.TextInput(
                                   attrs={'class': "validate",
                                          'name': "username-input",
                                          'id': "username"}))
    password = forms.CharField(max_length=200,
                               widget=forms.PasswordInput(
                                   attrs={'class': "validate",
                                          'name': "password",
                                          'id': "password"}))
    confirm_password = forms.CharField(max_length=200,
                                       widget=forms.PasswordInput(
                                           attrs={'class': "validate",
                                                  'name': "confirm-password",
                                                  'id': "confirm-password"}))
    phone = forms.CharField(max_length=12,
                            widget=forms.NumberInput(
                                attrs={'class': "validate",
                                       'name': "phone-input",
                                       'id': "phone"}))

    def clean(self):
        cleaned_data = super(CustomerRegistrationForm, self).clean()

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords did not match.")

        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        return username

class VendorRegistrationForm(forms.Form):
    phone = forms.CharField(max_length=12,
                            widget=forms.NumberInput(
                                attrs={'class': "validate",
                                       'name': "phone-input",
                                       'id': "phone"}))
    email = forms.CharField(max_length=50,
                            widget=forms.EmailInput(
                                attrs={'class': "validate",
                                       'name': "email-input",
                                       'id': "email"}))
    company_name = forms.CharField(max_length=30,
                                   widget=forms.TextInput(
                                       attrs={'class': "validate",
                                              'name': "company-name-input",
                                              'id': "company-name"}))
    license = forms.CharField(max_length=30,
                              widget=forms.TextInput(
                                  attrs={'class': "validate",
                                         'name': "license-input",
                                         'id': "license"}))
    username = forms.CharField(max_length=20,
                               widget=forms.TextInput(
                                   attrs={'class': "validate",
                                          'name': "username-input",
                                          'id':"username"}))
    password = forms.CharField(max_length=200,
                               widget=forms.PasswordInput(
                                   attrs={'class': "validate",
                                          'name': "password",
                                          'id': "password"}))
    confirm_password = forms.CharField(max_length=200,
                                       widget=forms.PasswordInput(
                                           attrs={'class': "validate",
                                                  'name': "confirm-password",
                                                  'id': "confirm-password"}))
    payment_key = forms.CharField(max_length=50,
                                  widget=forms.TextInput(
                                      attrs={'class': "validate",
                                             'name': "payment-key",
                                             'id': "payment-key"}))

    def clean(self):
        cleaned_data = super(VendorRegistrationForm, self).clean()

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords did not match.")

        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        return username


class VendorMealForm(forms.ModelForm):
    avail_quantity = forms.IntegerField(required=False,
                                        widget=forms.NumberInput(attrs={
                                            'placeholder': "e.g. 100",
                                            'id': "avail_quantity",
                                            'class': 'materialize-textarea'
                                        }),
                                        label='Starting Volumes')

    class Meta:
        model = VendorMeal
        widgets = {
            'meal_name': forms.TextInput(attrs={
                'placeholder': "e.g. A/B/C",
                'id': "meal_name"
            }),
            'price': forms.TextInput(attrs={
                'placeholder': "e.g. 10",
                'id': "price"
            }),
            'meal_detail': forms.Textarea(attrs={
                'placeholder': "e.g. Ma Po Tofu with rice/麻婆豆腐配饭",
                'id': "meal_description",
                'class': "materialize-textarea"
            }),
            'drink': forms.Textarea(attrs={
                'placeholder': "e.g. Watermelon Juice",
                'id': "drink",
                'class': "materialize-textarea",
            }),
            'meal_type': forms.Textarea(attrs={
                'placeholder': "e.g. Lunch/Dinner",
                'id': "meal_type",
                'class': "materialize-textarea",
            }),
            'picture': forms.FileInput(),
        }
        labels = {
            'picture': _('Profile Picture'),
            'meal_name': _('Meal Number'),
            'price': _('Price($)'),
            'meal_detail': _('Meal Description'),
            'drink': _('Drink Description'),
            'meal_type': _('Meal Type'),
        }
        exclude = ('number_ordered', 'vendor', 'content_type', )

    def clean_picture(self):
        picture = self.cleaned_data['picture']
        if not picture:
            raise forms.ValidationError('You must upload a picture')
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture



class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        widgets = {
            'phone': forms.TextInput(attrs={
                                         'id': 'phone',
                                         'type': 'tel',
                                         'class': 'validate',
                                     }),
            'profile_pic': forms.FileInput(),
        }
        labels = {
            'phone': _('Phone'),
            'profile_pic': _('Profile Picture')
        }
        exclude = ('customer', 'andrew_id', 'content_type', )
        
    def clean_picture(self):
        picture = self.cleaned_data['profile_pic']
        if not picture:
            raise forms.ValidationError('You must upload a picture')
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture



class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        widgets = {
            'email': forms.TextInput(attrs={
                'id': 'email',
                'type': 'email',
                'class': 'validate',
            }),
            'first_name': forms.TextInput(attrs={
                'id': 'first_name',
                'type': 'text',
                'class': 'validate',
            }),
            'last_name': forms.TextInput(attrs={
                'id': 'last_name',
                'type': 'text',
                'class': 'validate',
            }),
        }
        labels = {
            'email': _('Email'),
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
        }
        fields = ('email', 'first_name', 'last_name', )


class VendorProfileForm(forms.ModelForm):
    phone = forms.CharField(required=False,
                            widget=forms.TextInput(attrs={
                                'id': 'phone',
                                'type': 'tel',
                                'class': 'validate'
                            }),
                            label='Phone')
    time_slot = forms.CharField(required=False,
                                widget=forms.TextInput(attrs={
                                    'id': 'time_slot',
                                    'type': 'text',
                                    'class': 'validate'
                                }),
                                label='Time Slot')

    parking_location = forms.CharField(required=False,
                                       widget=forms.TextInput(attrs={
                                           'id': 'location',
                                           'type': 'text',
                                           'class': 'validate'
                                       }),
                                       label='Location')

    car = forms.CharField(required=False,
                          widget=forms.TextInput(attrs={
                              'id': 'car',
                              'type': 'text',
                              'class': 'validate',
                              'placeholder': 'e.g. Grey Audi, license SEF9823'
                          }),
                          label='Car')

    profile_pic = forms.FileField(required=False,
                                  widget=forms.FileInput())

    class Meta:
        model = VendorProfile
        exclude = ('vendor', 'license', 'company_name', 'payment_key', 'content_type',)

    def clean_picture(self):
        picture = self.cleaned_data['profile_pic']
        if not picture:
            raise forms.ValidationError('You must upload a picture')
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if picture.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return picture
