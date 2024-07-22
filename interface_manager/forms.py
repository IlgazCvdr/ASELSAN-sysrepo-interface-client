# interface_manager/forms.py

import os
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from dotenv import load_dotenv

load_dotenv()

class ConnectForm(forms.Form):
    host = forms.CharField(label='Host', max_length=100)
    port = forms.IntegerField(label='Port', initial=830)
    username = forms.CharField(label='Username', max_length=100, initial="root")
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Connect'))
