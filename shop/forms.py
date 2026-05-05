from django import forms
from .models import Review


class CheckoutForm(forms.Form):
    address      = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label="Shipping Address")
    coupon_code  = forms.CharField(max_length=20, required=False, label="Coupon Code")


class ProductSearchForm(forms.Form):
    q         = forms.CharField(required=False, label='Search')
    min_price = forms.DecimalField(required=False, min_value=0, label='Min Price')
    max_price = forms.DecimalField(required=False, min_value=0, label='Max Price')
    category  = forms.CharField(required=False, widget=forms.HiddenInput())


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
