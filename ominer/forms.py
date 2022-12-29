from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError


class TwitterForm(forms.Form):
    Keyword = forms.CharField(max_length=50)
    Count = forms.IntegerField(min_value= 500, max_value=10000)
    