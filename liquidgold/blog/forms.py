# blog/forms.py

from django import forms

PRIZE_CHOICES = [
    ("Hat", "Hat"),
    ("Shirt", "Shirt"),
    ("Bong", "Bong"),
    ("Hoody", "Hoody"),
]

class PrizeClaimForm(forms.Form):
    prize = forms.ChoiceField(choices=PRIZE_CHOICES, widget=forms.Select(attrs={"readonly": True}))
    full_name = forms.CharField(max_length=120)
    email = forms.EmailField()
    phone = forms.CharField(max_length=30, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)
    size = forms.ChoiceField(
        choices=[("N/A","N/A"),("S","S"),("M","M"),("L","L"),("XL","XL")],
        initial="N/A",
        help_text="Used for shirt/hoody."
    )
    notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)
    accept = forms.BooleanField(label="I confirm my info is correct.")

class OrderForm(forms.Form):
    full_name = forms.CharField(max_length=120)
    email = forms.EmailField()
    phone = forms.CharField(max_length=30, required=False)
    items = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), help_text="What would you like to order?")
    notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)

class CommentForm(forms.Form):
    author = forms.CharField(
        max_length=60,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Your Name"}
        ),
    )
    body = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "Leave a comment!"}
        )
    )