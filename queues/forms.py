from .models import Queue, Entry
from django import forms


class QueueForm(forms.ModelForm):
    class Meta:
        model = Queue
        fields = ('name','description')

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ("title","video_id")