from django.urls import path
from . import views

urlpatterns = [
    # attention made test home for dev reasons.
    path("create_queue", views.create_queue, name="create_queue"),
    path("edit_queue/<int:queue_id>", views.edit_queue, name="edit_queue")
]
