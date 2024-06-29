from .models import Queue
from django import forms


class QueueForm(forms.ModelForm):
    class Meta:
        model = Queue
        fields = ('title', 'description')
