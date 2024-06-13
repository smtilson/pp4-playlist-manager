from django.urls import path
from . import views

urlpatterns = [
    # attention made test home for dev reasons.
    path("profile", views.profile, name="profile"),
    path("test", views.test, name="test"),
    path("test_function", views.test_function, name="test_function"),
    path("revoke_authorization", views.revoke_authorization, name="revoke_authorization"),
    path("guest_sign_in", views.guest_sign_in,name="guest_sign_in"),
    path("", views.index, name="index"),
]
