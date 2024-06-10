from django.urls import path
from . import views

urlpatterns = [
    # attention made test home for dev reasons.
    path("create_queue", views.create_queue, name="create_queue"),
]
