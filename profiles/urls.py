from django.urls import path
from . import views

urlpatterns = [
    # attention made test home for dev reasons.
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("authorization", views.authorization, name="authorization"),
    path("test", views.test, name="test"),
    path("remove_authorization", views.remove_authorization, name="remove_authorization"),
    path("", views.index, name="index"),
]
