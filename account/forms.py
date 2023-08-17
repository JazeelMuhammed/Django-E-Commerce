from django import forms
from .models import Account, UserProfile


class RegistrationForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter the password'
    }))
    conf_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm password'
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone', 'email', 'password', 'conf_password']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter your first name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter your last name'
        self.fields['phone'].widget.attrs['placeholder'] = 'Enter your phone number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter your email address'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean_conf_password(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        conf_password = cleaned_data.get('conf_password')

        if password != conf_password:
            raise forms.ValidationError('Password does not match')


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone']

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        # self.fields['first_name'].widget.attrs['placeholder'] = 'Enter your first name'
        # self.fields['last_name'].widget.attrs['placeholder'] = 'Enter your last name'
        # self.fields['phone'].widget.attrs['placeholder'] = '1234567'
        # self.fields['email'].widget.attrs['placeholder'] = 'user123@gmail.com'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    profile_img = forms.ImageField(required=False, error_messages={'invalid':("Image files only")}, widget=forms.FileInput)

    class Meta:
        model = UserProfile
        fields = ['profile_img', 'address_1', 'city', 'state', 'country']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        # self.fields['address_1'].widget.attrs['placeholder'] = 'Enter your address'
        # self.fields['city'].widget.attrs['placeholder'] = 'eg: Bangalore'
        # self.fields['state'].widget.attrs['placeholder'] = 'eg: Kerala'
        # self.fields['country'].widget.attrs['placeholder'] = 'eg: India'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'