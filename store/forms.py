from django import forms


class CheckoutForm(forms.Form):
    first_name = forms.CharField(max_length=50, label="First name")
    last_name = forms.CharField(max_length=50, label="Last name")
    email = forms.EmailField(label="Email")
    phone = forms.CharField(max_length=10, label="Phone")
    address = forms.CharField(
        max_length=50,
        label="Shipping address",
        widget=forms.Textarea(attrs={"rows": 3}),
    )
