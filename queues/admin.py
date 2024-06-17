from django.contrib import admin
from .models import Queue

# Register your models here.
admin.site.register(
    Queue,
    list_display=(
        "title",
        "owner",
        "description",
    ),
)