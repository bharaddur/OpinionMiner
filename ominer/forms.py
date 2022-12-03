from django import forms

class TwitterForm(forms.Form):
    Keyword = forms.CharField(max_length=50)
    Count = forms.IntegerField(max_value=10000)