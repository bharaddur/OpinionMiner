from django import forms

class TwitterForm(forms.Form):
    Keyword = forms.CharField(max_length=50)