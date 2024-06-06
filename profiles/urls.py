from django.urls import path
from . import views

urlpatterns = [
    # attention made test home for dev reasons.
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("authorization", views.authorization, name="authorization"),
    path("test", views.test, name="test"),
    path("", views.index, name="index"),
]
