__author__ = 'xulei'

from django import forms

class buildForm(forms.Form):

    CHOICES = (('1', 'First',), ('2', 'Second',))
    choice_field = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)


