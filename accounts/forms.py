from django import forms
from .models import Account

class RegistrationForm(forms.ModelForm):
    # Since Password and Repeat Password are not in our fields, we will create those here.
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Your Password Here',
        'class': 'form-control',
    }))

    repeat_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password',
        'class': 'form-control',
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password']
    
    # Enter attributes via Backend python cod
    # Overwritting form functionality
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # Adding Placeholder attribute 
        self.fields['first_name'].widget.attrs['placeholder'] = 'Your First Name Here'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Your Last Name Here'
        self.fields['email'].widget.attrs['placeholder'] = 'Your Email Here'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Your Phone Number Here'

        # Adding Class to each field present
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    

    # Check if passwords doesn't match
    # In which case raise Validation Error with a message
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('repeat_password')

        if password != confirm_password:
            raise forms.ValidationError(
                'Passwords Does not match. Please Try Again'
            )