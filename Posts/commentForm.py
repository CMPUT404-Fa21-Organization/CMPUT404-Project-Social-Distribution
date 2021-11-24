from django import forms
from .commentModel import *


# comment form
class CommentForm(forms.Form):
    content_type = (("text/markdown", "text/markdown"),
                    ("text/plain", "text/plain"),
                    ("application/app", "application/base64"),
                    ("image/png", "image/png;base64"),
                    ("image/jpeg", "image/jpeg;base64"),
                    ("HTML", "HTML"),
                    )
    contentType = forms.CharField(max_length=20, required=True, widget=forms.Select(choices=content_type))
    text = forms.CharField(required=False)
    file = forms.FileField(required=False)
    
    fields = [
        'content_type',
        'text'
        'file'
    ]