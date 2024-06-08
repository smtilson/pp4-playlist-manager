from django.urls import path
from . import views

urlpatterns = [
    # attention made test home for dev reasons.
    path("profile", views.profile, name="profile"),
    #path("authorization", views.authorization, name="authorization"),
    path("test", views.test, name="test"),
    path("after-auth", views.after_auth, name="after_auth"),
    path("auth-code", views.auth_code, name="auth_code"),
    path("test_function", views.test_function, name="test_function"),
    path("remove_authorization", views.remove_authorization, name="remove_authorization"),
    path("", views.index, name="index"),
]
