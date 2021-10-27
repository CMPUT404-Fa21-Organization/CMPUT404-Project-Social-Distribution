from django import forms
from .commentModel import *


# comment form
class CommentForm(forms.Form):
    content_type = (("markdown", "text/markdown"),
                ("plain", "text/plain"),
                ("app", "application/base64"),
                ("png", "image/png;base64"),
                ("jpeg", "image/jpeg;base64"),
                ("html", "HTML"),
                )
    contentType = forms.CharField(max_length=20, required=True, widget=forms.Select(choices=content_type))
    text = forms.CharField(required=False)
    file = forms.FileField(required=False)
    
    fields = [
        'content_type',
        'text'
        'file'
    ]