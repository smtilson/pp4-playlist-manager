from django.contrib import admin
from .models import Queue

# Register your models here.
admin.site.register(
    Queue,
    list_display=(
        "title",
        "owner",
        "youtube_id",
        "description",
        "created_at",
        "updated_at",
    ),
)