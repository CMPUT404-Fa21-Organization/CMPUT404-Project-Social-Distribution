from django import forms
from commentModel import *


# comment form
class CommentForm(forms.Forms):
    text = forms.CharField(required=False)
    file = forms.FileField(required=False)
    unlisted = forms.BooleanField(required=False)
    
    fields = [
        #'page'
        #'size',
        'file',
        'unlisted'
    ]
