from django import forms
from .models import Payment


class PaymentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.fields['amount'].widget.attrs['readonly'] = True

    class Meta:
        model = Payment
        fields = ['credit_card_number', 'expiry_date', 'amount']
        widgets = {
            'extended_user': forms.HiddenInput(),
            'credit_card_number': forms.TextInput(attrs={'placeholder': 'Format: 1234 5678 1234 5678'}),
            'expiry_date': forms.TextInput(attrs={'placeholder': 'Format: 09/2022'})
        }
