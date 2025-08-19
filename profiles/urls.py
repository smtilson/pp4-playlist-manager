from django.urls import path
from . import views

urlpatterns = [
    path("profile", views.profile, name="profile"),  # type: ignore
    path("set_name", views.set_name, name="set_name"),  # type: ignore
    path(
        "revoke_authorization", views.revoke_authorization, name="revoke_authorization"  # type: ignore
    ),
    path("guest_sign_in", views.guest_sign_in, name="guest_sign_in"),
    path("redirect_action", views.redirect_action, name="redirect_action"),
    path(
        "return_from_authorization",  # type: ignore
        views.return_from_authorization,  # type: ignore
        name="return_from_authorization",
    ),
    path("delete", views.delete_profile, name="delete_profile"),  # type: ignore
    path("", views.index, name="index"),  # type: ignore
]
